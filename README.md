# danilodauria.github.io

Sito di presentazione di **Danilo D'Auria** — Tecnologia Gentile.

La pagina è una sola, `index.html`, e qui dentro c'è tutto quello che le serve: caratteri, traduzioni, dati, PDF. La tabella dice a cosa serve ogni file, così si trova subito quello da toccare.

| File | Cosa contiene |
|---|---|
| `index.html` | La pagina completa (progetti, libro, servizi, Green-Tech, adesioni dei partner, bandi, domande frequenti, contatti) |
| `bandi.json` | L'elenco dei bandi: la pagina lo rilegge a ogni apertura (LED verde) |
| `offerte.json` | Calendario delle offerte e prodotti da confrontare: le date ricorrenti (Black Friday, saldi, Prime Day…) si ricalcolano da sole ogni anno |
| `fenice.svg` | Il logo della fenice, usato anche come icona della scheda |
| `fonti/` | I caratteri del sito in `.woff2` (Young Serif, Atkinson Hyperlegible, JetBrains Mono) e `fonti.css`: si servono da qui, senza chiamare Google |
| `progetti.json` | I progetti e le loro versioni: lo aggiorna da solo ogni ora GitHub Actions (vale la versione più alta tra Release, etichette e package.json); in più la pagina, quando c'è linea, guarda subito su GitHub se è uscita una versione più nuova |
| `strumenti/aggiorna-progetti.py` | Lo script che legge i repository di danilodauria su GitHub. Prima di scrivere controlla che ogni progetto compaia una volta sola: il quiz vecchio non deve tornare |
| `strumenti/versioni-schede.py` | Riallinea a `progetti.json` le versioni scritte dentro `index.html`: il badge di ogni scheda e la copia di riserva dell'elenco (`PROGETTI_SALVATI`), che si vede subito e anche senza rete. Lo lancia il robot dopo `aggiorna-progetti.py`, così non restano versioni vecchie |
| `strumenti/controlla-pagine.py` | Controlla link e file locali, file JSON, lunghezza dei titoli, caratteri presi da Google (devono restare in `fonti/`) e indirizzi del sitemap: a mano (`python3 strumenti/controlla-pagine.py`), dal robot settimanale, oppure sulle pagine davvero online con `--pubblicato`, che apre sitemap, pagine, fogli di stile e caratteri del sito e segnala quello che non risponde 200 |
| `strumenti/sicurezza.py` | Il controllo di sicurezza: segreti finiti per sbaglio nel repository, permessi dei robot, azioni di GitHub fissate a un'impronta, indirizzi che da un file dati potrebbero diventare comandi, versione del lettore PDF, lista offline del service worker, file privati che GitHub Pages servirebbe lo stesso. Con `--pubblicato` guarda anche il sito vero; esce rosso se c'è qualcosa da sistemare |
| `.github/workflows/progetti.yml` | L'aggiornamento automatico (ogni ora, e con il pulsante «Run workflow» nella scheda Actions) |
| `pdf/leggi.html` | Il lettore dei PDF per i telefoni: si apre in una nuova scheda (usa PDF.js 4.10.38, licenza Apache 2.0, in `pdf/pdfjs/`; la versione sta in `pdf/pdfjs/versione.txt`). Dopo un caricamento riuscito salva il documento nella copia locale del service worker, così senza rete mostra le pagine invece dell'avviso |
| `pdf/` | Il profilo in PDF, per lo schermo e da stampare: lo rifà da solo GitHub Actions (`.github/workflows/pdf.yml`) quando cambia il sito, quando cambiano i progetti e ogni giorno per i bandi |
| `guide/` | Le guide gratuite (backup, truffe, vendere o donare un dispositivo, password, PC più veloce) in sei lingue: italiano in `guide/`, le altre in `guide/en/`, `guide/fr/`… Si scrivono in `strumenti/guide/crea-guide.py` (traduzioni in `strumenti/guide/guide_<lingua>.py`); i PDF li fa il robot in `pdf/guide/` |
| `pdf/Danilo_DAuria_volantino.pdf`, `pdf/Danilo_DAuria_biglietti.pdf` | Volantino A4 con linguette e biglietti da visita (10 per foglio): li rifà da solo il robot dei PDF (`strumenti/stampa/stampa.py`) con i prezzi del sito |
| `pdf/Kit_bandi_Danilo_DAuria.docx` / `.pdf` | Il kit per i bandi: scheda di progetto da adattare e lettera di adesione (`strumenti/kit/kit-bandi.py`) |
| `pdf/info.json` | Il numero di pagine dei PDF: il sito lo legge e lo mostra sempre giusto |
| `prenota.json` | I giorni e le fasce orarie proposti per prenotare il check-up: si cambia qui, senza toccare la pagina. La richiesta parte dall'email del cliente |
| `lezioni.json` | I prezzi delle **lezioni individuali** (a domicilio, pacchetto da 5, online, persona in più, km compresi): si cambiano i numeri qui e il sito li mostra da solo, anche il prezzo all'ora del pacchetto. Valori iniziali dalla media italiana (20–30 € l'ora) |
| `novita.json`, `feed.xml` | Le novità del sito e il feed (Atom): nuove versioni e nuovi progetti si aggiungono da sole ogni ora (`strumenti/novita.py`), con una sola voce per progetto all'ultima versione; le voci con `"a_mano": true` si scrivono a mano |
| `vetrine.json`, `strumenti/vetrine.py` | Le schede dei programmi nella home si aggiornano da sole: i **numeri** (schede, domande, capitoli…) seguono la tabella dei contenuti del README di ogni programma; se nel README compare una **sezione nuova**, la scheda riceve una riga «Novità della x.y.z» (una sola per scheda: la nuova sostituisce la vecchia, e dopo 90 giorni sparisce); quando esce una **versione nuova** la fotografia della scheda si rifà dalla pagina del programma. `vetrine.json` ricorda sezioni viste e versione fotografata |
| `strumenti/notizie.py`, `.github/workflows/notizie.yml` | Ogni mattina ricontrolla **bandi** e **calendario delle offerte**: data di controllo sempre di oggi, scadenze lette dalle fonti quando mancano, **avvisi nuovi** presi dalle fonti ufficiali (entrano come «Segnalato» con il link; dopo 45 giorni escono se nessuno li completa), bandi chiusi da più di 120 giorni spostati in `bandi-archivio.json`, eventi delle offerte già finiti tolti. Aggiorna anche le copie di riserva dentro `index.html`. `fonti-viste.json` ricorda gli avvisi già visti |
| Sito «in casa» | Aperto dal GitHub di casa (`http://localhost:8080` o dall'indirizzo del PC in rete), la pagina tiene in casa i collegamenti: quelli a `danilodauria.github.io` diventano pagine locali, quelli a `github.com/danilodauria` vanno al GitHub di casa (porta 3000). I collegamenti ad altri siti, se manca Internet, mostrano un avviso con «Copia l'indirizzo» invece di una pagina d'errore. Su GitHub Pages non cambia niente |
| `sitemap.xml`, `robots.txt` | Per Google: l'elenco delle pagine in tutte le lingue. I dati strutturati nella pagina (persona, servizi con prezzi, libro, domande frequenti) li scrive `strumenti/seo/seo.py` rileggendo la pagina stessa |
| `i18n/` | Il sito in inglese, francese, spagnolo, tedesco e rumeno. Le traduzioni si scrivono a mano in `i18n/fonti/<lingua>.tsv`, poi `python3 strumenti/i18n/componi.py`. Le frasi nuove ancora da tradurre restano in italiano e le segnala il controllo settimanale |
| `casi.json` | I casi reali «prima e dopo», solo con il consenso del cliente: si preparano con la scheda intervento |
| `scheda/` | La scheda intervento per il tecnico (danilodauria.github.io/scheda/): si compila sul posto, si stampa per il cliente, prepara il caso per il sito. Non è collegata dal sito |
| `vista.html`, `torna.js` | Sul telefono i siti dei progetti si aprono con la barra del sito e il pulsante «← Sito» per tornare indietro |
| `manifest.webmanifest`, `sw.js`, `icone/` | Il sito installabile come app, che funziona anche senza Internet |
| `.github/workflows/controllo.yml` | Il controllo di ogni lunedì: link delle fonti, bandi in scadenza, prezzi da rivedere, traduzioni mancanti, accessibilità (WCAG 2.1 AA con axe-core, `strumenti/accessibilita/controlla.py`) e il sito davvero online (`--pubblicato`, riprovando con calma per non prendere per guasto un ritardo di GitHub Pages). Se c'è qualcosa da fare apre un avviso nella scheda «Issues» (e GitHub manda un'email) |
| `.github/workflows/sicurezza.yml` | Il controllo di sicurezza a ogni push che tocca pagina, schede, JSON o robot, e ogni lunedì alle 06:13 UTC: non scrive niente, se trova qualcosa l'esecuzione diventa rossa e GitHub manda un'email |
| `anteprima.png` | L'immagine che compare quando si condivide il link su WhatsApp e social |
| `README.md` | Questa mappa: a cosa serve ogni file, cosa scrivono i robot, i numeri delle pubblicazioni |

