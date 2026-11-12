"""Schede dei progetti sempre allineate ai programmi: testi e immagini.

Lo esegue GitHub Actions (progetti.yml) ogni ora, dopo aggiorna-progetti.py e versioni-schede.py.
Per ogni scheda della home con data-repo="…":

1. NUMERI. Legge la tabella «Che cosa contiene / Cosa fa / Cosa offre» del README del progetto e,
   se nella scheda c'è «70 schede di piante» e nel README ora c'è «72 schede di piante», corregge il
   numero. Si confronta la stessa espressione (numero + parole che seguono), quindi non tocca altro.
2. ARGOMENTI NUOVI. Se nella tabella del README compare una sezione nuova, aggiunge alla scheda una
   riga «Novità della 1.3.38: …». C'è al massimo una riga di novità per scheda: la nuova sostituisce
   la vecchia, e dopo 90 giorni sparisce da sola. Così la scheda non si allunga mai.
3. IMMAGINE. Quando cambia la versione, rifà la fotografia della pagina del programma (1280×800,
   ridotta a 960×600) e la mette nella scheda; aggiorna anche il numero di versione nel testo
   alternativo. Le fotografie richiedono Playwright: il primo passaggio scrive in .scatti-da-fare
   quali servono, il workflow installa Playwright solo se serve e rilancia con --scatti.

Lo stato (sezioni viste, versione fotografata) sta in vetrine.json.
Uso: python3 strumenti/vetrine.py [--scatti] [--tutti-gli-scatti] [--readme-da CARTELLA]
Autore: Danilo D'Auria - MIT."""
import base64, datetime, html, io, json, os, re, sys, time, urllib.request

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(QUI)
UTENTE = "danilodauria"
PAGINA = os.path.join(REPO, "index.html")
STATO = os.path.join(REPO, "vetrine.json")
DA_FARE = os.path.join(REPO, ".scatti-da-fare")
OGGI = datetime.date.today()

# Come fotografare ogni programma. "salta": la scheda ha un'immagine fissa (per esempio una copertina).
SCATTI = {
    "professore-digitale": {"url": "https://danilodauria.github.io/professore-digitale/"},
    "feniceos": {"url": "https://danilodauria.github.io/feniceos/"},
    "consulente-digitale": {"url": "https://danilodauria.github.io/consulente-digitale/"},
    "naturopata-digitale": {"url": "https://danilodauria.github.io/naturopata-digitale/"},
    "psicologo-digitale": {"url": "https://danilodauria.github.io/psicologo-digitale/"},
    "grande-quiz": {"url": "https://danilodauria.github.io/grande-quiz/"},
    "nonni-teach": {"salta": True},
}
# Sezioni del README che non sono argomenti da mostrare a chi visita il sito.
NON_ARGOMENTI = {"licenze", "installa", "installare", "sviluppo", "desktop", "sicurezza", "stop", "reset", "backup"}
GIORNI_NOVITA = 90

argomenti = sys.argv[1:]
SCATTI_ORA = "--scatti" in argomenti
TUTTI_GLI_SCATTI = "--tutti-gli-scatti" in argomenti
README_DA = argomenti[argomenti.index("--readme-da") + 1] if "--readme-da" in argomenti else None


def scarica(url, tentativi=3):
    for n in range(tentativi):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "vetrine-sito"}), timeout=30) as r:
                return r.read().decode("utf-8", "replace")
        except Exception:
            time.sleep(3 * (n + 1))
    return None


def readme(nome):
    if README_DA:
        f = os.path.join(README_DA, nome, "README.md")
        return open(f, encoding="utf-8").read() if os.path.exists(f) else None
    return scarica("https://raw.githubusercontent.com/%s/%s/HEAD/README.md" % (UTENTE, nome))


def pulisci_md(t):
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
    t = re.sub(r"[*_`]", "", t)
    t = re.sub(r"[\U0001F000-\U0001FAFF☀-➿️]", "", t)
    return re.sub(r"\s+", " ", t).strip()


def sezioni(testo):
    """Righe della tabella dei contenuti: | **Erbario** | 70 schede … |  →  [("Erbario", "70 schede …")]."""
    out = []
    for riga in testo.splitlines():
        m = re.match(r"\|\s*([^|]*\*\*[^|]+\*\*[^|]*)\|\s*(.+?)\s*\|\s*$", riga)
        if m:
            nome = pulisci_md(m.group(1)).strip(" ·")
            if nome and len(nome) < 60:
                out.append((nome, pulisci_md(m.group(2))))
    return out


def chiave(nome):
    return re.sub(r"[^a-zà-ù0-9]+", " ", nome.lower()).strip()


