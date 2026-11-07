"""Volantino A4 (con linguette da strappare) e biglietti da visita (10 per foglio A4, fronte e retro) da stampare.
Prende prezzi e testi dal sito, così restano sempre uguali al listino. Rifà i PDF solo se qualcosa è cambiato.
Uso: python3 strumenti/stampa/stampa.py URL_DEL_SITO [--sempre]   · Lo esegue GitHub Actions (pdf.yml).
Autore: Danilo D'Auria · codice MIT, testi e grafica CC BY-NC-SA 4.0"""
import base64, hashlib, html, io, json, os, re, sys, time
import segno
from playwright.sync_api import sync_playwright

URL = sys.argv[1].rstrip("/") + "/"
SEMPRE = "--sempre" in sys.argv
QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(QUI))
OUT = os.path.join(REPO, "pdf")
SITO = "https://danilodauria.github.io/"
EMAIL = "danilodauria.site@gmail.com"
CHROME = os.environ.get("CHROME") or (os.path.exists("/usr/bin/google-chrome") and "/usr/bin/google-chrome") or None
E = html.escape

def caratteri_del_sito():
    """I caratteri di fonti/ incorporati nel documento: nessuna richiesta a Google e nessun carattere da installare.
    Sono gli stessi WOFF2 che serve il sito, messi dentro come data: URI."""
    cartella = os.path.join(REPO, "fonti")
    def dentro(m):
        dati = base64.b64encode(open(os.path.join(cartella, m.group(1)), "rb").read()).decode()
        return 'url("data:font/woff2;base64,%s") format("woff2")' % dati
    css = open(os.path.join(cartella, "fonti.css"), encoding="utf-8").read()
    return re.sub(r'url\("([^"]+\.woff2)"\) format\("woff2"\)', dentro, css)

def qr(testo, scuro="#14232e", chiaro="#ffffff"):
    b = io.BytesIO()
    segno.make(testo, error="m").save(b, kind="svg", scale=4, border=3, dark=scuro, light=chiaro, xmldecl=False, omitsize=True)
    return b.getvalue().decode("utf-8")

FENICE = open(os.path.join(REPO, "fenice.svg"), encoding="utf-8").read()
FENICE = FENICE[FENICE.index("<svg"):]

ESTRAI = """() => {
  const t = el => el ? el.textContent.replace(/\\s+/g, ' ').trim() : '';
  const pacc = root => [...root.querySelectorAll('.pacchetto')].map(p => ({ nome: t(p.querySelector('.label')).replace(/^\\d+\\s*·\\s*/, ''), prezzo: t(p.querySelector('.prezzo')) }));
  return {
    linux: pacc(document.querySelector('#servizi .listino')),
    windows: pacc(document.querySelector('.listino-os[data-os="Windows"]')),
    apple: pacc(document.querySelector('.listino-os[data-os="Apple"]')),
    telefono: t(document.querySelector('.os-extra b')),
    altri: [...document.querySelectorAll('#servizi .servizio h4, #servizi .altri h4, #servizi article h3')].map(t).filter(Boolean).slice(0, 8)
  };
}"""

