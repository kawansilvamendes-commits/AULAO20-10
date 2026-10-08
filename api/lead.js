/**
 * Recebe as inscrições do formulário e cria uma negociação no RD Station CRM
 * (não no RD Station Marketing — esta conta usa só o CRM).
 *
 * Configuração na Vercel (Settings > Environment Variables):
 *   RDCRM_TOKEN        (obrigatório) — token do usuário, gerado no RD Station CRM
 *                       em Perfil > Gerar Token, ou em Configurações > Preferências
 *                       > Tokens de API.
 *   RDCRM_SOURCE_NAME   (opcional) — nome da "fonte" da negociação no CRM.
 *                       Se não existir uma fonte com esse nome, ela é criada
 *                       automaticamente na primeira inscrição. Padrão abaixo.
 *   RDCRM_PIPELINE_NAME (opcional) — nome exato do funil onde a negociação
 *                       deve entrar (ex.: "LIVE – LEADS"). Se não for
 *                       encontrado, a negociação NÃO entra em nenhum funil
 *                       específico (para não arriscar cair num funil
 *                       errado) — mas o lead nunca se perde por isso.
 *   RDCRM_STAGE_NAME    (opcional) — nome exato da etapa, dentro do funil
 *                       acima, onde a negociação deve entrar. Se vazio ou
 *                       não encontrada, usa a primeira etapa do funil.
 *
 * Os padrões abaixo (funil "LIVE – LEADS", etapa "Em andamento") refletem o
 * funil criado no RD Station CRM em 08/10/2026. Ajuste via variável de
 * ambiente se os nomes mudarem.
 *
 * Veja docs/rd-station.md para o passo a passo completo.
 */

const CRM_BASE = 'https://crm.rdstation.com/api/v1';
const SOURCE_NAME = (process.env.RDCRM_SOURCE_NAME || 'Aulão Patrimônio Alavancado (20/10)').trim();
const PIPELINE_NAME = (process.env.RDCRM_PIPELINE_NAME || 'LIVE – LEADS').trim();
const STAGE_NAME = (process.env.RDCRM_STAGE_NAME || 'Em andamento').trim();

// Compara nomes de forma bem tolerante: tira acento, maiúsculas/minúsculas
// e QUALQUER espaço, hífen, en-dash (–), em-dash (—) ou outra pontuação.
// "LIVE – LEADS", "live-leads" e "Live Leads" todas ficam "liveleads".
const chave = s => texto(s).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]/g, '');

// Cache em memória: vale enquanto a função serverless ficar "quente" entre
// chamadas, só para evitar repetir essas duas consultas em toda inscrição.
let cachedSourceId = null;
let stageLookupDone = false;
let cachedStageId = null;

const OBJETIVOS = new Set(['Imóvel', 'Veículo', 'Investir e gerar renda', 'Para minha empresa']);
const INVESTIMENTOS = new Set(['Até R$ 1.000', 'De R$ 1.000 a R$ 3.000', 'De R$ 3.000 a R$ 5.000', 'Acima de R$ 5.000', 'Ainda não sei']);

const texto = (v, max = 200) => String(v ?? '').trim().slice(0, max);
const emailValido = v => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v);

function lerCorpo(req) {
  const b = req.body;
  if (b && typeof b === 'object') return b;
  if (typeof b === 'string') {
    try { return JSON.parse(b); } catch (_) { return {}; }
  }
  return {};
}

