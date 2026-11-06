"""Scrive pdf/info.json con il numero di pagine dei PDF: il sito lo legge e mostra sempre il numero giusto.
Uso: python3 strumenti/pdf/info.py   · Lo esegue GitHub Actions (pdf.yml). Autore: Danilo D'Auria - MIT."""
import json, os
from pypdf import PdfReader
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(REPO, "pdf")
def pagine(nome):
    f = os.path.join(P, nome)
    return len(PdfReader(f).pages) if os.path.exists(f) else None
info = {"profilo": pagine("Danilo_DAuria_Tecnologia_Gentile.pdf"), "volantino": pagine("Danilo_DAuria_volantino.pdf"),
        "biglietti": pagine("Danilo_DAuria_biglietti.pdf"), "kit": pagine("Kit_bandi_Danilo_DAuria.pdf")}
f = os.path.join(P, "info.json")
if not os.path.exists(f) or json.load(open(f)) != info:
    json.dump(info, open(f, "w"), indent=1)
print("Pagine:", info)
