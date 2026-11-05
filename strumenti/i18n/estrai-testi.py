"""Raccoglie tutte le frasi del sito da tradurre (i18n/it.json) e quelle che mancano in ogni lingua (i18n/mancanti.json).
Apre il sito con Chromium, passa per tutte le schermate (profili, test, calcolatori, bandi, offerte) e usa lo stesso
motore della pagina: numeri e date diventano {n0}, {d0}, così una frase vale per tutti i numeri.
Uso: python3 strumenti/i18n/estrai-testi.py URL_DEL_SITO   · Autore: Danilo D'Auria · MIT."""
import itertools, json, os, sys, time
from playwright.sync_api import sync_playwright
URL = sys.argv[1]
QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(QUI))
DIR = os.path.join(REPO, "i18n")
os.makedirs(DIR, exist_ok=True)
CHROME = os.environ.get("CHROME") or (os.path.exists("/usr/bin/google-chrome") and "/usr/bin/google-chrome") or None

# Frasi che compaiono solo in certi momenti (senza rete, a una certa data…): già nella forma con {n0} e {d0}
EXTRA = [
 "Scade oggi", "Scade domani", "Mancano {n0} giorni", "Chiuso", "Aperto", "In arrivo", "Domani", "Tra {n0} giorni", "Ancora {n0} giorni", "Ultimo giorno",
 "Scadenza tra {n0} giorni", "Tutto l'anno", "Niente in questo periodo.",
 "Senza connessione: mostro l'elenco salvato del {d0}.", "Controllo l'elenco aggiornato…", "Online, ma l'elenco aggiornato non è raggiungibile: mostro quello salvato del {d0}.",
 "Online: elenco aggiornato al {d0}.", "Senza connessione: calendario salvato del {d0}. I prezzi di oggi si aprono quando torna Internet.", "Controllo le offerte aggiornate…",
 "Online, ma il calendario aggiornato non è raggiungibile: mostro quello salvato. I prezzi di oggi si aprono comunque.", "Online: calendario aggiornato al {d0}, prezzi di oggi a un clic.",
 "Nessuna scadenza aperta da aggiungere.", "Nessun bando con questi filtri. Provate «Tutti» oppure scrivetemi: cerco io quello adatto a voi.",
 "Copiato: incollatelo dove volete.", "Copiato. Ora incollatelo in una email a danilodauria.site@gmail.com.", "Non riesco a copiare da qui: selezionate il testo e copiatelo.", "Indirizzo copiato.", "Selezionate l'indirizzo e copiatelo.",
 "Il testo è selezionato: premete Ctrl + C (o Copia) per copiarlo.",
 "Ho preparato {n0} risposte: controllatele andando avanti.", "Da questo dispositivo non riesco a capire molto: rispondete voi.",
 "State usando un telefono o un tablet: fate il test dal computer da controllare, oppure rispondete a memoria.",
 "Per {n0} o più computer vi faccio un prezzo dedicato: chiedetemelo.", "Aggiornato in tempo reale da GitHub.", "Elenco dei progetti al {d0}.", "Per il Turbo Mac il ricambio dipende dal modello e lo concordiamo prima.",
 "{n0} anno", "{n0} anni", "Controllo la connessione…",
]

