"""Bandi e calendario delle offerte sempre al giorno: lo esegue ogni mattina GitHub Actions (notizie.yml).

BANDI (bandi.json)
- «controllato» diventa la data di oggi: il sito mostra quando l'elenco è stato ricontrollato.
- Per i bandi senza scadenza (e non «previsti») legge la pagina della fonte: se trova una sola data
  futura vicino a «scadenza / entro / termine / chiusura», la mette come scadenza, con la nota
  «data letta in automatico dalla fonte: verificatela».
- I bandi chiusi da più di 120 giorni escono dall'elenco e passano in bandi-archivio.json.
- Bandi nuovi: guarda le pagine e i feed delle fonti ufficiali (FONTI qui sotto). Un avviso mai visto,
  con le parole giuste nel titolo, entra nell'elenco come «Segnalato» (campo "auto": true), con il
  collegamento alla fonte. Se resta «auto» per 45 giorni senza essere completato a mano, esce da solo.
  Al primo passaggio su una fonte si ricordano gli avvisi già presenti, senza aggiungerli.
- Una fonte che non risponde più finisce nel controllo del lunedì (campo "fonte_ko").

OFFERTE (offerte.json)
- «controllato» diventa la data di oggi; gli eventi con date fisse già finiti escono dal file
  (quelli con una regola annuale, come il Black Friday, si ricalcolano da soli sulla pagina).

In fondo copia i due elenchi aggiornati dentro index.html (le copie di riserva SALVATI e OFF_SALVATE),
così anche senza linea, e nel GitHub di casa, si vede l'elenco nuovo.
Uso: python3 strumenti/notizie.py [--senza-rete] [--elenca]   · Autore: Danilo D'Auria - MIT."""
import datetime, hashlib, html, json, os, re, sys, time, urllib.request

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(QUI)
OGGI = datetime.date.today()
SENZA_RETE = "--senza-rete" in sys.argv
ELENCA = "--elenca" in sys.argv   # stampa gli avvisi delle fonti che hanno le parole giuste, già visti o no
GIORNI_CHIUSI = 120
GIORNI_SEGNALATI = 45

# Dove cercare avvisi nuovi. Un feed RSS o una pagina con l'elenco degli avvisi.
FONTI = [
    {"nome": "Fondo per la Repubblica Digitale", "url": "https://www.fondorepubblicadigitale.it/feed/", "per": ["terzo-settore", "enti", "scuole"]},
    {"nome": "Fondo per la Repubblica Digitale", "url": "https://www.fondorepubblicadigitale.it/iniziative/", "per": ["terzo-settore", "enti", "scuole"]},
    {"nome": "Agenzia Erasmus+ INDIRE", "url": "https://www.erasmusplus.it/feed/", "per": ["terzo-settore", "enti", "scuole"]},
    {"nome": "Dipartimento per la trasformazione digitale", "url": "https://innovazione.gov.it/notizie/", "per": ["enti", "terzo-settore"]},
    {"nome": "Regione Lazio", "url": "https://www.regione.lazio.it/avvisi-e-bandi", "per": ["enti", "terzo-settore", "aziende"]},
    {"nome": "Regione Lazio · Fondi europei", "url": "https://fesr.regione.lazio.it/category/bandi/feed/", "per": ["enti", "terzo-settore", "aziende"]},
]
AVVISO = re.compile(r"\b(bando|bandi|avviso|call|invito a presentare|voucher|contribut|finanziament)", re.I)
TEMA = re.compile(r"(digital|competenz|inclusion|alfabetizz|formazion|erasmus|adulti|innovazion|intelligenza artificiale|\bia\b|informatic|anzian|scuol|stem)", re.I)

MESI = {m: i + 1 for i, m in enumerate(["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio",
                                         "agosto", "settembre", "ottobre", "novembre", "dicembre"])}


def scarica(url, tentativi=2):
    if SENZA_RETE:
        return None, None
    for n in range(tentativi):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (sito danilodauria.github.io; controllo bandi)"})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status, r.read(3_000_000).decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code < 500:
                return e.code, None
        except Exception:
            pass
        time.sleep(4 * (n + 1))
    return None, None


def testo_di(h):
    h = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", h)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", h))).strip()