## I tre robot

Tre robot di GitHub Actions si occupano del sito da soli. Ognuno scrive **solo i propri file**, e nessuno rifà partire sé stesso: così i robot non si pestano i piedi e non si accendono a vicenda all'infinito.

| Robot | Quando parte | Cosa fa | Cosa scrive |
|---|---|---|---|
| **Aggiorna i progetti** (`.github/workflows/progetti.yml`) | ogni ora (al minuto 17), con il pulsante «Run workflow» della scheda Actions, e a ogni modifica del sito su `main` | legge i repository pubblici di danilodauria e le versioni, aggiorna le Novità e il feed, riallinea le versioni dentro `index.html` (badge delle schede e copia di riserva `PROGETTI_SALVATI`) | `progetti.json`, `novita.json`, `feed.xml`, `index.html` — e solo se qualcosa è davvero cambiato |
| **Aggiorna il PDF** (`.github/workflows/pdf.yml`) | dopo ogni modifica del sito su `main`, dopo ogni esecuzione del robot dei progetti, e ogni giorno alle 05:47 UTC | rifà profilo, guide, volantino e biglietti da visita con i caratteri di `fonti/`, poi conta le pagine dei documenti | `pdf/` — e solo se i contenuti sono cambiati; il pulsante manuale ha l'opzione per rifare tutto comunque |
| **Controllo settimanale** (`.github/workflows/controllo.yml`) | ogni lunedì alle 06:23 UTC, oppure a mano | cerca le frasi ancora da tradurre, controlla l'accessibilità con axe-core, poi link e file locali, bandi in scadenza, prezzi da rivedere e il sito davvero online | nessun file: scrive nella scheda «Issues» |

