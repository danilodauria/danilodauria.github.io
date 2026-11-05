"""Crea le guide gratuite (guide/*.html) dai testi qui sotto. Le versioni PDF le fa strumenti/pdf/guide-pdf.py.
Per correggere una guida: modificate il testo qui e rilanciate  python3 strumenti/guide/crea-guide.py
Autore: Danilo D'Auria · testi CC BY-NC-SA 4.0 · codice MIT."""
import html, json, os
QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(QUI))
OUT = os.path.join(REPO, "guide")
os.makedirs(OUT, exist_ok=True)
E = html.escape
AGGIORNATA = "novembre 2026"

# Ogni guida: id, titolo, sottotitolo per la scheda, introduzione, sezioni [(titolo, [paragrafi o ("lista", [...])])], box finale
GUIDE = [
 {"id": "backup", "titolo": "Il backup: foto e documenti al sicuro",
  "breve": "La regola del 3-2-1 e come attivare la copia automatica su Windows, Mac, Linux e telefono.",
  "intro": "Un computer si può riparare o ricomprare; le foto di famiglia e i documenti no. Il backup è una copia di sicurezza: la prima volta richiede mezz'ora, poi lavora da solo.",
  "sezioni": [
   ("La regola del 3-2-1", [("lista", [
     "<b>3 copie</b> dei vostri dati: l'originale e due copie.",
     "<b>2 supporti diversi</b>: per esempio il disco del computer e un disco esterno.",
     "<b>1 copia fuori casa</b> o online: un servizio cloud, oppure un disco tenuto da un familiare."])]),
   ("Su Windows", [
     "Collegate un disco esterno. Nel Pannello di controllo aprite <b>Cronologia file</b> e premete <b>Attiva</b>: Windows copierà da solo documenti, immagini, musica e desktop, ogni ora.",
     "Su Windows 11 c'è anche l'app <b>Backup di Windows</b>, che salva cartelle e impostazioni sull'account Microsoft (OneDrive, 5 GB gratuiti)."]),
   ("Su Mac", ["Collegate un disco esterno e aprite <b>Impostazioni di Sistema › Generali › Time Machine › Aggiungi disco di backup</b>. Il Mac fa da solo copie orarie, giornaliere e settimanali."]),
   ("Su Linux", ["Usate l'app <b>Backup</b> (Déjà Dup) o lo strumento di backup della vostra distribuzione: scegliete le cartelle da salvare, il disco esterno e la frequenza."]),
   ("Sul telefono", [("lista", [
     "<b>Android</b>: attivate il backup in Google Foto e nelle impostazioni di Google (15 GB gratuiti, condivisi con Gmail e Drive).",
     "<b>iPhone e iPad</b>: Impostazioni › il vostro nome › iCloud › Backup iCloud (5 GB gratuiti), oppure una copia sul computer."])]),
   ("Tre abitudini che fanno la differenza", [("lista", [
     "Scollegate il disco esterno quando la copia è finita: un virus non può raggiungerlo.",
     "Ogni tanto provate a recuperare un file: un backup che non si riapre non serve.",
     "Mettete un promemoria mensile nel calendario."])]),
  ],
  "box": "Il momento giusto per fare il backup è prima che succeda qualcosa. Se volete, lo configuro io insieme a voi."},

 {"id": "truffe", "titolo": "Truffe online: come riconoscerle e cosa fare",
  "breve": "I segnali d'allarme, le truffe più diffuse e cosa fare subito se ci siete cascati.",
  "intro": "I truffatori non attaccano il computer: attaccano la fretta e la fiducia. Quasi tutte le truffe hanno gli stessi segnali, e imparare a vederli è la difesa migliore.",
  "sezioni": [
   ("I segnali d'allarme", [("lista", [
     "<b>Fretta</b>: «entro 24 ore», «conto bloccato», «ultimo avviso».",
     "<b>Richiesta di codici</b>: password, PIN, il codice arrivato via SMS, i dati della carta.",
     "<b>Link</b> in SMS, email o WhatsApp che portano a una pagina dove inserire i vostri dati.",
     "<b>Mittente o sito strano</b>: l'indirizzo non è quello ufficiale, anche se il logo sembra giusto.",
     "<b>Pagamenti insoliti</b>: ricariche, bonifici istantanei, criptovalute, carte regalo.",
     "<b>Offerte troppo belle</b>: guadagni facili, premi, prodotti a metà prezzo."])]),
   ("Le truffe più diffuse", [("lista", [
     "Il finto SMS della banca o delle Poste che segnala un accesso sospetto.",
     "Il finto corriere: un pacco in giacenza e un piccolo pagamento da fare.",
     "Il finto operatore della banca che telefona, a volte con il numero vero falsificato, e chiede di spostare i soldi su un «conto sicuro».",
     "«Ciao mamma, ho cambiato numero» su WhatsApp, con una richiesta urgente di soldi.",
     "I falsi investimenti pubblicizzati con volti famosi.",
     "Il finto tecnico che chiede di installare un programma per controllare il computer a distanza."])]),
   ("Le regole d'oro", [("lista", [
     "Banca, Poste e forze dell'ordine non vi chiederanno mai codici, password o di spostare denaro.",
     "Nel dubbio, chiudete e richiamate voi il numero ufficiale: quello sul retro della carta o sul sito, scritto a mano.",
     "Non installate programmi su richiesta di chi vi chiama.",
     "Attivate le notifiche dei movimenti della carta.",
     "Prima di pagare in fretta, parlatene con qualcuno di fiducia."])]),
   ("Se ci siete cascati", [("lista", [
     "Bloccate subito la carta o il conto chiamando il numero ufficiale della banca.",
     "Cambiate le password, iniziando dall'email, e attivate la verifica in due passaggi.",
     "Se avete installato un programma per il controllo a distanza, spegnete il computer e fatelo controllare.",
     "Denunciate alla Polizia Postale, anche online su commissariatodips.it.",
     "Conservate SMS, email e ricevute: servono come prove."])]),
  ],
  "box": "Vergognarsi non serve: le truffe sono fatte da professionisti e colpiscono tutti. Parlarne aiuta anche gli altri a non cascarci."},

 {"id": "vendere-donare", "titolo": "Prima di vendere, regalare o buttare un computer o un telefono",
  "breve": "Copiare i dati, uscire dagli account, cancellare tutto in sicurezza e dove portarlo.",
  "intro": "Un computer o un telefono contiene la vostra vita: foto, documenti, password, accessi alla banca. Prima che cambi mano, quattro passi.",
  "sezioni": [
   ("1. Copiate i dati", ["Fate un backup completo e controllate che si apra (c'è una guida apposta). Su WhatsApp salvate anche le chat."]),
   ("2. Uscite dagli account", [("lista", [
     "<b>Mac, iPhone e iPad</b>: disattivate «Trova il mio» e uscite dall'account Apple. Altrimenti resta il Blocco attivazione e il nuovo proprietario non può usarlo.",
     "<b>Android</b>: togliete l'account Google prima del ripristino, altrimenti il telefono chiederà la vostra password a chi lo riceve.",
     "<b>Windows</b>: uscite dall'account Microsoft e togliete il dispositivo dall'elenco su account.microsoft.com/devices.",
     "Togliete la SIM e la scheda di memoria."])]),
   ("3. Cancellate tutto in modo sicuro", [("lista", [
     "<b>Windows 10 e 11</b>: Impostazioni › Sistema › Ripristino › Reimposta il PC › Rimuovi tutto, e nelle impostazioni aggiuntive attivate la pulizia dell'unità.",
     "<b>Mac recenti</b>: Impostazioni di Sistema › Generali › Trasferisci o inizializza › Inizializza contenuti e impostazioni.",
     "<b>iPhone e iPad</b>: Impostazioni › Generali › Trasferisci o inizializza › Inizializza contenuto e impostazioni.",
     "<b>Android</b>: Impostazioni › Sistema › Opzioni di ripristino › Cancella tutti i dati (il percorso cambia un po' da marca a marca).",
     "Se il disco è rotto o i dati sono molto delicati, la soluzione sicura è distruggerlo fisicamente."])]),
   ("4. Dove portarlo", [("lista", [
     "<b>Donatelo</b>: scuole, associazioni e centri anziani possono usarlo ancora per anni. Posso rigenerarlo prima.",
     "<b>Isola ecologica</b> del vostro Comune: il ritiro dei rifiuti elettronici (RAEE) è gratuito.",
     "<b>«Uno contro uno»</b>: il negozio ritira gratis l'apparecchio vecchio quando ne comprate uno equivalente.",
     "<b>«Uno contro zero»</b>: i negozi di elettronica con almeno 400 m² di vendita ritirano gratis i piccoli apparecchi sotto i 25 cm, come telefoni e caricabatterie, anche senza acquisto.",
     "Mai nell'indifferenziata: contiene materiali preziosi e sostanze inquinanti."])]),
  ],
  "box": "Se non siete sicuri di aver cancellato tutto, portatelo a me: lo faccio e vi lascio la scheda di cosa ho fatto."},

 {"id": "password", "titolo": "Password e accessi sicuri, senza impazzire",
  "breve": "Password che si ricordano, un gestore di password, la verifica in due passaggi, SPID e CIE.",
  "intro": "Non serve una memoria da campioni: servono poche regole e lo strumento giusto.",
  "sezioni": [
   ("Una buona password", [("lista", [
     "Lunga almeno 12–14 caratteri: per esempio una frase di quattro o cinque parole a caso, come «cavallo-matita-luna-forno».",
     "Mai la stessa per due siti, soprattutto quella dell'email.",
     "Niente nomi, date di nascita o sequenze come 123456."])]),
   ("Il gestore di password", [
     "È un'app che ricorda tutte le password per voi, protetta da una sola password principale. Scelte gratuite e affidabili: <b>Bitwarden</b> (su computer e telefono), <b>KeePassXC</b> (sul computer, senza Internet), oppure quello integrato nel browser o nel telefono."]),
   ("La verifica in due passaggi", [
     "Oltre alla password serve un codice dal telefono: anche se qualcuno scopre la password, non entra. Attivatela prima di tutto su email, banca e social.",
     "Quando la attivate vi vengono dati dei codici di recupero: stampateli e conservateli con i documenti importanti."]),
   ("SPID, CIE e codici via SMS", [("lista", [
     "Le credenziali SPID e il PIN della carta d'identità elettronica sono come le chiavi di casa: non si danno a nessuno.",
     "Se qualcuno vi chiede di leggergli un codice arrivato via SMS, o di approvare una notifica che non avete chiesto voi, è una truffa.",
     "Se vi fate aiutare, restate davanti allo schermo e digitate voi i codici."])]),
   ("Gli aggiornamenti", ["Installate sempre gli aggiornamenti del sistema, del browser e delle app: chiudono le porte che i truffatori usano per entrare."]),
  ],
  "box": "Iniziate da una cosa sola: cambiate la password dell'email e attivate la verifica in due passaggi. È la porta di tutti gli altri account."},

 {"id": "pc-veloce", "titolo": "Un computer più veloce, gratis, in un pomeriggio",
  "breve": "Programmi all'avvio, spazio libero, browser, pulizia e quando conviene un SSD.",
  "intro": "Prima di pensare a un computer nuovo, provate questi passi: spesso bastano.",
  "sezioni": [
   ("1. Meno programmi all'accensione", [("lista", [
     "<b>Windows</b>: aprite Gestione attività (Ctrl + Maiusc + Esc) › App di avvio e disattivate ciò che non serve appena acceso. L'antivirus lasciatelo attivo.",
     "<b>Mac</b>: Impostazioni di Sistema › Generali › Elementi login."])]),
   ("2. Spazio libero sul disco", [
     "Lasciate libero almeno il 15–20% del disco. Su Windows: Impostazioni › Sistema › Archiviazione › Consigli per la pulizia. Svuotate la cartella Download e il cestino, e disinstallate i programmi che non usate."]),
   ("3. Un browser leggero", ["Poche schede aperte, via le estensioni che non usate. Un solo browser basta."]),
   ("4. Aggiornamenti e un controllo", [
     "Aggiornate sistema e driver e fate una scansione con Microsoft Defender, già incluso in Windows.",
     "Diffidate dei «programmi per velocizzare il PC» pubblicizzati online: spesso rallentano il computer, o sono truffe."]),
   ("5. Polvere e calore", [
     "La polvere nelle ventole fa scaldare il computer, che si rallenta per proteggersi. A computer spento e scollegato, soffiate aria compressa a brevi colpi tenendo ferma la ventola.",
     "Se la batteria di un portatile è gonfia, smettete di usarlo e fatela sostituire: è pericolosa."]),
   ("Quando non basta", [("lista", [
     "<b>Disco meccanico</b>: sostituirlo con un SSD è il cambio che si sente di più.",
     "<b>4 GB di memoria o meno</b>: se si può, aggiungere RAM costa poco.",
     "<b>Sistema troppo pesante</b>: un Linux leggero ridà vita anche ai computer di dieci o quindici anni."])]),
  ],
  "box": "Volete sapere cosa conviene fare con il vostro computer? Fate il test di un minuto sul sito: vi dico la strada e il costo."},
]

