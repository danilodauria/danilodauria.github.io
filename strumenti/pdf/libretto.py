"""Versione stampabile (A4) del sito di Danilo D'Auria, impaginata per la carta.

Legge i testi dal sito (così PDF e sito dicono le stesse cose), compone un documento A4 con
copertina e retro a pagina intera, e lo stampa con Chromium. Due uscite:
  Danilo_DAuria_Tecnologia_Gentile.pdf        (per lo schermo, con collegamenti cliccabili)
  Danilo_DAuria_Tecnologia_Gentile_stampa.pdf (uguale, ma le pagine colorate a fondo pieno si stampano chiare)
Uso: python3 libretto.py URL_DEL_SITO CARTELLA_USCITA"""
import base64, html, io, json, json as _j, os, sys, time
import segno
from playwright.sync_api import sync_playwright

URL, OUT = sys.argv[1], sys.argv[2]
QUI = os.path.dirname(os.path.abspath(__file__))
SITO = "https://danilodauria.github.io/"
REPO = os.path.dirname(os.path.dirname(QUI))
os.makedirs(OUT, exist_ok=True)
E = html.escape

def qr(testo, colore="#14232e"):
    b = io.BytesIO()
    segno.make(testo, error="m").save(b, kind="svg", scale=4, border=3, dark="#14232e", light="#ffffff", xmldecl=False, omitsize=True)
    return b.getvalue().decode("utf-8")

def data_uri(path, tipo):
    return "data:%s;base64,%s" % (tipo, base64.b64encode(open(path, "rb").read()).decode())

with sync_playwright() as p:
    br = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    pg = br.new_page(viewport={"width": 1280, "height": 900})
    pg.goto(URL, wait_until="load"); time.sleep(1.5)
    D = pg.evaluate(open(os.path.join(QUI, "estrai.js")).read())
    br.close()

bandi = json.load(open(os.path.join(REPO, "bandi.json")))
OGGI = time.strftime("%Y-%m-%d")
MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
def data_it(iso):
    a, m, g = iso.split("-"); return "%d %s %s" % (int(g), MESI[int(m) - 1], a)

# ---------------- pezzi
def chi_sono():
    c = D["chi"]
    perc = "".join('<li class="%s"><span class="anno">%s</span><div><b>%s</b><span>%s</span></div></li>' % ("futuro" if x["futuro"] else "", E(x["anno"]), E(x["titolo"]), E(x["testo"])) for x in c["percorso"])
    pil = "".join("<li><b>%s</b> %s</li>" % (E(a), E(b)) for a, b in c["marca"]["pilastri"])
    return f"""
<section class="capitolo">
  <p class="occhiello">Chi sono</p>
  <h1>{E(c['h2'])}</h1>
  <div class="due">
    <div class="testo">{''.join('<p>%s</p>' % x for x in c['par'][:2])}</div>
    <div class="testo">{''.join('<p>%s</p>' % x for x in c['par'][2:])}</div>
  </div>
  <blockquote class="metafora">{c['metafora']}</blockquote>
  <div class="due" style="margin-top:7mm">
    <div><h3 class="sotto">Il mio percorso</h3><ol class="percorso">{perc}</ol><p class="piccolo">{E(c['formazione'])}</p></div>
    <aside class="marca"><p class="motto">{E(c['marca']['motto'])}</p><p class="nome">{c['marca']['nome']}</p><ul class="pil">{pil}</ul>
      <p class="strum">{' · '.join(E(x) for x in c['marca']['strumenti'])}</p></aside>
  </div>
</section>"""

def profili():
    out = []
    for x in D["profili"]:
        off = "".join("<li><b>%s</b> — %s</li>" % (E(a), E(b)) for a, b in x["offerte"])
        out.append(f'<div class="profilo"><p class="occhiello">{E(x["nome"])}</p><h3>{E(x["titolo"])}</h3><p class="perche">{E(x["perche"])}</p><ul>{off}</ul><p class="cons">Progetti consigliati: {" · ".join(E(y) for y in x["progetti"])}</p></div>')
    return f"""
<section class="capitolo">
  <p class="occhiello">Su misura</p>
  <h1>Chi siete? Ecco come posso esservi utile.</h1>
  <p class="lead">Sei realtà diverse, sei proposte. Trovate la vostra e scrivetemi per un preventivo.</p>
  <div class="profili">{''.join(out)}</div>
</section>"""