C'è anche un quarto controllo, che non scrive niente e per questo non sta nella tabella dei tre robot: `.github/workflows/sicurezza.yml` esegue `strumenti/sicurezza.py` a ogni push che tocca la pagina, le schede, i JSON, il service worker o i robot, e ogni lunedì alle 06:13 UTC. Cerca segreti finiti per sbaglio, permessi troppo larghi, azioni di GitHub fissate a un'etichetta invece che a un'impronta del commit, indirizzi che da un file dati potrebbero diventare `javascript:`, il lettore PDF da aggiornare, la lista offline del service worker (sw.js) e file privati che GitHub Pages servirebbe lo stesso. Se trova qualcosa l'esecuzione diventa rossa e GitHub manda un'email; a mano si lancia con `python3 strumenti/sicurezza.py --pubblicato`.

Come si tengono separati: il robot dei progetti non riparte quando cambiano i suoi quattro file, e quello dei PDF non riparte quando cambia `pdf/` o quando cambia solo una versione in `index.html`. Per questo un commit di un robot non ne risveglia un altro.

**Cosa scrivono e cosa non toccano.** Il robot dei progetti scrive solo `progetti.json`, `novita.json`, `feed.xml` e i numeri di versione dentro `index.html`; quello dei PDF scrive solo `pdf/`; il controllo settimanale non scrive nel repository, apre soltanto un avviso nella scheda Issues — e i due che scrivono lo fanno solo quando il contenuto è davvero cambiato. Non toccano mai testi, grafici, guide, `fonti/` né il resto dei file: se qualcosa non torna si fermano rossi, non correggono da soli.

**Il quiz una volta sola.** «Il Grande Quiz dell'Informatica» esiste in due repository: quello buono (`grande-quiz`) e una copia vecchia (`Quiz-Interattivo-Terminale-Fenice-OS`), che è lo stesso programma. La copia sta nell'elenco `ESCLUSI` dentro `strumenti/aggiorna-progetti.py`, e prima di scrivere `progetti.json` il robot controlla cinque cose: che nessun nome escluso sia ricomparso, che i quiz elencati siano uno solo, e che due progetti non portino allo stesso indirizzo, non abbiano lo stesso titolo e non abbiano la stessa descrizione (spazi e maiuscole non contano, e i campi vuoti sono esclusi dal confronto). Se una di queste non torna non scrive niente e l'esecuzione diventa rossa nella scheda Actions: il doppione si vede subito, invece di finire online.

