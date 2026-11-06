"""Kit per i bandi: scheda di progetto modificabile (Word) e la stessa in PDF, per enti, scuole e associazioni
che vogliono candidare un progetto di inclusione digitale con Danilo D'Auria come partner tecnico e formativo.
Uso: python3 strumenti/kit/kit-bandi.py   (il PDF richiede LibreOffice: soffice)
Autore: Danilo D'Auria · testi CC BY-NC-SA 4.0 · codice MIT"""
import os, subprocess
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor, Mm, Cm

QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(QUI))
OUT = os.path.join(REPO, "pdf")
NOME = "Kit_bandi_Danilo_DAuria"
NOTTE, BRACE, INK2 = RGBColor(0x14, 0x23, 0x2E), RGBColor(0xB8, 0x40, 0x0C), RGBColor(0x4F, 0x5C, 0x68)
LISTINO = "novembre 2026"

doc = Document()
sez = doc.sections[0]
sez.page_width, sez.page_height = Mm(210), Mm(297)
for lato in ("left_margin", "right_margin"): setattr(sez, lato, Mm(20))
sez.top_margin, sez.bottom_margin = Mm(18), Mm(18)
st = doc.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(10.5)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
st.paragraph_format.space_after = Pt(5); st.paragraph_format.line_spacing = 1.15
for n, dim in (("Heading 1", 15), ("Heading 2", 12.5)):
    h = doc.styles[n]; h.font.name = "Georgia"; h.font.size = Pt(dim); h.font.bold = False; h.font.color.rgb = NOTTE
    h.element.rPr.rFonts.set(qn("w:eastAsia"), "Georgia"); h.paragraph_format.space_before = Pt(14); h.paragraph_format.space_after = Pt(5)
    h.paragraph_format.keep_with_next = True

def sfondo(cella, colore):
    tc = cella._tc.get_or_add_tcPr(); s = OxmlElement("w:shd"); s.set(qn("w:val"), "clear"); s.set(qn("w:color"), "auto"); s.set(qn("w:fill"), colore); tc.append(s)

def par(testo="", grassetto=False, corsivo=False, colore=None, dim=None, allinea=None):
    p = doc.add_paragraph()
    for i, pezzo in enumerate(testo.split("**")):
        r = p.add_run(pezzo); r.bold = grassetto or (i % 2 == 1); r.italic = corsivo
        if colore: r.font.color.rgb = colore
        if dim: r.font.size = Pt(dim)
    if allinea: p.alignment = allinea
    return p

def elenco(voci):
    for v in voci:
        p = doc.add_paragraph(style="List Bullet")
        for i, pezzo in enumerate(v.split("**")):
            r = p.add_run(pezzo); r.bold = i % 2 == 1

def tabella(intest, righe, larghezze=None, ultima_forte=False):
    t = doc.add_table(rows=1, cols=len(intest)); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, x in enumerate(intest):
        c = t.rows[0].cells[i]; c.text = ""; r = c.paragraphs[0].add_run(x); r.bold = True; r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF); r.font.size = Pt(9.5); sfondo(c, "14232E")
    for k, riga in enumerate(righe):
        cel = t.add_row().cells
        for i, x in enumerate(riga):
            cel[i].text = ""; r = cel[i].paragraphs[0].add_run(str(x)); r.font.size = Pt(9.5)
            if ultima_forte and k == len(righe) - 1: r.bold = True; sfondo(cel[i], "FBEEDD")
    if larghezze:
        for riga in t.rows:
            for i, w in enumerate(larghezze): riga.cells[i].width = Cm(w)
    doc.add_paragraph()
    return t

# ---------------------------------------------------------------- copertina
p = par("KIT PER I BANDI · SCHEDA DI PROGETTO", colore=BRACE, dim=9, grassetto=True)
t = doc.add_paragraph(); r = t.add_run("Seconda vita digitale"); r.font.name = "Georgia"; r.font.size = Pt(26); r.font.color.rgb = NOTTE
par("Computer rigenerati e competenze digitali per [territorio o destinatari]", dim=13, colore=NOTTE)
par("Modello da adattare per comuni, scuole, biblioteche, centri anziani, associazioni e imprese che cofinanziano progetti sociali. "
    "Partner tecnico e formativo: Danilo D'Auria.", colore=INK2)
box = doc.add_table(rows=1, cols=1); c = box.rows[0].cells[0]; sfondo(c, "FBEEDD"); c.text = ""
c.paragraphs[0].add_run("Come usare questo modello. ").bold = True
c.paragraphs[0].add_run("Le parti tra [parentesi quadre] sono da completare o adattare. Ogni bando ha le sue regole: "
                        "copiate le sezioni nel formulario ufficiale e rispettate limiti di caratteri, voci di spesa ammesse e quote di cofinanziamento. "
                        "L'elenco dei bandi aperti, aggiornato ogni giorno, è su danilodauria.github.io nella sezione «Bandi». "
                        "Per adattarlo insieme scrivete a danilodauria.site@gmail.com.")
