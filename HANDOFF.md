# HANDOFF — passaggio di consegne tra assistenti IA

Questo file è l'**ingresso unico** per qualunque assistente IA (o persona) che riprende il lavoro di **Danilo D'Auria** (`github.com/danilodauria`) senza aver visto le chat precedenti. Vale per **tutti i repository**, anche quelli che nasceranno in futuro.

Non sostituisce i file di consegna dei singoli progetti: li **precede**. Dice dove cercarli, con quali regole lavorare e come proporre idee nuove senza rompere ciò che funziona.

Tre strumenti lavorano insieme:
- **`HANDOFF.md`** (questo file): regole comuni a tutti i repository.
- **`AGENTS.md`** in ogni repository: poche righe che rimandano qui e dicono come verificare *quel* progetto.
- **`HANDOFF-REGISTRO.md`**: il registro dei passaggi (§9), separato da questo file perché cambia spesso.

> Ultimo aggiornamento di questo file: 24 novembre 2026.
> Il file è pubblico (GitHub Pages lo serve): **niente segreti, token, numeri di telefono, indirizzi di casa, foto personali**.

---

## 1. Regola fondamentale

**Il codice esistente che funziona non si riscrive, non si rinomina, non si rifattorizza.**

Si aggiunge, si corregge un difetto dimostrato, si estende in modo compatibile. Se pensi che una parte vada rifatta, **non farlo**: scrivilo come proposta (§6) e aspetta il sì di Danilo.

### Il percorso obbligatorio

1. **Leggi** (§2 e §3) prima di toccare qualunque cosa.
2. **Analizza** repository, ultimi commit, architettura, stile e convenzioni del progetto in cui lavori.
3. **Proponi un piano dettagliato**: quali file tocchi, quali aggiungi, cosa non tocchi, come verifichi, come torni indietro. Includi i miglioramenti che vedi, ma solo se compatibili con la struttura attuale.
4. **Attendi la conferma esplicita di Danilo.** Nessuna riga di codice prima del sì.
5. **Modifica il minimo**, in un ramo a parte quando possibile (§6).
6. **Verifica** con i controlli del progetto (§5). Se qualcosa diventa rosso e prima era verde, hai rotto tu: torna indietro.
7. **Consegna** (§7): commit chiaro, backup, registro dei passaggi (§9).

Un'eccezione ammessa senza piano: correggere un refuso o un link rotto *dentro un file di testo*, dicendolo subito dopo.

---

## 2. Come scoprire tutti i repository (anche i futuri)

Non fidarti di un elenco scritto qui: sarebbe già vecchio. Ricavalo ogni volta, in quest'ordine:

1. **`https://danilodauria.github.io/progetti.json`** — l'elenco dei progetti con versione, sito e indirizzo GitHub. Lo aggiorna da solo un robot ogni ora (`strumenti/aggiorna-progetti.py`): i repository nuovi compaiono lì senza che nessuno scriva niente.
2. **`https://github.com/danilodauria?tab=repositories`** — l'elenco reale. Confrontalo con il punto 1: `progetti.json` può non contenere tutto (esempio al 24/11/2026: `Quiz-Interattivo-Terminale-Fenice-OS` è nella home del sito ma non in `progetti.json`).
3. **API** `https://api.github.com/users/danilodauria/repos?per_page=100&sort=updated` — comoda, ma senza autenticazione ha un limite di richieste basso e può rispondere «rate limit exceeded»: in quel caso usa i punti 1 e 2.

Il robot dei progetti **ignora** i repository privati, le copie (fork) e quelli archiviati: un repository così non comparirà né in `progetti.json` né sul sito. È voluto (vale per il repository modello del §10).

Per ogni repository, **in questo ordine** leggi: il file di consegna del progetto (`CLAUDE.md`, `CONSEGNA.md`, `AGENTS.md`, se esistono) → `README.md` → `CHANGELOG.md` / `MIGLIORIE.md` → gli ultimi 20–30 commit (`git log --oneline -30`) → la cartella `tests/` e i workflow in `.github/workflows/`.

