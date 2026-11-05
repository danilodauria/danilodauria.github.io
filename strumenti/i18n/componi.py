"""Compone i dizionari del sito (i18n/<lingua>.json) dalle traduzioni scritte a mano in i18n/fonti/<lingua>.tsv.
Ogni riga del .tsv: codice<TAB>traduzione. Il codice sono i primi 6 caratteri dello SHA-1 della frase italiana (vedi i18n/it.json).
«=» vuol dire «uguale all'italiano» (nomi propri, sigle). Controlla che {n0}, {d0}… siano tutti al loro posto.
Uso: python3 strumenti/i18n/componi.py   · Autore: Danilo D'Auria · MIT."""
import hashlib, json, os, re
QUI = os.path.dirname(os.path.abspath(__file__)); DIR = os.path.join(os.path.dirname(os.path.dirname(QUI)), "i18n")
chiavi = json.load(open(os.path.join(DIR, "it.json"), encoding="utf-8"))
per_codice = {hashlib.sha1(k.encode()).hexdigest()[:6]: k for k in chiavi}
segnaposto = lambda t: sorted(re.findall(r"\{[dn]\d+\}", t))
for l in ["en", "fr", "es", "de", "ro"]:
    f = os.path.join(DIR, "fonti", l + ".tsv")
    if not os.path.exists(f): continue
    vecchio = os.path.join(DIR, l + ".json")
    diz = json.load(open(vecchio, encoding="utf-8")) if os.path.exists(vecchio) else {}
    errori = 0
    for riga in open(f, encoding="utf-8"):
        riga = riga.rstrip("\n")
        if not riga.strip() or riga.startswith("#"): continue
        cod, _, tr = riga.partition("\t")
        k = per_codice.get(cod.strip())
        if k is None: print(l, "codice sconosciuto:", cod); errori += 1; continue
        tr = k if tr.strip() == "=" else tr.strip()
        if segnaposto(tr) != segnaposto(k): print(l, "segnaposto diversi:", cod, k, "→", tr); errori += 1; continue
        diz[k] = tr
    diz = {k: v for k, v in diz.items() if k in set(chiavi)}
    json.dump(diz, open(vecchio, "w", encoding="utf-8"), ensure_ascii=False, indent=0, sort_keys=True)
    print(l, "frasi:", len(diz), "di", len(chiavi), "· errori:", errori)
