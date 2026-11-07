#!/usr/bin/env python3
"""Controllo delle pagine del sito: link e file locali che non esistono, file JSON non validi,
titoli piu' lunghi del limite, indirizzi del sitemap che non corrispondono a una pagina.

Legge soltanto, non tocca niente. Esce con 0 se non c'e' nulla da sistemare, con 1 se c'e'.

A mano:            python3 strumenti/controlla-pagine.py
Su un'altra copia:  python3 strumenti/controlla-pagine.py /percorso/del/repository
Solo l'esito:       python3 strumenti/controlla-pagine.py --json     (lo usa il robot settimanale)
Autore: Danilo D'Auria - licenza MIT.
"""
import html
import json
import os
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITO = "https://danilodauria.github.io"
TITOLO_MAX = 70          # oltre questa lunghezza Google taglia il titolo nei risultati
SALTA = {".git", "node_modules"}
SCHEMI = ("#", "//", "http://", "https://", "mailto:", "tel:", "sms:", "data:", "javascript:", "blob:")
DETTAGLI_MAX = 10        # quanti esempi elencare per ogni tipo di problema


def relativo(percorso, radice):
    return os.path.relpath(percorso, radice).replace(os.sep, "/")


def pagine_html(radice):
    """Tutte le pagine del sito, in ordine."""
    fuori = []
    for cartella, sottocartelle, nomi in os.walk(radice):
        sottocartelle[:] = [s for s in sottocartelle if s not in SALTA]
        for nome in nomi:
            if nome.lower().endswith(".html"):
                fuori.append(os.path.join(cartella, nome))
    return sorted(fuori)


def testi(pagine):
    """Legge ogni pagina una volta sola e la restituisce con il suo percorso."""
    for pagina in pagine:
        with open(pagina, encoding="utf-8", errors="replace") as f:
            yield pagina, f.read()


def controlla_link(radice, pagine):
    """Riferimenti locali a file che non ci sono: link, immagini, script, fogli di stile."""
    mancanti = []
    for pagina, testo in testi(pagine):
        gia_visti = set()
        for trovato in re.finditer(r"""(?:href|src)\s*=\s*["']([^"']+)["']""", testo):
            voce = trovato.group(1).strip()
            if not voce or voce.startswith(SCHEMI):
                continue
            pulito = urllib.parse.unquote(voce.split("#")[0].split("?")[0])
            if not pulito:
                continue
            if pulito.startswith("/"):
                bersaglio = os.path.normpath(os.path.join(radice, pulito.lstrip("/")))
            else:
                bersaglio = os.path.normpath(os.path.join(os.path.dirname(pagina), pulito))
            if bersaglio in gia_visti:
                continue
            gia_visti.add(bersaglio)
            if not os.path.exists(bersaglio):
                mancanti.append("%s -> %s" % (relativo(pagina, radice), voce))
    return mancanti


def controlla_json(radice):
    """File JSON che non si aprono (il sito li legge a ogni visita). Restituisce (rotti, quanti)."""
    rotti, quanti = [], 0
    for cartella, sottocartelle, nomi in os.walk(radice):
        sottocartelle[:] = [s for s in sottocartelle if s not in SALTA]
        for nome in sorted(nomi):
            if not nome.lower().endswith(".json"):
                continue
            quanti += 1
            percorso = os.path.join(cartella, nome)
            try:
                with open(percorso, encoding="utf-8") as f:
                    json.load(f)
            except Exception as errore:
                rotti.append("%s: %s" % (relativo(percorso, radice), str(errore).split("\n")[0]))
    return rotti, quanti


def controlla_titoli(radice, pagine):
    """Titoli piu' lunghi del limite e pagine senza titolo."""
    lunghi, senza = [], []
    for pagina, testo in testi(pagine):
        trovato = re.search(r"<title>(.*?)</title>", testo, re.S)
        if not trovato:
            senza.append(relativo(pagina, radice))
            continue
        titolo = re.sub(r"\s+", " ", html.unescape(trovato.group(1))).strip()
        if len(titolo) > TITOLO_MAX:
            lunghi.append("%s (%d caratteri): %s" % (relativo(pagina, radice), len(titolo), titolo))
    return lunghi, senza


