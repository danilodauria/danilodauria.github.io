#!/usr/bin/env python3
"""Aggiorna progetti.json con i repository pubblici di danilodauria su GitHub.

Lo esegue da solo GitHub Actions (ogni giorno e a ogni modifica del sito): legge l'elenco dei
repository, la versione di ognuno (la più alta tra ultima Release, etichette, file VERSION, VERSIONE,
version.txt e package.json) e l'indirizzo del sito pubblicato. La pagina index.html legge poi progetti.json.
Solo libreria standard di Python. Autore: Danilo D'Auria - licenza MIT."""
import datetime, json, os, re, sys, urllib.error, urllib.request

UTENTE = "danilodauria"
ESCLUSI = {
    "danilodauria.github.io",  # il sito stesso
    # Vecchia copia di «Il Grande Quiz dell'Informatica»: è lo stesso programma di grande-quiz,
    # quindi non va contata due volte (la pagina resta online, ma il sito elenca solo grande-quiz).
    # Per farla ricomparire basta togliere questa riga.
    "Quiz-Interattivo-Terminale-Fenice-OS",
}
QUI = os.path.dirname(os.path.abspath(__file__))
USCITA = os.path.join(os.path.dirname(QUI), "progetti.json")
TOKEN = os.environ.get("GITHUB_TOKEN", "")

# Nomi scritti come li scrive Danilo (gli altri si ricavano dal nome del repository)
TITOLI = {
    "feniceos": "FeniceOS",
    "grande-quiz": "Il Grande Quiz dell'Informatica",
    "nonni-teach": "Nonni Teach",
}


def chiedi(url, json_atteso=True):
    req = urllib.request.Request(url, headers={"User-Agent": "aggiorna-progetti", "Accept": "application/vnd.github+json"})
    if TOKEN and "api.github.com" in url:
        req.add_header("Authorization", "Bearer " + TOKEN)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            dati = r.read().decode("utf-8", "replace")
            return json.loads(dati) if json_atteso else dati
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def titolo(nome):
    return TITOLI.get(nome) or " ".join(p[:1].upper() + p[1:] for p in nome.replace("_", "-").split("-"))


def pulisci(v):
    """«psd-v1.3.32», «v2.2», «2.2» -> «1.3.32», «2.2», «2.2»."""
    m = re.search(r"\d+(?:\.\d+)+", v or "")
    return m.group(0) if m else ""


def _tupla(v):
    return tuple(int(x) for x in v.split("."))


def versione(repo):
    """La versione più alta tra: ultima Release, etichette (tag), file VERSION/VERSIONE/version.txt e package.json.

    Prima valeva solo la Release: se un progetto smetteva di pubblicare Release e usava solo le
    etichette (es. psd-v1.3.36), il sito restava fermo all'ultima Release (1.3.32). Ora vince la più recente."""
    nome, ramo = repo["name"], repo.get("default_branch") or "main"
    trovate = []
    rel = chiedi("https://api.github.com/repos/%s/%s/releases/latest" % (UTENTE, nome))
    if rel and rel.get("tag_name"):
        trovate.append(pulisci(rel["tag_name"]))
    tag = chiedi("https://api.github.com/repos/%s/%s/tags?per_page=100" % (UTENTE, nome)) or []
    trovate += [pulisci(t.get("name")) for t in tag]
    for f in ("VERSION", "VERSIONE", "version.txt"):
        t = chiedi("https://raw.githubusercontent.com/%s/%s/%s/%s" % (UTENTE, nome, ramo, f), json_atteso=False)
        if t and t.strip() and len(t.strip()) < 20 and "\n" not in t.strip():
            trovate.append(pulisci(t.strip()))
    for f in ("package.json", "desktop/package.json"):
        pkg = chiedi("https://raw.githubusercontent.com/%s/%s/%s/%s" % (UTENTE, nome, ramo, f), json_atteso=False)
        if pkg:
            try:
                trovate.append(pulisci(json.loads(pkg).get("version") or ""))
            except ValueError:
                pass
    trovate = [v for v in trovate if v]
    return max(trovate, key=_tupla) if trovate else ""