def date_in(t):
    out = []
    for g, m, a in re.findall(r"\b(\d{1,2})[/.-](\d{1,2})[/.-](20\d\d)\b", t):
        out.append((int(a), int(m), int(g)))
    for g, m, a in re.findall(r"\b(\d{1,2})(?:°|º)?\s+(" + "|".join(MESI) + r")\s+(20\d\d)\b", t, re.I):
        out.append((int(a), MESI[m.lower()], int(g)))
    res = []
    for a, m, g in out:
        try:
            res.append(datetime.date(a, m, g))
        except ValueError:
            pass
    return res


def scadenza_dalla_fonte(url):
    stato, h = scarica(url)
    if not h:
        return stato, None
    t = testo_di(h)
    vicine = set()
    for m in re.finditer(r"(scadenz|entro (?:il|le ore)|termine|chiusura|fino al)", t, re.I):
        for d in date_in(t[m.start(): m.start() + 120]):
            if d >= OGGI:
                vicine.add(d)
    return stato, (min(vicine) if len(vicine) == 1 else None)


STATO_FONTI = []


def avvisi_della_fonte(f):
    """[(titolo, link, data_pubblicazione|None)] dalla fonte: feed RSS/Atom o pagina HTML."""
    stato, h = scarica(f["url"])
    STATO_FONTI.append("%s %s" % (f["url"], stato or "non raggiungibile"))
    if not h:
        return None
    out = []
    if "<rss" in h[:500] or "<feed" in h[:500] or "<channel" in h[:2000]:
        for it in re.findall(r"(?is)<(?:item|entry)\b.*?</(?:item|entry)>", h):
            ti = re.search(r"(?is)<title[^>]*>(.*?)</title>", it)
            li = re.search(r"(?is)<link[^>]*>(.*?)</link>", it) or re.search(r'(?is)<link[^>]*href="([^"]+)"', it)
            pd = re.search(r"(?is)<(?:pubDate|published|updated)>(.*?)</", it)
            if ti and li:
                tit = testo_di(re.sub(r"<!\[CDATA\[|\]\]>", "", ti.group(1)))
                out.append((tit, li.group(1).strip(), pd.group(1).strip() if pd else None))
    else:
        base = re.match(r"https?://[^/]+", f["url"]).group(0)
        for href, corpo in re.findall(r'(?is)<a\b[^>]*href="([^"#]+)"[^>]*>(.*?)</a>', h):
            tit = testo_di(corpo)
            if 12 <= len(tit) <= 160:
                if href.startswith("/"):
                    href = base + href
                if href.startswith("http"):
                    out.append((tit, href, None))
    return out