PAROLA = r"[a-zà-ù'’]+"
VUOTE = {"di", "da", "in", "e", "ed", "a", "con", "del", "della", "dei", "delle", "degli", "per", "su", "il", "la", "le", "i", "gli", "lo", "un", "una", "tra", "fra", "o"}


def aggiorna_numeri(li, fonte):
    """Nel testo della riga sostituisce «N parole» con il numero del README per la stessa espressione."""
    def sost(m):
        n, coda = m.group(1), m.group(2)
        parole = re.findall(PAROLA, coda.lower())
        for k in (3, 2, 1):
            if len(parole) < k:
                continue
            frase = r"\s+".join(re.escape(p) for p in parole[:k])
            if parole[k - 1] in VUOTE:
                continue                      # «schede di»: finisce con una parolina, troppo generica
            if k == 1 and len(parole[0]) < 5:
                continue                      # «12 mesi»: una parola corta da sola è troppo generica
            trovati = set(re.findall(r"(?<![\d.,])(\d+)\s+" + frase + r"(?![a-zà-ù])", fonte.lower()))
            if len(trovati) == 1:
                nuovo = trovati.pop()
                return nuovo + coda if nuovo != n else m.group(0)
            if len(trovati) > 1:
                return m.group(0)             # ambiguo: meglio non toccare
        return m.group(0)
    # solo nei pezzi di testo, non dentro i tag
    pezzi = re.split(r"(<[^>]+>)", li)
    for i, p in enumerate(pezzi):
        if not p.startswith("<"):
            pezzi[i] = re.sub(r"(?<![\d.,v])(\d+)((?:\s+" + PAROLA + r"){1,3})", sost, p)
    return "".join(pezzi)


def prima_frase(t, massimo=160):
    f = re.split(r"(?<=[.;:])\s", t, maxsplit=1)[0].rstrip(".;:")
    return f if len(f) <= massimo else f[:massimo].rsplit(" ", 1)[0] + "…"