def controlla_elenco(progetti):
    """Un progetto, una scheda: il quiz non deve mai comparire due volte.

    La copia vecchia «Quiz-Interattivo-Terminale-Fenice-OS» è lo stesso programma di
    «grande-quiz», per questo sta in ESCLUSI. Se un giorno quella riga sparisse, o se il
    repository venisse rinominato, il sito mostrerebbe due quiz. Qui si guarda prima di
    scrivere: meglio un'esecuzione rossa che un doppione online. Oltre al nome, due schede
    non devono ripetere né l'indirizzo né il titolo né la descrizione: è così che un progetto
    ricaricato con un altro nome si riconosce lo stesso.
    """
    problemi = []
    nomi = [p["nome"] for p in progetti]
    for escluso in sorted(ESCLUSI):
        if escluso in nomi:
            problemi.append("c'è %s, che deve restare fuori (vedi ESCLUSI)" % escluso)
    quiz = [p["nome"] for p in progetti if "quiz" in p["nome"].lower()]
    if quiz != ["grande-quiz"]:
        problemi.append("i quiz elencati dovrebbero essere solo grande-quiz, invece sono: %s"
                        % (", ".join(quiz) or "nessuno"))
    problemi += _ripetuti(progetti, "sito", "%s e %s portano allo stesso sito (%s)")
    problemi += _ripetuti(progetti, "titolo", "%s e %s hanno lo stesso titolo (%s)")
    problemi += _ripetuti(progetti, "descrizione",
                          "%s e %s hanno la stessa descrizione (%s)", taglia=60)
    return problemi


def _ripetuti(progetti, campo, frase, taglia=0):
    """Progetti che ripetono lo stesso valore in `campo`, ignorando spazi e maiuscole.

    I valori vuoti non contano: un progetto può non avere descrizione. `taglia` accorcia
    il valore nel messaggio, per non stampare una descrizione intera."""
    visti, problemi = {}, []
    for p in progetti:
        valore = " ".join((p.get(campo) or "").split())
        if campo == "sito":
            valore = valore.rstrip("/")
        if not valore:
            continue
        chiave = valore.casefold()
        if chiave in visti:
            breve = valore if not taglia or len(valore) <= taglia else valore[:taglia].rstrip() + "…"
            problemi.append(frase % (visti[chiave], p["nome"], breve))
        else:
            visti[chiave] = p["nome"]
    return problemi


def main():
    repos, pagina = [], 1
    while True:
        blocco = chiedi("https://api.github.com/users/%s/repos?per_page=100&type=owner&page=%d" % (UTENTE, pagina))
        if not blocco:
            break
        repos += blocco
        pagina += 1
    progetti = []
    for r in repos:
        if r["name"] in ESCLUSI or r.get("fork") or r.get("archived") or r.get("private"):
            continue
        sito = r.get("homepage") or ""
        if not sito and r.get("has_pages"):
            sito = "https://%s.github.io/%s/" % (UTENTE, r["name"])
        progetti.append({
            "nome": r["name"],
            "titolo": titolo(r["name"]),
            "descrizione": r.get("description") or "",
            "versione": versione(r),
            "sito": sito,
            "github": r["html_url"],
            "linguaggio": r.get("language") or "",
            "creato": (r.get("created_at") or "")[:10],
            "aggiornato": (r.get("pushed_at") or "")[:10],
        })
    progetti.sort(key=lambda p: p["creato"], reverse=True)
    problemi = controlla_elenco(progetti)
    if problemi:
        for problema in problemi:
            print("Doppione nell'elenco: " + problema, file=sys.stderr)
        print("progetti.json lasciato com'era: prima si sistema l'elenco.", file=sys.stderr)
        return 1
    oggi = datetime.date.today().isoformat()
    vecchio = {}
    if os.path.exists(USCITA):
        try:
            vecchio = json.load(open(USCITA, encoding="utf-8"))
        except ValueError:
            vecchio = {}
    cambiato = vecchio.get("progetti") != progetti
    nuovo = {
        "aggiornato": oggi if cambiato else vecchio.get("aggiornato", oggi),
        # il primo del mese si scrive comunque, cosi' GitHub non sospende l'aggiornamento automatico
        "controllato": oggi if (cambiato or oggi.endswith("-01")) else vecchio.get("controllato", oggi),
        "progetti": progetti,
    }
    if nuovo != vecchio:
        with open(USCITA, "w", encoding="utf-8") as f:
            json.dump(nuovo, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("progetti.json aggiornato: %d progetti" % len(progetti))
    else:
        print("nessuna novità (%d progetti)" % len(progetti))


if __name__ == "__main__":
    sys.exit(main())
