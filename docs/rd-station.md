# Leads do aulão no RD Station

## Como os dados fluem

```
Formulário da página  →  /api/lead (função na Vercel)  →  RD Station Marketing  →  RD Station CRM
                                                          (conversão + tags)       (oportunidade, Kawan/Luan)
```

Cada inscrição vira uma **conversão** no RD Station Marketing com o identificador `aulao-patrimonio-alavancado` e as tags:

| Tag | Significado |
|---|---|
| `aulao-20-10` | Todo inscrito no aulão |
| `objetivo-imovel`, `objetivo-veiculo`, `objetivo-renda`, `objetivo-empresa` | O objetivo escolhido no formulário |
| `invest-ate-1k`, `invest-1k-3k`, `invest-3k-5k`, `invest-acima-5k`, `invest-nao-sabe` | A faixa de investimento mensal |

Também são enviados nome, e-mail, celular, consentimento (LGPD) e a origem do tráfego (UTMs).

---

## Passo 1: gerar a chave de API no RD (5 min)

> É preciso ter perfil **Gestor** ou **Dono** no RD Station Marketing.

1. No RD Station Marketing, abra a **App Store** e entre em **App Publisher**.
2. Clique em **Gerar chave de API** e copie a chave.

## Passo 2: guardar a chave na Vercel

1. Na Vercel, abra o projeto do aulão e vá em **Settings > Environment Variables**.
2. Crie a variável:
   - **Key:** `RD_STATION_API_KEY`
   - **Value:** a chave copiada do RD
   - **Environments:** Production e Preview
3. Salve. Depois, em **Deployments**, abra o último deploy e clique em **Redeploy**. A variável só vale a partir do próximo deploy.

> A chave fica só na Vercel. Ela não aparece no código do site nem no GitHub.

## Passo 3: testar

Faça uma inscrição na página com o seu próprio e-mail. Em até 1 minuto o contato deve aparecer na base de contatos do RD, com a conversão `aulao-patrimonio-alavancado` e as tags.

Se aparecer a mensagem "Não conseguimos confirmar sua inscrição", veja o motivo em **Vercel > projeto > Logs**. As linhas começam com `[lead]`.

## Passo 4 (opcional): campos personalizados

As tags já bastam para segmentar. Se quiser ver objetivo e investimento como campos no perfil do contato, crie dois campos personalizados de texto no RD com estes identificadores de API:

- `cf_objetivo_consorcio` (ex.: "Objetivo com consórcio")
- `cf_investimento_mensal` (ex.: "Investimento mensal")

Se os campos não existirem, a função reenvia o lead sem eles automaticamente, e nada se perde.

---

## Organização no RD Station Marketing

### Segmentações

- **Inscritos Aulão 20/10:** contatos que converteram em `aulao-patrimonio-alavancado` (ou que têm a tag `aulao-20-10`).
- **Inscritos com maior potencial:** inscritos com a tag `invest-acima-5k` ou `invest-3k-5k`. Vale chamar esses primeiro.

### Passagem para o CRM (você e o Luan)

No fluxo de automação de confirmação (abaixo), adicione a ação **Marcar como oportunidade** logo depois do e-mail 1. Com a integração entre RD Station Marketing e RD Station CRM ativa, cada inscrito vira uma negociação no CRM. Lá vocês definem o responsável de cada lead.

Sugestão de etapas no funil do CRM para este aulão:
`Inscrito` → `Contato feito` → `Participou do aulão` → `Diagnóstico agendado` → `Proposta` → `Fechado`

---

## E-mails

**E-mail 1** é enviado por um **fluxo de automação**, com entrada = conversão em `aulao-patrimonio-alavancado`. Assim ele chega na hora da inscrição.
**E-mails 2 a 6** são **e-mails agendados** para a segmentação "Inscritos Aulão 20/10".

Antes de enviar:
- Substitua os textos entre colchetes.
- Use o botão de campos dinâmicos do editor do RD para inserir o nome do contato onde aparece `[Nome]`.
- Se os bônus não forem confirmados, remova os trechos sobre eles.

### E-mail 1: confirmação (imediato, via automação)

**Assunto:** Sua vaga no Aulão Patrimônio Alavancado está confirmada
**Pré-cabeçalho:** Terça, 20/10, às 20h. Já salve na sua agenda.

