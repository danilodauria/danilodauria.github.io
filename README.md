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
| `guide/` | Le guide gratuite (backup, truffe, vendere o donare un dispositivo, password, PC più veloce). Si scrivono in `strumenti/guide/crea-guide.py`; i PDF li fa il robot in `pdf/guide/` |
| `i18n/` | Il sito in inglese, francese, spagnolo, tedesco e rumeno. Le traduzioni si scrivono a mano in `i18n/fonti/<lingua>.tsv`, poi `python3 strumenti/i18n/componi.py`. Le frasi nuove ancora da tradurre restano in italiano e le segnala il controllo settimanale |
| `casi.json` | I casi reali «prima e dopo», solo con il consenso del cliente: si preparano con la scheda intervento |
| `scheda/` | La scheda intervento per il tecnico (danilodauria.github.io/scheda/): si compila sul posto, si stampa per il cliente, prepara il caso per il sito. Non è collegata dal sito |
| `vista.html`, `torna.js` | Sul telefono i siti dei progetti si aprono con la barra del sito e il pulsante «← Sito» per tornare indietro |
| `manifest.webmanifest`, `sw.js`, `icone/` | Il sito installabile come app, che funziona anche senza Internet |
| `.github/workflows/controllo.yml` | Il controllo di ogni lunedì: link delle fonti, bandi in scadenza, prezzi da rivedere, traduzioni mancanti. Se c'è qualcosa da fare apre un avviso nella scheda «Issues» (e GitHub manda un'email) |
| `anteprima.png` | L'immagine che compare quando si condivide il link su WhatsApp e social |

Per aggiornare solo i bandi o le offerte basta modificare `bandi.json` o `offerte.json`: la pagina non va toccata.

Statistiche senza cookie (GoatCounter): dopo l'iscrizione gratuita su goatcounter.com, si scrive il codice scelto nella riga `var STATISTICHE = "";` di `index.html`.

I nuovi progetti pubblicati su GitHub compaiono da soli nella sezione «Gli altri progetti», e i numeri di versione delle schede si aggiornano da soli.

Testi e grafica © 2026 Danilo D'Auria, CC BY-NC-SA 4.0 · codice MIT.