def main():
    fb = os.path.join(REPO, "bandi.json")
    fo = os.path.join(REPO, "offerte.json")
    fv = os.path.join(REPO, "fonti-viste.json")
    fa = os.path.join(REPO, "bandi-archivio.json")
    bandi = json.load(open(fb, encoding="utf-8"))
    offerte = json.load(open(fo, encoding="utf-8"))
    viste = json.load(open(fv, encoding="utf-8")) if os.path.exists(fv) else {}
    archivio = json.load(open(fa, encoding="utf-8")) if os.path.exists(fa) else {"bandi": []}
    prima = json.dumps(bandi["bandi"], ensure_ascii=False, sort_keys=True)
    resoconto = []

    # 1) scadenze trovate sulle fonti e fonti che non rispondono
    for b in bandi["bandi"]:
        if not b.get("fonte") or SENZA_RETE:
            continue
        if b.get("scadenza") is None and not b.get("previsto") and not b.get("auto"):
            stato, d = scadenza_dalla_fonte(b["fonte"])
            if d:
                b["scadenza"] = d.isoformat()
                b["nota_scadenza"] = "data letta in automatico dalla fonte: verificatela"
                resoconto.append("scadenza trovata per «%s»: %s" % (b["titolo"], d))
        else:
            stato, _ = scarica(b["fonte"])
        if stato in (404, 410):
            b["fonte_ko"] = OGGI.isoformat()
        else:
            b.pop("fonte_ko", None)

    # 2) avvisi nuovi dalle fonti ufficiali
    noti = {b.get("fonte") for b in bandi["bandi"]} | {b.get("fonte") for b in archivio["bandi"]}
    for f in FONTI:
        avvisi = avvisi_della_fonte(f)
        if avvisi is None:
            continue
        chiave = f["url"]
        primo_giro = chiave not in viste
        gia = set(viste.get(chiave, []))
        for tit, link, _ in avvisi:
            if ELENCA and AVVISO.search(tit) and TEMA.search(tit):
                print("  avviso alla fonte %s: %s · %s%s" % (f["nome"], tit, link, " (già in elenco)" if link in noti else ""))
            h = hashlib.sha1(link.encode()).hexdigest()[:12]
            if h in gia:
                continue
            gia.add(h)
            if primo_giro or link in noti or not (AVVISO.search(tit) and TEMA.search(tit)):
                continue
            bandi["bandi"].append({
                "id": "auto-" + h, "auto": True, "trovato": OGGI.isoformat(),
                "titolo": tit, "ente": f["nome"], "per": f["per"],
                "cosa": "Avviso nuovo, trovato in automatico tra le fonti ufficiali: leggete requisiti, importi e date sul sito della fonte.",
                "importo": "da leggere sulla fonte", "scadenza": None,
                "aiuto": "Se fa per voi, scrivetemi: prepariamo insieme il progetto con il kit per i bandi.",
                "fonte": link})
            resoconto.append("avviso nuovo: «%s» (%s)" % (tit, f["nome"]))
        viste[chiave] = sorted(gia)[-2000:]
        STATO_FONTI[-1] += " (%d collegamenti)" % len(avvisi)

    # 3) pulizia: segnalati scaduti e chiusi vecchi
    restano = []
    for b in bandi["bandi"]:
        if b.get("auto") and (OGGI - datetime.date.fromisoformat(b["trovato"])).days > GIORNI_SEGNALATI:
            resoconto.append("tolto il segnalato «%s» (45 giorni)" % b["titolo"]); continue
        if b.get("scadenza") and (OGGI - datetime.date.fromisoformat(b["scadenza"])).days > GIORNI_CHIUSI:
            archivio["bandi"].append(b); resoconto.append("archiviato «%s»" % b["titolo"]); continue
        restano.append(b)
    bandi["bandi"] = restano
    if json.dumps(bandi["bandi"], ensure_ascii=False, sort_keys=True) != prima:
        bandi["aggiornato"] = OGGI.isoformat()
    bandi["controllato"] = OGGI.isoformat()

    # 4) offerte: via gli eventi a date fisse finiti
    ev = [e for e in offerte["eventi"] if not (e.get("al") and datetime.date.fromisoformat(e["al"]) < OGGI)]
    if len(ev) != len(offerte["eventi"]):
        resoconto.append("offerte: tolti %d eventi finiti" % (len(offerte["eventi"]) - len(ev)))
        offerte["eventi"] = ev
        offerte["aggiornato"] = OGGI.isoformat()
    offerte["controllato"] = OGGI.isoformat()

    def scrivi(f, d, indent=2):
        t = json.dumps(d, ensure_ascii=False, indent=indent)
        if indent:   # elenchi brevi di parole su una riga, come nei file scritti a mano
            t = re.sub(r'\[\s*((?:"[^"\n]{0,40}",\s*)*"[^"\n]{0,40}")\s*\]', lambda m: "[" + re.sub(r",\s+", ", ", m.group(1)) + "]", t)
        open(f, "w", encoding="utf-8").write(t + "\n")
    scrivi(fb, bandi); scrivi(fo, offerte); scrivi(fv, viste, None)
    if archivio["bandi"]:
        scrivi(fa, archivio)

    # 5) copie di riserva dentro la pagina
    fi = os.path.join(REPO, "index.html")
    s = open(fi, encoding="utf-8").read()
    s2 = re.sub(r"(?m)^(  var SALVATI = ).*;$", lambda m: m.group(1) + json.dumps(bandi, ensure_ascii=False).replace("</", "<\\/") + ";", s, count=1)
    s2 = re.sub(r"(?m)^(  var OFF_SALVATE = ).*;$", lambda m: m.group(1) + json.dumps(offerte, ensure_ascii=False).replace("</", "<\\/") + ";", s2, count=1)
    if s2 != s:
        open(fi, "w", encoding="utf-8").write(s2)
    print("Bandi e offerte:", "; ".join(resoconto) if resoconto else "nessun cambiamento, solo la data di controllo")
    print("Fonti:", " · ".join(STATO_FONTI) or "nessuna")


if __name__ == "__main__":
    main()
