#!/usr/bin/env python3
"""Controllo di sicurezza del sito: segreti finiti per sbaglio, robot di GitHub troppo
permissivi, indirizzi che diventano comandi, lettore PDF vecchio, file privati che GitHub
Pages servirebbe lo stesso.

Uso:
    python3 strumenti/sicurezza.py               # solo i file del repository
    python3 strumenti/sicurezza.py --pubblicato  # anche il sito online

Esce con 1 se c'è qualcosa da sistemare, 0 se è tutto a posto. Solo libreria standard.
Autore: Danilo D'Auria · licenza MIT.
"""
import json, os, re, subprocess, sys
import urllib.error, urllib.request
import xml.etree.ElementTree as ET

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(QUI)
INDIRIZZO = "https://danilodauria.github.io/"

# Il lettore PDF deve restare almeno alla 4.2.67, che chiude CVE-2024-4367 (JavaScript
# arbitrario dentro un PDF costruito apposta). La versione sta in pdf/pdfjs/versione.txt e
# il controllo verifica che corrisponda davvero ai file, non solo alla riga scritta a mano.
PDFJS_SICURO = (4, 2, 67)

SCHEMI_BUONI = ("http://", "https://", "mailto:", "/", "#", "./", "../")

SEGRETI = [
    (re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}"), "token di GitHub"),
    (re.compile(r"github_pat_[A-Za-z0-9_]{20,}"), "token di GitHub"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "chiave di AWS"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "chiave privata"),
    (re.compile(r"(?i)\b(api[_-]?key|segreto|secret|password|passwd|token)\b\s*[:=]\s*['\"][^'\"]{12,}['\"]"),
     "chiave o password scritta in chiaro"),
]

# File che non devono mai stare nel repository: sono copie locali, registri o pacchetti.
NOMI_VIETATI = re.compile(
    r"(^|/)(\.env(\..*)?|id_rsa|.*\.(pem|key|p12|pfx|log|zip|bundle|bak|ps1|kdbx))$", re.I)

FILE_DATI = ["progetti.json", "novita.json", "casi.json", "bandi.json", "offerte.json",
             "prenota.json", "guide/elenco.json", "guide/piedi.json", "pdf/info.json"]
CHIAVI_LINK = ("link", "sito", "github", "url", "fonte", "homepage")

# Indirizzi che GitHub Pages non deve servire, e che invece servirebbe se qualcuno
# lasciasse in giro una copia del lavoro.
DA_NON_TROVARE = [".git/config", ".git/HEAD", ".env", "pubblica.ps1", "server.log",
                  "backup-sito.zip", "aggiornamenti.bundle", "controllo.md", "node_modules/"]

# Pagine che robots.txt chiede ai motori di non elencare: restano raggiungibili a chi
# conosce l'indirizzo, perché su GitHub Pages non esiste un lucchetto.
NASCOSTE_MA_APERTE = ["scheda/", "strumenti/", "vista.html"]

problemi, avvisi = [], []


def problema(testo):
    problemi.append(testo)


def avviso(testo):
    avvisi.append(testo)


def percorso(relativo):
    return os.path.join(REPO, relativo)


def testo_di(relativo):
    """Il contenuto del file, oppure None se è un binario (caratteri nulli nei primi byte)."""
    try:
        with open(percorso(relativo), "rb") as f:
            dati = f.read()
    except OSError:
        return None
    if b"\0" in dati[:2048]:
        return None
    return dati.decode("utf-8", "replace")


def tracciati():
    """I file che stanno davvero nel repository (git ls-files), o tutti se git non c'è."""
    try:
        esito = subprocess.run(["git", "-C", REPO, "ls-files"], capture_output=True,
                               text=True, check=True)
        elenco = [r.strip() for r in esito.stdout.splitlines() if r.strip()]
        if elenco:
            return elenco
    except (OSError, subprocess.CalledProcessError):
        pass
    elenco = []
    for base, cartelle, file in os.walk(REPO):
        cartelle[:] = [c for c in cartelle if c not in (".git", "node_modules", "__pycache__")]
        for nome in file:
            elenco.append(os.path.relpath(os.path.join(base, nome), REPO).replace(os.sep, "/"))
    return sorted(elenco)


