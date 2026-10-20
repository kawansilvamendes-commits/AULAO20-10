"""Gera as ilustrações (SVG) que ocupam os espaços de foto do site.
São modelos ilustrativos na paleta da Monetizze; podem ser trocados por fotos reais
mantendo o mesmo nome de arquivo em /site/img (ou mudando a extensão no converter)."""
import os

OUT = os.path.join(os.path.dirname(__file__), '..', 'img')

NAVY, DEEP, MID, BLUE, SKY, LIGHT, PALE, WHITE = '#0B2A45', '#071D30', '#124A7C', '#2E7BB8', '#5B9BD5', '#9CC6E8', '#EAF2F9', '#FFFFFF'
SKIN = ['#E9C3A3', '#C8936E', '#8E5C40']
HAIR = ['#1B2330', '#4A2E22', '#2B1B14']


# ---------------------------------------------------------------- fundo

def fundo(w, h, escuro, uid):
    if escuro:
        grad = (f'<radialGradient id="bg{uid}" cx="22%" cy="0%" r="120%">'
                f'<stop offset="0" stop-color="{MID}"/><stop offset=".55" stop-color="{NAVY}"/><stop offset="1" stop-color="{DEEP}"/></radialGradient>')
        linha, chao, sol = 'rgba(156,198,232,.08)', 'rgba(156,198,232,.10)', 'rgba(91,155,213,.18)'
    else:
        grad = (f'<linearGradient id="bg{uid}" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0" stop-color="{PALE}"/><stop offset="1" stop-color="#F7FAFD"/></linearGradient>')
        linha, chao, sol = 'rgba(18,74,124,.06)', 'rgba(18,74,124,.08)', 'rgba(91,155,213,.16)'
    grid = ''.join(f'<path d="M{x} 0V{h}" />' for x in range(0, w + 1, 40)) + ''.join(f'<path d="M0 {y}H{w}" />' for y in range(0, h + 1, 40))
    return (f'<defs>{grad}</defs><rect width="{w}" height="{h}" fill="url(#bg{uid})"/>'
            f'<g stroke="{linha}" stroke-width="1">{grid}</g>'
            f'<circle cx="{w * .72:.0f}" cy="{h * .3:.0f}" r="{min(w, h) * .3:.0f}" fill="{sol}"/>'
            f'<ellipse cx="{w / 2:.0f}" cy="{h * .86:.0f}" rx="{w * .46:.0f}" ry="{h * .05:.0f}" fill="{chao}"/>')


# ---------------------------------------------------------------- peças