def progetti():
    e = D["eco"]
    cards = []
    for x in D["progetti"]:
        punti = "".join("<li>%s</li>" % y for y in x["punti"])
        link = " · ".join('<a href="%s">%s</a>' % (E(u), E(u.replace("https://", "").rstrip("/"))) for n, u in x["link"] if "github.io" in u or "sourceforge" in u)
        img = '<img src="%s" alt="">' % x["img"] if x["img"] else ""
        ver = '<span class="ver">%s</span>' % E(x["versione"]) if x["versione"] else ""
        cards.append(f"""<article class="prog"><div class="scatto">{img}</div><div class="corpo">
          <div class="cima"><h3>{E(x['titolo'])}</h3>{ver}</div><p class="ruolo">{E(x['ruolo'])}</p><ul>{punti}</ul>
          <p class="piatt">{' · '.join(E(y) for y in x['piattaforme'])}</p><p class="link">{link}</p></div></article>""")
    altri = ""
    if D["altri"]:
        altri = '<h3 class="sotto" style="margin-top:6mm">Gli altri progetti su GitHub</h3><ul class="altri">' + "".join(
            "<li><b>%s</b> — %s <span class=\"url\">%s</span></li>" % (E(a["titolo"]), E(a["testo"]), E(a["link"].replace("https://", ""))) for a in D["altri"]) + "</ul>"
    return f"""
<section class="capitolo">
  <p class="occhiello">Una sola visione</p>
  <h1>{E(e['h2'])}</h1>
  <p class="lead">{E(e['lead'])}</p>
  <div class="mappa">{e['svg']}</div>
  <h1 style="margin-top:9mm">{E(D['progettiTesta']['h2'])}</h1>
  <p class="lead">{E(D['progettiTesta']['lead'])}</p>
  {''.join(cards)}
  {altri}
</section>"""

def libro_patto():
    l = D["libro"]
    cap = "".join("<li>%s</li>" % E(x) for x in l["capitoli"])
    patto = "".join("<div><b>%s</b><span>%s</span></div>" % (E(a), E(b)) for a, b in D["patto"]["punti"])
    return f"""
<section class="capitolo">
  <p class="occhiello">Il libro · su Amazon</p>
  <div class="libro"><img src="{l['img']}" alt="">
    <div><h1>{E(l['titolo'])}</h1><p class="lead">{E(l['lead'])}</p><blockquote class="cit">{E(l['citazione'])}</blockquote>
    <p class="piccolo">Su Amazon: {E(l['amazon'].replace('https://', ''))}</p></div></div>
  <h3 class="sotto">I venti capitoli</h3>
  <ol class="capitoli">{cap}</ol>
  <div class="patto-blocco"><p class="occhiello">Il patto gentile</p><h2>{E(D['patto']['h2'])}</h2><div class="patto">{patto}</div></div>
</section>"""

def video():
    v = D["video"]
    rrr = "".join("<li><b>%s</b><span>%s</span></li>" % (E(a), E(b)) for a, b in v["rrr"])
    poster = data_uri(os.path.join(REPO, "video", "seconda-vita-digitale.jpg"), "image/jpeg")
    return f"""
<section class="capitolo">
  <div class="video"><img src="{poster}" alt="">
    <div><p class="occhiello">Video · 2 minuti e mezzo</p><h1>{E(v['h2'])}</h1><p class="lead">{E(v['lead'])}</p><ul class="rrr">{rrr}</ul>
    <div class="qr">{qr(SITO + '#video')}<p><b>Guardate il video</b>Inquadrate il codice con la fotocamera del telefono. Altri video su youtube.com/@Danilo-A6Zero</p></div>
    <p class="piccolo">{E(v['nota'])}</p></div></div>
</section>"""

