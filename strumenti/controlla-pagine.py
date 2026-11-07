#!/usr/bin/env python3
"""Controllo delle pagine del sito: link e file locali che non esistono, file JSON non validi,
titoli piu' lunghi del limite, caratteri presi da Google, indirizzi del sitemap che non
corrispondono a una pagina.

Legge soltanto, non tocca niente. Esce con 0 se non c'e' nulla da sistemare, con 1 se c'e'.

A mano:            python3 strumenti/controlla-pagine.py
Su un'altra copia:  python3 strumenti/controlla-pagine.py /percorso/del/repository
Sul sito online:    python3 strumenti/controlla-pagine.py --pubblicato
Altro indirizzo:    python3 strumenti/controlla-pagine.py --pubblicato --indirizzo https://esempio.it
Solo l'esito:       python3 strumenti/controlla-pagine.py --json     (lo usa il robot settimanale)

Con --pubblicato non guarda i file del computer ma il sito vero: legge sitemap.xml, apre
ogni pagina e ogni file che cita (fogli di stile e caratteri compresi) e segnala quello che
non risponde 200, i caratteri ancora presi da Google e i titoli troppo lunghi. Serve a
sapere se quello che e' online e' davvero la versione che si e' preparata.

Autore: Danilo D'Auria - licenza MIT.
"""
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITO = "https://danilodauria.github.io"
TITOLO_MAX = 70          # oltre questa lunghezza Google taglia il titolo nei risultati
SALTA = {".git", "node_modules"}
SCHEMI = ("#", "//", "http://", "https://", "mailto:", "tel:", "sms:", "data:", "javascript:", "blob:")
DETTAGLI_MAX = 10        # quanti esempi elencare per ogni tipo di problema
# I caratteri stanno tutti in fonti/ (self-hosted): se ricompare uno di questi domini,
# una pagina torna a scaricarli da Google, e va tolta la pagina a chi la visita.
DOMINI_CARATTERI = ("fonts.googleapis.com", "fonts.gstatic.com")
# Per leggere il sito online senza che la CDN di GitHub Pages serva la copia vecchia.
INTESTAZIONI = {
    "User-Agent": "controlla-pagine/1.0 (+https://danilodauria.github.io)",
    "Cache-Control": "no-cache",
    "Accept-Encoding": "identity",
}


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


def fogli_di_stile(radice):
    """Tutti i fogli di stile .css del sito, in ordine: anche loro possono importare caratteri."""
    fuori = []
    for cartella, sottocartelle, nomi in os.walk(radice):
        sottocartelle[:] = [s for s in sottocartelle if s not in SALTA]
        for nome in nomi:
            if nome.lower().endswith(".css"):
                fuori.append(os.path.join(cartella, nome))
    return sorted(fuori)


def controlla_caratteri(radice, pagine):
    """Caratteri presi da Google invece che da fonti/. Restituisce (colpevoli, quante_pagine, quanti_fogli)."""
    fogli = fogli_di_stile(radice)
    colpevoli = []
    for percorso, testo in list(testi(pagine)) + list(testi(fogli)):
        for dominio in DOMINI_CARATTERI:
            if dominio in testo:
                colpevoli.append("%s -> %s" % (relativo(percorso, radice), dominio))
                break
    return colpevoli, len(pagine), len(fogli)


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


def scarica(indirizzo, cache):
    """Scarica un indirizzo una volta sola. Restituisce (stato, tipo, testo, errore).

    Lo stato 0 vuol dire che non si e' riusciti a parlare col server, e allora `errore`
    dice perche'. Il testo viene decodificato solo per le risposte che possono contenerlo.
    """
    if indirizzo in cache:
        return cache[indirizzo]
    esito = (0, "", "", "nessuna risposta")
    try:
        with urllib.request.urlopen(urllib.request.Request(indirizzo, headers=INTESTAZIONI), timeout=20) as risposta:
            tipo = risposta.headers.get("Content-Type", "")
            dati = risposta.read()
            leggibile = any(parola in tipo for parola in ("text", "json", "xml", "javascript"))
            esito = (risposta.status, tipo, dati.decode("utf-8", "replace") if leggibile else "", "")
    except urllib.error.HTTPError as errore:
        esito = (errore.code, "", "", "")
    except Exception as errore:                      # rete assente, nome non risolto, timeout
        esito = (0, "", "", str(errore).split("\n")[0])
    cache[indirizzo] = esito
    return esito


def stesso_sito(indirizzo, base):
    """Vero se l'indirizzo resta dentro il sito che stiamo controllando."""
    return indirizzo == base or indirizzo.startswith(base + "/")


def indirizzi_del_sitemap(base, cache):
    """Le pagine da controllare, lette dal sitemap online. Senza sitemap, almeno la home."""
    stato, _, testo, errore = scarica(base + "/sitemap.xml", cache)
    if stato != 200:
        causa = "non raggiungibile (%s)" % errore if stato == 0 else "risposta %d" % stato
        return [base + "/"], ["sitemap.xml: %s" % causa]

    indirizzi = []
    for trovato in re.finditer(r"<loc>\s*([^<]+?)\s*</loc>", testo):
        voce = html.unescape(trovato.group(1)).strip()
        # Il sitemap nomina sempre l'indirizzo pubblico: per provare un'altra copia
        # (un server locale, un'anteprima) basta cambiare la testa.
        if base != SITO and voce.startswith(SITO):
            voce = base + voce[len(SITO):]
        if stesso_sito(voce, base):
            indirizzi.append(voce)
    return (indirizzi or [base + "/"]), []


# Dentro i fogli di stile: url("atkinson-400.woff2") puo' stare con o senza virgolette.
URL_IN_CSS = re.compile(r"""url\(\s*["']?([^"')]+)["']?\s*\)""")


