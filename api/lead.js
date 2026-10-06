/**
 * Recebe as inscrições do formulário e envia para o RD Station Marketing
 * como uma conversão. A chave fica na variável de ambiente RD_STATION_API_KEY
 * (Vercel > Settings > Environment Variables), nunca no código do site.
 */

const RD_URL = 'https://api.rd.services/platform/conversions';
const CONVERSION_ID = 'aulao-patrimonio-alavancado';
const TAG_EVENTO = 'aulao-20-10';

// Só aceitamos os valores que existem no formulário; cada um vira uma tag para segmentar no RD.
const OBJETIVOS = {
  'Imóvel': 'objetivo-imovel',
  'Veículo': 'objetivo-veiculo',
  'Investir e gerar renda': 'objetivo-renda',
  'Para minha empresa': 'objetivo-empresa'
};
const INVESTIMENTOS = {
  'Até R$ 1.000': 'invest-ate-1k',
  'De R$ 1.000 a R$ 3.000': 'invest-1k-3k',
  'De R$ 3.000 a R$ 5.000': 'invest-3k-5k',
  'Acima de R$ 5.000': 'invest-acima-5k',
  'Ainda não sei': 'invest-nao-sabe'
};

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

async function enviarConversao(apiKey, payload) {
  const resp = await fetch(`${RD_URL}?api_key=${encodeURIComponent(apiKey)}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', accept: 'application/json' },
    body: JSON.stringify({ event_type: 'CONVERSION', event_family: 'CDP', payload }),
    signal: AbortSignal.timeout(9000)
  });
  const corpo = await resp.text();
  return { ok: resp.ok, status: resp.status, corpo };
}

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', 'POST');
    return res.status(405).json({ ok: false, erro: 'metodo' });
  }

  const dados = lerCorpo(req);

  // Campo invisível para humanos: se vier preenchido, é robô. Respondemos "ok" sem enviar nada.
  if (texto(dados.website)) return res.status(200).json({ ok: true });

  const nome = texto(dados.nome, 120);
  const email = texto(dados.email, 160).toLowerCase();
  const digitos = texto(dados.whatsapp, 30).replace(/\D/g, '');
  const consentiu = dados.consentimento === 'sim';

  if (nome.length < 3 || !emailValido(email) || !(digitos.length === 10 || digitos.length === 11) || !consentiu) {
    return res.status(422).json({ ok: false, erro: 'dados_invalidos' });
  }

  const apiKey = process.env.RD_STATION_API_KEY;
  if (!apiKey) {
    console.error('[lead] RD_STATION_API_KEY não configurada na Vercel. Lead não enviado.');
    return res.status(500).json({ ok: false, erro: 'configuracao' });
  }

  const objetivo = OBJETIVOS[dados.objetivo] ? dados.objetivo : '';
  const investimento = INVESTIMENTOS[dados.investimento] ? dados.investimento : '';

  const payload = {
    conversion_identifier: CONVERSION_ID,
    name: nome,
    email,
    mobile_phone: `+55 ${digitos.slice(0, 2)} ${digitos.slice(2, -4)}-${digitos.slice(-4)}`,
    tags: [TAG_EVENTO, OBJETIVOS[objetivo], INVESTIMENTOS[investimento]].filter(Boolean),
    available_for_mailing: true,
    legal_bases: [{ category: 'communications', type: 'consent', status: 'granted' }]
  };

  const opcionais = {
    traffic_source: texto(dados.utm_source, 100),
    traffic_medium: texto(dados.utm_medium, 100),
    traffic_campaign: texto(dados.utm_campaign, 100),
    traffic_value: texto(dados.utm_term, 100),
    client_tracking_id: texto(dados.client_tracking_id, 100),
    // Campos personalizados (opcionais): crie no RD com estes identificadores para vê-los no perfil do lead.
    cf_objetivo_consorcio: objetivo,
    cf_investimento_mensal: investimento
  };
  for (const [chave, valor] of Object.entries(opcionais)) {
    if (valor) payload[chave] = valor;
  }

  try {
    let r = await enviarConversao(apiKey, payload);

    // Se os campos personalizados ainda não existirem no RD, a API recusa (400). Reenviamos sem eles:
    // as tags já carregam objetivo e investimento.
    if (r.status === 400 && (payload.cf_objetivo_consorcio || payload.cf_investimento_mensal)) {
      console.warn('[lead] RD recusou com campos personalizados, reenviando sem eles:', r.corpo);
      delete payload.cf_objetivo_consorcio;
      delete payload.cf_investimento_mensal;
      r = await enviarConversao(apiKey, payload);
    }

    if (!r.ok) {
      console.error(`[lead] RD Station respondeu ${r.status}:`, r.corpo);
      return res.status(502).json({ ok: false, erro: 'crm' });
    }
    return res.status(200).json({ ok: true });
  } catch (err) {
    console.error('[lead] Falha ao falar com o RD Station:', err && err.message);
    return res.status(502).json({ ok: false, erro: 'crm' });
  }
};