def servizi():
    s = D["servizi"]
    lis = "".join(f'<div class="pacc{" top" if x["top"] else ""}"><p class="occhiello">{E(x["nome"])}</p><p class="prezzo">{E(x["prezzo"])}</p><p>{E(x["testo"])}</p><p class="ideale">{E(x["ideale"])}</p></div>' for x in s["listino"])
    alt = "".join('<div class="serv"><p class="occhiello">%s</p><h3>%s</h3><p>%s</p></div>' % (E(a), E(b), E(c)) for a, b, c in s["altri"])
    met = "".join("<li><b>%s</b><span>%s</span></li>" % (E(a), E(b)) for a, b in s["metodo"])
    return f"""
<section class="capitolo">
  <p class="occhiello">Servizi su richiesta</p>
  <h1>{E(s['h2'])}</h1>
  <h3 class="sotto">Listino rigenerazione green</h3>
  <div class="listino">{lis}</div>
  <div class="flex"><b>{E(s['flex'][0])}</b><span>{E(s['flex'][1])}</span></div>
  <h3 class="sotto">Altri servizi</h3>
  <div class="servizi">{alt}</div>
  <h3 class="sotto">Come lavoro</h3>
  <ol class="metodo">{met}</ol>
</section>"""

def stato(b):
    if b.get("previsto"): return ("In arrivo", "arrivo")
    if not b.get("scadenza"): return ("Aperto", "aperto")
    return ("Chiuso", "chiuso") if b["scadenza"] < OGGI else ("Aperto", "aperto")

def bandi_pag():
    righe = []
    ordine = {"aperto": 0, "arrivo": 1, "chiuso": 2}
    for b in sorted(bandi["bandi"], key=lambda b: (ordine[stato(b)[1]], b.get("scadenza") or "9999")):
        st, cls = stato(b)
        sc = data_it(b["scadenza"]) if b.get("scadenza") else "da definire"
        nota = ' <span class="nota">(%s)</span>' % E(b["nota_scadenza"]) if b.get("nota_scadenza") else ""
        righe.append(f"""<div class="bando"><div class="cima"><h3>{E(b['titolo'])}</h3><span class="stato {cls}">{st}</span></div>
          <p class="ente">{E(b['ente'])}</p><p>{E(b['cosa'])}</p>
          <p class="dati"><b>Importo</b> {E(b['importo'])} · <b>Scadenza</b> {sc}{nota}</p>
          <p class="aiuto"><b>Come posso aiutarvi:</b> {E(b['aiuto'])}</p></div>""")
    return f"""
<section class="capitolo">
  <p class="occhiello">Bandi e finanziamenti</p>
  <h1>C'è un bando che può pagare il vostro progetto?</h1>
  <p class="lead">Situazione al {data_it(OGGI)}. Scadenze e requisiti cambiano spesso: l'elenco aggiornato ogni giorno è sul sito, nella sezione «Bandi», con il link alla fonte ufficiale di ogni bando.</p>
  <div class="bandi">{''.join(righe)}</div>
  <p class="piccolo">{E(bandi['nota'])}</p>
</section>"""

def faq():
    return """
<section class="capitolo">
  <p class="occhiello">Domande frequenti</p>
  <h1>Le domande che mi fanno più spesso.</h1>
  <div class="faq">%s</div>
</section>""" % "".join("<div><h3>%s</h3><p>%s</p></div>" % (E(a), E(b)) for a, b in D["faq"])

def copertina():
    h = D["hero"]
    dati = "".join("<div><b>%s</b><span>%s</span></div>" % (E(a), E(b)) for a, b in h["dati"])
    return f"""
<section class="copertina">
  <div class="cop-fenice">{D['fenice']}</div>
  <p class="cop-label">{E(h['label'])}</p>
  <h1 class="cop-titolo">{h['h1']}</h1>
  <p class="cop-lead">{h['lead']}</p>
  <div class="cop-dati">{dati}</div>
  <div class="cop-piede"><div><span>Profilo, progetti e servizi</span><b>danilodauria.github.io</b><span>Edizione del {data_it(OGGI)}</span></div>{qr(SITO, '#fde9b0')}</div>
</section>"""