def pessoa(x, base, h, roupa, calca, pele=0, cabelo=0, longo=False, braco=None, gravata=None):
    """Pessoa em pé, vista de frente. x = centro, base = pés."""
    s = h / 100
    p = SKIN[pele]
    out = [f'<g>']
    # pernas e sapatos
    out.append(f'<rect x="{x - 13 * s:.1f}" y="{base - 46 * s:.1f}" width="{11 * s:.1f}" height="{44 * s:.1f}" rx="{3 * s:.1f}" fill="{calca}"/>')
    out.append(f'<rect x="{x + 2 * s:.1f}" y="{base - 46 * s:.1f}" width="{11 * s:.1f}" height="{44 * s:.1f}" rx="{3 * s:.1f}" fill="{calca}"/>')
    out.append(f'<ellipse cx="{x - 8 * s:.1f}" cy="{base - 1 * s:.1f}" rx="{8 * s:.1f}" ry="{3 * s:.1f}" fill="{DEEP}"/>')
    out.append(f'<ellipse cx="{x + 8 * s:.1f}" cy="{base - 1 * s:.1f}" rx="{8 * s:.1f}" ry="{3 * s:.1f}" fill="{DEEP}"/>')
    # braços
    out.append(f'<rect x="{x - 25 * s:.1f}" y="{base - 80 * s:.1f}" width="{8 * s:.1f}" height="{36 * s:.1f}" rx="{4 * s:.1f}" fill="{roupa}"/>')
    if braco == 'acena':
        out.append(f'<rect x="{x + 17 * s:.1f}" y="{base - 108 * s:.1f}" width="{8 * s:.1f}" height="{34 * s:.1f}" rx="{4 * s:.1f}" fill="{roupa}" transform="rotate(18 {x + 21 * s:.1f} {base - 76 * s:.1f})"/>')
        out.append(f'<circle cx="{x + 31 * s:.1f}" cy="{base - 108 * s:.1f}" r="{4.5 * s:.1f}" fill="{p}"/>')
    else:
        out.append(f'<rect x="{x + 17 * s:.1f}" y="{base - 80 * s:.1f}" width="{8 * s:.1f}" height="{36 * s:.1f}" rx="{4 * s:.1f}" fill="{roupa}"/>')
        out.append(f'<circle cx="{x + 21 * s:.1f}" cy="{base - 43 * s:.1f}" r="{4.5 * s:.1f}" fill="{p}"/>')
    out.append(f'<circle cx="{x - 21 * s:.1f}" cy="{base - 43 * s:.1f}" r="{4.5 * s:.1f}" fill="{p}"/>')
    # tronco
    out.append(f'<rect x="{x - 18 * s:.1f}" y="{base - 82 * s:.1f}" width="{36 * s:.1f}" height="{40 * s:.1f}" rx="{8 * s:.1f}" fill="{roupa}"/>')
    out.append(f'<path d="M{x - 6 * s:.1f} {base - 82 * s:.1f} L{x:.1f} {base - 74 * s:.1f} L{x + 6 * s:.1f} {base - 82 * s:.1f}Z" fill="{WHITE}" opacity=".9"/>')
    if gravata:
        out.append(f'<path d="M{x - 2 * s:.1f} {base - 76 * s:.1f} h{4 * s:.1f} l{2 * s:.1f} {14 * s:.1f} l-{4 * s:.1f} {4 * s:.1f} l-{4 * s:.1f} -{4 * s:.1f}Z" fill="{gravata}"/>')
    # pescoço e cabeça
    out.append(f'<rect x="{x - 4 * s:.1f}" y="{base - 88 * s:.1f}" width="{8 * s:.1f}" height="{8 * s:.1f}" fill="{p}"/>')
    if longo:
        out.append(f'<path d="M{x - 11 * s:.1f} {base - 96 * s:.1f} q0 {16 * s:.1f} -{3 * s:.1f} {20 * s:.1f} h{28 * s:.1f} q-{3 * s:.1f} -{4 * s:.1f} -{3 * s:.1f} -{20 * s:.1f}Z" fill="{HAIR[cabelo]}"/>')
    out.append(f'<circle cx="{x:.1f}" cy="{base - 97 * s:.1f}" r="{10 * s:.1f}" fill="{p}"/>')
    out.append(f'<path d="M{x - 10.5 * s:.1f} {base - 97 * s:.1f} a{10.5 * s:.1f} {10.5 * s:.1f} 0 0 1 {21 * s:.1f} 0 q-{8 * s:.1f} -{4 * s:.1f} -{21 * s:.1f} 0Z" fill="{HAIR[cabelo]}"/>')
    out.append('</g>')
    return ''.join(out)


def busto(x, base, h, roupa, pele=0, cabelo=0, longo=False, gravata=None):
    """Pessoa atrás de uma mesa: só tronco, braços e cabeça."""
    s = h / 60
    p = SKIN[pele]
    o = []
    if longo:
        o.append(f'<path d="M{x - 11 * s:.1f} {base - 56 * s:.1f} q0 {16 * s:.1f} -{3 * s:.1f} {20 * s:.1f} h{28 * s:.1f} q-{3 * s:.1f} -{4 * s:.1f} -{3 * s:.1f} -{20 * s:.1f}Z" fill="{HAIR[cabelo]}"/>')
    o.append(f'<rect x="{x - 20 * s:.1f}" y="{base - 42 * s:.1f}" width="{40 * s:.1f}" height="{44 * s:.1f}" rx="{10 * s:.1f}" fill="{roupa}"/>')
    o.append(f'<path d="M{x - 6 * s:.1f} {base - 42 * s:.1f} L{x:.1f} {base - 34 * s:.1f} L{x + 6 * s:.1f} {base - 42 * s:.1f}Z" fill="{WHITE}" opacity=".9"/>')
    if gravata:
        o.append(f'<path d="M{x - 2 * s:.1f} {base - 36 * s:.1f} h{4 * s:.1f} l{2 * s:.1f} {14 * s:.1f} l-{4 * s:.1f} {4 * s:.1f} l-{4 * s:.1f} -{4 * s:.1f}Z" fill="{gravata}"/>')
    o.append(f'<rect x="{x - 4 * s:.1f}" y="{base - 48 * s:.1f}" width="{8 * s:.1f}" height="{8 * s:.1f}" fill="{p}"/>')
    o.append(f'<circle cx="{x:.1f}" cy="{base - 57 * s:.1f}" r="{10 * s:.1f}" fill="{p}"/>')
    o.append(f'<path d="M{x - 10.5 * s:.1f} {base - 57 * s:.1f} a{10.5 * s:.1f} {10.5 * s:.1f} 0 0 1 {21 * s:.1f} 0 q-{8 * s:.1f} -{4 * s:.1f} -{21 * s:.1f} 0Z" fill="{HAIR[cabelo]}"/>')
    return ''.join(o)


