# Landing page do Aulão Patrimônio Alavancado (Monetizze Investimentos)

Página única (`index.html`) + uma função serverless (`api/lead.js`) na Vercel. Sem build e sem dependências.

## 1. Leads → RD Station CRM

As inscrições vão do formulário para a função `api/lead.js` (Vercel), que cria cada lead como uma **negociação** direto no **RD Station CRM** (esta conta não tem o RD Station Marketing).

Para funcionar, crie a variável de ambiente `RDCRM_TOKEN` na Vercel. O passo a passo completo, as variáveis opcionais e o aviso sobre e-mail de confirmação/lembretes estão em [docs/rd-station.md](docs/rd-station.md).

> Sem a variável configurada, o formulário mostra uma mensagem de erro ao visitante (o lead não é perdido em silêncio).

### Outras configurações (bloco `CONFIG`, no final do `index.html`)

```js
const CONFIG = {
  evento: 'Aulão Patrimônio Alavancado',
  inicio: '2026-10-20T20:00:00-03:00',   // data/hora de início (horário de Brasília)
  fim: '2026-10-20T21:30:00-03:00',      // usado na agenda e no aviso "ao vivo"
  endpoint: '/api/lead',                  // função que envia ao RD Station
  grupoWhatsapp: '',                      // link do grupo VIP (botão aparece após a inscrição)
  paginaObrigado: ''                      // opcional: redireciona para uma página de obrigado
};
```

## 2. Pixel / Analytics

Se o Meta Pixel (`fbq`), o Google Analytics (`gtag`) ou o Google Tag Manager (`dataLayer`) estiverem instalados no `<head>`, a página dispara automaticamente:

- Meta: `fbq('track', 'Lead')`
- GA4: `gtag('event', 'generate_lead')`
- GTM: `dataLayer.push({ event: 'lead_aulao' })`

## 3. O que revisar antes de publicar

- **Horário:** a página assume 20h (Brasília) e duração de 1h30.
- **Política de Privacidade:** troque os links `href="#"` pelo endereço real.
- **Logo:** o logo foi recriado em vetor a partir da identidade visual. Se tiver o SVG oficial, substitua o `<symbol id="logo">` no topo do `<body>`.
- **Simulação de custo:** os números são ilustrativos (R$ 300 mil, 240 meses, financiamento SAC a 11% a.a., consórcio com taxa de administração de 20%). Ajuste se preferir outro cenário.

## 4. Publicação

O repositório está ligado à Vercel: cada `git push` na branch `main` publica automaticamente. `README.md` e `docs/` não vão para o site (veja `.vercelignore`).
