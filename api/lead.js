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
 *   RDCRM_STAGE_NAME    (opcional) — nome exato da etapa (coluna do quadro
 *                       de negociações) onde o lead deve entrar. Busca em
 *                       todos os funis da conta. Sem ela, o lead cai na
 *                       etapa padrão da conta.
 *   RDCRM_PIPELINE_NAME (opcional, raramente necessário) — se a etapa acima
 *                       existir com o mesmo nome em mais de um funil, use
 *                       esta variável para dizer em qual funil procurar.
 *
 * Se o RD recusar a negociação com a etapa ou a fonte indicadas, a função
 * tenta de novo sem elas — o lead nunca se perde por causa disso.
 *
 * Veja docs/rd-station.md para o passo a passo completo.
 */

const CRM_BASE = 'https://crm.rdstation.com/api/v1';
const SOURCE_NAME = (process.env.RDCRM_SOURCE_NAME || 'Aulão Patrimônio Alavancado (20/10)').trim();
const PIPELINE_NAME = (process.env.RDCRM_PIPELINE_NAME || '').trim();
const STAGE_NAME = (process.env.RDCRM_STAGE_NAME || '').trim();
const VERSAO = '2026-10-09b';

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
  if (!STAGE_NAME && !PIPELINE_NAME) return null;
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

// Primeira etapa (por ordem) do primeiro funil (por ordem) da conta. Usada
// como alternativa quando o RD recusa a negociação sem etapa indicada.
async function primeiraEtapa(token) {
  try {
    const lista = await rdFetch(token, '/deal_pipelines?limit=200');
    const funis = Array.isArray(lista.json) ? lista.json : (lista.json && lista.json.deal_pipelines) || [];
    const porOrdem = (a, b) => (a.order ?? 0) - (b.order ?? 0);
    for (const funil of [...funis].sort(porOrdem)) {
      const etapa = [...(funil.deal_stages || [])].sort(porOrdem)[0];
      if (!etapa) continue;
      const ids = [...new Set([etapa.id, etapa._id].filter(Boolean))];
      return { ids, descricao: `${funil.name} > ${etapa.name}` };
    }
    console.warn('[lead] Nenhum funil com etapas retornado pelo RD:', lista.status, lista.texto.slice(0, 300));
  } catch (err) {
    console.warn('[lead] Falha ao buscar a primeira etapa:', err && err.message);
  }
  return null;
}

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ ok: false, erro: 'metodo', versao: VERSAO });
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

  const tentativas = [];
  const criar = async (corpo, rotulo) => {
    const r = await rdFetch(token, '/deals', { method: 'POST', body: corpo });
    tentativas.push({ tentativa: rotulo, status: r.status });
    if (!r.ok) console.warn(`[lead] Tentativa "${rotulo}" recusada pelo RD (${r.status}): ${r.texto.slice(0, 300)}`);
    return r;
  };

  try {
    // 1) Completo (com etapa e fonte, se houver).
    let r = await criar(payload, 'completo');

    // 2) Sem etapa e sem fonte.
    if (!r.ok && (payload.deal.deal_stage_id || payload.deal_source)) {
      delete payload.deal.deal_stage_id;
      delete payload.deal_source;
      r = await criar(payload, 'sem_etapa_fonte');
    }

    // 3) Indicando explicitamente a primeira etapa do primeiro funil — cobre o
    //    caso de a etapa padrão da conta ter sido movida ou removida no CRM.
    let primeira = null;
    if (!r.ok) {
      primeira = await primeiraEtapa(token);
      for (const id of (primeira ? primeira.ids : [])) {
        payload.deal.deal_stage_id = id;
        r = await criar(payload, `primeira_etapa:${primeira.descricao}`);
        if (r.ok) break;
      }
    }

    // 4) Contato mínimo (sem telefone estruturado nem base legal), com o
    //    WhatsApp no nome da negociação para não perder o dado.
    if (!r.ok) {
      const minimo = {
        contacts: [{ name: nome, emails: [{ email }] }],
        deal: {
          name: `${nomeDaNegociacao} · WhatsApp +55${digitos}`.slice(0, 200),
          ...(primeira && primeira.ids[0] ? { deal_stage_id: primeira.ids[0] } : {})
        }
      };
      r = await criar(minimo, 'minimo');
    }

    if (!r.ok) {
      const sondagem = {};
      for (const [rotulo, caminho] of [['listar_negociacoes', '/deals?limit=1'], ['listar_funis', '/deal_pipelines?limit=1']]) {
        try { sondagem[rotulo] = (await rdFetch(token, caminho)).status; } catch (_) { sondagem[rotulo] = 'falhou'; }
      }
      console.error('[lead] RD Station CRM recusou todas as tentativas.', JSON.stringify({ tentativas, sondagem, ultima_resposta: r.texto.slice(0, 300) }));
      return res.status(502).json({ ok: false, erro: 'crm', versao: VERSAO, tentativas, sondagem, mensagem_rd: r.texto.slice(0, 160) });
    }
    if (tentativas.length > 1) console.warn('[lead] Lead salvo depois de tentativas extras:', JSON.stringify(tentativas));
    return res.status(200).json({ ok: true });
  } catch (err) {
    console.error('[lead] Falha ao falar com o RD Station CRM:', err && err.message);
    return res.status(502).json({ ok: false, erro: 'crm', versao: VERSAO, tentativas });
  }
};