CSS = """
@page { size: A4; margin: 0; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; font-family: "Atkinson Hyperlegible", "Noto Sans", sans-serif; color: #1c2730; }
.f-disp { font-family: "Young Serif", "Noto Serif Display", Georgia, serif; font-weight: 400; }
.mono { font-family: "DejaVu Sans Mono", monospace; letter-spacing: .12em; text-transform: uppercase; }
/* volantino */
.vol { width: 210mm; height: 297mm; display: grid; grid-template-rows: auto auto 1fr auto 36mm; overflow: hidden; }
.vol-testa { background: #14232e; color: #f6efe4; padding: 11mm 14mm 9mm; display: grid; grid-template-columns: 1fr 34mm; gap: 6mm; align-items: center; }
.vol-testa .marchio { display: flex; align-items: center; gap: 3mm; font-size: 11pt; color: #fde9b0; }
.vol-testa .marchio svg { width: 11mm; height: 11mm; }
.vol-testa h1 { font-size: 34pt; line-height: 1.05; margin: 5mm 0 3mm; color: #fff; }
.vol-testa h1 em { font-style: normal; color: #f2b33d; }
.vol-testa p { margin: 0; font-size: 11.5pt; color: #d7dee3; line-height: 1.4; }
.vol-testa .qr-grande { background: #fff; border-radius: 3mm; padding: 1.5mm; text-align: center; }
.vol-testa .qr-grande svg { width: 100%; height: auto; display: block; }
.vol-testa .qr-grande span { display: block; font-size: 7.5pt; color: #14232e; font-weight: 700; padding: 0 1mm 1mm; line-height: 1.2; }
.gratis { background: #f2b33d; color: #14232e; padding: 4mm 14mm; display: flex; justify-content: space-between; align-items: center; gap: 6mm; }
.gratis b { font-size: 17pt; }
.gratis span { font-size: 10.5pt; }
.vol-corpo { padding: 8mm 14mm 6mm; display: grid; grid-template-rows: auto auto; gap: 9mm; align-content: space-evenly; }
.listini { display: grid; grid-template-columns: repeat(3, 1fr); gap: 4mm; }
.col { border: 1.2pt solid #e3d8c6; border-radius: 3mm; padding: 5mm 5mm; }
.col h2 { font-size: 17pt; margin: 0 0 2mm; }
.col .riga { display: flex; justify-content: space-between; align-items: baseline; gap: 2mm; padding: 2.6mm 0; border-top: 0.6pt solid #e3d8c6; font-size: 11pt; line-height: 1.25; }
.col .riga b { font-size: 15pt; white-space: nowrap; }
.col .riga.gr b { color: #2a7043; }
.col .nota { font-size: 9pt; color: #4f5c68; margin-top: 1.5mm; }
.anche { display: grid; grid-template-columns: 1fr 1fr; gap: 3mm 8mm; }
.anche h3 { grid-column: 1 / -1; font-size: 16pt; margin: 0; }
.anche div { font-size: 11.5pt; padding-left: 4mm; border-left: 2pt solid #e8702a; line-height: 1.35; }
.anche div b { display: block; font-size: 12.5pt; }
.vol-piede { padding: 3mm 14mm 4mm; display: flex; justify-content: space-between; align-items: center; gap: 6mm; border-top: 1pt solid #e3d8c6; }
.vol-piede .contatti { font-size: 12pt; line-height: 1.45; }
.vol-piede .contatti b { font-size: 13pt; }
.vol-piede .motto { font-size: 9pt; color: #4f5c68; max-width: 70mm; text-align: right; }
.linguette { display: grid; grid-template-columns: repeat(8, 1fr); border-top: 1pt dashed #4f5c68; }
.linguetta { border-right: 1pt dashed #4f5c68; display: grid; place-items: center; overflow: hidden; }
.linguetta:last-child { border-right: 0; }
.linguetta div { transform: rotate(-90deg); white-space: nowrap; font-size: 8pt; line-height: 1.35; text-align: center; }
.linguetta b { font-size: 8.6pt; }
/* biglietti: 85×55 mm, 2 colonne × 5 righe su A4, centrati */
.foglio { width: 210mm; height: 297mm; position: relative; page-break-after: always; }
.griglia { position: absolute; left: 20mm; top: 11mm; display: grid; grid-template-columns: 85mm 85mm; grid-template-rows: repeat(5, 55mm); }
.bv { width: 85mm; height: 55mm; position: relative; overflow: hidden; outline: 0.2pt solid #d8d8d8; }
.bv-f { padding: 6mm 6.5mm; display: grid; grid-template-rows: auto 1fr auto; background: #fff; }
.bv-f .alto { display: flex; align-items: center; gap: 2.5mm; }
.bv-f .alto svg { width: 10mm; height: 10mm; }
.bv-f .nome { font-size: 13.5pt; line-height: 1.05; }
.bv-f .ruolo { font-size: 7pt; color: #4f5c68; margin-top: 1mm; letter-spacing: .06em; }
.bv-f .frase { align-self: center; font-size: 8.6pt; line-height: 1.35; color: #1c2730; }
.bv-f .contatti { font-size: 7.8pt; line-height: 1.45; border-top: 0.6pt solid #e3d8c6; padding-top: 1.5mm; }
.bv-f .contatti b { color: #b8400c; }
.bv-r { background: #14232e; color: #f6efe4; padding: 5mm 6mm; display: grid; grid-template-columns: 1fr 27mm; gap: 4mm; align-items: center; }
.bv-r h3 { font-size: 12pt; line-height: 1.15; margin: 0 0 2mm; color: #fff; }
.bv-r p { margin: 0; font-size: 7.6pt; line-height: 1.4; color: #d7dee3; }
.bv-r .gr { display: inline-block; margin-top: 2.5mm; background: #f2b33d; color: #14232e; font-weight: 700; font-size: 8pt; padding: 1mm 2.5mm; border-radius: 99px; }
.bv-r .q { background: #fff; border-radius: 2mm; padding: 1mm; }
.bv-r .q svg { width: 100%; height: auto; display: block; }
.taglio { position: absolute; background: #9aa5ad; }
.istr { position: absolute; left: 20mm; bottom: 6mm; font-size: 7pt; color: #4f5c68; }
"""
CSS += caratteri_del_sito()