def casa(x, base, w, parede=WHITE, telhado=NAVY, janela=LIGHT, porta=BLUE, contorno=None):
    h = w * .62
    st = f' stroke="{contorno}" stroke-width="2"' if contorno else ''
    o = [f'<rect x="{x + w * .68:.1f}" y="{base - h - w * .3:.1f}" width="{w * .08:.1f}" height="{w * .2:.1f}" fill="{telhado}"/>']
    o.append(f'<rect x="{x:.1f}" y="{base - h:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{parede}"{st}/>')
    o.append(f'<polygon points="{x - w * .08:.1f},{base - h + 2:.1f} {x + w / 2:.1f},{base - h - w * .34:.1f} {x + w * 1.08:.1f},{base - h + 2:.1f}" fill="{telhado}"/>')
    o.append(f'<rect x="{x + w * .42:.1f}" y="{base - h * .5:.1f}" width="{w * .16:.1f}" height="{h * .5:.1f}" fill="{porta}"/>')
    o.append(f'<circle cx="{x + w * .55:.1f}" cy="{base - h * .25:.1f}" r="{w * .01 + 1:.1f}" fill="{WHITE}"/>')
    for jx in (x + w * .1, x + w * .68):
        o.append(f'<rect x="{jx:.1f}" y="{base - h * .72:.1f}" width="{w * .22:.1f}" height="{h * .3:.1f}" fill="{janela}"/>')
        o.append(f'<path d="M{jx + w * .11:.1f} {base - h * .72:.1f}v{h * .3:.1f}M{jx:.1f} {base - h * .57:.1f}h{w * .22:.1f}" stroke="{parede}" stroke-width="2.5"/>')
    return ''.join(o)


def casa_moderna(x, base, w, escuro=False):
    h = w * .5
    a, b = (WHITE, PALE) if not escuro else ('#E9F1F8', '#C9DCEC')
    o = [f'<rect x="{x:.1f}" y="{base - h:.1f}" width="{w * .6:.1f}" height="{h:.1f}" fill="{a}"/>',
         f'<rect x="{x + w * .45:.1f}" y="{base - h * 1.45:.1f}" width="{w * .55:.1f}" height="{h * 1.45:.1f}" fill="{b}"/>',
         f'<rect x="{x - w * .03:.1f}" y="{base - h - 8:.1f}" width="{w * .66:.1f}" height="9" fill="{NAVY}"/>',
         f'<rect x="{x + w * .42:.1f}" y="{base - h * 1.45 - 9:.1f}" width="{w * .61:.1f}" height="10" fill="{NAVY}"/>',
         f'<rect x="{x + w * .55:.1f}" y="{base - h * 1.3:.1f}" width="{w * .36:.1f}" height="{h * .5:.1f}" fill="{SKY}" opacity=".85"/>',
         f'<path d="M{x + w * .67:.1f} {base - h * 1.3:.1f}v{h * .5:.1f}M{x + w * .79:.1f} {base - h * 1.3:.1f}v{h * .5:.1f}" stroke="{b}" stroke-width="3"/>',
         f'<rect x="{x + w * .06:.1f}" y="{base - h * .78:.1f}" width="{w * .32:.1f}" height="{h * .5:.1f}" fill="{LIGHT}"/>',
         f'<path d="M{x + w * .22:.1f} {base - h * .78:.1f}v{h * .5:.1f}" stroke="{a}" stroke-width="3"/>',
         f'<rect x="{x + w * .62:.1f}" y="{base - h * .62:.1f}" width="{w * .14:.1f}" height="{h * .62:.1f}" fill="{NAVY}"/>',
         f'<rect x="{x + w * .8:.1f}" y="{base - h * .62:.1f}" width="{w * .12:.1f}" height="{h * .3:.1f}" fill="{LIGHT}"/>']
    return ''.join(o)


def predio(x, base, w, h, cor, janela, cols=3):
    o = [f'<rect x="{x:.1f}" y="{base - h:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{cor}"/>']
    jw, gap = w / (cols * 1.8 + .8), None
    gap = (w - cols * jw) / (cols + 1)
    y = base - h + gap
    while y + jw * 1.3 < base - jw * .6:
        for c in range(cols):
            o.append(f'<rect x="{x + gap + c * (jw + gap):.1f}" y="{y:.1f}" width="{jw:.1f}" height="{jw * 1.2:.1f}" fill="{janela}"/>')
        y += jw * 1.2 + gap * .8
    return ''.join(o)


def arvore(x, base, h, cor=SKY, tronco=MID):
    return (f'<rect x="{x - h * .03:.1f}" y="{base - h * .45:.1f}" width="{h * .06:.1f}" height="{h * .45:.1f}" fill="{tronco}"/>'
            f'<ellipse cx="{x:.1f}" cy="{base - h * .62:.1f}" rx="{h * .2:.1f}" ry="{h * .34:.1f}" fill="{cor}"/>')