def controlla_sitemap(radice):
    """Indirizzi del sitemap senza pagina. Restituisce (mancanti, quanti_indirizzi)."""
    percorso = os.path.join(radice, "sitemap.xml")
    if not os.path.isfile(percorso):
        return ["manca sitemap.xml"], 0
    try:
        albero = ET.parse(percorso).getroot()
    except Exception as errore:
        return ["sitemap.xml non e' XML valido: %s" % str(errore).split("\n")[0]], 0

    quanti, mancanti = 0, []
    for elemento in albero.iter():
        if not elemento.tag.endswith("loc") or not elemento.text:
            continue
        indirizzo = elemento.text.strip()
        quanti += 1
        rel = urllib.parse.unquote(indirizzo.replace(SITO, "", 1)).split("#")[0].split("?")[0]
        if rel in ("", "/"):
            continue
        bersaglio = os.path.normpath(os.path.join(radice, rel.lstrip("/")))
        if os.path.isdir(bersaglio):
            bersaglio = os.path.join(bersaglio, "index.html")
        if not os.path.exists(bersaglio):
            mancanti.append(indirizzo)
    return mancanti, quanti


def controlla(radice=None):
    """Controlla tutto e restituisce tre elenchi di righe pronte: (problemi, attenzione, info)."""
    radice = os.path.abspath(radice or RADICE)
    pagine = pagine_html(radice)
    problemi, attenzione, info = [], [], []

    link = controlla_link(radice, pagine)
    if link:
        problemi.append("Link o file locali che non esistono: %d" % len(link))
        problemi += link[:DETTAGLI_MAX]
    else:
        info.append("Link e file locali: tutti a posto.")

    rotti, quanti_json = controlla_json(radice)
    if rotti:
        problemi.append("File JSON non validi: %d" % len(rotti))
        problemi += rotti
    else:
        info.append("File JSON letti: %d, nessun errore." % quanti_json)

    mancanti, quanti_url = controlla_sitemap(radice)
    if mancanti:
        problemi.append("Indirizzi del sitemap senza pagina: %d" % len(mancanti))
        problemi += mancanti[:DETTAGLI_MAX]
    elif quanti_url:
        info.append("Sitemap: %d indirizzi, tutti con la loro pagina." % quanti_url)

    lunghi, senza = controlla_titoli(radice, pagine)
    if senza:
        problemi.append("Pagine senza <title>: %d" % len(senza))
        problemi += senza[:DETTAGLI_MAX]
    if lunghi:
        attenzione.append("Titoli piu' lunghi di %d caratteri: %d (Google li taglia nei risultati)"
                          % (TITOLO_MAX, len(lunghi)))
        attenzione += lunghi[:DETTAGLI_MAX]
    else:
        info.append("Titoli entro %d caratteri: tutti." % TITOLO_MAX)

    info.insert(0, "Pagine controllate: %d." % len(pagine))
    return problemi, attenzione, info


def main():
    argomenti = sys.argv[1:]
    cartelle = [a for a in argomenti if not a.startswith("--")]
    radice = os.path.abspath(cartelle[0]) if cartelle else RADICE
    problemi, attenzione, info = controlla(radice)

    if "--json" in argomenti:
        print(json.dumps({"problemi": problemi, "attenzione": attenzione, "info": info}, ensure_ascii=False))
        return 1 if problemi else 0

    print("Controllo delle pagine di %s\n" % radice)
    for riga in info:
        print("  %s" % riga)
    if attenzione:
        print("\nDa tenere d'occhio:")
        for riga in attenzione:
            print("  - %s" % riga)
    if problemi:
        print("\nDa sistemare:")
        for riga in problemi:
            print("  - %s" % riga)
        print("\n%d cose da sistemare." % len(problemi))
        return 1
    print("\nTutto a posto." if not attenzione else "\nNiente da sistemare.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
