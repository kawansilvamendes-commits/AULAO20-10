"""Converte as páginas do Claude Design (bundle "monetizze site.html") em HTML estático
para /site, com cabeçalho comum e os efeitos do site do aulão."""
import base64, gzip, html, json, re, zlib, os, sys

BUNDLE = '/Users/kawanmendes/Downloads/monetizze site.html'
OUT = '/Users/kawanmendes/Desktop/PROJETO AULAO/site'

PAGES = {
    'ff3e92a9-44d9-41d2-83b1-ce0399d8e322': ('home', 'index.html',
        ['Consórcio', 'Home Equity', 'Auto Equity', 'Planos de Saúde', 'Carta de crédito'],
        ['Crédito', 'Patrimônio', 'Proteção', 'Monetizze Investimentos', 'Um só atendimento']),
    'cfb51c33-2713-4efb-863e-5ca4c58e315e': ('consorcio', 'consorcio/index.html',
        ['Sem juros', 'Carta de crédito', 'Imóvel', 'Veículo', 'Estratégia de lances'],
        ['Contemplação', 'Compra à vista', 'Patrimônio', 'Monetizze Investimentos', 'Planejamento']),
    '6621e3de-bacc-40b0-8ea3-13e5581ff2a1': ('equity', 'home-equity/index.html',
        ['Garantia de imóvel', 'Taxas menores', 'Prazos longos', 'Auto equity', 'Capital de giro'],
        ['Liquidez', 'Imóvel continua seu', 'Análise responsável', 'Monetizze Investimentos', 'Crédito com garantia']),
    '7f928c9f-abd8-452e-bbd3-8e78f5c3dee9': ('saude', 'planos-de-saude/index.html',
        ['Individual', 'Familiar', 'Empresarial', 'Odontológico', 'Migração de plano'],
        ['Proteção patrimonial', 'Rede credenciada', 'Carências', 'Monetizze Investimentos', 'Cotação sem compromisso']),
}

LINKS = [
    (r'\./Monetizze Cons%C3%B3rcio\.dc\.html', '/site/consorcio/'),
    (r'\./Monetizze Consórcio\.dc\.html', '/site/consorcio/'),
    (r'\./Monetizze Home Equity\.dc\.html', '/site/home-equity/'),
    (r'\./Monetizze Planos de Saude\.dc\.html', '/site/planos-de-saude/'),
    (r'\./Monetizze Investimentos v2\.dc\.html', '/site/'),
    (r'\./monetizze-logo-branca\.png', '/site/logo-monetizze.png'),
]

MSG_CONSULTOR = 'Olá! Vim pelo site da Monetizze e gostaria de falar com um consultor.'


def load_bundle():
    t = open(BUNDLE, encoding='utf-8').read()
    man = json.loads(re.search(r'<script type="__bundler/manifest">\s*(.*?)\s*</script>', t, re.S).group(1))
    out = {}
    for k, v in man.items():
        raw = base64.b64decode(v['data'])
        if v.get('compressed') in (True, 'True', 'true'):
            for f in (gzip.decompress, zlib.decompress, lambda b: zlib.decompress(b, -15)):
                try:
                    raw = f(raw); break
                except Exception:
                    pass
        out[k] = raw
    return out