def volantino(L):
    def colonna(titolo, pacc, nota=""):
        righe = "".join('<div class="riga%s"><span>%s</span><b>%s</b></div>' % (" gr" if "GRATIS" in p["prezzo"] else "", E(p["nome"].split(" · ")[0]), E(p["prezzo"].replace(" a computer", ""))) for p in pacc)
        return '<div class="col"><h2 class="f-disp">%s</h2>%s%s</div>' % (E(titolo), righe, '<p class="nota">%s</p>' % E(nota) if nota else "")
    ling = "".join('<div class="linguetta"><div><b>Danilo D\'Auria</b><br>%s<br>danilodauria.github.io</div></div>' % EMAIL for _ in range(8))
    return f"""<section class="vol">
  <header class="vol-testa">
    <div>
      <div class="marchio">{FENICE}<span class="f-disp">Danilo D'Auria · Tecnologia Gentile</span></div>
      <h1 class="f-disp">Il computer è lento?<br><em>Non buttatelo.</em></h1>
      <p style="font-size:12.5pt">Ridò vita ai computer che il mercato chiama obsoleti, e aggiorno quelli nuovi. E insegno a usarli con consapevolezza.</p>
    </div>
    <div class="qr-grande">{qr(SITO + "#test")}<span>Test gratuito del vostro PC: 1 minuto</span></div>
  </header>
  <div class="gratis"><b>Check-up sempre GRATIS</b><span>Diagnosi del computer e preventivo chiaro, senza impegno.</span></div>
  <div class="vol-corpo">
    <div class="listini">
      {colonna("Con Linux", L["linux"], "Sistema libero e sicuro, senza licenze da pagare.")}
      {colonna("Con Windows", L["windows"], "La licenza già presente si riattiva.")}
      {colonna("Con Mac", L["apple"], (L["telefono"] + " configurazione e trasferimento dati.") if L["telefono"] else "")}
    </div>
    <div class="anche">
      <h3 class="f-disp">E poi</h3>
      <div><b>Corsi e laboratori</b>Per anziani, scuole e associazioni, anche senza Internet.</div>
      <div><b>Recupero dei dati</b>Foto e documenti da dischi e chiavette che non si aprono.</div>
      <div><b>Consigli prima di comprare</b>Cosa serve davvero e il momento giusto.</div>
      <div><b>Computer donati</b>Rigenerati e pronti per chi ne ha bisogno.</div>
    </div>
  </div>
  <footer class="vol-piede">
    <div class="contatti"><b>{EMAIL}</b><br>danilodauria.github.io</div>
    <div class="motto">Ogni computer rigenerato è un rifiuto elettronico in meno. Programmi liberi, gratuiti, che funzionano anche senza Internet.</div>
  </footer>
  <div class="linguette">{ling}</div>
</section>"""