def controlla_segreti(elenco):
    for relativo in elenco:
        if NOMI_VIETATI.search(relativo):
            problema("%s: è un file che non va pubblicato (copia, registro o chiave), "
                     "va tolto dal repository" % relativo)
        contenuto = testo_di(relativo)
        if contenuto is None:
            continue
        for espressione, cosa in SEGRETI:
            trovato = espressione.search(contenuto)
            if trovato:
                pezzo = trovato.group(0)[:60].replace("\n", " ")
                problema("%s: sembra esserci %s (%s…)" % (relativo, cosa, pezzo[:28]))


def controlla_workflow():
    """I robot girano con un gettone che può scrivere nel repository: va tenuto corto."""
    cartella = os.path.join(REPO, ".github", "workflows")
    if not os.path.isdir(cartella):
        return
    for nome in sorted(os.listdir(cartella)):
        if not nome.endswith((".yml", ".yaml")):
            continue
        etichetta = ".github/workflows/" + nome
        contenuto = open(os.path.join(cartella, nome), encoding="utf-8").read()
        if not re.search(r"(?m)^permissions:", contenuto):
            problema("%s: manca «permissions:», quindi il gettone prende i permessi che "
                     "GitHub dà di suo (scrivere su tutto il repository)" % etichetta)
        if "pull_request_target" in contenuto:
            problema("%s: usa «pull_request_target», che esegue codice di estranei con i "
                     "segreti del repository" % etichetta)
        if re.search(r"permissions:\s*(write-all|\{\s*\})", contenuto):
            problema("%s: i permessi sono troppo larghi (write-all o vuoti)" % etichetta)
        if re.search(r"\$\{\{\s*github\.(event|head_ref)", contenuto):
            problema("%s: mette nel comando un valore che arriva da fuori "
                     "(github.event / github.head_ref): è un modo per far eseguire comandi" % etichetta)
        for riga in contenuto.splitlines():
            azione = re.match(r"\s*-?\s*uses:\s*(\S+)", riga)
            if not azione:
                continue
            nome_azione = azione.group(1).strip("'\"")
            if nome_azione.startswith(("./", "docker://")):
                continue
            if not re.search(r"@[0-9a-f]{40}$", nome_azione):
                problema("%s: «%s» è fissata a un'etichetta, non a un'impronta: se "
                         "qualcuno riscrive quell'etichetta, il robot esegue altro codice"
                         % (etichetta, nome_azione))


def controlla_indirizzi():
    """Un indirizzo che arriva da un file dati non deve poter diventare «javascript:»."""
    for relativo in FILE_DATI:
        contenuto = testo_di(relativo)
        if contenuto is None:
            continue
        try:
            dati = json.loads(contenuto)
        except ValueError:
            problema("%s: non è JSON valido" % relativo)
            continue
        cattivi = []

        def cammina(valore, dove=""):
            if isinstance(valore, dict):
                for chiave, sotto in valore.items():
                    cammina(sotto, dove + "." + str(chiave))
            elif isinstance(valore, list):
                for n, sotto in enumerate(valore):
                    cammina(sotto, "%s[%d]" % (dove, n))
            elif isinstance(valore, str) and valore.strip():
                if any(c in dove.lower() for c in CHIAVI_LINK) and not valore.startswith(SCHEMI_BUONI):
                    cattivi.append((dove, valore[:70]))

        cammina(dati)
        for dove, valore in cattivi[:5]:
            problema("%s: %s contiene «%s», che non è un indirizzo web sicuro"
                     % (relativo, dove.lstrip("."), valore))


