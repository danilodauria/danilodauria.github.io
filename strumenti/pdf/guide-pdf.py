"""Versioni PDF delle guide gratuite (guide/*.html → pdf/guide/*.pdf). Rifà solo le guide cambiate.
Uso: python3 strumenti/pdf/guide-pdf.py URL_DEL_SITO [--sempre]   · Lo esegue GitHub Actions (pdf.yml). Autore: Danilo D'Auria - MIT."""
import hashlib, json, os, sys, time
from playwright.sync_api import sync_playwright
URL = sys.argv[1].rstrip("/") + "/"
SEMPRE = "--sempre" in sys.argv
QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(QUI))
OUT = os.path.join(REPO, "pdf", "guide")
os.makedirs(OUT, exist_ok=True)
CHROME = os.environ.get("CHROME") or (os.path.exists("/usr/bin/google-chrome") and "/usr/bin/google-chrome") or None
elenco = json.load(open(os.path.join(REPO, "guide", "elenco.json"), encoding="utf-8"))
f_imp = os.path.join(OUT, "impronte.json")
impronte = json.load(open(f_imp)) if os.path.exists(f_imp) else {}
motore = hashlib.sha256(open(__file__, "rb").read()).hexdigest()[:12]
da_fare = []
for g in elenco:
    h = motore + hashlib.sha256(open(os.path.join(REPO, "guide", g["id"] + ".html"), "rb").read()).hexdigest()
    if SEMPRE or impronte.get(g["id"]) != h or not os.path.exists(os.path.join(OUT, g["id"] + ".pdf")):
        da_fare.append((g, h))
if not da_fare:
    print("Guide PDF già aggiornate."); sys.exit(0)
PIEDE = ('<div style="width:100%;font-family:sans-serif;font-size:7.5px;color:#4f5c68;padding:0 16mm;display:flex;justify-content:space-between">'
         "<span>Guide gratuite di Danilo D'Auria · danilodauria.github.io · CC BY-NC-SA 4.0</span><span class=\"pageNumber\"></span></div>")
with sync_playwright() as p:
    br = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox"])
    pg = br.new_page()
    for g, h in da_fare:
        pg.goto(URL + "guide/" + g["id"] + ".html", wait_until="load"); pg.evaluate("document.fonts.ready"); time.sleep(.5)
        pg.emulate_media(media="print", color_scheme="light")
        pg.pdf(path=os.path.join(OUT, g["id"] + ".pdf"), format="A4", print_background=True, display_header_footer=True,
               header_template="<span></span>", footer_template=PIEDE, margin={"top": "16mm", "bottom": "18mm", "left": "16mm", "right": "16mm"})
        impronte[g["id"]] = h
        print("PDF:", g["id"])
    br.close()
json.dump(impronte, open(f_imp, "w"), indent=1, sort_keys=True)