def retro():
    c = D["contatti"]
    return f"""
<section class="retro">
  <div class="retro-dentro">
    <p class="cop-label">Contatti</p>
    <h1 class="retro-titolo">{E(c['h2'])}</h1>
    <p class="cop-lead">{E(c['lead'])}</p>
    <div class="retro-schede">
      <div><span>Email</span><b>{E(c['email'])}</b></div>
      <div><span>Sito</span><b>danilodauria.github.io</b></div>
      <div><span>Progetti</span><b>github.com/danilodauria</b></div>
      <div><span>Video</span><b>youtube.com/@Danilo-A6Zero</b></div>
    </div>
    <div class="retro-qr">{qr(SITO, '#fde9b0')}<p>Inquadrate il codice per aprire il sito: progetti, bandi e novità sempre aggiornati.</p></div>
  </div>
  <p class="retro-lic">© 2026 Danilo D'Auria · testi e grafica CC BY-NC-SA 4.0 · logo FeniceOS © Danilo D'Auria</p>
</section>"""

CSS = open(os.path.join(QUI, "libretto.css")).read()
pagina = f"""<!doctype html><html lang="it"><head><meta charset="utf-8"><title>Danilo D'Auria · Tecnologia Gentile</title>
<style>{CSS}</style></head><body>
{copertina()}
<div class="segnaposto"></div>
{chi_sono()}
{profili()}
{progetti()}
{libro_patto()}
{video()}
{servizi()}
{bandi_pag()}
{faq()}
{retro()}
</body></html>"""
html_path = os.path.join(OUT, "libretto.html")
open(html_path, "w", encoding="utf-8").write(pagina)

FOOTER = ('<div style="width:100%;font-family:\'Atkinson Hyperlegible\',sans-serif;font-size:7.5px;color:#4f5c68;'
          'padding:0 16mm;display:flex;justify-content:space-between">'
          "<span>Danilo D'Auria · Tecnologia Gentile · danilodauria.github.io</span>"
          '<span class="pageNumber"></span></div>')
from pypdf import PdfReader, PdfWriter
import tempfile
tmp = tempfile.mkdtemp(prefix="libretto-")
with sync_playwright() as p:
    br = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    pg = br.new_page()
    pg.goto("file://" + html_path, wait_until="load"); pg.evaluate("document.fonts.ready"); time.sleep(.8)
    for nome, extra in [("Danilo_DAuria_Tecnologia_Gentile.pdf", ""), ("Danilo_DAuria_Tecnologia_Gentile_stampa.pdf", "stampa")]:
        parti = []
        for modo, piede in [("solo-cop", False), ("corpo", True), ("solo-retro", False)]:
            pg.evaluate("c => { document.body.className = c; }", (extra + " " + modo).strip())
            f = os.path.join(tmp, modo + ".pdf")
            if piede:
                pg.pdf(path=f, format="A4", print_background=True, display_header_footer=True,
                       header_template="<span></span>", footer_template=FOOTER,
                       margin={"top": "14mm", "bottom": "15mm", "left": "16mm", "right": "16mm"})
            else:
                pg.pdf(path=f, format="A4", print_background=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
            parti.append((modo, PdfReader(f)))
        w = PdfWriter()
        for modo, r in parti:
            pagine = r.pages[1:] if modo == "corpo" else r.pages[:1]   # il corpo perde la pagina segnaposto
            for pagina in pagine:
                w.add_page(pagina)
        w.add_metadata({"/Title": "Danilo D'Auria · Tecnologia Gentile", "/Author": "Danilo D'Auria",
                        "/Subject": "Profilo, progetti e servizi · versione stampabile del sito danilodauria.github.io"})
        with open(os.path.join(OUT, nome), "wb") as fh:
            w.write(fh)
    br.close()
print("ok")
