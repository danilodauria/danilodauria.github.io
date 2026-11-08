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
| `strumenti/aggiorna-progetti.py` | Lo script che legge i repository di danilodauria su GitHub. Prima di scrivere controlla che ogni progetto compaia una volta sola: il quiz vecchio non deve tornare |
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
| `.github/workflows/controllo.yml` | Il controllo di ogni lunedì: link delle fonti, bandi in scadenza, prezzi da rivedere, traduzioni mancanti, accessibilità (WCAG 2.1 AA con axe-core, `strumenti/accessibilita/controlla.py`) e il sito davvero online (`--pubblicato`, riprovando con calma per non prendere per guasto un ritardo di GitHub Pages). Se c'è qualcosa da fare apre un avviso nella scheda «Issues» (e GitHub manda un'email) |
| `anteprima.png` | L'immagine che compare quando si condivide il link su WhatsApp e social |

## I tre robot

Tre robot di GitHub Actions si occupano del sito da soli. Ognuno scrive **solo i propri file**, e nessuno rifà partire sé stesso: così i robot non si pestano i piedi e non si accendono a vicenda all'infinito.

| Robot | Quando parte | Cosa fa | Cosa scrive |
|---|---|---|---|
| **Aggiorna i progetti** (`.github/workflows/progetti.yml`) | ogni giorno alle 05:17 UTC, con il pulsante «Run workflow» della scheda Actions, e a ogni modifica del sito su `main` | legge i repository pubblici di danilodauria e le versioni, aggiorna le Novità e il feed, riallinea le versioni dentro `index.html` (badge delle schede e copia di riserva `PROGETTI_SALVATI`) | `progetti.json`, `novita.json`, `feed.xml`, `index.html` — e solo se qualcosa è davvero cambiato |
| **Aggiorna il PDF** (`.github/workflows/pdf.yml`) | dopo ogni modifica del sito su `main`, dopo ogni esecuzione del robot dei progetti, e ogni giorno alle 05:47 UTC | rifà profilo, guide, volantino e biglietti da visita con i caratteri di `fonti/`, poi conta le pagine dei documenti | `pdf/` — e solo se i contenuti sono cambiati; il pulsante manuale ha l'opzione per rifare tutto comunque |
| **Controllo settimanale** (`.github/workflows/controllo.yml`) | ogni lunedì alle 06:23 UTC, oppure a mano | cerca le frasi ancora da tradurre, controlla l'accessibilità con axe-core, poi link e file locali, bandi in scadenza, prezzi da rivedere e il sito davvero online | nessun file: scrive nella scheda «Issues» |

Come si tengono separati: il robot dei progetti non riparte quando cambiano i suoi quattro file, e quello dei PDF non riparte quando cambia `pdf/` o quando cambia solo una versione in `index.html`. Per questo un commit di un robot non ne risveglia un altro.

**Il quiz una volta sola.** «Il Grande Quiz dell'Informatica» esiste in due repository: quello buono (`grande-quiz`) e una copia vecchia (`Quiz-Interattivo-Terminale-Fenice-OS`), che è lo stesso programma. La copia sta nell'elenco `ESCLUSI` dentro `strumenti/aggiorna-progetti.py`, e prima di scrivere `progetti.json` il robot controlla tre cose: che nessun nome escluso sia ricomparso, che i quiz elencati siano uno solo, e che due progetti non portino allo stesso indirizzo. Se una di queste non torna non scrive niente e l'esecuzione diventa rossa nella scheda Actions: il doppione si vede subito, invece di finire online.

Il controllo settimanale non tocca il repository: se trova qualcosa apre un avviso nella scheda Issues con l'etichetta `controllo` (e GitHub manda un'email), lo aggiorna alla settimana dopo, e lo chiude da solo quando è tutto a posto. Il sito online lo guarda con qualche minuto di pazienza, riprovando, per non scambiare per guasto un ritardo di GitHub Pages; il resoconto comincia con una riga che dice a colpo d'occhio se il sito online è allineato a quello preparato qui.

Le ore sono UTC: in inverno in Italia sono un'ora più tardi (06:17, 06:47, 07:23), in estate due. Il registro di ogni esecuzione, con l'uscita di ogni passo, è nella scheda Actions del repository; da lì ogni robot si può anche lanciare a mano.

## Quando il push non parte dalla sandbox

A volte il lavoro viene preparato in un ambiente che non ha il token di GitHub: i commit restano lì e non possono uscire. In quel caso si porta tutto online con un **pacchetto** (`git bundle`), un file unico che contiene solo i commit nuovi.

1. Scarica il pacchetto `aggiornamenti.bundle` dal pannello della chat e mettilo dove ti è comodo.
2. Nella copia del repository sul tuo computer, con il **percorso assoluto** del pacchetto:

   ```bash
   cd /percorso/del/sito
   git checkout main
   git status --short                      # non deve stampare niente
   git log --oneline -1                    # il commit da cui parte il pacchetto
   git bundle verify /percorso/aggiornamenti.bundle
   git pull /percorso/aggiornamenti.bundle main
   ```

   Il `verify` deve dire `is okay` ed elencare due riferimenti: quello **contenuto** (l'ultimo commit) e quello **richiesto** (il punto di partenza). Se la tua copia è più indietro di quel punto, prima `git pull origin main`, poi riparti da qui.

3. Guarda l'esito del pull: deve comparire `Fast-forward`. Se invece leggi `merge made by`, hai commit tuoi in locale: fermati e sistemali prima di portare online, perché si sta unendo storia diversa.

4. Porta online e confronta i due lati:

   ```bash
   git push origin main
   git fetch origin
   git log --oneline origin/main -1        # lo stesso commit che hai in locale
   ```

5. Aspetta un minuto o due che GitHub Pages pubblichi, poi controlla il sito vero:

   ```bash
   curl -s -o /dev/null -w '%{http_code}\n' 'https://danilodauria.github.io/fonti/fonti.css?v=1'
   python3 strumenti/controlla-pagine.py --pubblicato
   ```

   Il primo comando deve dire `200`: è il modo più rapido per sapere se il sito è già la versione nuova, perché quel foglio arriva con i caratteri. Il secondo deve finire senza voci sui caratteri presi da Google.

Due cose fanno perdere tempo: il percorso **relativo** del pacchetto (dopo un `cd` punta altrove, e il pull fallisce con un messaggio poco chiaro) e il push rifiutato con `! [rejected] ... fetch first`, che si risolve con `git pull --rebase origin main` e un secondo `git push`. Nessun segreto va salvato sulla macchina: al push git chiede utente e token una volta sola, e il portachiavi di sistema se li ricorda.

Per aggiornare solo i bandi o le offerte basta modificare `bandi.json` o `offerte.json`: la pagina non va toccata.

Statistiche senza cookie con GoatCounter (codice «danilodauria»): danilodauria.goatcounter.com.

I nuovi progetti pubblicati su GitHub compaiono da soli nella sezione «Gli altri progetti» e nelle «Novità», e i numeri di versione delle schede si aggiornano da soli.

Testi e grafica © 2026 Danilo D'Auria, CC BY-NC-SA 4.0 · codice MIT.