def header_html():
    nav = [('home', '/site/', 'Início'), ('consorcio', '/site/consorcio/', 'Consórcio'),
           ('equity', '/site/home-equity/', 'Home Equity'), ('saude', '/site/planos-de-saude/', 'Planos de Saúde'), ('tributario', '/site/tributario/', 'Tributário')]
    desk = '\n'.join(f'        <a href="{u}" data-nav="{k}">{t}</a>' for k, u, t in nav)
    mob = '\n'.join(f'        <a href="{u}" data-nav="{k}">{t}</a>' for k, u, t in nav)
    return f'''<header class="mz-header">
    <div class="mz-header__inner">
      <a class="mz-brand" href="/site/" aria-label="Monetizze Investimentos, início"><img src="/site/logo-monetizze.png" alt="Monetizze Investimentos" width="923" height="215"></a>
      <nav class="mz-nav" aria-label="Páginas">
{desk}
        <a class="mz-cta" data-wa="{MSG_CONSULTOR}" href="#" target="_blank" rel="noopener">Falar com um consultor</a>
      </nav>
      <div class="mz-mobile">
        <a class="mz-cta" data-wa="{MSG_CONSULTOR}" href="#" target="_blank" rel="noopener">Consultor</a>
        <button class="mz-menu" type="button" aria-label="Abrir menu" aria-expanded="false" data-menu><span></span><span></span></button>
      </div>
    </div>
    <div class="mz-mnav"><div>
      <nav aria-label="Páginas">
{mob}
      </nav>
    </div></div>
  </header>'''


def tapes_html(a, b):
    tri = '<svg><use href="#i-tri"/></svg>'
    ta = ''.join(f'<span class="tape__item">{html.escape(x)}{tri}</span>' for x in a)
    tb = ''.join(f'<span class="tape__item">{html.escape(x)}{tri}</span>' for x in b)
    return f'''
  <div class="tapes" aria-hidden="true">
    <div class="tape tape--b"><div class="tape__track" data-marquee>{ta}</div></div>
    <div class="tape tape--a"><div class="tape__track" data-marquee>{tb}</div></div>
  </div>
'''


DECOR_HERO = ('<div class="bg-grid" aria-hidden="true"></div><div class="blob blob--1" aria-hidden="true"></div>'
              '<div class="blob blob--2" aria-hidden="true"></div><div class="blob blob--3" aria-hidden="true"></div>'
              '<svg class="hero__mark" viewBox="-2 -2 184 104" aria-hidden="true"><use href="#mk"/></svg>')
DECOR_FINAL = ('<div class="bg-grid" aria-hidden="true"></div><div class="blob blob--1" aria-hidden="true"></div>'
               '<div class="blob blob--2" aria-hidden="true"></div><span class="fx-ring" aria-hidden="true"></span>')