> Olá, [Nome]!
>
> Sua vaga no **Aulão Patrimônio Alavancado** está garantida.
>
> **Terça-feira, 20 de outubro, às 20h (horário de Brasília)**
> Online e ao vivo
>
> O link de acesso será enviado por aqui e no nosso grupo VIP do WhatsApp. Entre no grupo agora para não perder nenhum aviso:
>
> **[Botão: Entrar no grupo VIP]** → [LINK DO GRUPO]
>
> No aulão, você vai ver:
> - por que o consórcio pode ser o crédito mais barato do mercado, e quando ele não é;
> - como planejar a contemplação com estratégia de lances;
> - como usar a carta de crédito para adquirir ativos que geram renda.
>
> Até terça!
> Equipe Monetizze Investimentos

### E-mail 2: véspera (segunda, 19/10, às 19h)

**Assunto:** Amanhã, 20h: o consórcio como estratégia de investimento
**Pré-cabeçalho:** Reserve 90 minutos na sua agenda.

> Olá, [Nome].
>
> Amanhã, às 20h, acontece o Aulão Patrimônio Alavancado.
>
> Uma pergunta para você pensar até lá: se o mesmo imóvel pode custar até R$ 255 mil a menos no total, por que tanta gente ainda escolhe o financiamento?
>
> Amanhã vamos colocar os números lado a lado e mostrar as estratégias que investidores usam para multiplicar patrimônio com consórcio, sem pagar juros.
>
> Fique até o final: quem participa ao vivo recebe o simulador consórcio x financiamento e pode agendar um diagnóstico gratuito com um especialista.
>
> **[Botão: Entrar no grupo VIP]** → [LINK DO GRUPO]
>
> Equipe Monetizze Investimentos

### E-mail 3: manhã do evento (terça, 20/10, às 10h)

**Assunto:** É hoje, [Nome]: aulão às 20h
**Pré-cabeçalho:** O link de acesso chega aqui 1 hora antes.

> Olá, [Nome]!
>
> É hoje, às 20h (horário de Brasília).
>
> Uma sugestão: anote as suas dúvidas sobre consórcio durante o dia. O último bloco do aulão é de perguntas e respostas ao vivo com os especialistas.
>
> O link de acesso chega neste e-mail e no grupo VIP 1 hora antes do início.
>
> Até a noite!
> Equipe Monetizze Investimentos

### E-mail 4: 1 hora antes (terça, 20/10, às 19h)

**Assunto:** Começa em 1 hora: aqui está o seu link
**Pré-cabeçalho:** Aulão Patrimônio Alavancado, hoje às 20h.

> [Nome], falta 1 hora.
>
> Este é o seu link de acesso ao Aulão Patrimônio Alavancado:
>
> **[Botão: Acessar o aulão]** → [LINK DA TRANSMISSÃO]
>
> Entre uns 5 minutos antes para garantir que está tudo funcionando.
>
> Te vejo lá!
> Equipe Monetizze Investimentos

### E-mail 5: ao vivo (terça, 20/10, às 20h)

**Assunto:** Estamos ao vivo agora
**Pré-cabeçalho:** Ainda dá tempo de entrar.

> [Nome], começou!
>
> O Aulão Patrimônio Alavancado está no ar agora.
>
> **[Botão: Entrar agora]** → [LINK DA TRANSMISSÃO]
>
> Equipe Monetizze Investimentos

### E-mail 6: dia seguinte (quarta, 21/10, às 10h)

**Assunto:** Obrigado por participar, [Nome]. Qual é o seu próximo passo?
**Pré-cabeçalho:** Seu diagnóstico gratuito com um especialista.

> Olá, [Nome].
>
> Obrigado por estar com a gente no Aulão Patrimônio Alavancado.
>
> Recapitulando os três pontos principais:
> 1. O consórcio troca juros por uma taxa de administração, o que muda o custo total do crédito.
> 2. Com estratégia de lances, a contemplação deixa de depender só da sorte.
> 3. A carta de crédito pode ser usada para adquirir ativos que ajudam a pagar as próprias parcelas.
>
> Agora é hora de aplicar isso ao **seu** objetivo. Nos próximos dias, o Kawan ou o Luan, da nossa equipe, vai entrar em contato pelo WhatsApp para agendar o seu diagnóstico gratuito.
>
> Se preferir adiantar, é só responder este e-mail.
>
> Equipe Monetizze Investimentos
