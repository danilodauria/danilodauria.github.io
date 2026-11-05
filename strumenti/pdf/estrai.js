async () => {
  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => [...(r || document).querySelectorAll(s)];
  const t = (e) => (e ? e.textContent.replace(/\s+/g, ' ').trim() : '');
  const h = (e) => (e ? e.innerHTML.trim() : '');
  const d = {};
  d.hero = { label: t($('.hero .label')), h1: h($('.hero h1')), lead: h($('.hero .lead')),
             dati: $$('.dati div').map(x => [t($('b', x)), t($('span', x))]) };
  d.fenice = $('.hero .fenice svg').outerHTML;
  const chi = $('#chi-sono');
  d.chi = { h2: t($('h2', chi)), par: $$('.testo > p:not(.label):not(.small)', chi).map(h),
            metafora: h($('.metafora', chi)), percorso: $$('.percorso li', chi).map(li => ({ anno: t($('.anno', li)), titolo: t($('b', li)), testo: t(li.querySelector(':scope > div > span')), futuro: li.classList.contains('futuro') })),
            formazione: t($('.testo p.small', chi)),
            marca: { motto: t($('.motto', chi)), nome: h($('.marca-green .nome', chi)), pilastri: $$('.pilastri li', chi).map(li => [t($('b', li)), t($('span', li))]), strumenti: $$('.strumenti span', chi).map(t) } };
  d.profili = [];
  for (const b of $$('#scelta button')) {
    b.click(); await new Promise(r => setTimeout(r, 20));
    d.profili.push({ nome: t(b), titolo: t($('#sm-titolo')), perche: t($('#sm-perche')),
      offerte: $$('#sm-offerte li').map(li => [t($('b', li)), t($('span', li))]),
      progetti: $$('#sm-progetti a:not([data-chi-bandi])').map(t) });
  }
  const eco = $('#ecosistema');
  d.eco = { h2: t($('h2', eco)), lead: t($('.lead', eco)), svg: $('.mappa svg', eco).outerHTML };
  const pr = $('#progetti');
  d.progettiTesta = { h2: t($('h2', pr)), lead: t($('.testa .lead', pr)) };
  d.progetti = $$('article.prog', pr).map(a => ({
    titolo: t($('h3', a)), versione: t($('.versione', a)), ruolo: t($('.ruolo', a)),
    punti: $$('ul li', a).map(h), piattaforme: $$('.piattaforme span', a).map(t),
    link: $$('.collegamenti a', a).map(x => [t(x), x.href]), img: ($('.scatto img', a) || {}).src || '' }));
  d.altri = $$('.lab-card').map(c => ({ titolo: t($('h4', c)), testo: t($('p', c)), link: ($('a[href*="github.com"]', c) || {}).href || '' }));
  const lb = $('#libro');
  d.libro = { titolo: t($('h2', lb)), lead: t($('.lead', lb)), citazione: t($('blockquote', lb)), capitoli: $$('.capitoli li', lb).map(t),
              img: $('img', lb).src, amazon: ($('a[href*="amazon"]', lb) || {}).href || '' };
  const pa = $('#patto');
  d.patto = { h2: t($('h2', pa)), punti: $$('.patto div', pa).map(x => [t($('b', x)), t($('span', x))]) };
  const vi = $('#video');
  d.video = { h2: t($('h2', vi)), lead: t($('.lead', vi)), rrr: $$('.rrr li', vi).map(x => [t($('b', x)), t($('span', x))]), nota: t($('.video-nota', vi)) };
  const se = $('#servizi');
  d.servizi = { h2: t($('h2', se)),
    listino: $$('.pacchetto', se).map(x => ({ nome: t($('.label', x)), prezzo: t($('.prezzo', x)), testo: t($$('p', x)[2]), ideale: t($('.ideale', x)), top: x.classList.contains('top') })),
    flex: [t($('.flex-nota b', se)), t($('.flex-nota p', se))],
    altri: $$('.serv', se).map(x => [t($('.label', x)), t($('h3', x)), t($('p:not(.label)', x))]),
    metodo: $$('.metodo li', se).map(x => [t($('b', x)), t($('span', x))]) };
  d.faq = $$('.faq details').map(x => [t($('summary', x)), t($('p', x))]);
  const co = $('#contatti');
  d.contatti = { h2: t($('h2', co)), lead: t($('.lead', co)), email: t($('#email')) };
  return d;
}