def convert(src, key, tapes_a, tapes_b):
    src = re.sub(r'/\*[^*]*\*/\s*@font-face\s*\{[^}]*\}\s*', '', src)
    title = re.search(r'<title>(.*?)</title>', src, re.S).group(1).strip()
    desc = re.search(r'<meta name="description" content="([^"]*)"', src).group(1)
    kw_m = re.search(r'<meta name="keywords" content="([^"]*)"', src)
    kw = kw_m.group(1) if kw_m else ''

    dc_script = re.search(r'<script type="text/x-dc"[^>]*?data-props="(.*?)">(.*?)</script>', src, re.S)
    props_raw = html.unescape(dc_script.group(1))
    props = {k: v.get('default') for k, v in json.loads(props_raw).items() if isinstance(v, dict) and 'default' in v}
    logic = dc_script.group(2).strip()

    body = src.split('<template id="__bundler_thumbnail">')[1] if '__bundler_thumbnail' in src else src
    body = body[body.index('<div style="width:100%;overflow-x:hidden'):]
    body = body[:body.rindex('</x-dc>')]
    body = body.rstrip()
    assert body.endswith('</div>')

    # cabeçalho comum
    body = re.sub(r'<header .*?</header>', '%%HEADER%%', body, count=1, flags=re.S)
    body = body.replace('overflow-x:hidden', 'overflow-x:clip', 1)

    # depoimentos que eram espaços reservados não vão para o ar
    body = re.sub(r'\s*<section id="autoridade".*?</section>', '', body, flags=re.S)

    # sc-if → wrappers
    out, stack = [], []
    for part in re.split(r'(<sc-if [^>]*>|</sc-if>)', body):
        m = re.match(r'<sc-if value="\{\{\s*(\w+)\s*\}\}"[^>]*>', part)
        if m:
            name = m.group(1)
            if name in ('wide', 'narrow'):
                out.append(f'<div class="only-{name}">'); stack.append('</div>')
            else:
                out.append(f'<div class="if-wrap" data-if="{name}"><div>'); stack.append('</div></div>')
        elif part == '</sc-if>':
            out.append(stack.pop())
        else:
            out.append(part)
    body = ''.join(out)

    # espaços de foto
    # ilustrações geradas por fontes/ilustracoes.py (img/<id>.svg)
    def slot(m):
        uid = re.search(r'id="([^"]+)"', m.group(0)).group(1)
        uid = {'mz-kawan': 'mz-sobre'}.get(uid, uid)
        # foto real (jpg/webp/png) tem prioridade sobre a ilustração
        for ext in ('jpg', 'webp', 'png', 'svg'):
            if os.path.exists(os.path.join(OUT, 'img', f'{uid}.{ext}')):
                return f'<img class="ph-img" src="/site/img/{uid}.{ext}" alt="" loading="lazy" decoding="async">'
        return '<div class="ph" aria-hidden="true"><svg viewBox="-2 -2 184 104"><use href="#mk"/></svg></div>'
    body = re.sub(r'<image-slot [^>]*></image-slot>', slot, body)

    # hover inline → CSS
    hovers = {}
    def hv(m):
        css = m.group(1)
        n = hovers.setdefault(css, len(hovers))
        return f'data-hv="{n}"'
    body = re.sub(r'style-hover="([^"]*)"', hv, body)
    hover_css = '\n'.join(
        f'[data-hv="{n}"]:hover {{ ' + '; '.join(d.strip() + ' !important' for d in css.split(';') if d.strip()) + '; }'
        for css, n in hovers.items())

    # eventos e atributos dinâmicos
    body = re.sub(r'onClick="\{\{\s*(\w+)\s*\}\}"', r'data-on-click="\1"', body)
    body = re.sub(r'onInput="\{\{\s*(\w+)\s*\}\}"', r'data-on-input="\1"', body)
    body = re.sub(r'(\s)([\w-]+)="([^"]*\{\{[^"]*)"', lambda m: f'{m.group(1)}data-tpl-{m.group(2)}="{m.group(3)}"', body)
    # href dinâmico precisa de um valor inicial
    body = re.sub(r'(<a )(?![^>]*\shref=)([^>]*data-tpl-href)', r'\1href="#" \2', body)
    body = ''.join(part if part.startswith('<') else re.sub(r'\{\{\s*([\w.]+)\s*\}\}', r'<span data-v="\1"></span>', part)
                   for part in re.split(r'(<[^>]+>)', body))

    for pat, rep in LINKS:
        body = re.sub(pat, rep, body)

    # topo: efeitos
    hs = body.index('<section', body.index('%%HEADER%%'))
    he = body.index('>', hs)
    tag = body[hs:he]
    tag = tag.replace('<section', '<section class="fx-hero fx-dark fx-has-tapes"', 1)
    body = body[:hs] + tag + body[he:]
    # decoração depois do fundo em degradê (primeira div absoluta)
    m = re.compile(r'(<div style="position:absolute;inset:0;[^"]*"></div>)').search(body, hs)
    body = body[:m.end()] + DECOR_HERO + body[m.end():]
    # título palavra a palavra, com o destaque em degradê
    h1s = body.index('<h1', hs)
    h1e = body.index('</h1>', h1s)
    h1 = body[h1s:h1e]
    h1 = h1.replace('<h1 ', '<h1 data-split ', 1)
    h1 = re.sub(r'<span style="color:#7FB3DE;font-weight:400">(.*?)</span>', r'<em class="grad">\1</em>', h1)
    body = body[:h1s] + h1 + body[h1e:]
    # faixas depois do topo
    se = body.index('</section>', hs) + len('</section>')
    body = body[:se] + tapes_html(tapes_a, tapes_b) + body[se:]

    # chamada final escura
    for m in list(re.finditer(r'<section ([^>]*background:#071D30[^>]*)>', body))[::-1]:
        tag = '<section class="fx-dark" ' + m.group(1) + '>'
        inner_start = m.end()
        g = re.compile(r'<div style="position:absolute;inset:0;[^"]*"></div>').match(body, inner_start + len(re.match(r'\s*', body[inner_start:]).group(0)))
        if g:
            body = body[:m.start()] + tag + body[inner_start:g.end()] + DECOR_FINAL + body[g.end():]
        else:
            body = body[:m.start()] + tag + body[inner_start:]

    body = body.replace('%%HEADER%%', header_html())

    page = f'''<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <meta name="keywords" content="{kw}">
  <meta name="theme-color" content="#071D30">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='-10 -40 200 180'%3E%3Crect x='-10' y='-40' width='200' height='180' fill='%230B2A45'/%3E%3Cg fill='%23fff'%3E%3Cpath d='M0 100L64.7 0 87.7 35.5 46.4 100Z'/%3E%3Cpath fill-rule='evenodd' d='M51.7 100L115.7 0 179.7 100ZM89 100L115.7 49 142.4 100Z'/%3E%3Cpath d='M100 100L115.7 74.5 131.4 100Z'/%3E%3C/g%3E%3C/svg%3E">
  <script>document.documentElement.classList.add('js')</script>
  <link rel="stylesheet" href="/site/assets/efeitos.css">
  <style>
{hover_css}
  </style>
</head>
<body data-page="{key}">
  <svg class="sprite" aria-hidden="true" focusable="false">
    <symbol id="mk" viewBox="0 0 180 100"><path d="M0 100L64.7 0 87.7 35.5 46.4 100Z"/><path fill-rule="evenodd" d="M51.7 100L115.7 0 179.7 100ZM89 100L115.7 49 142.4 100Z"/><path d="M100 100L115.7 74.5 131.4 100Z"/></symbol>
    <symbol id="i-tri" viewBox="0 0 11 10"><path d="M5.5 0L11 10H0z" fill="currentColor"/></symbol>
  </svg>
  <div class="progress" aria-hidden="true"></div>
  <main>
{body}
  </main>
  <script src="/site/assets/efeitos.js"></script>
  <script>
{logic}
MZ.mount(Component, {json.dumps(props, ensure_ascii=False)});
  </script>
</body>
</html>
'''
    return page