async function rdFetch(token, path, { method = 'GET', body } = {}) {
  const url = `${CRM_BASE}${path}${path.includes('?') ? '&' : '?'}token=${encodeURIComponent(token)}`;
  const resp = await fetch(url, {
    method,
    headers: { 'Content-Type': 'application/json', accept: 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
    signal: AbortSignal.timeout(9000)
  });
  const texto = await resp.text();
  let json = null;
  try { json = texto ? JSON.parse(texto) : null; } catch (_) { /* resposta não-JSON */ }
  return { ok: resp.ok, status: resp.status, texto, json };
}

// Acha (ou cria, na primeira vez) a "fonte" da negociação pelo nome.
async function resolveSourceId(token) {
  if (cachedSourceId) return cachedSourceId;
  try {
    const lista = await rdFetch(token, '/deal_sources?limit=200');
    const fontes = Array.isArray(lista.json) ? lista.json : (lista.json && lista.json.deal_sources) || [];
    if (!fontes.length) console.warn('[lead] GET /deal_sources não retornou nenhuma fonte. Resposta recebida:', lista.status, lista.texto.slice(0, 500));
    const achada = fontes.find(f => chave(f.name) === chave(SOURCE_NAME));
    if (achada) {
      cachedSourceId = achada._id || achada.id;
      return cachedSourceId;
    }
    const criada = await rdFetch(token, '/deal_sources', {
      method: 'POST',
      body: { deal_source: { name: SOURCE_NAME, description: 'Criada automaticamente pela landing page do aulão.' } }
    });
    // Mesmo quando o RD recusa (ex.: 422 porque o nome já existe), a resposta
    // costuma trazer o próprio registro existente — aproveitamos o _id dela
    // em vez de desistir.
    if (criada.json && (criada.json._id || criada.json.id)) {
      cachedSourceId = criada.json._id || criada.json.id;
      return cachedSourceId;
    }
    console.warn('[lead] Não consegui achar nem criar a fonte no RD CRM:', criada.status, criada.texto);
  } catch (err) {
    console.warn('[lead] Falha ao resolver a fonte da negociação no RD CRM:', err && err.message);
  }
  return null;
}

// Acha o id da etapa onde a negociação deve entrar.
// Se RDCRM_PIPELINE_NAME estiver definido, a busca é restrita a ESSE funil
// (evita cair na etapa de mesmo nome de outro funil, por engano). Sem um
// funil configurado, procura a etapa em todos os funis da conta.
async function resolveStageId(token) {
  if (stageLookupDone) return cachedStageId;
  stageLookupDone = true;
  try {
    const lista = await rdFetch(token, '/deal_pipelines?limit=200');
    const funis = Array.isArray(lista.json) ? lista.json : (lista.json && lista.json.deal_pipelines) || [];

    if (!funis.length) {
      console.warn('[lead] GET /deal_pipelines não retornou nenhum funil. Resposta recebida:', lista.status, lista.texto.slice(0, 500));
      return null;
    }

    let candidatos = funis;
    if (PIPELINE_NAME) {
      const alvo = chave(PIPELINE_NAME);
      const funil = funis.find(f => chave(f.name) === alvo || chave(f.nickname) === alvo);
      if (!funil) {
        console.warn(`[lead] Funil "${PIPELINE_NAME}" (RDCRM_PIPELINE_NAME) não encontrado. Funis existentes na conta: ${funis.map(f => `"${f.name}"`).join(', ')}. Negociação criada sem funil específico.`);
        return null;
      }
      candidatos = [funil];
    }

    for (const funil of candidatos) {
      const etapas = [...(funil.deal_stages || [])].sort((a, b) => (a.order ?? 0) - (b.order ?? 0));
      if (!etapas.length) continue;
      const alvoEtapa = chave(STAGE_NAME);
      const achada = STAGE_NAME ? etapas.find(e => chave(e.name) === alvoEtapa || chave(e.nickname) === alvoEtapa) : null;
      if (achada) { cachedStageId = achada._id || achada.id; break; }
      // Etapa não informada ou não encontrada: se já sabemos o funil certo
      // (PIPELINE_NAME casou), usamos a primeira etapa dele como fallback
      // seguro, em vez de desistir.
      if (PIPELINE_NAME) {
        if (STAGE_NAME) console.warn(`[lead] Etapa "${STAGE_NAME}" não encontrada no funil "${funil.name}". Etapas existentes nele: ${etapas.map(e => `"${e.name}"`).join(', ')}. Usando a primeira etapa dele.`);
        cachedStageId = etapas[0]._id || etapas[0].id;
        break;
      }
    }
    if (!cachedStageId && !PIPELINE_NAME) console.warn(`[lead] Etapa "${STAGE_NAME}" (RDCRM_STAGE_NAME) não encontrada em nenhum funil. Usando a etapa padrão da conta.`);
  } catch (err) {
    console.warn('[lead] Falha ao resolver a etapa de funil no RD CRM:', err && err.message);
  }
  return cachedStageId;
}

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ ok: false, erro: 'metodo' });
  }

  const dados = lerCorpo(req);

  // Campo invisível para humanos: se vier preenchido, é robô. Respondemos "ok" sem criar nada.
  if (texto(dados.website)) return res.status(200).json({ ok: true });

  const nome = texto(dados.nome, 120);
  const email = texto(dados.email, 160).toLowerCase();
  const digitos = texto(dados.whatsapp, 30).replace(/\D/g, '');
  const consentiu = dados.consentimento === 'sim';

  if (nome.length < 3 || !emailValido(email) || !(digitos.length === 10 || digitos.length === 11) || !consentiu) {
    return res.status(422).json({ ok: false, erro: 'dados_invalidos' });
  }

  const token = process.env.RDCRM_TOKEN;
  if (!token) {
    console.error('[lead] RDCRM_TOKEN não configurada na Vercel. Lead não enviado.');
    return res.status(500).json({ ok: false, erro: 'configuracao' });
  }

  const objetivo = OBJETIVOS.has(dados.objetivo) ? dados.objetivo : '';
  const investimento = INVESTIMENTOS.has(dados.investimento) ? dados.investimento : '';

  const [sourceId, stageId] = await Promise.all([resolveSourceId(token), resolveStageId(token)]);

  const nomeDaNegociacao = [nome, objetivo, investimento].filter(Boolean).join(' · ') + ' · Aulão 20/10';

  const payload = {
    contacts: [{
      name: nome,
      emails: [{ email }],
      phones: [{ phone: `+55${digitos}`, type: 'home' }],
      legal_bases: [{ type: 'consent', category: 'communications', status: 'granted' }]
    }],
    deal: {
      name: nomeDaNegociacao.slice(0, 200),
      ...(stageId ? { deal_stage_id: stageId } : {})
    },
    ...(sourceId ? { deal_source: { _id: sourceId } } : {})
  };

  try {
    const r = await rdFetch(token, '/deals', { method: 'POST', body: payload });
    if (!r.ok) {
      console.error(`[lead] RD Station CRM respondeu ${r.status}:`, r.texto);
      return res.status(502).json({ ok: false, erro: 'crm' });
    }
    return res.status(200).json({ ok: true });
  } catch (err) {
    console.error('[lead] Falha ao falar com o RD Station CRM:', err && err.message);
    return res.status(502).json({ ok: false, erro: 'crm' });
  }
};