def carro(x, base, w, cor=BLUE, vidro=LIGHT):
    h = w * .32
    r = w * .085
    return (f'<path d="M{x:.1f} {base - r:.1f} v-{h * .45:.1f} q0 -{h * .12:.1f} {w * .08:.1f} -{h * .16:.1f} l{w * .14:.1f} -{h * .06:.1f} '
            f'l{w * .14:.1f} -{h * .3:.1f} q{w * .03:.1f} -{h * .06:.1f} {w * .1:.1f} -{h * .06:.1f} h{w * .26:.1f} q{w * .06:.1f} 0 {w * .1:.1f} {h * .06:.1f} '
            f'l{w * .12:.1f} {h * .3:.1f} l{w * .06:.1f} {h * .02:.1f} q{w * .06:.1f} {h * .03:.1f} {w * .06:.1f} {h * .14:.1f} v{h * .37:.1f} Z" fill="{cor}"/>'
            f'<path d="M{x + w * .25:.1f} {base - r - h * .62:.1f} l{w * .12:.1f} -{h * .26:.1f} h{w * .17:.1f} v{h * .26:.1f}Z" fill="{vidro}"/>'
            f'<path d="M{x + w * .57:.1f} {base - r - h * .62:.1f} v-{h * .26:.1f} h{w * .1:.1f} q{w * .03:.1f} 0 {w * .05:.1f} {h * .05:.1f} l{w * .09:.1f} {h * .21:.1f}Z" fill="{vidro}"/>'
            f'<rect x="{x + w * .92:.1f}" y="{base - r - h * .5:.1f}" width="{w * .06:.1f}" height="{h * .1:.1f}" fill="#FFE8A3"/>'
            f'<rect x="{x + w * .01:.1f}" y="{base - r - h * .5:.1f}" width="{w * .04:.1f}" height="{h * .1:.1f}" fill="#F08A7A"/>'
            + ''.join(f'<circle cx="{cx:.1f}" cy="{base - r:.1f}" r="{r:.1f}" fill="{DEEP}"/><circle cx="{cx:.1f}" cy="{base - r:.1f}" r="{r * .45:.1f}" fill="#C9D6E2"/>'
                      for cx in (x + w * .22, x + w * .78)))


def documento(x, y, w, cor=WHITE, linha=LIGHT, titulo=BLUE, rot=0, check=False, grafico=False):
    h = w * 1.3
    o = [f'<g transform="rotate({rot} {x + w / 2:.1f} {y + h / 2:.1f})">',
         f'<rect x="{x + 6:.1f}" y="{y + 6:.1f}" width="{w:.1f}" height="{h:.1f}" fill="rgba(7,29,48,.12)"/>',
         f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{cor}"/>',
         f'<rect x="{x + w * .12:.1f}" y="{y + w * .14:.1f}" width="{w * .5:.1f}" height="{w * .07:.1f}" fill="{titulo}"/>']
    yy = y + w * .34
    n = 3 if grafico else 6
    for i in range(n):
        if check:
            o.append(f'<rect x="{x + w * .12:.1f}" y="{yy - w * .03:.1f}" width="{w * .08:.1f}" height="{w * .08:.1f}" fill="none" stroke="{SKY}" stroke-width="2"/>')
            if i < 4:
                o.append(f'<path d="M{x + w * .135:.1f} {yy + w * .01:.1f} l{w * .025:.1f} {w * .025:.1f} l{w * .045:.1f} -{w * .05:.1f}" fill="none" stroke="{BLUE}" stroke-width="2.5"/>')
            o.append(f'<rect x="{x + w * .26:.1f}" y="{yy - w * .01:.1f}" width="{w * (.62 - .08 * (i % 3)):.1f}" height="{w * .04:.1f}" fill="{linha}"/>')
        else:
            o.append(f'<rect x="{x + w * .12:.1f}" y="{yy:.1f}" width="{w * (.76 - .12 * (i % 3)):.1f}" height="{w * .04:.1f}" fill="{linha}"/>')
        yy += w * .13
    if grafico:
        bx, by = x + w * .14, y + h - w * .14
        for i, v in enumerate((.18, .3, .26, .42, .52)):
            o.append(f'<rect x="{bx + i * w * .15:.1f}" y="{by - w * v:.1f}" width="{w * .1:.1f}" height="{w * v:.1f}" fill="{SKY if i < 4 else BLUE}"/>')
    o.append('</g>')
    return ''.join(o)