def controlla_lettore_pdf():
    """Il lettore PDF è un modulo ES: la versione dichiarata in pdf/pdfjs/versione.txt deve
    comparire anche dentro i file, così il numero non può restare indietro da solo."""
    for vecchio in ("pdf/pdfjs/pdf.min.js", "pdf/pdfjs/pdf.worker.min.js"):
        if os.path.exists(percorso(vecchio)):
            problema("%s: è la copia vecchia del lettore PDF, va tolta" % vecchio)
    contenuto = testo_di("pdf/pdfjs/pdf.min.mjs")
    if contenuto is None:
        problema("pdf/pdfjs/pdf.min.mjs manca: il lettore PDF non si carica "
                 "(pdf/leggi.html lo importa)")
        return
    dichiarata = (testo_di("pdf/pdfjs/versione.txt") or "").strip()
    if not re.match(r"^\d+\.\d+\.\d+$", dichiarata):
        problema("pdf/pdfjs/versione.txt manca o non contiene una versione (es. 4.10.38)")
        return
    if dichiarata not in contenuto:
        problema("pdf/pdfjs/versione.txt dice %s, ma dentro pdf.min.mjs quel numero non c'è: "
                 "il file è stato sostituito senza aggiornare la versione" % dichiarata)
    worker = testo_di("pdf/pdfjs/pdf.worker.min.mjs")
    if worker is None:
        problema("pdf/pdfjs/pdf.worker.min.mjs manca: il lettore non riesce a leggere i PDF")
    elif dichiarata not in worker:
        problema("pdf/pdfjs: pdf.min.mjs è la %s ma pdf.worker.min.mjs no: devono essere "
                 "la stessa versione" % dichiarata)
    pagina = testo_di("pdf/leggi.html") or ""
    if "pdf.min.mjs" not in pagina:
        problema("pdf/leggi.html non carica il lettore da pdf/pdfjs/pdf.min.mjs")
    versione = tuple(int(n) for n in dichiarata.split("."))
    if versione < PDFJS_SICURO and not re.search(r"isEvalSupported\s*:\s*false", pagina):
        problema("pdf/leggi.html: il lettore PDF è la %s, precedente alla %s che chiude "
                 "CVE-2024-4367; serve «isEvalSupported: false» in getDocument (oppure "
                 "l'aggiornamento del lettore)"
                 % (dichiarata, ".".join(map(str, PDFJS_SICURO))))


def controlla_collegamenti_esterni(elenco):
    for relativo in elenco:
        if not relativo.endswith((".html", ".js")):
            continue
        contenuto = testo_di(relativo)
        if contenuto is None:
            continue
        for pezzo in re.findall(r'<a\b[^>]*target="_blank"[^>]*>', contenuto):
            if "noopener" not in pezzo:
                problema("%s: un collegamento con target=\"_blank\" senza rel=\"noopener\" "
                         "lascia la pagina aperta in mano al sito di destinazione" % relativo)


def controlla_file_generati():
    for relativo in ("feed.xml", "sitemap.xml"):
        try:
            ET.parse(percorso(relativo))
        except (OSError, ET.ParseError) as errore:
            problema("%s: non si legge come XML (%s)" % (relativo, errore))


def scarica(percorso_web):
    richiesta = urllib.request.Request(INDIRIZZO + percorso_web, headers={"User-Agent": "sicurezza-sito"})
    try:
        with urllib.request.urlopen(richiesta, timeout=20) as risposta:
            return risposta.status
    except urllib.error.HTTPError as errore:
        return errore.code
    except (urllib.error.URLError, OSError):
        return None


def controlla_pubblicato():
    irraggiungibile = False
    for relativo in DA_NON_TROVARE:
        stato = scarica(relativo)
        if stato is None:
            irraggiungibile = True
            continue
        if stato != 404:
            problema("%s%s risponde %d: è un file che non deve stare online"
                     % (INDIRIZZO, relativo, stato))
    for relativo in NASCOSTE_MA_APERTE:
        stato = scarica(relativo)
        if stato is None:
            irraggiungibile = True
            continue
        if stato == 200:
            avviso("%s%s è raggiungibile: robots.txt lo nasconde ai motori di ricerca, "
                   "ma non lo chiude a chi ha l'indirizzo (su GitHub Pages non c'è un lucchetto)"
                   % (INDIRIZZO, relativo))
    if irraggiungibile:
        avviso("non ho potuto raggiungere il sito online: controlli online rimandati")


def main():
    pubblicato = "--pubblicato" in sys.argv[1:]
    elenco = tracciati()
    controlla_segreti(elenco)
    controlla_workflow()
    controlla_indirizzi()
    controlla_lettore_pdf()
    controlla_collegamenti_esterni(elenco)
    controlla_file_generati()
    if pubblicato:
        controlla_pubblicato()

    print("Controllo di sicurezza del sito · %d file" % len(elenco))
    if problemi:
        print("\n  Da sistemare (%d):" % len(problemi))
        for testo in problemi:
            print("   - " + testo)
    if avvisi:
        print("\n  Da sapere (%d):" % len(avvisi))
        for testo in avvisi:
            print("   - " + testo)
    if not problemi:
        print("\nTutto a posto: nessun accesso non consentito trovato.")
    return 1 if problemi else 0


if __name__ == "__main__":
    sys.exit(main())
