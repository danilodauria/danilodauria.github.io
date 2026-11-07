"""Novità del sito: legge progetti.json e annota nuovi progetti e nuove versioni in novita.json, poi scrive feed.xml (Atom).
Le voci scritte a mano (con "a_mano": true) restano sempre; "nome": true = titolo da non tradurre (nome e versione). Lo esegue GitHub Actions (progetti.yml), dopo aggiorna-progetti.py.
Uso: python3 strumenti/novita.py   · Autore: Danilo D'Auria - MIT."""
import copy, datetime, json, os, html
QUI = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(QUI)
SITO = "https://danilodauria.github.io/"
F = os.path.join(REPO, "novita.json")
MAX = 40
oggi = datetime.date.today().isoformat()
dati = json.load(open(F, encoding="utf-8")) if os.path.exists(F) else {"versioni": {}, "voci": []}
progetti = json.load(open(os.path.join(REPO, "progetti.json"), encoding="utf-8"))["progetti"]
noti, voci = copy.deepcopy(dati.get("versioni", {})), copy.deepcopy(dati.get("voci", []))
prima_volta = not noti
for p in progetti:
    nome, v = p["nome"], p.get("versione") or ""
    quando = p.get("aggiornato") or oggi
    link = p.get("sito") or p.get("github")
    if nome not in noti:
        if not prima_volta:
            voci.append({"data": p.get("creato") or quando, "titolo": p["titolo"], "testo": "Nuovo progetto: un programma libero e gratuito, da provare.", "nome": True, "link": link, "id": nome + "@nuovo"})
        elif v:
            voci.append({"data": quando, "titolo": p["titolo"] + " " + v, "testo": "La versione più recente, con le novità descritte su GitHub.", "nome": True, "link": link, "id": nome + "@" + v})
    elif v and noti[nome] != v:
        voci.append({"data": quando, "titolo": p["titolo"] + " " + v, "testo": "La versione più recente, con le novità descritte su GitHub.", "nome": True, "link": link, "id": nome + "@" + v})
    noti[nome] = v
visti, unici = set(), []
for x in sorted(voci, key=lambda x: (x["data"], x.get("a_mano", False)), reverse=True):
    if x["id"] in visti:
        continue
    visti.add(x["id"]); unici.append(x)
# Una sola voce automatica per progetto, sempre la piu' recente (e quindi all'ultima versione):
# le voci scritte a mano restano tutte, perche' raccontano il sito, non i programmi.
manuali, automatiche, gia_visto = [], [], set()
for x in unici:
    if x.get("a_mano"):
        manuali.append(x)
        continue
    progetto = (x.get("id") or "").split("@")[0]
    if not progetto or progetto in gia_visto:
        continue
    gia_visto.add(progetto)
    automatiche.append(x)
voci = sorted(manuali + automatiche[:MAX], key=lambda x: x["data"], reverse=True)
nuovo = {"versioni": dict(sorted(noti.items())), "voci": voci}
if nuovo != {"versioni": dati.get("versioni", {}), "voci": dati.get("voci", [])}:
    nuovo["aggiornato"] = oggi
    json.dump(nuovo, open(F, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
else:
    nuovo["aggiornato"] = dati.get("aggiornato", oggi)
E = lambda t: html.escape(t or "", quote=True)
righe = ['<?xml version="1.0" encoding="utf-8"?>', '<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="it">',
         "  <title>Novità di Danilo D'Auria</title>", "  <subtitle>Programmi liberi, guide gratuite e servizi del sito danilodauria.github.io</subtitle>",
         f'  <link href="{SITO}"/>', f'  <link rel="self" href="{SITO}feed.xml"/>', f"  <id>{SITO}</id>",
         f"  <updated>{nuovo['aggiornato']}T06:00:00Z</updated>", "  <author><name>Danilo D'Auria</name></author>"]
for x in voci[:30]:
    link = x.get("link") or SITO
    if not link.startswith("http"):
        link = SITO + link.lstrip("/")
    righe += ["  <entry>", f"    <title>{E(x['titolo'])}</title>", f'    <link href="{E(link)}"/>',
              f"    <id>{SITO}#novita-{E(x['id'])}</id>", f"    <updated>{x['data']}T06:00:00Z</updated>",
              f"    <summary>{E(x.get('testo'))}</summary>", "  </entry>"]
righe.append("</feed>")
open(os.path.join(REPO, "feed.xml"), "w", encoding="utf-8").write("\n".join(righe) + "\n")
print(f"Novità: {len(voci)} voci")