def moeda(x, y, r, cor='#F2C14E', borda='#D9A62E', simbolo='$'):
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{borda}"/><circle cx="{x:.1f}" cy="{y - r * .08:.1f}" r="{r * .92:.1f}" fill="{cor}"/>'
            f'<text x="{x:.1f}" y="{y + r * .26:.1f}" font-family="Arial, Helvetica, sans-serif" font-weight="700" font-size="{r * .9:.1f}" text-anchor="middle" fill="{borda}">{simbolo}</text>')


def pilha(x, base, r, n):
    o = []
    for i in range(n):
        y = base - i * r * .32
        o.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r:.1f}" ry="{r * .32:.1f}" fill="#D9A62E"/>'
                 f'<ellipse cx="{x:.1f}" cy="{y - r * .08:.1f}" rx="{r:.1f}" ry="{r * .3:.1f}" fill="#F2C14E"/>')
    return ''.join(o)


def chave(x, y, s, cor='#F2C14E', rot=-30):
    return (f'<g transform="rotate({rot} {x:.1f} {y:.1f})"><circle cx="{x:.1f}" cy="{y:.1f}" r="{s * .5:.1f}" fill="none" stroke="{cor}" stroke-width="{s * .2:.1f}"/>'
            f'<rect x="{x + s * .55:.1f}" y="{y - s * .09:.1f}" width="{s * 1.5:.1f}" height="{s * .18:.1f}" fill="{cor}"/>'
            f'<rect x="{x + s * 1.65:.1f}" y="{y:.1f}" width="{s * .14:.1f}" height="{s * .35:.1f}" fill="{cor}"/>'
            f'<rect x="{x + s * 1.35:.1f}" y="{y:.1f}" width="{s * .14:.1f}" height="{s * .25:.1f}" fill="{cor}"/></g>')


def escudo(x, y, s, cor=BLUE, simbolo='check', sc=WHITE):
    o = [f'<path d="M{x:.1f} {y - s:.1f} L{x + s * .82:.1f} {y - s * .68:.1f} V{y - s * .05:.1f} C{x + s * .82:.1f} {y + s * .5:.1f} {x + s * .4:.1f} {y + s * .82:.1f} {x:.1f} {y + s:.1f} '
         f'C{x - s * .4:.1f} {y + s * .82:.1f} {x - s * .82:.1f} {y + s * .5:.1f} {x - s * .82:.1f} {y - s * .05:.1f} V{y - s * .68:.1f}Z" fill="{cor}"/>']
    if simbolo == 'check':
        o.append(f'<path d="M{x - s * .36:.1f} {y:.1f} l{s * .26:.1f} {s * .26:.1f} l{s * .48:.1f} -{s * .5:.1f}" fill="none" stroke="{sc}" stroke-width="{s * .14:.1f}" stroke-linecap="round" stroke-linejoin="round"/>')
    elif simbolo == 'cruz':
        o.append(f'<path d="M{x - s * .12:.1f} {y - s * .42:.1f}h{s * .24:.1f}v{s * .3:.1f}h{s * .3:.1f}v{s * .24:.1f}h-{s * .3:.1f}v{s * .3:.1f}h-{s * .24:.1f}v-{s * .3:.1f}h-{s * .3:.1f}v-{s * .24:.1f}h{s * .3:.1f}Z" fill="{sc}"/>')
    elif simbolo == 'coracao':
        o.append(f'<path d="M{x:.1f} {y + s * .35:.1f} C{x - s * .6:.1f} {y - s * .05:.1f} {x - s * .35:.1f} {y - s * .55:.1f} {x:.1f} {y - s * .25:.1f} C{x + s * .35:.1f} {y - s * .55:.1f} {x + s * .6:.1f} {y - s * .05:.1f} {x:.1f} {y + s * .35:.1f}Z" fill="{sc}"/>')
    return ''.join(o)


def selo(x, y, r, texto, cor=SKY, tc=WHITE):
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{cor}"/>'
            f'<text x="{x:.1f}" y="{y + r * .3:.1f}" font-family="Arial, Helvetica, sans-serif" font-weight="700" font-size="{r * .82:.1f}" text-anchor="middle" fill="{tc}">{texto}</text>')


