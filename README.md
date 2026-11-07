# danilodauria.github.io

Sito di presentazione di **Danilo D'Auria** — Tecnologia Gentile.

| File | Cosa contiene |
|---|---|
| `index.html` | La pagina completa (progetti, libro, servizi, bandi, domande frequenti, contatti) |
| `bandi.json` | L'elenco dei bandi: la pagina lo rilegge a ogni apertura (LED verde) |
| `offerte.json` | Calendario delle offerte e prodotti da confrontare: le date ricorrenti (Black Friday, saldi, Prime Day…) si ricalcolano da sole ogni anno |
| `fenice.svg` | Il logo della fenice, usato anche come icona della scheda |
| `fonti/` | I caratteri del sito in `.woff2` (Young Serif, Atkinson Hyperlegible, JetBrains Mono) e `fonti.css`: si servono da qui, senza chiamare Google |
| `progetti.json` | I progetti e le loro versioni: lo aggiorna da solo ogni giorno GitHub Actions |
| `strumenti/aggiorna-progetti.py` | Lo script che legge i repository di danilodauria su GitHub |
| `strumenti/versioni-schede.py` | Riallinea a `progetti.json` le versioni scritte dentro `index.html`: il badge di ogni scheda e la copia di riserva dell'elenco (`PROGETTI_SALVATI`), che si vede subito e anche senza rete. Lo lancia il robot dopo `aggiorna-progetti.py`, così non restano versioni vecchie |
| `strumenti/controlla-pagine.py` | Controlla link e file locali, file JSON, lunghezza dei titoli, caratteri presi da Google (devono restare in `fonti/`) e indirizzi del sitemap: a mano (`python3 strumenti/controlla-pagine.py`), dal robot settimanale, oppure sulle pagine davvero online con `--pubblicato`, che apre sitemap, pagine, fogli di stile e caratteri del sito e segnala quello che non risponde 200 |
| `.github/workflows/progetti.yml` | L'aggiornamento automatico (ogni giorno, e con il pulsante «Run workflow» nella scheda Actions) |
| `pdf/leggi.html` | Il lettore dei PDF per i telefoni: si apre in una nuova scheda (usa PDF.js, licenza Apache 2.0, in `pdf/pdfjs/`) |
| `pdf/` | Il profilo in PDF, per lo schermo e da stampare: lo rifà da solo GitHub Actions (`.github/workflows/pdf.yml`) quando cambia il sito, quando cambiano i progetti e ogni giorno per i bandi |
| `guide/` | Le guide gratuite (backup, truffe, vendere o donare un dispositivo, password, PC più veloce) in sei lingue: italiano in `guide/`, le altre in `guide/en/`, `guide/fr/`… Si scrivono in `strumenti/guide/crea-guide.py` (traduzioni in `strumenti/guide/guide_<lingua>.py`); i PDF li fa il robot in `pdf/guide/` |
| `pdf/Danilo_DAuria_volantino.pdf`, `pdf/Danilo_DAuria_biglietti.pdf` | Volantino A4 con linguette e biglietti da visita (10 per foglio): li rifà da solo il robot dei PDF (`strumenti/stampa/stampa.py`) con i prezzi del sito |
| `pdf/Kit_bandi_Danilo_DAuria.docx` / `.pdf` | Il kit per i bandi: scheda di progetto da adattare e lettera di adesione (`strumenti/kit/kit-bandi.py`) |
| `pdf/info.json` | Il numero di pagine dei PDF: il sito lo legge e lo mostra sempre giusto |
| `prenota.json` | I giorni e le fasce orarie proposti per prenotare il check-up: si cambia qui, senza toccare la pagina. La richiesta parte dall'email del cliente |
| `novita.json`, `feed.xml` | Le novità del sito e il feed (Atom): nuove versioni e nuovi progetti si aggiungono da soli ogni giorno (`strumenti/novita.py`), con una sola voce per progetto all'ultima versione; le voci con `"a_mano": true` si scrivono a mano |
| `sitemap.xml`, `robots.txt` | Per Google: l'elenco delle pagine in tutte le lingue. I dati strutturati nella pagina (persona, servizi con prezzi, libro, domande frequenti) li scrive `strumenti/seo/seo.py` rileggendo la pagina stessa |
| `i18n/` | Il sito in inglese, francese, spagnolo, tedesco e rumeno. Le traduzioni si scrivono a mano in `i18n/fonti/<lingua>.tsv`, poi `python3 strumenti/i18n/componi.py`. Le frasi nuove ancora da tradurre restano in italiano e le segnala il controllo settimanale |
| `casi.json` | I casi reali «prima e dopo», solo con il consenso del cliente: si preparano con la scheda intervento |
| `scheda/` | La scheda intervento per il tecnico (danilodauria.github.io/scheda/): si compila sul posto, si stampa per il cliente, prepara il caso per il sito. Non è collegata dal sito |
| `vista.html`, `torna.js` | Sul telefono i siti dei progetti si aprono con la barra del sito e il pulsante «← Sito» per tornare indietro |
| `manifest.webmanifest`, `sw.js`, `icone/` | Il sito installabile come app, che funziona anche senza Internet |
| `.github/workflows/controllo.yml` | Il controllo di ogni lunedì: link delle fonti, bandi in scadenza, prezzi da rivedere, traduzioni mancanti, accessibilità (WCAG 2.1 AA con axe-core, `strumenti/accessibilita/controlla.py`). Se c'è qualcosa da fare apre un avviso nella scheda «Issues» (e GitHub manda un'email) |
| `anteprima.png` | L'immagine che compare quando si condivide il link su WhatsApp e social |

Per aggiornare solo i bandi o le offerte basta modificare `bandi.json` o `offerte.json`: la pagina non va toccata.

Statistiche senza cookie con GoatCounter (codice «danilodauria»): danilodauria.goatcounter.com.

I nuovi progetti pubblicati su GitHub compaiono da soli nella sezione «Gli altri progetti» e nelle «Novità», e i numeri di versione delle schede si aggiornano da soli.

Testi e grafica © 2026 Danilo D'Auria, CC BY-NC-SA 4.0 · codice MIT.
