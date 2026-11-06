"""Controllo di accessibilità (WCAG 2.1 AA) con axe-core su pagina principale, guide, scheda e lettore PDF,
in chiaro e in scuro, su computer e su telefono. Scrive accessibilita.json, che legge il controllo settimanale.
Uso: python3 strumenti/accessibilita/controlla.py URL_DEL_SITO PERCORSO/axe.min.js   · Autore: Danilo D'Auria - MIT."""
import json, os, sys, time
from playwright.sync_api import sync_playwright
URL = sys.argv[1].rstrip("/") + "/"
AXE = open(sys.argv[2], encoding="utf-8").read()
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CHROME = os.environ.get("CHROME") or None
PAGINE = [("?lang=it", 1280, "light", "Pagina principale (computer, chiaro)"), ("?lang=it", 375, "dark", "Pagina principale (telefono, scuro)"),
          ("?lang=en", 375, "light", "Pagina principale in inglese (telefono)"), ("guide/truffe.html", 375, "light", "Guida «Truffe»"),
          ("guide/de/backup.html", 1280, "dark", "Guida in tedesco"), ("scheda/", 390, "light", "Scheda intervento"), ("pdf/leggi.html", 390, "light", "Lettore PDF")]
TAG = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]
esito = []
with sync_playwright() as p:
    br = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox"])
    for rel, w, cs, nome in PAGINE:
        pg = br.new_page(viewport={"width": w, "height": 900}, color_scheme=cs, locale="it-IT")
        try:
            pg.goto(URL + rel, wait_until="load", timeout=60000); time.sleep(1.5)
            pg.add_script_tag(content=AXE)
            r = pg.evaluate("t => axe.run(document, { runOnly: { type: 'tag', values: t } })", TAG)
            v = [{"regola": x["id"], "gravita": x.get("impact"), "quanti": len(x["nodes"]), "aiuto": x["help"],
                  "dove": [" ".join(n["target"]) for n in x["nodes"][:3]]} for x in r["violations"]]
            esito.append({"pagina": nome, "url": rel, "violazioni": v})
            print(nome, "→", len(v), "problemi")
        except Exception as e:
            esito.append({"pagina": nome, "url": rel, "errore": str(e)[:200]})
            print(nome, "→ non controllata:", e)
        pg.close()
    br.close()
json.dump(esito, open(os.path.join(REPO, "accessibilita.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