def cartao(x, y, w, fundo=WHITE, rot=0, rotulo='CARTA DE CRÉDITO', valor='R$ 300.000'):
    h = w * .6
    return (f'<g transform="rotate({rot} {x + w / 2:.1f} {y + h / 2:.1f})">'
            f'<rect x="{x + 8:.1f}" y="{y + 10:.1f}" width="{w:.1f}" height="{h:.1f}" rx="6" fill="rgba(7,29,48,.25)"/>'
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="6" fill="{fundo}"/>'
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w * .05:.1f}" height="{h:.1f}" fill="{SKY}"/>'
            f'<text x="{x + w * .12:.1f}" y="{y + h * .28:.1f}" font-family="Arial, Helvetica, sans-serif" font-size="{w * .055:.1f}" letter-spacing="2" font-weight="600" fill="{MID}">{rotulo}</text>'
            f'<text x="{x + w * .12:.1f}" y="{y + h * .6:.1f}" font-family="Arial, Helvetica, sans-serif" font-size="{w * .12:.1f}" font-weight="700" fill="{NAVY}">{valor}</text>'
            f'<rect x="{x + w * .12:.1f}" y="{y + h * .74:.1f}" width="{w * .4:.1f}" height="{w * .03:.1f}" fill="{LIGHT}"/>'
            f'<path d="M{x + w * .74:.1f} {y + h * .82:.1f} l{w * .08:.1f} -{w * .16:.1f} l{w * .08:.1f} {w * .16:.1f}Z" fill="none" stroke="{SKY}" stroke-width="2.5"/></g>')


def notebook(x, base, w, tela=SKY):
    h = w * .62
    return (f'<rect x="{x:.1f}" y="{base - h:.1f}" width="{w:.1f}" height="{h:.1f}" rx="4" fill="{NAVY}"/>'
            f'<rect x="{x + w * .05:.1f}" y="{base - h + w * .05:.1f}" width="{w * .9:.1f}" height="{h - w * .1:.1f}" fill="{tela}"/>'
            f'<path d="M{x + w * .15:.1f} {base - h * .3:.1f} l{w * .18:.1f} -{h * .2:.1f} l{w * .15:.1f} {h * .1:.1f} l{w * .25:.1f} -{h * .3:.1f}" fill="none" stroke="{WHITE}" stroke-width="3"/>'
            f'<rect x="{x - w * .08:.1f}" y="{base:.1f}" width="{w * 1.16:.1f}" height="{w * .04:.1f}" rx="2" fill="{MID}"/>')


def svg(w, h, corpo, titulo):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" preserveAspectRatio="xMidYMid slice" role="img">'
            f'<title>{titulo}</title>{corpo}</svg>\n')


# ---------------------------------------------------------------- cenas

def reuniao(escuro=False):
    w, h = 800, 600
    c = [fundo(w, h, escuro, 'a')]
    c.append(predio(560, 470, 150, 300, '#DCE8F3', WHITE, 3))
    c.append(busto(265, 400, 190, NAVY, pele=1, cabelo=0, gravata=SKY))
    c.append(busto(535, 400, 190, BLUE, pele=0, cabelo=1, longo=True))
    c.append(f'<rect x="150" y="398" width="500" height="18" fill="{MID}"/><rect x="190" y="416" width="14" height="110" fill="{MID}"/><rect x="596" y="416" width="14" height="110" fill="{MID}"/>')
    c.append(notebook(330, 398, 120, SKY))
    c.append(documento(470, 340, 52, rot=-8))
    c.append(f'<rect x="210" y="372" width="34" height="26" rx="3" fill="{WHITE}"/><path d="M244 380 q14 0 0 12" fill="none" stroke="{WHITE}" stroke-width="4"/>')
    c.append(selo(640, 150, 34, '%', SKY))
    return svg(w, h, ''.join(c), 'Ilustração: reunião de consultoria')


def fachada(escuro=False):
    w, h = 800, 600
    c = [fundo(w, h, escuro, 'b')]
    c.append(arvore(150, 512, 220, SKY))
    c.append(arvore(670, 512, 170, LIGHT))
    c.append(casa_moderna(230, 512, 360, escuro))
    c.append(f'<rect x="0" y="512" width="{w}" height="88" fill="{"#0E3354" if escuro else "#DCE8F3"}"/><rect x="380" y="512" width="70" height="88" fill="{"#124A7C" if escuro else "#C9DCEC"}"/>')
    return svg(w, h, ''.join(c), 'Ilustração: imóvel residencial')


def familia(escuro=False):
    w, h = 800, 600
    c = [fundo(w, h, escuro, 'c')]
    c.append(casa(430, 500, 280, WHITE if not escuro else '#E9F1F8', NAVY if not escuro else MID, LIGHT, BLUE))
    c.append(arvore(110, 500, 190, SKY))
    c.append(pessoa(250, 520, 250, NAVY, '#24384D', pele=1, cabelo=0))
    c.append(pessoa(345, 520, 235, SKY, NAVY, pele=1, cabelo=2, longo=True))
    c.append(pessoa(300, 522, 135, '#F2C14E', BLUE, pele=1, cabelo=0, braco='acena'))
    c.append(escudo(660, 150, 48, BLUE, 'coracao'))
    return svg(w, h, ''.join(c), 'Ilustração: família')


