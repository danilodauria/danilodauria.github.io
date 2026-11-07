"""Controllo settimanale del sito: link delle fonti, link interni e file locali, bandi in scadenza, date da rivedere, traduzioni mancanti, accessibilità, casi reali.
Scrive il resoconto in controllo.md e dice (variabile PROBLEMI) se c'è qualcosa da fare. Lo esegue GitHub Actions (controllo.yml),
che apre o aggiorna un avviso nella scheda «Issues» del repository: GitHub vi manda anche un'email.
Uso locale: python3 strumenti/controllo-settimanale.py [CARTELLA_REPO]. Autore: Danilo D'Auria · MIT."""
import datetime as dt, json, os, re, sys, urllib.request, urllib.error

REPO = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OGGI = dt.date.today()
MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto", "settembre", "ottobre", "novembre", "dicembre"]
def d_it(d): return "%d %s %d" % (d.day, MESI[d.month - 1], d.year)
def iso(s): return dt.date.fromisoformat(s)
def leggi(nome): return json.load(open(os.path.join(REPO, nome), encoding="utf-8"))

da_fare, attenzione, info = [], [], []

# ---- link delle fonti
def prova(url, tentativi=2):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (controllo settimanale del sito danilodauria.github.io)"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        if tentativi > 1:
            import time; time.sleep(5)
            return prova(url, tentativi - 1)
        return "errore: " + type(e).__name__

bandi, offerte = leggi("bandi.json"), leggi("offerte.json")
link = [("Bando «%s»" % b["titolo"], b["fonte"]) for b in bandi["bandi"] if b.get("fonte")]
link += [("Offerta «%s»" % e["titolo"], e["fonte"]) for e in offerte["eventi"] if e.get("fonte")]
link += [("Pulsante «%s» di %s" % (c["ufficiale"][0], c["nome"]), c["ufficiale"][1]) for c in offerte["cerca"] if c.get("ufficiale")]
visti = set()
for nome, url in link:
    if url in visti: continue
    visti.add(url)
    st = prova(url)
    if isinstance(st, int) and st < 400: continue
    if st in (401, 403, 405, 429, 503):
        info.append("%s: il sito blocca i controlli automatici (%s). Se volete, aprite il link a mano: %s" % (nome, st, url))
    else:
        da_fare.append("%s: il link non risponde (%s). Va sostituito: %s" % (nome, st, url))

# ---- bandi
for b in bandi["bandi"]:
    if b.get("previsto"):
        info.append("Bando in arrivo «%s»: controllate se è stato pubblicato (%s)." % (b["titolo"], b.get("nota_scadenza", "")))
        continue
    if not b.get("scadenza"): continue
    g = (iso(b["scadenza"]) - OGGI).days
    if 0 <= g <= 14:
        attenzione.append("Il bando «%s» scade tra %d giorni (%s)." % (b["titolo"], g, d_it(iso(b["scadenza"]))))
    elif -30 <= g < 0:
        info.append("Il bando «%s» è chiuso dal %s: si può tenere tra i chiusi o togliere." % (b["titolo"], d_it(iso(b["scadenza"]))))
eta_b = (OGGI - iso(bandi["aggiornato"])).days
if eta_b > 30:
    da_fare.append("L'elenco dei bandi non viene rivisto da %d giorni: chiedete a Claude di cercare i bandi nuovi." % eta_b)

# ---- offerte e prezzi delle licenze
eta_o = (OGGI - iso(offerte["aggiornato"])).days
if eta_o > 120:
    da_fare.append("Il calendario delle offerte non viene rivisto da %d giorni." % eta_o)
pagina = open(os.path.join(REPO, "index.html"), encoding="utf-8").read()
m = re.search(r"prezzi delle licenze verificati il (\d{1,2}) (\w+) (\d{4})", pagina)
if m and m.group(2) in MESI:
    verif = dt.date(int(m.group(3)), MESI.index(m.group(2)) + 1, int(m.group(1)))
    if (OGGI - verif).days > 90:
        da_fare.append("I prezzi delle licenze Windows e Office sono stati verificati il %s: è ora di ricontrollarli." % d_it(verif))