### Panoramica (24 novembre 2026 — verifica sempre dal vivo)

| Repository | Cos'è | File di consegna già presente |
|---|---|---|
| `danilodauria.github.io` | Sito di presentazione (pagina unica, 6 lingue, PDF, robot) | questo file + `README.md` |
| `professore-digitale` | Cattedra Digitale Portatile: app didattica offline, Linux e Windows XP–11 | `CLAUDE.md` (lungo: leggerlo per intero) |
| `consulente-digitale` | Programma con IA locale: scelta, aggiornamento e ottimizzazione dei dispositivi | `CLAUDE.md` |
| `tutor-digitale` | Lezioni di tecnologia su misura, PWA offline | `README.md`, `CHANGELOG.md`, `MIGLIORIE.md` |
| `psicologo-digitale` | PWA statica «La stanza d'ascolto» | `CONSEGNA.md` |
| `naturopata-digitale` | PWA, stessa famiglia di psicologo-digitale | `README.md` |
| `feniceos` | Distro Linux live basata su Debian | `README.md`, `docs/` |
| `grande-quiz` | Il Grande Quiz dell'Informatica | `README.md`, `docs/` |
| `nonni-teach` | Podcast/sito statico con feed | `README.md`, `LEGGIMI.txt` |
| `Quiz-Interattivo-Terminale-Fenice-OS` | Quiz e manuali interattivi offline per FeniceOS | `README.md` |
| `modello-progetto` (privato) | Modello da cui nascono i repository futuri (§10) | `README.md`, `AGENTS.md`, `CONSEGNA.md` |

**Se il repository ha già un suo file di consegna, quello vince su questo file** per tutto ciò che riguarda quel progetto. Questo file dà le regole comuni; non le contraddice.

---

## 3. Architettura e convenzioni comuni (verificate sul codice)

- **Lingua**: italiano semplice e gentile, pensato anche per chi è meno pratico. Commenti, README e messaggi di commit sono in italiano.
- **Filosofia**: offline per primo, nessun server obbligatorio, nessun account, nessuna telemetria. Dove si può: PWA statica con `sw.js`. I programmi devono poter funzionare dal vecchio al nuovo (Windows da XP a 11, Linux Debian/Ubuntu/Mint/Zorin).
- **Niente CDN, niente caratteri da Google**: i caratteri stanno in `fonti/` e si servono dal sito. Il controllo del sito lo verifica.
- **Statistiche**: solo GoatCounter, senza cookie.
- **Licenze**: codice MIT (`LICENSE`), testi e grafica CC BY-NC-SA 4.0 (`LICENZA-CONTENUTI.md` o `LICENSE-CONTENT.md`). Un file nuovo segue la licenza del repository in cui entra.
- **Traduzioni (sito)**: sei lingue (`it, en, fr, es, de, ro`). Le frasi nuove si scrivono in `i18n/fonti/<lingua>.tsv`, **senza cifre** (il motore le trasforma in segnaposto), poi `python3 strumenti/i18n/componi.py` deve chiudere con «errori: 0».
- **Service worker**: `sw.js` ha una versione del tipo `dd-AAAA-MM-GGx` (oggi `dd-2026-11-13b`). Se cambia ciò che finisce offline, la versione si incrementa, altrimenti i visitatori vedono la copia vecchia.
- **Azioni GitHub fissate all'impronta del commit** (sha), non all'etichetta `v4`: un'etichetta si può riscrivere, un'impronta no. Per aggiornare si cambia lo sha *e* il commento.
- **Permessi dei workflow al minimo** (`contents: read`, `write` solo dove serve) e `concurrency` per non sovrapporre i robot.
- **Messaggi di commit** (esempi reali): `Aggiunge il backup cifrato con password` · `Corregge la scheda da portare su schermo e stampa` · `Release 1.7.17: …` · `Versione 3.8.0` · `Tutor Digitale 1.12.3: …`. I robot usano frasi fisse tipo `PDF aggiornato in automatico`: non imitarle a mano.
- **Ramo**: `main` (i workflow lo nominano esplicitamente).