def equity(escuro=False):
    w, h = 800, 600
    c = [fundo(w, h, escuro, 'd')]
    c.append(casa(170, 500, 330, WHITE if not escuro else '#E9F1F8', NAVY if not escuro else MID, LIGHT, BLUE))
    c.append(arvore(560, 500, 150, SKY))
    c.append(pilha(610, 505, 44, 6))
    c.append(pilha(690, 505, 38, 4))
    c.append(chave(560, 210, 64))
    c.append(selo(170, 170, 40, '%', SKY))
    return svg(w, h, ''.join(c), 'Ilustração: imóvel como garantia')


def consultor(escuro=False):
    w, h = 640, 800
    c = [fundo(w, h, escuro, 'e')]
    c.append(predio(70, 690, 130, 380, '#DCE8F3' if not escuro else '#123B60', WHITE if not escuro else '#1E5585', 3))
    c.append(predio(450, 690, 120, 300, '#DCE8F3' if not escuro else '#123B60', WHITE if not escuro else '#1E5585', 3))
    c.append(pessoa(320, 700, 470, NAVY, '#1A2B3C', pele=1, cabelo=0, gravata=SKY))
    c.append(documento(390, 470, 70, rot=8, grafico=True))
    return svg(w, h, ''.join(c), 'Ilustração: consultor da Monetizze')


def conquista():
    w, h = 800, 600
    c = [fundo(w, h, True, 'f')]
    c.append(casa_moderna(400, 500, 330, True))
    c.append(arvore(120, 500, 170, SKY, LIGHT))
    c.append(pessoa(230, 520, 240, '#E9F1F8', BLUE, pele=0, cabelo=1, longo=True))
    c.append(pessoa(320, 520, 255, SKY, '#24384D', pele=2, cabelo=0, braco='acena'))
    c.append(chave(398, 236, 22, rot=-60))
    c.append(cartao(500, 90, 230, rot=6))
    return svg(w, h, ''.join(c), 'Ilustração: casal com o imóvel conquistado')


def imoveis():
    w, h = 1000, 400
    c = [fundo(w, h, False, 'g')]
    c.append(predio(250, 340, 130, 270, MID, LIGHT, 3))
    c.append(predio(380, 340, 100, 200, BLUE, PALE, 2))
    c.append(casa(530, 340, 190))
    c.append(arvore(790, 340, 150, SKY))
    c.append(f'<rect x="0" y="340" width="{w}" height="60" fill="#DCE8F3"/>')
    return svg(w, h, ''.join(c), 'Ilustração: imóveis residenciais e comerciais')


def veiculo():
    w, h = 1000, 400
    c = [fundo(w, h, False, 'h')]
    c.append(predio(600, 300, 110, 190, '#DCE8F3', WHITE, 3))
    c.append(predio(720, 300, 90, 140, '#E3EDF6', WHITE, 2))
    c.append(f'<rect x="0" y="300" width="{w}" height="100" fill="#DCE8F3"/><path d="M0 368H{w}" stroke="{WHITE}" stroke-width="5" stroke-dasharray="40 30"/>')
    c.append(carro(310, 345, 380, BLUE))
    c.append(chave(250, 110, 40, '#F2C14E', -20))
    return svg(w, h, ''.join(c), 'Ilustração: veículo')


def he_hero():
    w, h = 800, 600
    c = [fundo(w, h, True, 'i')]
    c.append(casa(140, 500, 340, '#E9F1F8', MID, LIGHT, BLUE))
    c.append(escudo(610, 270, 92, SKY, 'check', NAVY))
    c.append(pilha(560, 505, 40, 5))
    c.append(pilha(650, 505, 40, 7))
    c.append(selo(600, 110, 32, '%', '#F2C14E', NAVY))
    return svg(w, h, ''.join(c), 'Ilustração: crédito com garantia de imóvel')


def criterios():
    w, h = 800, 600
    c = [fundo(w, h, False, 'j')]
    c.append(documento(170, 110, 220, rot=-6, check=True))
    c.append(documento(400, 140, 200, rot=5, grafico=True))
    c.append(f'<circle cx="560" cy="430" r="66" fill="none" stroke="{NAVY}" stroke-width="16"/><circle cx="560" cy="430" r="58" fill="rgba(156,198,232,.35)"/>'
             f'<rect x="604" y="478" width="26" height="100" rx="8" fill="{NAVY}" transform="rotate(-40 617 528)"/>')
    c.append(escudo(150, 440, 46, BLUE, 'check'))
    return svg(w, h, ''.join(c), 'Ilustração: análise de documentação')