for e in offerte["eventi"]:
    if e.get("dal") and e.get("scadenza"):
        g = (iso(e["dal"]) - OGGI).days
        if 0 <= g <= 60:
            attenzione.append("«%s» tra %d giorni: avvisate i clienti che hanno ancora Windows 10." % (e["titolo"], g))

# ---- casi reali
try:
    casi = leggi("casi.json")["casi"]
    for k in casi:
        for campo in ("cliente", "contatto", "seriale"):
            if campo in k:
                da_fare.append("Nel caso «%s» c'è il campo «%s», che non va pubblicato: toglietelo." % (k.get("titolo", "?"), campo))
    info.append("Casi reali pubblicati: %d." % len(casi))
except Exception as e:
    da_fare.append("casi.json non è leggibile: %s" % e)

# ---- traduzioni (le prepara strumenti/i18n/estrai-testi.py, se è stato eseguito prima)
f_trad = os.path.join(REPO, "i18n", "mancanti.json")
if os.path.exists(f_trad):
    mancanti = json.load(open(f_trad, encoding="utf-8"))
    tot = {k: len(v) for k, v in mancanti.items() if v}
    if tot:
        da_fare.append("Frasi del sito ancora da tradurre: " + ", ".join("%s %d" % (k.upper(), n) for k, n in sorted(tot.items())) +
                       ". Chiedete a Claude di completare le traduzioni (finché mancano, quelle frasi restano in italiano).")

# ---- accessibilità (la prepara strumenti/accessibilita/controlla.py con axe-core, se è stato eseguito prima)
f_acc = os.path.join(REPO, "accessibilita.json")
if os.path.exists(f_acc):
    for pag in json.load(open(f_acc, encoding="utf-8")):
        if pag.get("errore"):
            info.append("Accessibilità: la pagina «%s» non si è potuta controllare." % pag["pagina"])
        for v in pag.get("violazioni", []):
            voce = "Accessibilità, %s: %s (%s, %d punti, per esempio %s)." % (pag["pagina"], v["aiuto"], v["regola"], v["quanti"], ", ".join(v["dove"][:2]))
            (da_fare if v.get("gravita") in ("critical", "serious") else attenzione).append(voce)
    if not any(pag.get("violazioni") for pag in json.load(open(f_acc, encoding="utf-8"))):
        info.append("Accessibilità (WCAG 2.1 AA, axe-core): nessun problema sulle pagine controllate.")

# ---- pagine: link locali, file JSON, lunghezza dei titoli, indirizzi del sitemap
# Li controlla strumenti/controlla-pagine.py, lo stesso che si può lanciare a mano:
#   python3 strumenti/controlla-pagine.py
try:
    import importlib.util
    specifica = importlib.util.spec_from_file_location("controlla_pagine", os.path.join(REPO, "strumenti", "controlla-pagine.py"))
    modulo = importlib.util.module_from_spec(specifica)
    specifica.loader.exec_module(modulo)
    p_problemi, p_attenzione, p_info = modulo.controlla(REPO)
    da_fare += p_problemi
    attenzione += p_attenzione
    info += p_info
except Exception as e:
    info.append("Controllo delle pagine non riuscito: %s" % e)

# ---- resoconto
def blocco(titolo, voci): return ("### %s\n\n" % titolo + "\n".join("- [ ] " + v if titolo.startswith("Da fare") else "- " + v for v in voci) + "\n\n") if voci else ""
corpo = "Controllo automatico del %s.\n\n" % d_it(OGGI)
corpo += blocco("Da fare", da_fare) + blocco("Da tenere d'occhio", attenzione) + blocco("Per informazione", info)
if not (da_fare or attenzione):
    corpo += "Tutto in ordine: nessun link rotto, nessuna scadenza imminente, niente da rivedere.\n"
corpo += "\n_Questo avviso lo scrive ogni lunedì il robot del sito (.github/workflows/controllo.yml)._\n"
open(os.path.join(REPO, "controllo.md"), "w", encoding="utf-8").write(corpo)
print(corpo)
problemi = "si" if (da_fare or attenzione) else "no"
if os.environ.get("GITHUB_OUTPUT"):
    open(os.environ["GITHUB_OUTPUT"], "a").write("problemi=%s\n" % problemi)