def add_footer_link(page):
    i, j = page.index('<footer'), page.index('</footer>')
    ft = page[i:j]
    if 'href="/site/tributario/"' in ft:
        return page
    m = re.search(r'<a href="/site/planos-de-saude/"[^>]*>Planos de Saúde</a>', ft) or re.search(r'<a href="/site/"[^>]*>Todas as soluções</a>', ft)
    a = m.group(0)
    novo = re.sub(r'href="[^"]*"', 'href="/site/tributario/"', a, 1)
    novo = re.sub(r'>[^<]*</a>$', '>Tributário</a>', novo)
    ft = ft.replace(a, a + '\n          ' + novo, 1) if 'Planos de Saúde</a>' in a else ft.replace(a, novo + '\n          ' + a, 1)
    return page[:i] + ft + page[j:]


def hero_tributario(src):
    """Home: Tributário como 4ª opção no herói, ao lado das outras três frentes."""
    m = re.search(r'<a href="\./Monetizze Planos de Saude\.dc\.html" style="background:rgba\(255,255,255,0\.06\).*?</a>', src, re.S)
    card = m.group(0)
    novo = card.replace('./Monetizze Planos de Saude.dc.html', '/site/tributario/', 1)
    novo = novo.replace('>Planos de Saúde<', '>Tributário<', 1).replace('>Proteção do que você construiu<', '>Planejamento fiscal para sua empresa<', 1)
    src = src.replace(card, card + '\n' + novo, 1)
    src = src.replace('Consórcio, home equity e planos de saúde em um só atendimento. Reunimos as três frentes',
                      'Consórcio, home equity, planos de saúde e planejamento tributário em um só atendimento. Reunimos as quatro frentes', 1)
    src = re.sub(r'>3(</span>\s*<span[^>]*>Frentes de negócio)', r'>4\1', src, 1)
    return src


