# danilodauria.github.io

Sito di presentazione di **Danilo D'Auria** — Tecnologia Gentile.

| File | Cosa contiene |
|---|---|
| `index.html` | La pagina completa (progetti, libro, servizi, bandi, domande frequenti, contatti) |
| `bandi.json` | L'elenco dei bandi: la pagina lo rilegge a ogni apertura (LED verde) |
| `offerte.json` | Calendario delle offerte e prodotti da confrontare: le date ricorrenti (Black Friday, saldi, Prime Day…) si ricalcolano da sole ogni anno |
| `fenice.svg` | Il logo della fenice, usato anche come icona della scheda |
| `progetti.json` | I progetti e le loro versioni: lo aggiorna da solo ogni giorno GitHub Actions |
| `strumenti/aggiorna-progetti.py` | Lo script che legge i repository di danilodauria su GitHub |
| `.github/workflows/progetti.yml` | L'aggiornamento automatico (ogni giorno, e con il pulsante «Run workflow» nella scheda Actions) |
| `pdf/leggi.html` | Il lettore dei PDF per i telefoni: si apre in una nuova scheda (usa PDF.js, licenza Apache 2.0, in `pdf/pdfjs/`) |
| `pdf/` | Il profilo in PDF, per lo schermo e da stampare: lo rifà da solo GitHub Actions (`.github/workflows/pdf.yml`) quando cambia il sito, quando cambiano i progetti e ogni giorno per i bandi |
| `anteprima.png` | L'immagine che compare quando si condivide il link su WhatsApp e social |

Per aggiornare solo i bandi o le offerte basta modificare `bandi.json` o `offerte.json`: la pagina non va toccata.

I nuovi progetti pubblicati su GitHub compaiono da soli nella sezione «Gli altri progetti», e i numeri di versione delle schede si aggiornano da soli.

Testi e grafica © 2026 Danilo D'Auria, CC BY-NC-SA 4.0 · codice MIT.