FENICE = open(os.path.join(REPO, "fenice.svg"), encoding="utf-8").read()
FENICE = FENICE[FENICE.index("<svg"):]

CSS = """
:root { --notte:#14232e; --brace:#b8400c; --fuoco:#e8702a; --oro:#f2b33d; --alba:#fde9b0; --bg:#fbf6ee; --foglio:#fff; --ink:#1c2730; --ink2:#4f5c68; --linea:#e6dccb; --morbido:#fbeedd; --verde:#2f7a4a; --verde-morbido:#e2f1e6; color-scheme: light; }
@media (prefers-color-scheme: dark) { :root { --bg:#0f1a22; --foglio:#16242f; --ink:#ecf1f4; --ink2:#a7b5c0; --linea:#263a48; --morbido:#2a2117; --brace:#f2a35c; --verde:#74cf98; --verde-morbido:#15301f; color-scheme: dark; } }
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink); font: 1.0625rem/1.65 "Atkinson Hyperlegible", "Segoe UI", system-ui, sans-serif; }
.barra { background: var(--notte); color: #f6efe4; padding: 10px max(16px, env(safe-area-inset-left)); display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.barra a.marchio { display: flex; align-items: center; gap: 10px; color: inherit; text-decoration: none; font-family: "Young Serif", Georgia, serif; }
.barra svg { width: 34px; height: 34px; }
.barra .azioni { margin-left: auto; display: flex; gap: 8px; flex-wrap: wrap; }
.barra .azioni a, .barra .azioni button { font: 700 .9rem inherit; font-family: inherit; padding: 7px 14px; border-radius: 99px; border: 1.5px solid rgba(253,233,176,.45); background: transparent; color: var(--alba); text-decoration: none; cursor: pointer; }
.barra .azioni .pieno { background: var(--oro); border-color: var(--oro); color: var(--notte); }
main { max-width: 760px; margin: 0 auto; padding: 36px 16px 56px; }
.label { font: .74rem/1.4 "JetBrains Mono", ui-monospace, monospace; letter-spacing: .12em; text-transform: uppercase; color: var(--ink2); }
h1, h2 { font-family: "Young Serif", Georgia, serif; font-weight: 400; line-height: 1.15; }
h1 { font-size: clamp(1.8rem, 1.3rem + 2vw, 2.5rem); margin: 8px 0 14px; }
h2 { font-size: 1.35rem; margin: 30px 0 8px; }
.intro { font-size: 1.15rem; color: var(--ink2); }
p { margin: 0 0 10px; }
ul { margin: 0 0 10px; padding-left: 22px; }
li { margin: 6px 0; }
.box { margin-top: 30px; padding: 16px 20px; border-radius: 14px; background: var(--verde-morbido); }
.piede { margin-top: 34px; padding-top: 14px; border-top: 1px solid var(--linea); font-size: .86rem; color: var(--ink2); }
a { color: var(--brace); }
@media print {
  @page { size: A4; margin: 16mm 16mm 18mm; }
  :root { --bg:#fff; --foglio:#fff; --ink:#1c2730; --ink2:#4f5c68; --linea:#e6dccb; --verde-morbido:#eaf5ed; }
  body { font-size: 10.5pt; }
  .barra { background: none; color: var(--ink); padding: 0 0 6mm; border-bottom: 1px solid var(--linea); }
  .barra .azioni { display: none; }
  main { padding: 6mm 0 0; max-width: none; }
  h2 { break-after: avoid; } li, .box { break-inside: avoid; }
}
"""