def main():
    s = open(PAGINA, encoding="utf-8").read()
    stato = json.load(open(STATO, encoding="utf-8")) if os.path.exists(STATO) else {}
    progetti = {p["nome"]: p for p in json.load(open(os.path.join(REPO, "progetti.json"), encoding="utf-8"))["progetti"]}
    scatti = []
    resoconto = []

    def scheda(m):
        nome, corpo = m.group(2), m.group(3)
        st = stato.setdefault(nome, {})
        versione = (progetti.get(nome) or {}).get("versione") or ""
        testo = readme(nome)
        sez = sezioni(testo) if testo else []
        if sez:
            fonte = " \n ".join(a + ": " + b for a, b in sez)
            # 1) numeri nelle righe scritte a mano
            def riga(mm):
                if 'class="nuovo-auto"' in mm.group(1):
                    return mm.group(0)
                nuova = aggiorna_numeri(mm.group(2), fonte)
                if nuova != mm.group(2):
                    resoconto.append("%s: %s → %s" % (nome, re.sub("<[^>]+>", "", mm.group(2))[:60], re.sub("<[^>]+>", "", nuova)[:60]))
                return mm.group(1) + nuova + "</li>"
            corpo = re.sub(r"(<li[^>]*>)(.*?)</li>", riga, corpo, flags=re.S)
            # 2) argomenti nuovi
            viste = st.get("sezioni")
            attuali = [chiave(a) for a, _ in sez]
            if viste is not None:
                nuove = [(a, b) for a, b in sez if chiave(a) not in viste and chiave(a) not in NON_ARGOMENTI]
                if nuove:
                    a, b = nuove[0]
                    st["novita"] = {"sezione": a, "testo": prima_frase(b), "versione": versione, "data": OGGI.isoformat()}
                    resoconto.append("%s: argomento nuovo «%s»" % (nome, a))
            st["sezioni"] = sorted(set(attuali) | set(viste or []))
        # riga delle novità: al massimo una, e solo per 90 giorni
        corpo = re.sub(r"\s*<li class=\"nuovo-auto\"[^>]*>.*?</li>", "", corpo, flags=re.S)
        nv = st.get("novita")
        if nv and (OGGI - datetime.date.fromisoformat(nv["data"])).days > GIORNI_NOVITA:
            st.pop("novita"); nv = None
        if nv:
            et = "Novità della %s" % nv["versione"] if nv.get("versione") else "Novità"
            li = '<li class="nuovo-auto" data-dal="%s">%s: <b>%s</b> — %s.</li>' % (
                nv["data"], html.escape(et), html.escape(nv["sezione"]), html.escape(nv["testo"]))
            corpo = re.sub(r"(\s*)</ul>", lambda x: x.group(1) + "  " + li + x.group(1) + "</ul>", corpo, count=1)
        # 3) immagine da rifare?
        conf = SCATTI.get(nome, {})
        if not conf.get("salta") and conf.get("url") and versione and (TUTTI_GLI_SCATTI or st.get("versione_foto") not in (None, versione)):
            scatti.append(nome)
        if st.get("versione_foto") is None and versione:
            st["versione_foto"] = versione        # primo passaggio: la foto attuale vale per questa versione
        return m.group(1) + corpo + "</article>"

    s2 = re.sub(r'(<article class="prog[^"]*" id="p-[a-z]+" data-repo="([^"]+)">)(.*?)</article>', scheda, s, flags=re.S)

    if scatti and SCATTI_ORA:
        s2 = fotografa(s2, scatti, progetti, stato, resoconto)
        scatti = []
    if s2 != s:
        open(PAGINA, "w", encoding="utf-8").write(s2)
    json.dump(stato, open(STATO, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
    if scatti:
        open(DA_FARE, "w").write("\n".join(scatti) + "\n")
    elif os.path.exists(DA_FARE):
        os.remove(DA_FARE)
    print("Schede dei progetti:", "; ".join(resoconto) if resoconto else "niente da cambiare",
          ("· fotografie da rifare: " + ", ".join(scatti)) if scatti else "")


def chiudi_finestrelle(pg):
    """Chiude benvenuti, avvisi e banner che coprirebbero la pagina nella fotografia."""
    for testo in ("Non mostrarmelo più", "Non mostrare più", "Ho capito", "Chiudi", "Accetta", "Rifiuta", "Più tardi", "Salta"):
        try:
            b = pg.get_by_role("button", name=testo, exact=False)
            if b.count() and b.first.is_visible():
                b.first.click(timeout=2000); time.sleep(.6)
        except Exception:
            pass
    for sel in ('[aria-label^="Chiudi" i]', '[aria-label="Close" i]', "button.chiudi", ".chiudi"):
        try:
            for el in pg.locator(sel).all()[:3]:
                if el.is_visible():
                    el.click(timeout=2000); time.sleep(.4)
        except Exception:
            pass
    pg.keyboard.press("Escape"); time.sleep(.5)


def fotografa(s, nomi, progetti, stato, resoconto):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    chrome = os.environ.get("CHROME") or ("/usr/bin/google-chrome" if os.path.exists("/usr/bin/google-chrome") else None)
    with sync_playwright() as p:
        br = p.chromium.launch(executable_path=chrome, args=["--no-sandbox"])
        for nome in nomi:
            conf = SCATTI[nome]
            pg = br.new_page(viewport={"width": 1280, "height": 800}, locale="it-IT", color_scheme="light")
            try:
                risposta = pg.goto(conf["url"] + ("&" if "?" in conf["url"] else "?") + "v=" + str(int(time.time())), wait_until="networkidle", timeout=60000)
                if not risposta or not risposta.ok:
                    raise RuntimeError("la pagina risponde %s" % (risposta.status if risposta else "niente"))
                time.sleep(conf.get("attesa", 2.5))
                for sel in conf.get("clic", []):
                    pg.click(sel, timeout=5000); time.sleep(1)
                chiudi_finestrelle(pg)
                png = pg.screenshot()
            except Exception as e:
                resoconto.append("%s: fotografia non riuscita (%s)" % (nome, str(e)[:80]))
                pg.close(); continue
            pg.close()
            im = Image.open(io.BytesIO(png)).convert("RGB").resize((960, 600), Image.LANCZOS)
            buf = io.BytesIO(); im.save(buf, "JPEG", quality=74, optimize=True, progressive=True)
            if len(buf.getvalue()) < 20 * 1024 or len(im.resize((48, 30)).getcolors(48 * 30) or []) < 40:
                resoconto.append("%s: fotografia scartata, la pagina sembra vuota: resta quella di prima" % nome)
                continue                      # una pagina bianca o di errore non sostituisce la foto buona
            b64 = base64.b64encode(buf.getvalue()).decode()
            versione = progetti[nome].get("versione") or ""

            def cambia(m):
                art = re.sub(r'(<figure class="scatto"><img src="data:image/)\w+;base64,[^"]+"',
                             lambda x: x.group(1) + 'jpeg;base64,' + b64 + '"', m.group(0), count=1)
                if versione:
                    art = re.sub(r'(alt="[^"]*?versione )\d+(?:\.\d+)+', lambda x: x.group(1) + versione, art, count=1)
                return art
            s = re.sub(r'<article class="prog[^"]*" id="p-[a-z]+" data-repo="%s">.*?</article>' % re.escape(nome), cambia, s, count=1, flags=re.S)
            stato[nome]["versione_foto"] = versione
            resoconto.append("%s: fotografia rifatta (v%s, %d KB)" % (nome, versione, len(buf.getvalue()) // 1024))
        br.close()
    return s


if __name__ == "__main__":
    main()
