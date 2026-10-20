/* Monetizze Investimentos — runtime das páginas + efeitos do site do aulão.
   Cada página traz a lógica original do Claude Design (classe Component com
   renderVals); este arquivo a executa sem React e aplica os efeitos. */
(() => {
  const CONFIG = {
    whatsapp: '5565996745162'
  };

  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => [...el.querySelectorAll(s)];
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const clamp = (v, a, b) => Math.min(Math.max(v, a), b);

  /* ---------------- Runtime da lógica do Claude Design ---------------- */
  let inst = null;
  let vals = {};
  const TPL = /\{\{\s*([\w.]+)\s*\}\}/g;
  const fill = t => t.replace(TPL, (_, k) => (vals[k] ?? ''));
  const ORDER = ['min', 'max', 'step'];

  function render() {
    if (!inst) return;
    vals = inst.renderVals() || {};
    $$('[data-v]').forEach(el => { const v = vals[el.dataset.v]; el.textContent = v ?? ''; });
    $$('*').forEach(el => {
      const tpls = [...el.attributes].filter(a => a.name.startsWith('data-tpl-'));
      if (!tpls.length) return;
      tpls.sort((a, b) => (ORDER.indexOf(b.name.slice(9)) - ORDER.indexOf(a.name.slice(9))));
      tpls.forEach(a => {
        const name = a.name.slice(9), v = fill(a.value);
        if (name === 'value') el.value = v; else el.setAttribute(name, v);
      });
    });
    $$('[data-if]').forEach(el => el.classList.toggle('is-on', !!vals[el.dataset.if]));
  }

  window.DCLogic = class DCLogic {
    constructor() { this.props = {}; this.state = {}; }
    setState(u) { Object.assign(this.state, typeof u === 'function' ? u(this.state) : u); render(); }
  };

  function mount(Component, props) {
    inst = new Component();
    inst.props = props || {};
    inst.state = Object.assign({}, inst.state, { narrow: innerWidth < 1060 });
    addEventListener('resize', () => { inst.state.narrow = innerWidth < 1060; });
    $$('[data-on-click]').forEach(el => el.addEventListener('click', e => { const f = vals[el.dataset.onClick]; if (typeof f === 'function') f(e); }));
    $$('[data-on-input]').forEach(el => el.addEventListener('input', e => { const f = vals[el.dataset.onInput]; if (typeof f === 'function') f(e); }));
    render();
    efeitos();
  }
  window.MZ = { mount };

  /* ---------------- Efeitos ---------------- */
  function efeitos() {
    const fone = CONFIG.whatsapp;
    $$('[data-wa]').forEach(a => { a.href = 'https://wa.me/' + fone + '?text=' + encodeURIComponent(a.dataset.wa); });

    /* Menu ativo e menu do celular */
    const pagina = document.body.dataset.page;
    $$('[data-nav]').forEach(a => a.classList.toggle('is-current', a.dataset.nav === pagina));
    const header = $('.mz-header'), menu = $('[data-menu]');
    if (menu) {
      menu.addEventListener('click', () => { const open = header.classList.toggle('is-open'); menu.setAttribute('aria-expanded', String(open)); });
      $$('.mz-mnav a').forEach(a => a.addEventListener('click', () => { header.classList.remove('is-open'); menu.setAttribute('aria-expanded', 'false'); }));
    }

    /* Título palavra a palavra */
    $$('[data-split]').forEach(el => {
      if (reduceMotion) return;
      let i = 0;
      const wrap = (text, cls = '') => text.split(/(\s+)/).map(p => p.trim() ? `<span class="w"><span class="w__i ${cls}" style="--i:${i++}">${p}</span></span>` : p).join('');
      el.innerHTML = [...el.childNodes].map(n => n.nodeType === 3 ? wrap(n.textContent) : wrap(n.textContent, n.className || '')).join('');
    });

    /* Faixas: duplica o conteúdo para rolar sem emenda */
    $$('[data-marquee]').forEach(t => { t.innerHTML += t.innerHTML; });

    /* Cards de grade (borda de 1px entre eles) */
    $$('[style*="display:grid"][style*="gap:1px"]').forEach(grid => {
      [...grid.children].forEach(card => {
        const st = card.getAttribute('style') || '';
        if (!/background:/.test(st) || card.tagName === 'LABEL') return;
        card.classList.add('fx-card');
        if (/background:#0B2A45/i.test(st)) card.classList.add('fx-card--dark');
        const first = card.firstElementChild;
        const num = first && first.textContent.trim();
        if (num && /^\d{2}$/.test(num)) {
          const g = document.createElement('span');
          g.className = 'fx-ghost'; g.setAttribute('aria-hidden', 'true'); g.textContent = num;
          card.appendChild(g);
        }
      });
    });
    $$('.fx-card').forEach(el => el.addEventListener('pointermove', e => {
      const r = el.getBoundingClientRect();
      el.style.setProperty('--mx', `${e.clientX - r.left}px`);
      el.style.setProperty('--my', `${e.clientY - r.top}px`);
    }));

    /* Borda luminosa nos blocos escuros dentro de seções claras */
    $$('main section').forEach(sec => {
      if (/background:#(0B2A45|071D30)/i.test(sec.getAttribute('style') || '')) return;
      $$('div', sec).forEach(d => {
        const st = d.getAttribute('style') || '';
        if (!d.classList.contains('fx-card') && /(^|;)\s*background:#0B2A45;padding/i.test(st)) d.classList.add('fx-glow');
      });
    });

    /* Botões: brilho e pulso */
    $$('main a[style], .mz-cta').forEach(a => {
      const st = a.getAttribute('style') || '';
      if (a.classList.contains('mz-cta') || /background:#FFFFFF;color:#0B2A45/i.test(st)) a.classList.add('fx-shine');
      else if (/background:#0B2A45;color:#FFFFFF/i.test(st)) a.classList.add('fx-shine', 'fx-shine--dark');
    });
    const heroCta = $('.fx-hero a[style*="background:#FFFFFF"]');
    if (heroCta) heroCta.classList.add('fx-pulse');

    /* Revelação ao rolar (mesma divisão do Claude Design, com desfoque) */
    if (!reduceMotion && 'IntersectionObserver' in window) {
      const alvos = [];
      $$('section[data-reveal]').forEach(sec => {
        [...sec.children].forEach(wrap => {
          if (wrap.classList.contains('bg-grid') || wrap.classList.contains('blob') || wrap.classList.contains('fx-ring')) return;
          const kids = [...wrap.children].filter(k => !k.classList.contains('bg-grid'));
          (kids.length > 1 ? kids : [wrap]).forEach((t, i) => { t.setAttribute('data-rv', ''); t.style.transitionDelay = Math.min(i, 6) * 80 + 'ms'; alvos.push(t); });
        });
      });
      const io = new IntersectionObserver(entries => entries.forEach(e => {
        if (!e.isIntersecting) return;
        const el = e.target;
        el.classList.add('is-in');
        io.unobserve(el);
        setTimeout(() => { el.removeAttribute('data-rv'); el.style.transitionDelay = ''; }, 1500);
      }), { rootMargin: '0px 0px -8% 0px', threshold: .05 });
      alvos.forEach(el => io.observe(el));
    }

    /* Scroll: barra de progresso e sombra do cabeçalho */
    const progress = $('.progress');
    let ticking = false;
    const onScroll = () => {
      ticking = false;
      const y = scrollY, max = document.documentElement.scrollHeight - innerHeight;
      if (progress) progress.style.transform = `scaleX(${max > 0 ? clamp(y / max, 0, 1) : 0})`;
      header && header.classList.toggle('is-scrolled', y > 10);
    };
    addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
    onScroll();
  }
})();