**Chi può spostare `main`.** Due robot su tre scrivono sul ramo: «Aggiorna i progetti» (commit su `progetti.json`, `novita.json`, `feed.xml`, `index.html`) e «Aggiorna il PDF» (commit su `pdf/`). Il «Controllo settimanale» no: ha solo il permesso di lettura e al massimo apre un avviso nella scheda Issues. I due che scrivono riprovano tre volte, con `git pull --rebase` fra un tentativo e l'altro, quindi il peggio che può capitare al tuo push è di essere rifiutato con `fetch first`: non si perde niente, si riprova. Se mentre spedisci un pacchetto non vuoi che pubblichino, metti la variabile `PACCHETTO_IN_ARRIVO` a `1` (Settings › Secrets and variables › Actions › Variables) prima del push e riportala a `0` appena hai finito: i robot lavorano lo stesso, ma saltano il passo che salva, e nel log compare un avviso che lo dice. Non dimenticare lo `0`: finché è a `1` il sito non si aggiorna da solo.

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

   Il `verify` deve elencare due riferimenti — quello **contenuto** (l'ultimo commit) e quello **richiesto** (il punto di partenza) — senza segnalare errori. In Git Bash compare anche la riga «is okay»; su Windows con PowerShell può non comparire, e allora vale il codice di uscita: se non stampa errori, il pacchetto è buono. Se la tua copia è più indietro del punto richiesto, prima `git pull origin main`, poi riparti da qui.

3. Guarda l'esito del pull: deve comparire `Fast-forward`. Se invece leggi `merge made by`, hai commit tuoi in locale: fermati e sistemali prima di portare online, perché si sta unendo storia diversa.

4. Porta online e confronta i due lati:

   ```bash
   for prova in 1 2 3; do                 # se un robot ha appena scritto, si riprova
     git push origin main && break
     git pull --rebase origin main
     sleep 10
   done
   git fetch origin
   git log --oneline origin/main -1        # lo stesso commit che hai in locale
   ```

5. Aspetta un minuto o due che GitHub Pages pubblichi, poi controlla il sito vero:

   ```bash
   curl -s -o /dev/null -w '%{http_code}\n' 'https://danilodauria.github.io/fonti/fonti.css?v=1'
   python3 strumenti/controlla-pagine.py --pubblicato
   ```

   Il primo comando deve dire `200`: è il modo più rapido per sapere se il sito è già la versione nuova, perché quel foglio arriva con i caratteri. Il secondo deve finire senza voci sui caratteri presi da Google.

Due cose fanno perdere tempo: il percorso **relativo** del pacchetto (dopo un `cd` punta altrove, e il pull fallisce con un messaggio poco chiaro) e il push rifiutato con `! [rejected] ... fetch first`, che il giro di ripetizioni del punto 4 risolve da solo. Dopo un `git pull --rebase` i tuoi commit hanno impronte nuove: il pacchetto vale per la copia da cui l'hai preso, non per una seconda macchina. Nessun segreto va salvato sulla macchina: al push git chiede utente e token una volta sola, e il portachiavi di sistema se li ricorda. Se su Windows `git` non risponde («Termine 'git' non riconosciuto»), non serve installare niente: GitHub Desktop ne porta uno suo in `%LOCALAPPDATA%\GitHubDesktop\app-<versione>\resources\app\git\cmd\git.exe`, e lo si chiama con il percorso completo.

## Il primo push dell'8 novembre 2026 (i caratteri)

Il push che ha portato online i caratteri ospitati è arrivato la sera dell'8 novembre 2026, fatto dal computer di Danilo col pacchetto perché la sandbox non ha il token: **16 commit** da `3098d6f` a `818fdb7`, 67 file, `988 insertions(+), 166 deletions(-)`. Subito dopo i robot hanno aggiunto i loro due, «Progetti aggiornati in automatico» e «PDF aggiornato in automatico». Il sito vero, misurato prima e dopo:

| Cosa | Prima del push | Dopo il push |
|---|---|---|
| `fonti/fonti.css` | 404 | **200** |
| File di caratteri raggiungibili | 0 su 12 | **12 su 12** |
| Pagine che prendono i caratteri da Google | 36 | **0** |
| Progetti in `progetti.json` | 8, con il quiz vecchio | **7, senza** |
| Titoli più lunghi di 70 caratteri | 30 | **0** |
| Voci «Da sistemare» in `controlla-pagine.py --pubblicato` | 11 | **0** |

Il controllo del sito pubblicato, rifatto appena GitHub Pages ha servito la versione nuova, chiude con «Tutto a posto»: nessun riferimento a Google in 36 pagine e 1 foglio di stile, titoli tutti entro il limite, 12 file di caratteri raggiungibili.

Per aggiornare solo i bandi o le offerte basta modificare `bandi.json` o `offerte.json`: la pagina non va toccata.

Statistiche senza cookie con GoatCounter (codice «danilodauria»): danilodauria.goatcounter.com.

I nuovi progetti pubblicati su GitHub compaiono da soli nella sezione «Gli altri progetti» e nelle «Novità», e i numeri di versione delle schede si aggiornano da soli.

## Il riquadro delle adesioni

Dentro la sezione `#green-tech` («Hub Green-Tech», subito dopo «Chi sono») c'è un riquadro per raccogliere le adesioni dei partner (`<form id="adesioni">`): nome e cognome, email, dove (quartiere o città), che tipo di partner (8 voci nella tendina: «Scegli…» più sette tipi), cosa si può offrire, e la casella del consenso con l'informativa apribile «Come tratto i dati». In tutto 11 elementi con un id `ad-*`, più il riquadro con il messaggio composto e i pulsanti «Prepara la richiesta», «Apri l'email», «Copia il messaggio».

Il modulo non ha un server: la richiesta si compone nel browser e parte dall'email di chi scrive, come per la richiesta di preventivo. Il sito non salva niente e non mette i dati nell'indirizzo — se lo script della pagina non è ancora partito, il modulo ha un ripiego (`action="mailto:…"`) che apre l'email invece di fare un invio normale con i campi nella barra degli indirizzi. Il testo che si compone resta in italiano; etichette, consenso, informativa e messaggi d'errore sono tradotti.

Per il modulo sono state tradotte **23 frasi nuove per lingua**: il sito passa così a **963 frasi** in ognuna delle sei lingue (`it, en, fr, es, de, ro`), e `python3 strumenti/i18n/componi.py` chiude con «errori: 0». Le frasi si scrivono in `i18n/fonti/<lingua>.tsv`: niente cifre, perché il motore le trasforma in segnaposto (`{n0}`) e la chiave non corrisponderebbe più — per questo l'informativa dice «come previsto dal GDPR» invece di citare l'articolo.

## Il secondo push dell'8 novembre 2026 (Green-Tech e adesioni)

Il secondo push della giornata ha portato online la sezione e il riquadro: **5 commit** da `04eff18` a `698d74d`, **14 file**, `707 insertions(+), 2 deletions(-)`. Qualche minuto dopo il robot dei PDF ha aggiunto il suo `935b154` «PDF aggiornato in automatico», rifacendo profilo e profilo da stampa (303 righe cambiate, impronta del contenuto `87edc232…` → `03e09601…`); il profilo ora pesa 888 088 byte.

| Cosa | Prima del push | Dopo il push |
|---|---|---|
| Sezioni della pagina | 18 | **19**, con `#green-tech` |
| Voci di menu che portano a Green-Tech | 0 | **2** (desktop e telefono) |
| Modulo delle adesioni | assente | **presente**: 11 elementi `ad-*`, 8 voci nella tendina |
| Frasi per lingua | 914 | **963** in tutte e sei |
| Service worker | `dd-2026-11-07a` | **`dd-2026-11-08a`** |
| Profilo in PDF | 20 pagine, testo vecchio | 20 pagine, testo nuovo |
| Indirizzi nel sitemap | 39 | **39**, tutti con la loro pagina |

Controllato sulla pagina vera dopo la pubblicazione: `index.html` da 779 123 byte, con sezione, modulo, consenso e menu; le sei lingue servite da GitHub Pages con 963 frasi ciascuna; service worker nuovo; `pdf/info.json` a 20/1/2/4 pagine; `controlla-pagine.py` chiude con «Tutto a posto». I PDF rigenerati l'8 novembre alle 22:38 contengono il testo nuovo, con impronta diversa dalla precedente; il robot rifà solo ciò che cambia, quindi volantino, biglietti e kit sono quelli di prima — il loro contenuto non è cambiato.

Testi e grafica © 2026 Danilo D'Auria, CC BY-NC-SA 4.0 · codice MIT.