def saude_hero():
    w, h = 800, 600
    c = [fundo(w, h, True, 'k')]
    c.append(escudo(560, 250, 150, SKY, 'cruz', WHITE))
    c.append(pessoa(170, 530, 260, '#E9F1F8', BLUE, pele=2, cabelo=0))
    c.append(pessoa(270, 530, 245, SKY, '#24384D', pele=2, cabelo=2, longo=True))
    c.append(pessoa(225, 532, 140, '#F2C14E', BLUE, pele=2, cabelo=0, braco='acena'))
    c.append(selo(700, 470, 34, '+', '#F2C14E', NAVY))
    return svg(w, h, ''.join(c), 'Ilustração: família protegida pelo plano de saúde')


def hospital():
    w, h = 800, 600
    c = [fundo(w, h, False, 'l')]
    c.append(predio(220, 500, 360, 300, WHITE, LIGHT, 6))
    c.append(f'<rect x="340" y="140" width="120" height="70" fill="{BLUE}"/><path d="M386 152h28v18h18v28h-18v18h-28v-18h-18v-28h18Z" fill="{WHITE}" transform="translate(0 -6) scale(1)"/>'
             f'<rect x="360" y="410" width="80" height="90" fill="{SKY}"/><path d="M400 410v90" stroke="{WHITE}" stroke-width="3"/>')
    c.append(arvore(150, 500, 170, SKY))
    c.append(arvore(650, 500, 190, LIGHT))
    c.append(f'<rect x="0" y="500" width="{w}" height="100" fill="#DCE8F3"/>')
    return svg(w, h, ''.join(c), 'Ilustração: atendimento hospitalar')


def migracao():
    w, h = 800, 600
    c = [fundo(w, h, False, 'm')]
    c.append(busto(400, 380, 210, NAVY, pele=0, cabelo=1, longo=True))
    c.append(f'<rect x="170" y="378" width="460" height="18" fill="{MID}"/><rect x="210" y="396" width="14" height="130" fill="{MID}"/><rect x="576" y="396" width="14" height="130" fill="{MID}"/>')
    c.append(notebook(345, 378, 110))
    for i, (x, y, r) in enumerate(((130, 110, -6), (575, 95, 5))):
        c.append(f'<g transform="rotate({r} {x + 50} {y + 60})"><rect x="{x}" y="{y}" width="100" height="120" fill="{WHITE}"/><rect x="{x}" y="{y}" width="100" height="26" fill="{BLUE if i else SKY}"/>'
                 f'<rect x="{x + 14}" y="{y + 42}" width="60" height="8" fill="{LIGHT}"/><rect x="{x + 14}" y="{y + 60}" width="72" height="8" fill="{LIGHT}"/><rect x="{x + 14}" y="{y + 78}" width="48" height="8" fill="{LIGHT}"/></g>')
    c.append(f'<path d="M240 160 q160 -80 320 -30" fill="none" stroke="{BLUE}" stroke-width="4" stroke-dasharray="10 10"/><path d="M546 118 l14 12 l-18 8" fill="none" stroke="{BLUE}" stroke-width="4"/>')
    return svg(w, h, ''.join(c), 'Ilustração: consultoria para troca de plano')


def tributario():
    w, h = 800, 600
    c = [fundo(w, h, False, 'n')]
    c.append(predio(110, 500, 190, 340, MID, LIGHT, 4))
    c.append(predio(300, 500, 130, 230, BLUE, PALE, 3))
    c.append(documento(470, 150, 170, rot=6, grafico=True))
    c.append(f'<rect x="590" y="330" width="120" height="160" rx="8" fill="{NAVY}"/><rect x="604" y="346" width="92" height="36" fill="{LIGHT}"/>'
             + ''.join(f'<rect x="{604 + (i % 3) * 32}" y="{396 + (i // 3) * 30}" width="24" height="22" rx="3" fill="{SKY if i != 8 else "#F2C14E"}"/>' for i in range(9)))
    c.append(selo(470, 130, 34, '%', '#F2C14E', NAVY))
    c.append(f'<rect x="0" y="500" width="{w}" height="100" fill="#DCE8F3"/>')
    return svg(w, h, ''.join(c), 'Ilustração: planejamento tributário para empresas')


CENAS = {
    'mz-ed-1': reuniao, 'mz-ed-2': fachada, 'mz-ed-3': familia, 'mz-equity': equity, 'mz-kawan': consultor,
    'cs-hero': conquista, 'cs-imovel': imoveis, 'cs-veiculo': veiculo,
    'he-hero': he_hero, 'he-criterios': criterios,
    'ps-hero': saude_hero, 'ps-cobertura': hospital, 'ps-migracao': migracao,
    'tb-parceria': tributario,
}

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for nome, f in CENAS.items():
        open(os.path.join(OUT, nome + '.svg'), 'w', encoding='utf-8').write(f())
        print(nome)