def biglietti():
    fronte = f"""<div class="bv bv-f"><div class="alto">{FENICE}<div><div class="nome f-disp">Danilo D'Auria</div><div class="ruolo mono">Tecnico IT · Formatore</div></div></div>
      <p class="frase">Rigenerazione dei computer, programmi liberi e corsi di informatica per tutte le età.</p>
      <div class="contatti"><b>{EMAIL}</b><br>danilodauria.github.io</div></div>"""
    retro = f"""<div class="bv bv-r"><div><h3 class="f-disp">Il vostro PC può tornare a volare?</h3><p>Fate il test gratuito di un minuto: vi dico la strada giusta e quanto costa.</p><span class="gr">Check-up GRATIS</span></div>
      <div class="q">{qr(SITO + "#test")}</div></div>"""
    def taglio():
        x0, y0, w, h = 20, 11, 85, 55
        out = []
        for i in range(3):
            x = x0 + i * w
            out.append(f'<div class="taglio" style="left:{x}mm;top:{y0-7}mm;width:0.2mm;height:5mm"></div><div class="taglio" style="left:{x}mm;top:{y0+5*h+2}mm;width:0.2mm;height:5mm"></div>')
        for j in range(6):
            y = y0 + j * h
            out.append(f'<div class="taglio" style="left:{x0-7}mm;top:{y}mm;width:5mm;height:0.2mm"></div><div class="taglio" style="left:{x0+2*w+2}mm;top:{y}mm;width:5mm;height:0.2mm"></div>')
        return "".join(out)
    return (f'<section class="foglio"><div class="griglia">{fronte * 10}</div>{taglio()}<p class="istr">Fronte · Stampate su cartoncino A4 (250–300 g), fronte e retro sul lato lungo, al 100% senza adattare alla pagina. Tagliate lungo i segni: 10 biglietti da 85 × 55 mm.</p></section>'
            f'<section class="foglio"><div class="griglia">{retro * 10}</div>{taglio()}<p class="istr">Retro</p></section>')

def pagina(corpo):
    return f'<!doctype html><html lang="it"><meta charset="utf-8"><style>{CSS}</style><body>{corpo}</body></html>'

with sync_playwright() as p:
    br = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox"])
    pg = br.new_page(locale="it-IT")
    pg.goto(URL + "?lang=it", wait_until="load"); time.sleep(1.2)
    L = pg.evaluate(ESTRAI)
    assert L["linux"] and L["windows"] and L["apple"], "listino non trovato"
    lavori = {"volantino": pagina(volantino(L)), "biglietti": pagina(biglietti())}
    f_imp = os.path.join(OUT, "stampa-impronte.json")
    imp = json.load(open(f_imp)) if os.path.exists(f_imp) else {}
    motore = hashlib.sha256(open(__file__, "rb").read()).hexdigest()[:12]
    for nome, h in lavori.items():
        firma = motore + hashlib.sha256(h.encode()).hexdigest()
        dest = os.path.join(OUT, "Danilo_DAuria_%s.pdf" % nome)
        if not SEMPRE and imp.get(nome) == firma and os.path.exists(dest):
            print(nome, ": già aggiornato"); continue
        tmp = os.path.join(QUI, "_%s.html" % nome)
        open(tmp, "w", encoding="utf-8").write(h)
        pg.goto("file://" + tmp, wait_until="load"); pg.evaluate("document.fonts.ready"); time.sleep(.6)
        pg.pdf(path=dest, format="A4", print_background=True, prefer_css_page_size=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        os.remove(tmp); imp[nome] = firma
        print(nome, ": PDF rifatto")
    br.close()
json.dump(imp, open(f_imp, "w"), indent=1, sort_keys=True)
