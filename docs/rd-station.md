# Leads do aulão no RD Station CRM

> Esta conta tem só o **RD Station CRM**, não o RD Station Marketing. A integração usa a API do CRM diretamente: cada inscrição no formulário vira uma **negociação** já dentro do CRM, pronta para você e o Luan distribuírem entre vocês.

## Como os dados fluem

```
Formulário da página  →  /api/lead (função na Vercel)  →  RD Station CRM
                                                           (negociação com contato e telefone)
```

Cada inscrição cria:
- um **contato** com nome, e-mail, celular e o aceite da LGPD (base legal de consentimento);
- uma **negociação** (deal) com esse contato, nomeada assim: `Nome · Objetivo · Faixa de investimento · Aulão 20/10` — por exemplo, `Ana Souza · Imóvel · Acima de R$ 5.000 · Aulão 20/10`. Assim vocês veem o essencial direto na lista de negociações, sem precisar abrir cada uma.
- a negociação sai marcada com a **fonte** "Aulão Patrimônio Alavancado (20/10)" (criada automaticamente no CRM na primeira inscrição, se ainda não existir);
- a negociação entra na **etapa padrão da conta** (hoje, a coluna "Leads"). Para direcionar para outra etapa, veja o Passo 4.

---

## Passo 1: gerar o token no RD Station CRM (2 min)

Qualquer uma destas duas telas funciona (o nome muda um pouco conforme a conta):

- Clique no seu nome (canto superior direito) → **Perfil** → se o código não aparecer, clique em **Gerar Token** e copie.
- Ou: **Configurações** → **Preferências** → **Tokens de API**.

## Passo 2: guardar o token na Vercel

1. Na Vercel, abra o projeto do aulão e vá em **Settings > Environment Variables**.
2. Crie a variável:
   - **Key:** `RDCRM_TOKEN`
   - **Value:** o token copiado do CRM
   - **Environments:** Production e Preview
3. Salve. Depois, em **Deployments**, abra o último deploy e clique em **Redeploy** — a variável só vale a partir do próximo deploy.

> O token fica só na Vercel. Não aparece no código do site nem no GitHub.

## Passo 3: testar

Inscreva-se na página com o seu próprio e-mail. Em até 1 minuto a negociação deve aparecer no RD Station CRM (na tela de Negociações, no funil e etapa padrão da conta).

Se aparecer "Não conseguimos confirmar sua inscrição", veja o motivo em **Vercel > projeto > Logs**. As linhas começam com `[lead]`.

## Passo 4 (opcional): direcionar para outra etapa

Por padrão, a negociação entra na etapa padrão da conta. Para tentar direcionar para uma etapa específica (ex.: "LIVE – LEADS"), crie a variável na Vercel:

- **Key:** `RDCRM_STAGE_NAME` → **Value:** o nome da etapa, como aparece no quadro de Negociações

> Em 08/10/2026, ao enviar a etapa "LIVE – LEADS", o RD recusou a criação da negociação (404). Por isso ficou desativado por padrão. Se ativarem de novo e o RD recusar, a função **tenta de novo sem a etapa** — o lead cai na etapa padrão, mas nunca se perde. O motivo aparece em Vercel > Logs, numa linha `[lead] RD recusou a negociação com etapa/fonte`.

## Passo 5 (opcional): renomear a fonte

Por padrão, a fonte é **"Aulão Patrimônio Alavancado (20/10)"**. Para usar outro nome, crie a variável `RDCRM_SOURCE_NAME` com o nome desejado — se não existir uma fonte com esse nome, ela é criada automaticamente.

---

## Distribuição entre você e o Luan

As negociações entram sem responsável definido. Vocês combinaram que a divisão é feita dentro do próprio CRM — no RD Station CRM isso é o campo **Responsável** de cada negociação, que pode ser definido manualmente ao abrir cada uma, ou em massa selecionando várias negociações na lista.

Sugestão de etapas de funil para este aulão, caso queiram um funil dedicado (em vez do funil padrão da conta):
`Inscrito` → `Contato feito` → `Participou do aulão` → `Diagnóstico agendado` → `Proposta` → `Fechado`

---

## ⚠️ Sobre e-mail de confirmação e lembretes

O RD Station **CRM** não tem fluxo de automação de e-mail (isso é um recurso do RD Station **Marketing**, que esta conta não tem). Hoje, quem se inscreve recebe só a confirmação na própria página — nenhum e-mail de confirmação, véspera, "1 hora antes" etc. é enviado automaticamente.

Como vocês decidiram usar e-mail + grupo de WhatsApp para os lembretes, isso precisa de uma destas soluções:

1. **WhatsApp como canal principal** — a tela de confirmação avisa que a pessoa vai receber mensagens por WhatsApp e e-mail (não há mais botão de grupo VIP na página). Os lembretes saem pelo WhatsApp da equipe.
2. **Adicionar envio de e-mail direto na função `/api/lead`** — eu implemento o envio do e-mail de confirmação (via um serviço como Resend ou SendGrid) no exato momento da inscrição. Os lembretes seguintes (véspera, 1h antes) precisariam de um agendamento separado (ex.: uma rotina programada), que também posso montar.
3. **Assinar o RD Station Marketing** — aí a automação de e-mail completa (os 6 e-mails abaixo) funciona como desenhado originalmente.

Me diga qual caminho vocês preferem e eu sigo.

Os textos abaixo ficam aqui prontos para quando a automação de e-mail existir (opção 2 ou 3):

### E-mail 1: confirmação (imediato)

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
