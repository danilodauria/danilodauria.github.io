#!/usr/bin/env python3
"""Scrive nelle schede della home la versione attuale dei progetti, letta da progetti.json.

La home mostra la versione in due punti: il badge dentro la scheda del progetto e la copia di
riserva dell'elenco (PROGETTI_SALVATI), che compare subito, prima che arrivi la risposta della
rete e anche quando la rete non c'e'. Se restano scritte a mano, prima o poi raccontano una
versione vecchia: questo script le riallinea a progetti.json, che e' la fonte.

Lo esegue GitHub Actions (progetti.yml) dopo aggiorna-progetti.py. Si puo' lanciare a mano:
    python3 strumenti/versioni-schede.py
Solo libreria standard di Python. Autore: Danilo D'Auria - licenza MIT.
"""
import json
import os
import re

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(QUI)
PAGINA = os.path.join(REPO, "index.html")
DATI = os.path.join(REPO, "progetti.json")


def leggi_progetti():
    with open(DATI, encoding="utf-8") as f:
        return json.load(f)


def aggiorna_badge(testo, progetti, cambi):
    """Il <span class="versione"> dentro la scheda di ogni progetto."""
    for progetto in progetti:
        numero = (progetto.get("versione") or "").strip()
        if not numero:
            continue            # progetti senza numero di versione (es. il podcast): si lascia com'e'
        scheda = re.compile(r"(<article\b[^>]*\bdata-repo=\"%s\"[^>]*>)(.*?)(</article>)"
                            % re.escape(progetto["nome"]), re.S)
        trovato = scheda.search(testo)
        if not trovato:
            continue
        dentro = trovato.group(2)
        nuovo, quante = re.subn(r'(<span class="versione">)[^<]*(</span>)',
                                r"\g<1>v%s\g<2>" % numero, dentro, count=1)
        if quante and nuovo != dentro:
            testo = testo[:trovato.start(2)] + nuovo + testo[trovato.end(2):]
            cambi.append("scheda %s: v%s" % (progetto["nome"], numero))
    return testo


def aggiorna_riserva(testo, dati, cambi):
    """L'elenco salvato dentro la pagina, che si vede prima della risposta della rete."""
    nuovo = json.dumps(dati, ensure_ascii=False, separators=(",", ":"))
    # PROGETTI_SALVATI sta su una riga sola: si sostituisce quella riga intera.
    modello = re.compile(r"^[ \t]*var PROGETTI_SALVATI = .*;$", re.M)
    trovato = modello.search(testo)
    if not trovato:
        return testo
    riga = "  var PROGETTI_SALVATI = %s;" % nuovo
    if trovato.group(0) == riga:
        return testo
    cambi.append("elenco di riserva: aggiornato al %s" % (dati.get("aggiornato") or "?"))
    return testo[:trovato.start()] + riga + testo[trovato.end():]


def main():
    dati = leggi_progetti()
    with open(PAGINA, encoding="utf-8") as f:
        testo = f.read()

    cambi = []
    aggiornato = aggiorna_badge(testo, dati.get("progetti", []), cambi)
    aggiornato = aggiorna_riserva(aggiornato, dati, cambi)

    if aggiornato == testo:
        print("Caselle della home gia' all'ultima versione: niente da fare.")
        return 0
    with open(PAGINA, "w", encoding="utf-8") as f:
        f.write(aggiornato)
    for riga in cambi:
        print("  " + riga)
    print("%d modifiche in index.html." % len(cambi))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