---

## 4. Il sito `danilodauria.github.io`: cosa è di chi

Il sito è una pagina unica (`index.html`, circa 850 KB) più dati e PDF. La tabella completa di ogni file è nel suo `README.md`: **leggila prima di toccare qualunque cosa**.

### Lo fanno i robot — non modificare a mano

| File | Chi lo scrive | Frequenza |
|---|---|---|
| `progetti.json`, `novita.json` (voci senza `"a_mano": true`), `feed.xml`, `vetrine.json` | «Aggiorna i progetti» | ogni ora |
| `bandi.json`, `offerte.json`, `fonti-viste.json`, `bandi-archivio.json` | «Bandi e offerte» | ogni giorno |
| `pdf/` (profilo, guide, volantino, biglietti, `info.json`) | «Aggiorna il PDF» | a ogni cambio e ogni giorno |
| In `index.html`: badge delle versioni e `PROGETTI_SALVATI` | `strumenti/versioni-schede.py` | dopo ogni aggiornamento progetti |

Controlli (non scrivono): «Controllo di sicurezza» e «Controllo settimanale» (apre un'Issue se qualcosa non va).

### Conseguenze pratiche per chi modifica

- I robot **committano su `main` di continuo**. Prima di ogni push: `git pull --rebase`. **Mai `push --force`.**
- **`index.html` è toccato sia da persone sia da robot**: modificalo con interventi piccoli e mirati, mai rigenerandolo o riformattandolo per intero.
- Variabile del repository **`PACCHETTO_IN_ARRIVO`**: se vale `1`, i robot non pubblicano (Danilo sta per caricare un pacchetto dalla sua macchina). Non cambiarla e non aggirarla; se la vedi a `1`, non spingere modifiche.
- Ogni robot ha un interruttore documentato nell'intestazione del suo workflow (Actions › nome › «Disable workflow»).
- Dati che si cambiano **senza toccare la pagina**: `prenota.json`, `lezioni.json`, `bandi.json`, `offerte.json`. Se un numero o una data stanno lì, cambia lì.
- Contenuti del sito: **nessuna foto personale, nessun numero di cellulare, nessun indirizzo di casa**.

---

## 5. Verifiche prima di consegnare

Per il sito, dalla cartella del repository (devono chiudere «Tutto a posto» **prima e dopo** la tua modifica):

```bash
python3 strumenti/controlla-pagine.py     # link, file locali, JSON, caratteri, titoli, sitemap
python3 strumenti/sicurezza.py            # segreti, permessi dei robot, file privati serviti
python3 strumenti/i18n/componi.py         # solo se hai toccato le traduzioni: «errori: 0»
```

Per gli altri progetti: usa ciò che trovi nel repository — `npm test` (tutor-digitale: `node tests/verify.cjs`), la cartella `tests/`, `build.sh`, i workflow in `.github/workflows/`. Se un progetto non ha test, **dillo nel piano** invece di inventarne.

Regola semplice: **se prima era verde e ora è rosso, la modifica non si consegna.**

---

## 6. Come aggiungere idee nuove in modo sicuro

1. **Solo in aggiunta**: file nuovi, funzioni nuove, sezioni nuove. Nessun nome esistente cambia.
2. **Ramo dedicato** (`idea/nome-breve`) e, dove possibile, una **Pull Request**: Danilo la rilegge e la unisce lui.
3. **Interruttore**: una funzione nuova nasce spenta o isolata, così si può togliere senza toccare il resto.
4. **Un'idea, un commit**: messaggi in italiano, nello stile del §3.
5. **Rete di salvataggio**: scrivi nel piano come si torna indietro (`git revert <sha>` o chiudere la PR).
6. **Fuori ambito**: se per fare l'idea servirebbe riscrivere qualcosa di esistente, ferma tutto e chiedi.

### Modello di piano (da incollare nella risposta a Danilo)

```
PIANO — <titolo breve>
Progetto: <repository> · ramo: idea/<nome>
Cosa voglio ottenere: …
File che AGGIUNGO: …
File che MODIFICO (solo righe indicate): …
File che NON tocco: …
Verifiche che lancio: …
Come si torna indietro: …
Miglioramenti compatibili che suggerisco (facoltativi): …
Rischi / domande aperte: …
→ Attendo il tuo sì prima di scrivere codice.
```

---

## 7. Consegna del lavoro (dopo la conferma e dopo la modifica)

- **Commit** piccoli e descrittivi; poi `git pull --rebase` e push senza forzare.
- **Non far partire i robot per niente.** Per un commit che aggiunge o cambia solo testo di consegna (`AGENTS.md`, `HANDOFF*.md`, `CONSEGNA.md`) in un repository con workflow attivi sul push, scrivi `[skip ci]` nel messaggio: GitHub non avvia nessun workflow per quel push. Non usarlo mai per codice, dati o pagine che devono essere pubblicati.
- **Backup**: dopo **ogni** modifica al sito `danilodauria.github.io`, senza che Danilo lo chieda, prepara e fagli scaricare un backup completo: una cartella `danilodauria.github.io_` seguita da data (e ora) e versione, compressa in zip. Dentro: `1_Sito`, `2_PDF`, `3_Cronologia` (con `storico-modifiche.txt`), `4_Sorgenti_di_lavoro`, `LEGGIMI.txt`, più il file `Cosa contiene.txt` con l'elenco puntato del contenuto, aggiornato a ogni backup.
- **Registro dei passaggi** (§9): una riga per ogni intervento.
- **Chiusura**: scrivi a Danilo cosa hai fatto, cosa hai verificato, cosa **non** hai potuto verificare.

---

## 8. Cosa non fare mai

- Riscrivere, rinominare, spostare o riformattare codice che funziona.
- Cambiare numeri di versione, licenze, prezzi o testi di servizio senza che Danilo lo chieda.
- Inserire segreti, token, dati personali (di Danilo o di terzi) in qualunque file.
- Aggiungere dipendenze esterne, CDN, tracciamenti, caratteri da Google, chiamate di rete nascoste.
- Disattivare un controllo (`sicurezza`, `controlla-pagine`, test) per far passare una modifica.
- `push --force`, riscrivere la cronologia, cancellare rami o tag che non hai creato tu.
- Modificare a mano i file dei robot (§4).
- Inventare: se non sai una cosa, scrivi «da verificare» e chiedi.

---

## 9. Registro dei passaggi

Il registro sta in **`HANDOFF-REGISTRO.md`** (stessa cartella di questo file). Una riga per intervento, **solo in aggiunta**, la più recente in fondo. Prima di chiudere il tuo lavoro, aggiungi la tua riga e leggi le ultime cinque: dicono cosa è rimasto a metà.

---

## 10. Repository nuovi

Un repository nuovo nasce dal modello **`modello-progetto`** (privato; su GitHub: «Use this template» › «Create a new repository»). Il modello contiene `README.md`, `AGENTS.md`, `CONSEGNA.md`, `.gitignore` e le licenze, già nello stile di questo file. Dopo averlo creato:

1. sostituisci i campi `<…>` in `README.md`, `AGENTS.md` e `CONSEGNA.md`;
2. aggiungi una riga al registro (§9);
3. se vuoi che compaia sul sito, il robot lo farà da solo (se il repository è pubblico).

Se un assistente crea un repository senza passare dal modello, deve comunque aggiungere almeno `AGENTS.md` con il rimando a questo file.
