"""Controllo settimanale del sito: link delle fonti, link interni e file locali, bandi in scadenza, date da rivedere, traduzioni mancanti, accessibilità, casi reali, sito pubblicato.
Il resoconto ha due parti separate: quello che c'è nei file del repository e quello che risponde davvero il sito online.
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
# Le righe del sito online stanno a parte: nel resoconto hanno una sezione loro, così non si
# confondono con quello che c'e' (o manca) nei file del repository.
pubblicato, pubblicato_avvisi = [], 0


def controllo_del_sito(modulo, pausa=40, tentativi=3):
    """Il sito davvero online, con calma: un ritardo di GitHub Pages non deve far rumore.

    Si riprova qualche volta aspettando: se il sito e' solo indietro di qualche minuto, al
    secondo o al terzo tentativo torna a posto e non resta niente nel resoconto. Se invece
    non risponde affatto, e' un disservizio di GitHub e non una cosa da correggere qui.
    Quello che si vede online nasce da una pubblicazione, quindi i suoi problemi diventano
    avvisi da tenere d'occhio, mai cose da fare. Restituisce (problemi, attenzione, info, stato),
    dove lo stato e' "allineato", "da guardare" o "non controllato".
    """
    import time
    for tentativo in range(1, tentativi + 1):
        stato, _, _, errore = modulo.scarica(modulo.SITO + "/", {})
        if stato != 200:
            if tentativo < tentativi:
                time.sleep(pausa)
                continue
            causa = "risposta %d" % stato if stato else errore
            return [], [], ["Sito pubblicato: non ha risposto (%s). Se il sito si apre, era un "
                            "disservizio passeggero di GitHub." % causa], "non controllato"
        try:
            problemi, _, resoconto = modulo.controlla_pubblicato(modulo.SITO)
        except Exception as errore:
            return [], [], ["Sito pubblicato: non si e' potuto controllare (%s)." % errore], "non controllato"
        if not problemi:
            return [], [], ["Sito pubblicato: " + riga for riga in resoconto], "allineato"
        if tentativo == tentativi:
            avvisi = ["Sito pubblicato: il sito che risponde non e' ancora quello preparato qui."]
            avvisi += ["Sito pubblicato: " + riga for riga in problemi[:8]]
            avvisi.append("Sito pubblicato: se avete appena pubblicato, GitHub Pages puo' impiegare qualche "
                          "minuto. Altrimenti la pubblicazione non e' arrivata. In dubbio, rilanciate il controllo.")
            return [], avvisi, [], "da guardare"
        time.sleep(pausa)
    return [], [], [], "non controllato"

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
modulo = None
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

# ---- il sito davvero online: quello che vede chi arriva (con la pazienza di controllo_del_sito)
# Nel resoconto ha una sezione sua, separata dai problemi dei file: gli avvisi contano come
# "problemi=si" (aprono l'avviso), ma non si mescolano con le cose da fare nel repository.
sito_online = "non controllato"
if modulo:
    o_problemi, o_attenzione, o_info, sito_online = controllo_del_sito(modulo)
    pubblicato_avvisi = len(o_attenzione)
    pubblicato += ["**Da guardare:** " + riga.replace("Sito pubblicato: ", "") for riga in o_attenzione]
    pubblicato += [riga.replace("Sito pubblicato: ", "") for riga in o_info]

# ---- resoconto
def blocco(titolo, voci): return ("### %s\n\n" % titolo + "\n".join("- [ ] " + v if titolo.startswith("Da fare") else "- " + v for v in voci) + "\n\n") if voci else ""
def blocco_pubblicato(voci):
    if not voci: return ""
    return ("### Sito pubblicato\n\n"
            "Quello che risponde davvero online. Qui non c'e' niente da correggere nei file: se qualcosa non "
            "torna, la pubblicazione non e' arrivata o non e' completa.\n\n"
            + "\n".join("- " + v for v in voci) + "\n\n")
# Prima riga: a colpo d'occhio, se il sito che risponde e' quello preparato qui.
RIGHE_STATO = {
    "allineato": "**Sito online: allineato** - quello che risponde e' la versione preparata qui.",
    "da guardare": "**Sito online: diverso da quello preparato** - i dettagli sono nella sezione «Sito pubblicato»; "
                   "se avete appena pubblicato, puo' essere un ritardo di GitHub Pages.",
    "non controllato": "**Sito online: non controllato** - il sito non ha risposto, oppure il controllo non e' partito.",
}
corpo = "Controllo automatico del %s.\n\n" % d_it(OGGI)
corpo += RIGHE_STATO.get(sito_online, RIGHE_STATO["non controllato"]) + "\n\n"
corpo += ("Due parti separate: **nei file** (quello che c'e' nel repository) e **sito pubblicato** "
          "(quello che risponde davvero online).\n\n")
corpo += (blocco("Da fare nei file", da_fare) + blocco_pubblicato(pubblicato)
          + blocco("Da tenere d'occhio nei file", attenzione) + blocco("Per informazione", info))
if not (da_fare or attenzione or pubblicato_avvisi):
    corpo += ("Tutto in ordine: nessun link rotto, nessuna scadenza imminente, niente da rivedere, "
              "e il sito online e' quello preparato qui.\n")
corpo = corpo.rstrip() + "\n\n_Questo avviso lo scrive ogni lunedì il robot del sito (.github/workflows/controllo.yml)._\n"
open(os.path.join(REPO, "controllo.md"), "w", encoding="utf-8").write(corpo)
print(corpo)
problemi = "si" if (da_fare or attenzione or pubblicato_avvisi) else "no"
if os.environ.get("GITHUB_OUTPUT"):
    open(os.environ["GITHUB_OUTPUT"], "a").write("problemi=%s\n" % problemi)