def controlla_pubblicato(indirizzo=None):
    """Gli stessi controlli, ma sulle pagine vere: quelle che vede chi visita il sito.

    Restituisce (problemi, attenzione, info) come `controlla`, cosi' l'uscita e' la stessa.
    """
    base = (indirizzo or SITO).rstrip("/")
    cache = {}
    problemi, attenzione, info = [], [], []

    indirizzi, problemi_sitemap = indirizzi_del_sitemap(base, cache)
    problemi += problemi_sitemap

    colpevoli, rotti, senza, lunghi = [], [], [], []
    fogli, caratteri = set(), set()
    pagine_lette = 0

    for pagina in indirizzi:
        corto = pagina.replace(base, "") or "/"
        stato, tipo, testo, errore = scarica(pagina, cache)
        if stato != 200:
            rotti.append("%s -> %s" % (corto, "risposta %d" % stato if stato else errore))
            continue
        if "html" not in tipo:
            # Il sitemap elenca anche i PDF: per quelli basta che rispondano.
            continue
        pagine_lette += 1

        trovato = re.search(r"<title>(.*?)</title>", testo, re.S)
        if not trovato:
            senza.append(corto)
        else:
            titolo = re.sub(r"\s+", " ", html.unescape(trovato.group(1))).strip()
            if len(titolo) > TITOLO_MAX:
                lunghi.append("%s (%d caratteri): %s" % (corto, len(titolo), titolo))

        for dominio in DOMINI_CARATTERI:
            if dominio in testo:
                colpevoli.append("%s -> %s" % (corto, dominio))
                break

        for risorsa in re.finditer(r"""(?:href|src)\s*=\s*["']([^"']+)["']""", testo):
            voce = risorsa.group(1).strip()
            if not voce or voce.startswith(SCHEMI):
                continue
            bersaglio = urllib.parse.urljoin(pagina, voce.split("#")[0].split("?")[0])
            if not stesso_sito(bersaglio, base):
                continue
            stato_r, _, contenuto, errore_r = scarica(bersaglio, cache)
            if stato_r != 200:
                rotti.append("%s -> %s (%s)" % (corto, voce,
                                                "risposta %d" % stato_r if stato_r else errore_r))
                continue
            if not bersaglio.endswith(".css"):
                continue
            fogli.add(bersaglio)
            for dominio in DOMINI_CARATTERI:
                if dominio in contenuto:
                    colpevoli.append("%s -> %s" % (bersaglio.replace(base, ""), dominio))
                    break
            for dentro in URL_IN_CSS.finditer(contenuto):
                file_carattere = urllib.parse.urljoin(bersaglio, dentro.group(1).strip())
                if not stesso_sito(file_carattere, base):
                    continue
                stato_f, _, _, errore_f = scarica(file_carattere, cache)
                if stato_f != 200:
                    rotti.append("%s -> %s (%s)" % (bersaglio.replace(base, ""), dentro.group(1).strip(),
                                                    "risposta %d" % stato_f if stato_f else errore_f))
                else:
                    caratteri.add(file_carattere)

    if rotti:
        problemi.append("Pagine o file che non rispondono 200: %d" % len(rotti))
        problemi += rotti[:DETTAGLI_MAX]
    if colpevoli:
        problemi.append("Caratteri caricati da Google invece che da fonti/: %d" % len(colpevoli))
        problemi += colpevoli[:DETTAGLI_MAX]
    else:
        info.append("Caratteri: nessun riferimento a Google in %d pagine e %d fogli di stile."
                    % (pagine_lette, len(fogli)))
    if senza:
        problemi.append("Pagine senza <title>: %d" % len(senza))
        problemi += senza[:DETTAGLI_MAX]
    if lunghi:
        attenzione.append("Titoli piu' lunghi di %d caratteri: %d (Google li taglia nei risultati)"
                          % (TITOLO_MAX, len(lunghi)))
        attenzione += lunghi[:DETTAGLI_MAX]
    else:
        info.append("Titoli entro %d caratteri: tutti." % TITOLO_MAX)

    info.insert(0, "Indirizzi controllati: %d, di cui pagine HTML: %d (%s)."
                % (len(indirizzi), pagine_lette, base))
    info.append("File di caratteri raggiungibili: %d." % len(caratteri))
    return problemi, attenzione, info


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

    google, quante_pagine, quanti_fogli = controlla_caratteri(radice, pagine)
    if google:
        problemi.append("Caratteri caricati da Google invece che da fonti/: %d" % len(google))
        problemi += google[:DETTAGLI_MAX]
    else:
        info.append("Caratteri: nessun riferimento a Google in %d pagine e %d fogli di stile."
                    % (quante_pagine, quanti_fogli))

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
    if "--pubblicato" in argomenti:
        indirizzo = SITO
        for posizione, argomento in enumerate(argomenti):
            if argomento == "--indirizzo" and posizione + 1 < len(argomenti):
                indirizzo = argomenti[posizione + 1]
            elif argomento.startswith("--indirizzo="):
                indirizzo = argomento.split("=", 1)[1]
        problemi, attenzione, info = controlla_pubblicato(indirizzo)
        testata = "Controllo del sito pubblicato su %s" % indirizzo.rstrip("/")
    else:
        cartelle = [a for a in argomenti if not a.startswith("--")]
        radice = os.path.abspath(cartelle[0]) if cartelle else RADICE
        problemi, attenzione, info = controlla(radice)
        testata = "Controllo delle pagine di %s" % radice

    if "--json" in argomenti:
        print(json.dumps({"problemi": problemi, "attenzione": attenzione, "info": info}, ensure_ascii=False))
        return 1 if problemi else 0

    print(testata + "\n")
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