doc.add_paragraph()

# ---------------------------------------------------------------- sezioni
doc.add_heading("1. Soggetto proponente", level=1)
tabella(["Voce", "Da compilare"], [["Ente o associazione capofila", "[nome, forma giuridica, codice fiscale]"], ["Sede e territorio", "[comune, quartiere]"],
        ["Referente del progetto", "[nome, ruolo, email, telefono]"], ["Altri partner", "[scuola, biblioteca, centro anziani, impresa cofinanziatrice…]"]], [6, 10.5])

doc.add_heading("2. Partner tecnico e formativo", level=1)
par("**Danilo D'Auria** è tecnico IT, formatore e divulgatore digitale, autore del libro «Tecnologia Gentile: Informatica Sostenibile» e ideatore di FeniceOS. "
    "Rigenera computer considerati obsoleti con sistemi liberi e insegna a usarli con consapevolezza, con programmi gratuiti che funzionano anche senza Internet.")
elenco(["**FeniceOS**: sistema operativo libero per PC rigenerati, in italiano, con i programmi didattici già inclusi.",
        "**Professore Digitale**: lezioni guidate di alfabetizzazione digitale, anche offline, testo grande, lettura ad alta voce.",
        "**Il Grande Quiz**: verifica finale in aula o a squadre, con correzione automatica.",
        "**Nonni Teach**: laboratorio intergenerazionale in cui i nonni raccontano e i ragazzi registrano.",
        "**Guide gratuite** da stampare: backup, truffe online, password e SPID, dispositivi da donare, PC più veloce.",
        "Tutti i programmi hanno codice MIT e contenuti Creative Commons: **nessuna licenza da pagare**, né durante né dopo il progetto."])

doc.add_heading("3. Contesto e bisogni", level=1)
par("[Descrivete il territorio e le persone: quanti anziani vivono soli, quanti non usano Internet, le difficoltà con SPID, sanità online e banca, "
    "il rischio di truffe. Usate un dato ufficiale, per esempio ISTAT o del vostro Comune, citando la fonte.]", corsivo=True, colore=INK2)
par("Molti enti hanno computer dismessi perché non compatibili con i sistemi più recenti, ma ancora funzionanti. "
    "Rigenerati, possono diventare la dotazione di un'aula o essere affidati alle famiglie che non ne hanno uno, invece di diventare rifiuti elettronici.")

doc.add_heading("4. Obiettivi", level=1)
elenco(["Dare competenze digitali di base e sicure a **[numero] persone** [anziani, adulti, famiglie, persone con disabilità].",
        "Rimettere in funzione **[numero] computer** dismessi, invece di smaltirli.",
        "Ridurre il rischio di truffe online e aiutare l'accesso ai servizi pubblici digitali (SPID, CIE, app IO).",
        "Lasciare al territorio un'aula e strumenti che continuano a funzionare dopo il progetto, senza costi di licenza."])

doc.add_heading("5. Attività", level=1)
tabella(["Modulo", "Cosa si fa", "Strumenti", "Durata"], [
    ["A · Computer", "Raccolta dei PC dismessi, check-up, rigenerazione, installazione dei programmi didattici", "FeniceOS o altro Linux, SSD dove serve", "[n] settimane"],
    ["B · Primi passi", "Mouse, tastatura, file, Internet, email, videochiamate", "Professore Digitale, proiettore", "[n] incontri da 2 ore"],
    ["C · Sicuri online", "Password, SPID e CIE, riconoscere le truffe, backup", "Guide gratuite, esercitazioni", "[n] incontri"],
    ["D · Verifica", "Quiz finale e attestato di partecipazione", "Il Grande Quiz", "1 incontro"],
    ["E · Insieme (facoltativo)", "Laboratorio nonni e ragazzi: ricordi e mestieri raccontati e registrati", "Nonni Teach", "[n] incontri"],
    ["F · Restituzione", "Consegna dei PC all'ente o ai partecipanti, schede tecniche, istruzioni stampate", "Schede intervento", "fine progetto"]],
    [3.2, 6.3, 4, 3])

doc.add_heading("6. Cronoprogramma", level=1)
mesi = ["Mese 1", "Mese 2", "Mese 3", "Mese 4", "Mese 5", "Mese 6"]
X = "●"
tabella(["Attività"] + mesi, [["A · Computer", X, X, "", "", "", ""], ["B · Primi passi", "", X, X, X, "", ""], ["C · Sicuri online", "", "", X, X, X, ""],
                              ["D · Verifica", "", "", "", "", X, ""], ["E · Insieme", "", "", X, X, X, ""], ["F · Restituzione", "", "", "", "", "", X]], [4.4] + [2] * 6)