def corpo(blocchi):
    out = []
    for b in blocchi:
        if isinstance(b, tuple) and b[0] == "lista":
            out.append("<ul>" + "".join("<li>%s</li>" % x for x in b[1]) + "</ul>")
        else:
            out.append("<p>%s</p>" % b)
    return "".join(out)

for g in GUIDE:
    sez = "".join("<h2>%s</h2>%s" % (E(t), corpo(bl)) for t, bl in g["sezioni"])
    pagina = f"""<!doctype html>
<html lang="it">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(g['titolo'])} · Guide gratuite di Danilo D'Auria</title>
<meta name="description" content="{E(g['breve'])}">
<link rel="icon" href="../fenice.svg" type="image/svg+xml">
<link rel="manifest" href="../manifest.webmanifest">
<meta name="theme-color" content="#14232e">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Young+Serif&family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=JetBrains+Mono&display=swap">
<style>{CSS}</style>
<body>
<header class="barra">
  <a class="marchio" href="../">{FENICE}<span>Danilo D'Auria · Guide gratuite</span></a>
  <div class="azioni">
    <a href="../#guide">Tutte le guide</a>
    <button type="button" class="pieno" onclick="window.print()">Stampa o salva in PDF</button>
  </div>
</header>
<main>
  <p class="label">Guida gratuita · aggiornata a {AGGIORNATA}</p>
  <h1>{E(g['titolo'])}</h1>
  <p class="intro">{E(g['intro'])}</p>
  {sez}
  <p class="box">{E(g['box'])}</p>
  <p class="piede">Guida di Danilo D'Auria · danilodauria.github.io · danilodauria.site@gmail.com<br>Testo con licenza Creative Commons BY-NC-SA 4.0: potete stamparla e condividerla liberamente, senza scopo di lucro, citando l'autore.</p>
</main>
<script>
/* sul telefono e sul tablet ogni collegamento si apre in una nuova scheda */
(function () {{
  if (!(/Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent) || (window.matchMedia && matchMedia("(pointer: coarse)").matches))) return;
  document.addEventListener("click", function (e) {{
    var a = e.target.closest ? e.target.closest("a[href]") : null; if (!a) return;
    var h = a.getAttribute("href") || "";
    if (!h || h.charAt(0) === "#" || /^(mailto|tel|sms|javascript|data|blob):/i.test(h) || a.hasAttribute("download")) return;
    a.setAttribute("target", "_blank"); a.setAttribute("rel", "noopener");
  }}, true);
}})();
</script>
</body>
</html>
"""
    open(os.path.join(OUT, g["id"] + ".html"), "w", encoding="utf-8").write(pagina)

json.dump([{"id": g["id"], "titolo": g["titolo"], "breve": g["breve"]} for g in GUIDE],
          open(os.path.join(OUT, "elenco.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("guide create:", len(GUIDE))
