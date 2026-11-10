"""Dati per Google: dati strutturati (JSON-LD) presi dalla pagina stessa, sitemap.xml e robots.txt.
Uso: python3 strumenti/seo/seo.py [index.html]   · Rilegge listino, domande frequenti e guide, così restano sempre allineati.
Autore: Danilo D'Auria - MIT."""
import html, json, os, re, sys, datetime
QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(QUI))
SITO = "https://danilodauria.github.io/"
LINGUE = ["it", "en", "fr", "es", "de", "ro"]
f = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO, "index.html")
s = open(f, encoding="utf-8").read()

def testo(h):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", h))).strip()

# listino: righe di LISTINO nello script della pagina
listino = []
for nome, pacc in re.findall(r'\w+:\s*\{ nome: "([^"]+)", pacc: \[(.*?)\] \}', s):
    for titolo, prezzo, da in re.findall(r'\["\w+", "([^"]+)", (\d+)(, true)?\]', pacc):
        listino.append((nome, titolo, int(prezzo), bool(da)))
assert listino, "listino non trovato"
offerte = []
for nome, titolo, prezzo, da in listino:
    o = {"@type": "Offer", "name": f"{titolo} ({nome})", "priceCurrency": "EUR",
         "itemOffered": {"@type": "Service", "name": f"{titolo} · {nome}", "provider": {"@id": SITO + "#danilo"}}}
    if da:
        o["priceSpecification"] = {"@type": "PriceSpecification", "minPrice": prezzo, "priceCurrency": "EUR"}
    else:
        o["price"] = prezzo
    offerte.append(o)

faq = []
m = re.search(r'<section class="blocco" id="domande">(.*?)</section>', s, re.S)
for q, a in re.findall(r"<details><summary>(.*?)</summary><p>(.*?)</p></details>", m.group(1), re.S):
    faq.append({"@type": "Question", "name": testo(q), "acceptedAnswer": {"@type": "Answer", "text": testo(a)}})
assert faq, "domande non trovate"

descr = re.search(r'<meta name="description" content="([^"]+)"', s).group(1)
grafo = [
    {"@type": "Person", "@id": SITO + "#danilo", "name": "Danilo D'Auria", "url": SITO,
     "jobTitle": "Tecnico IT e divulgatore digitale per il sociale", "description": html.unescape(descr),
     "knowsLanguage": LINGUE, "sameAs": ["https://github.com/danilodauria"],
     "knowsAbout": ["Rigenerazione di computer", "Linux", "FeniceOS", "Inclusione digitale", "Informatica sostenibile", "Formazione digitale per anziani"]},
    {"@type": "ProfessionalService", "@id": SITO + "#servizi", "name": "Danilo D'Auria · Tecnologia Gentile", "url": SITO,
     "founder": {"@id": SITO + "#danilo"}, "image": SITO + "anteprima.png", "areaServed": {"@type": "Country", "name": "Italia"},
     "description": "Rigenerazione di computer con Linux, Windows e Mac, configurazione di iPhone e iPad, corsi e assistenza. Check-up sempre gratuito.",
     "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Listino della rigenerazione", "itemListElement": offerte}},
    {"@type": "Book", "@id": SITO + "#libro", "name": "Tecnologia Gentile: Informatica Sostenibile", "author": {"@id": SITO + "#danilo"}, "inLanguage": "it"},
    {"@type": "WebSite", "@id": SITO + "#sito", "url": SITO, "name": "Danilo D'Auria", "inLanguage": LINGUE, "publisher": {"@id": SITO + "#danilo"}},
    {"@type": "FAQPage", "@id": SITO + "#domande", "mainEntity": faq},
]
blocco = ('<!--DATI-STRUTTURATI-->\n<script type="application/ld+json">\n'
          + json.dumps({"@context": "https://schema.org", "@graph": grafo}, ensure_ascii=False, indent=1).replace("</", "<\\/")
          + "\n</script>\n<!--/DATI-STRUTTURATI-->")
s2 = re.sub(r"<!--DATI-STRUTTURATI-->(.*?<!--/DATI-STRUTTURATI-->)?", lambda _: blocco, s, count=1, flags=re.S)
assert "<!--/DATI-STRUTTURATI-->" in s2, "segnaposto mancante"
if s2 != s:
    open(f, "w", encoding="utf-8").write(s2)

# sitemap con le versioni nelle altre lingue
oggi = datetime.date.today().isoformat()
def voce(it_url, alt):
    righe = [f"  <url>\n    <loc>{it_url}</loc>\n    <lastmod>{oggi}</lastmod>"]
    for l, u in alt:
        righe.append(f'    <xhtml:link rel="alternate" hreflang="{l}" href="{u}"/>')
    righe.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{it_url}"/>\n  </url>')
    return "\n".join(righe)
urls = []
alt_home = [(l, SITO if l == "it" else SITO + "?lang=" + l) for l in LINGUE]
for l, u in alt_home:
    urls.append(voce(u, alt_home))
elenco = json.load(open(os.path.join(REPO, "guide", "elenco.json"), encoding="utf-8"))
for g in elenco:
    alt = [(l, SITO + ("guide/" if l == "it" else "guide/" + l + "/") + g["id"] + ".html") for l in g.get("lingue", ["it"])]
    for l, u in alt:
        urls.append(voce(u, alt))
for extra in ["pdf/Danilo_DAuria_Tecnologia_Gentile.pdf", "pdf/Kit_bandi_Danilo_DAuria.pdf", "pdf/Danilo_DAuria_volantino.pdf"]:
    if os.path.exists(os.path.join(REPO, extra)):
        urls.append(f"  <url>\n    <loc>{SITO}{extra}</loc>\n    <lastmod>{oggi}</lastmod>\n  </url>")
mappa = ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
         + "\n".join(urls) + "\n</urlset>\n")
fm = os.path.join(REPO, "sitemap.xml")
vecchia = open(fm, encoding="utf-8").read() if os.path.exists(fm) else ""
if re.sub(r"<lastmod>[^<]+</lastmod>", "", vecchia) != re.sub(r"<lastmod>[^<]+</lastmod>", "", mappa):
    open(fm, "w", encoding="utf-8").write(mappa)
open(os.path.join(REPO, "robots.txt"), "w", encoding="utf-8").write(
    "# Questo file chiede ai motori di ricerca di non elencare alcune pagine: non è una serratura.\n"
    "# Su GitHub Pages tutto ciò che sta nel repository è raggiungibile da chi conosce l'indirizzo,\n"
    "# quindi qui dentro non va mai messo niente di privato.\n"
    "# Danilo D'Auria · danilodauria.github.io\nUser-agent: *\nAllow: /\nDisallow: /scheda/\nDisallow: /vista.html\nDisallow: /strumenti/\n\nSitemap: " + SITO + "sitemap.xml\n")
print(f"SEO: {len(offerte)} offerte, {len(faq)} domande, {len(urls)} indirizzi nella sitemap")