doc.add_page_break()
doc.add_heading("7. Risultati attesi e indicatori", level=1)
tabella(["Indicatore", "Valore atteso", "Come si misura"], [
    ["Persone formate", "[numero]", "Registro presenze"], ["Ore di formazione erogate", "[numero]", "Calendario degli incontri"],
    ["Computer rigenerati e consegnati", "[numero]", "Schede intervento con prima e dopo"],
    ["CO₂ evitata", "circa 82 kg per portatile e 128 kg per PC fisso, in 3 anni", "Fattori ADEME 2022: 27,3 kg (portatile) e 42,5 kg (fisso) per anno di utilizzo"],
    ["Verifica superata", "[percentuale] dei partecipanti", "Il Grande Quiz"], ["Gradimento", "[valore] su 5", "Questionario finale"]], [5, 4.5, 7])
par("Per calcolare la CO₂ e il risparmio del vostro progetto usate il calcolatore «Quanto risparmio» su danilodauria.github.io: copia un testo pronto per la relazione.", colore=INK2, dim=9.5)

doc.add_heading("8. Budget di esempio", level=1)
tabella(["Voce", "Quantità", "Costo unitario", "Totale"], [
    ["Check-up diagnostico dei computer", "10", "GRATIS", "0 €"],
    ["Rigenerazione «Turbo» con Linux e SSD nuovo", "10", "85 €", "850 €"],
    ["Formazione in aula", "[ore]", "[da concordare]", "[…]"],
    ["Stampa di guide e dispense", "[copie]", "[…]", "[…]"],
    ["Licenze software", "—", "0 €", "0 €"],
    ["Coordinamento e rendicontazione dell'ente", "[…]", "[…]", "[…]"],
    ["Totale", "", "", "[…]"]], [7, 2.5, 3.5, 3.5], ultima_forte=True)
par(f"Prezzi della rigenerazione dal listino fisso di Danilo D'Auria ({LISTINO}): Linux 45 € («Seconda vita») o 85 € («Turbo»); "
    "Windows 55 € o 95 €; Mac 60 € o da 110 €. Per 6 o più computer è previsto un prezzo dedicato. Verificate sempre quali spese ammette il bando.", colore=INK2, dim=9.5)

doc.add_heading("9. Sostenibilità e continuità", level=1)
elenco(["I programmi sono liberi e gratuiti per sempre: nessuna licenza da rinnovare alla fine del finanziamento.",
        "Funzionano senza Internet: l'aula resta utilizzabile anche dove la rete è debole.",
        "Volontari e operatori dell'ente vengono formati per continuare da soli; guide e schede restano all'ente.",
        "Ogni computer rigenerato è un rifiuto elettronico in meno; ciò che non si recupera va ai RAEE."])

doc.add_heading("10. Bandi adatti", level=1)
par("Il modello si adatta a bandi per l'inclusione digitale, l'educazione degli adulti e la transizione ecologica: per esempio il Fondo per la Repubblica Digitale, "
    "i partenariati su piccola scala Erasmus+ per l'educazione degli adulti, i bandi di fondazioni bancarie e regionali, i voucher delle Camere di commercio per le imprese. "
    "Scadenze e requisiti cambiano spesso: l'elenco aggiornato, con il link alla fonte ufficiale, è su danilodauria.github.io, sezione «Bandi».")

doc.add_heading("Allegato · Lettera di adesione del partner", level=1).paragraph_format.page_break_before = True
par("[Luogo], [data]", allinea=WD_ALIGN_PARAGRAPH.RIGHT)
par("Spettabile [ente capofila]")
par("Oggetto: adesione al progetto «Seconda vita digitale» in qualità di partner tecnico e formativo", grassetto=True)
par("Il sottoscritto Danilo D'Auria dichiara di aderire al progetto «Seconda vita digitale» presentato da [ente capofila] nell'ambito di [nome del bando], "
    "impegnandosi a svolgere le seguenti attività: [rigenerazione di n computer; n ore di formazione; installazione dei programmi didattici; materiali formativi].")
par("Dichiara inoltre che i programmi utilizzati sono liberi e gratuiti (codice MIT, contenuti Creative Commons) e resteranno a disposizione dell'ente "
    "anche dopo la conclusione del progetto, senza costi di licenza.")
par("In fede,")
par("Danilo D'Auria · danilodauria.site@gmail.com · danilodauria.github.io")
par("\n_______________________________\n(firma)")

for s in doc.sections:
    f = s.footer.paragraphs[0]; f.text = "Kit per i bandi · Danilo D'Auria · danilodauria.github.io · CC BY-NC-SA 4.0 · modello da adattare"
    f.runs[0].font.size = Pt(8); f.runs[0].font.color.rgb = INK2

docx = os.path.join(OUT, NOME + ".docx")
doc.save(docx)
print("Word:", docx)
try:
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", OUT, docx], check=True, capture_output=True, timeout=180)
    print("PDF:", os.path.join(OUT, NOME + ".pdf"))
except Exception as e:
    print("PDF non creato (serve LibreOffice):", e)