FONE_ANTIGO, FONE = '5565996039092', '5565996745162'


def site_da_empresa(page):
    """O site fala pela Monetizze: número principal da empresa e nenhuma menção pessoal."""
    page = page.replace(FONE_ANTIGO, FONE)
    page = page.replace(', Kawan Mendes">', '">')
    trocas = [
        ('À frente do atendimento está Kawan Mendes, consultor responsável pelo conteúdo educativo da marca no Instagram e pela estratégia de cada operação estruturada aqui.',
         'Cada cliente tem um consultor dedicado da nossa equipe, que acompanha a operação do primeiro contato até o fim, com a estratégia desenhada para o seu caso.'),
        ('Consultor responsável <strong style="font-weight:600;color:#124A7C;text-align:right">Kawan Mendes</strong>',
         'Atendimento <strong style="font-weight:600;color:#124A7C;text-align:right">Consultor dedicado</strong>'),
        ('Atuação <strong style="font-weight:600;color:#124A7C;text-align:right">Consórcio · Equity · Saúde</strong>',
         'Atuação <strong style="font-weight:600;color:#124A7C;text-align:right">Consórcio · Equity · Saúde · Tributário</strong>'),
        ('Conversar com o Kawan →', 'Falar com a Monetizze →'),
    ]
    for a, b in trocas:
        page = page.replace(a, b)
    # linha "Conteúdo educativo @…" do Sobre e o Instagram pessoal do rodapé
    page = re.sub(r'\s*<span [^>]*>Conteúdo educativo <a [^>]*instagramLink[^>]*>[^<]*</a></span>', '', page)
    page = re.sub(r'\s*<a href="#" data-tpl-href="\{\{ instagramLink \}\}"[^>]*>[^<]*</a>', '', page)
    page = page.replace('kawannmendess', '')
    assert 'Kawan' not in page and 'kawann' not in page
    return page


TRIB = ('tributario', 'tributario/index.html',
        ['Reforma Tributária', 'CBS e IBS', 'Recuperação de créditos', 'Incentivos fiscais', 'Governança'],
        ['Planejamento tributário', 'Compliance', 'Split payment', 'Monetizze + Valorya', 'Diagnóstico gratuito'])


def main():
    files = load_bundle()
    home_src = files['ff3e92a9-44d9-41d2-83b1-ce0399d8e322'].decode('utf-8')
    footer = re.search(r'<footer .*?</footer>', home_src, re.S).group(0)
    footer = re.sub(r'href="#(solucoes|simulador|sobre)"', r'href="./Monetizze Investimentos v2.dc.html#\1"', footer)
    trib_src = open(os.path.join(OUT, 'fontes/tributario.dc.html'), encoding='utf-8').read().replace('%%FOOTER%%', footer)
    jobs = [(files[uid].decode('utf-8'), key, path, ta, tb) for uid, (key, path, ta, tb) in PAGES.items()]
    jobs[0] = (hero_tributario(jobs[0][0]),) + jobs[0][1:]
    jobs.append((trib_src, TRIB[0], TRIB[1], TRIB[2], TRIB[3]))
    for src, key, path, ta, tb in jobs:
        page = site_da_empresa(add_footer_link(convert(src, key, ta, tb)))
        dest = os.path.join(OUT, path)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        open(dest, 'w', encoding='utf-8').write(page)
        left = re.findall(r'\{\{[^}]*\}\}', page.split('<script src="/site/assets/efeitos.js">')[0])
        tpl_attrs = len(re.findall(r'data-tpl-', page))
        print(f'{path}: {len(page)} bytes, data-tpl={tpl_attrs}, sobras de {{{{}}}} fora de atributos: {len([x for x in left])}')


main()