with sync_playwright() as p:
    br = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox"])
    pg = br.new_page(viewport={"width": 1280, "height": 900}, locale="it-IT")
    pg.goto(URL.rstrip("/") + "/?lang=it", wait_until="load"); time.sleep(2)
    raccogli = """() => { const ch = window.__i18n.chiave, out = new Set();
      const esc = el => !el || el.closest('script,style,noscript,.notranslate,[translate="no"],textarea,.email,title');
      const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let n;
      while ((n = w.nextNode())) { if (esc(n.parentNode)) continue; const t = n.nodeValue.replace(/\\s+/g, ' ').trim(); if (t && /[A-Za-zÀ-ÿ]/.test(t)) out.add(ch(t)); }
      document.querySelectorAll('[title],[aria-label],[placeholder],[alt]').forEach(el => { if (esc(el)) return; ['title','aria-label','placeholder','alt'].forEach(a => { const v = el.getAttribute(a); if (v && /[A-Za-zÀ-ÿ]/.test(v)) out.add(ch(v)); }); });
      out.add(ch(document.title)); return [...out]; }"""
    chiavi = set(pg.evaluate(raccogli))
    def giro(): chiavi.update(pg.evaluate(raccogli))
    # profili «Chi siete?»
    for b in pg.query_selector_all("#scelta button"):
        b.click(); time.sleep(.05); giro()
    # bandi: tutti
    pg.click("#filtro-stato button[data-v='tutti']"); time.sleep(.1); giro()
    for v in ["aperto", "arrivo", "chiuso"]:
        pg.click("#filtro-stato button[data-v='%s']" % v); time.sleep(.05); giro()
    # test: domande e tutte le risposte possibili del consiglio
    dati_test = pg.evaluate("""() => { const T = window.__test, ch = window.__i18n.chiave, out = new Set();
      T.DOMANDE.forEach(d => { out.add(ch(d.q)); if (d.aiuto) out.add(ch(d.aiuto)); d.o.forEach(o => out.add(ch(o[1]))); });
      const val = { tipo: ['portatile','fisso','mac'], eta: ['nuovo','medio','vecchio','?'], ram: ['2','4','8','?'], disco: ['ssd','hdd','?'],
                    sistema: ['win10'], uso: ['base','ufficio','pesante','semplice'], prog: ['si','no','?'] };
      const k = Object.keys(val); const rec = (i, r) => { if (i === k.length) { const e = T.consiglio(r); out.add(ch(e.titolo)); e.perche.forEach(x => out.add(ch(x))); if (e.alt) out.add(ch(e.alt));
          const p = T.LISTINO[e.sist].pacc.find(x => x[0] === e.pk) || T.LISTINO[e.sist].pacc[0]; out.add(ch(p[1])); return; }
        val[k[i]].forEach(v => { r[k[i]] = v; rec(i + 1, r); }); };
      rec(0, {}); Object.values(T.LISTINO).forEach(l => { out.add(ch(l.nome)); l.pacc.forEach(x => out.add(ch(x[1]))); }); return [...out]; }""")
    chiavi.update(dati_test)
    # un giro reale del test fino all'esito
    for v in ["mac", "medio", "?", "?", "base", "no"]:
        pg.click("#test-box .test-scelte button[data-v='%s']" % v); time.sleep(.05); giro()
    # calcolatori
    pg.click("#test-prev"); time.sleep(.2); giro()
    for _ in range(3): pg.click("#aggiungi-riga"); time.sleep(.05)
    pg.select_option("#righe-prev .riga-prev:nth-child(2) select[data-k='sist']", "mac"); time.sleep(.05)
    pg.select_option("#righe-prev .riga-prev:nth-child(2) select[data-k='pk']", "turbo"); time.sleep(.05)
    pg.select_option("#righe-prev .riga-prev:nth-child(3) select[data-k='sist']", "telefono"); time.sleep(.05)
    pg.fill("#righe-prev .riga-prev:nth-child(1) input", "7"); pg.dispatch_event("#righe-prev .riga-prev:nth-child(1) input", "change"); time.sleep(.05)
    pg.fill("[data-lic='w11pro']", "1"); pg.dispatch_event("[data-lic='w11pro']", "change"); time.sleep(.05); giro()
    pg.click("#tab-ris"); time.sleep(.1); giro()
    br.close()

chiavi.update(EXTRA)
chiavi = sorted(k for k in chiavi if k and any(c.isalpha() for c in k))
json.dump(chiavi, open(os.path.join(DIR, "it.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
mancanti = {}
for l in ["en", "fr", "es", "de", "ro"]:
    f = os.path.join(DIR, l + ".json")
    diz = json.load(open(f, encoding="utf-8")) if os.path.exists(f) else {}
    mancanti[l] = [k for k in chiavi if not diz.get(k)]
json.dump(mancanti, open(os.path.join(DIR, "mancanti.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("frasi:", len(chiavi), "· mancanti:", {k: len(v) for k, v in mancanti.items()})
