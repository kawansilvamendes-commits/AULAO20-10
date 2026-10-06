# Landing page do Aulão Patrimônio Alavancado (Monetizze Investimentos)

Página única (`index.html`), sem build e sem dependências. Basta subir o arquivo em qualquer hospedagem estática (Netlify, Vercel, Hostinger, cPanel, GitHub Pages...).

## 1. Configuração (obrigatória antes de publicar)

No final do `index.html` existe o bloco `CONFIG`:

```js
const CONFIG = {
  evento: 'Aulão Patrimônio Alavancado',
  inicio: '2026-10-20T20:00:00-03:00',   // data/hora de início (horário de Brasília)
  fim: '2026-10-20T21:30:00-03:00',      // usado na agenda e no aviso "ao vivo"
  webhookUrl: '',                         // para onde os leads são enviados
  grupoWhatsapp: '',                      // link do grupo VIP (botão aparece após a inscrição)
  paginaObrigado: ''                      // opcional: redireciona para uma página de obrigado
};
```

> **Importante:** com `webhookUrl` vazio, o formulário mostra a confirmação, mas **o lead não é salvo em lugar nenhum**.

### Salvar leads numa planilha Google (gratuito)

1. Crie uma planilha no Google Sheets.
2. Vá em **Extensões > Apps Script**, apague o conteúdo e cole o arquivo `google-apps-script.gs`.
3. **Implantar > Nova implantação > App da Web**. Em "Executar como", escolha **Eu**. Em "Quem pode acessar", escolha **Qualquer pessoa**.
4. Copie a URL gerada (termina em `/exec`) e cole em `webhookUrl`.

Cada inscrição vira uma linha na aba **Leads**, com nome, e-mail, WhatsApp, objetivo, faixa de investimento, consentimento, UTMs e página de origem.

### Outras ferramentas (RD Station, ActiveCampaign, HubSpot, n8n, Make, Zapier)

Crie um webhook de entrada na ferramenta e cole a URL em `webhookUrl`. Os dados são enviados via `POST` como `application/x-www-form-urlencoded`, com os campos:

`data_envio, evento, nome, email, whatsapp, objetivo, investimento, consentimento, utm_source, utm_medium, utm_campaign, utm_content, utm_term, fbclid, gclid, pagina, referrer`

## 2. Pixel / Analytics

Se o Meta Pixel (`fbq`), o Google Analytics (`gtag`) ou o Google Tag Manager (`dataLayer`) estiverem instalados no `<head>`, a página dispara automaticamente:

- Meta: `fbq('track', 'Lead')`
- GA4: `gtag('event', 'generate_lead')`
- GTM: `dataLayer.push({ event: 'lead_aulao' })`

## 3. O que revisar antes de publicar

- **Horário:** a página assume 20h (Brasília) e duração de 1h30. Os horários do roteiro (20h00 a 21h20) são uma sugestão.
- **Bônus:** os três bônus (simulador, material em PDF, diagnóstico com especialista) são sugestões. Confirme se serão entregues ou remova a seção.
- **Política de Privacidade:** troque os links `href="#"` pelo endereço real.
- **Logo:** o logo foi recriado em vetor a partir da identidade visual. Se tiver o SVG oficial, substitua o `<symbol id="logo">` no topo do `<body>`.
- **Simulação de custo:** os números são ilustrativos (R$ 300 mil, 240 meses, financiamento SAC a 11% a.a., consórcio com taxa de administração de 20%). Ajuste se preferir outro cenário.

## 4. Testar localmente

```bash
python3 -m http.server 5500
```

Depois, abra `http://localhost:5500`.
