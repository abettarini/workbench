"""Fogli costi separati: tavolo base, cassettiera, alzatina (xlsx con formule)."""
import json
from collections import Counter
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.comments import Comment
from openpyxl.utils import get_column_letter

F = "Arial"
BLUE, GREEN, NORM, BOLD = Font(name=F, color="0000FF"), Font(name=F, color="008000"), Font(name=F), Font(name=F, bold=True)
H1, NOTE = Font(name=F, bold=True, size=14), Font(name=F, italic=True, color="555555")
HEAD_FILL, YEL, SEL = PatternFill("solid", fgColor="E9DFCC"), PatternFill("solid", fgColor="FFF2A8"), PatternFill("solid", fgColor="DCEBD6")
thin = Side(style="thin", color="BBBBBB"); BOX = Border(top=thin, bottom=thin, left=thin, right=thin)
EUR = '#,##0.00 "€";-#,##0.00 "€";"-"'
EURM = '#,##0.00 "€/m"'

d = json.load(open("parts_kvh.json")); cf = json.load(open("confronto.json"))
parts = d["parts"]

def setc(ws, ref, value, font=NORM, fmt=None, fill=None, wrap=False, border=True):
    c = ws[ref]; c.value = value; c.font = font
    if fmt: c.number_format = fmt
    if fill: c.fill = fill
    if border: c.border = BOX
    c.alignment = Alignment(wrap_text=wrap, vertical="center")
    return c

def header(ws, row, cols, widths):
    for j, (c, w) in enumerate(zip(cols, widths), 1):
        cell = ws.cell(row=row, column=j, value=c); cell.font = BOLD; cell.fill = HEAD_FILL; cell.border = BOX
        cell.alignment = Alignment(wrap_text=True, vertical="center")
        ws.column_dimensions[get_column_letter(j)].width = w

def distinta(ws, title, subtitle, items, cats, foot):
    """items: (categoria, articolo, uso, qtà, unità, prezzo|formula, fonte, collegato)"""
    ws["A1"] = title; ws["A1"].font = H1
    ws["A2"] = subtitle; ws["A2"].font = NOTE
    header(ws, 4, ["Categoria", "Articolo", "Uso", "Q.tà", "Unità", "Prezzo unitario", "Totale", "Fonte prezzo"],
           [16, 48, 46, 8, 8, 15, 13, 26])
    r = 5
    for cat, art, use, q, u, pr, src, linked in items:
        setc(ws, f"A{r}", cat); setc(ws, f"B{r}", art, wrap=True); setc(ws, f"C{r}", use, wrap=True)
        setc(ws, f"D{r}", q, GREEN if linked else BLUE, "0")
        setc(ws, f"E{r}", u)
        setc(ws, f"F{r}", pr, GREEN if linked else BLUE, EUR, fill=YEL if src == "stima" else None)
        setc(ws, f"G{r}", f"=D{r}*F{r}", NORM, EUR)
        setc(ws, f"H{r}", {"fornito": "fornito da te", "obi": "OBI, verificato 18/10/2026",
                           "stima": "stima – da verificare", "base": "incluso nel tavolo base"}[src], wrap=True)
        ws.row_dimensions[r].height = 30
        r += 1
    first, last = 5, r - 1; r += 1
    def tot(label, formula, bold=False):
        nonlocal r
        setc(ws, f"F{r}", label, BOLD if bold else NORM, border=False); setc(ws, f"G{r}", formula, BOLD if bold else NORM, EUR); r += 1
    tot("Prezzi verificati", f'=SUMIFS(G{first}:G{last},H{first}:H{last},"fornito da te")+SUMIFS(G{first}:G{last},H{first}:H{last},"OBI, verificato 18/10/2026")')
    tot("Stime", f'=SUMIFS(G{first}:G{last},H{first}:H{last},"stima – da verificare")')
    tot("TOTALE", f"=SUM(G{first}:G{last})", True)
    r += 1
    for c in cats: tot(f"di cui {c.lower()}", f'=SUMIFS(G{first}:G{last},A{first}:A{last},"{c}")')
    r += 1
    for line in foot:
        ws[f"A{r}"] = line; ws[f"A{r}"].font = NOTE; r += 1
    ws.freeze_panes = "A5"
    return f"G{last + 4}"

def dims(p):
    x0, y0, z0, x1, y1, z1 = p["box"]; return sorted([round(x1 - x0), round(y1 - y0), round(z1 - z0)], reverse=True)

# ============================================================== 1. TAVOLO BASE
wb = Workbook(); ws = wb.active; ws.title = "Distinta costi"
OSB = 31.49
base_items = [
    ("Legno", "Trave KVH giuntato 80×120, barra 4 m", "gambe, traverse e i 4 montanti dell'alzatina (schema senza scorta)",
     "='Confronto travi'!I8", "pz", "='Confronto travi'!D8", "fornito", True),
    ("Legno", "Tavola abete lamellare 2000×800×40", "piano di lavoro (intero)", 1, "pz", 79.00, "fornito", False),
    ("Legno", "Pannello OSB/3 2500×1250×18", "3 ripiani bassi + rinforzo ricarica (2 strati)", 1, "pz", OSB, "obi", False),
    ("Legno", "Listello abete 30×40, barra 2,4 m", "reggiripiano: 4 × 560 + 2 × 260", 2, "pz", 5.00, "stima", False),
    ("Ferramenta telaio", "Bullone TCEI M10×180 + rondella Ø20 (B1)", "traverse laterali", 16, "pz", 1.20, "stima", False),
    ("Ferramenta telaio", "Bullone TCEI M10×140 + rondella Ø20 (B2)", "traverse longitudinali, gambe d'estremità", 8, "pz", 1.00, "stima", False),
    ("Ferramenta telaio", "Dado a tamburo M10 (D)", "32 nodi + 4 predisposizione alzatina", 36, "pz", 0.80, "stima", False),
    ("Ferramenta telaio", "Barra filettata M10 da 1 m (R)", "4 spezzoni da 220 per le gambe centrali", 1, "pz", 3.50, "stima", False),
    ("Ferramenta telaio", "Spine in faggio Ø12×50 (conf. 100)", "2 per nodo", 1, "conf", 6.00, "stima", False),
    ("Ferramenta telaio", "Colla vinilica D3 750 g", "spine, rinforzo, listelli", 1, "pz", 9.00, "stima", False),
    ("Ferramenta telaio", "Inserto filettato M10 + piedino livellatore", "sotto le gambe", 8, "pz", 3.00, "stima", False),
    ("Ferramenta telaio", "Squadrette con asola + viti", "fissaggio del piano", 16, "pz", 0.60, "stima", False),
    ("Ferramenta telaio", "Viti assortite (5×60, 5×70, 4×50, 4,5×25)", "rinforzo, listelli, ripiani, squadrette", 1, "set", 15.00, "stima", False),
    ("Ferramenta telaio", "Angolare a L 100×100 + tassello Ø8", "fissaggio a muro (G1P e G4P)", 4, "pz", 4.00, "stima", False),
    ("Zona ricarica", "Piastre acciaio tagliate e forate (base 180×180×12, contropiastra 220×220×6, 3 piastre attrezzo)",
     "attacco presse e morsa", 1, "lotto", 90.00, "stima", False),
    ("Zona ricarica", "Viti TSPEI M10×110 + rondella larga + dado autobloccante", "base, 2 posteriori", 2, "set", 1.50, "stima", False),
    ("Zona ricarica", "Viti TSPEI M10×200 + rondella larga + dado autobloccante", "base, 2 anteriori", 2, "set", 2.00, "stima", False),
    ("Zona ricarica", "Manopole a stella M12 + 2 spine Ø10 h8", "bloccaggio piastre", 1, "kit", 10.00, "stima", False),
    ("Elettrico", "Canalina passacavi sottoscrivania", "una per campata", 3, "pz", 15.00, "stima", False),
    ("Elettrico", "Passacavi Ø60 da incasso", "piano", 2, "pz", 4.00, "stima", False),
    ("Elettrico", "Ciabatta 6 prese con interruttore", "campata seduta", 1, "pz", 20.00, "stima", False),
    ("Finitura", "Olio/impregnante 750 ml + abrasivi", "telaio e piano; vernice trasparente per l'OSB", 1, "set", 30.00, "stima", False),
]
distinta(ws, "Modulo 1 – Tavolo base: distinta e costi",
         "Celle gialle = stime da sostituire con i prezzi reali. Testo blu = dato modificabile, verde = collegato a un altro foglio.",
         base_items, ["Legno", "Ferramenta telaio", "Zona ricarica", "Elettrico", "Finitura"],
         ["Travi e lamellare: prezzi forniti da te. OSB/3 18: prezzo OBI verificato il 18/10/2026. Il resto sono stime.",
          "I 4 dadi a tamburo della predisposizione vanno inseriti durante il montaggio: con il tavolo a muro non si raggiungono."])

# --- confronto travi
wt = wb.create_sheet("Confronto travi")
wt["A1"] = "Confronto travi per il telaio"; wt["A1"].font = H1
header(wt, 4, ["Trave", "Sezione", "Lungh. barra (m)", "Prezzo barra", "Prezzo al metro", "Metri necessari", "Rigidezza gamba (8×8=1)",
               "", "Barre necessarie", "Costo telaio"], [30, 11, 11, 12, 13, 12, 14, 2, 11, 13])
for i, r in enumerate(cf["results"]):
    row = 5 + i
    setc(wt, f"A{row}", r["name"], BOLD if r["kvh"] and r["b"] == 80 else NORM)
    setc(wt, f"B{row}", f'{r["b"]}×{r["h"]}'); setc(wt, f"C{row}", r["stock"] / 1000, BLUE, "0.0")
    setc(wt, f"D{row}", r["price"], BLUE, EUR); setc(wt, f"E{row}", f"=D{row}/C{row}", NORM, EURM)
    setc(wt, f"F{row}", r["need_mm"] / 1000, BLUE, "0.00"); setc(wt, f"G{row}", round(r["I_rel"], 1), BLUE, "0.0")
    setc(wt, f"I{row}", len(r["bars"]), BLUE, "0"); setc(wt, f"J{row}", f"=I{row}*D{row}", NORM, EUR)
    if r["kvh"] and r["b"] == 80:
        for j in range(1, 11): wt.cell(row=row, column=j).fill = SEL
assert cf["results"][3]["name"].startswith("KVH giuntato 80"), "riga 8 deve essere il KVH 80×120"
wt["A11"] = "Riga verde = trave scelta. Barre calcolate con ottimizzazione del taglio (foglio 'Taglio travi')."; wt["A11"].font = NOTE

# --- confronto ripiani
wr = wb.create_sheet("Confronto ripiani")
wr["A1"] = "Ripiani bassi e rinforzo ricarica: tre materiali a confronto"; wr["A1"].font = H1
wr["A2"] = "Servono: ripiano cassetti 500×560, ripiano ricarica 480×560, ripiano seduta 700×260, rinforzo 480×520 (spessore ≥ 36)."; wr["A2"].font = NOTE
header(wr, 4, ["Materiale", "Formato", "Spessore ripiani", "Pezzi necessari", "Prezzo unitario", "Costo", "Fonte", "Note"],
       [32, 18, 12, 12, 14, 12, 24, 60])
opts = [("OSB/3 18 (SCELTO)", "2500×1250", "18 mm", 1, OSB, "OBI, verificato 18/10/2026",
         "Un pannello per tutto: 3 ripiani + rinforzo in 2 strati (36 mm). Avanzano ~1,8 m² (utili anche per la cassettiera)."),
        ("Lamellare abete 40", "2000×800", "40 mm", 1, 79.00, "fornito da te",
         "Un pannello per tutto, ripiani più spessi e belli; costa 2,5 volte l'OSB."),
        ("Tavola OBI lamellare 14", "800×200", "14 mm", 14, 8.19, "OBI, verificato 18/10/2026",
         "8 tavole per i ripiani (3 + 3 + 2, una tagliata in larghezza) + 6 per il rinforzo in 2 strati da 28 mm. La più cara e la più sottile.")]
for i, (m, fmt, sp, q, pr, src, note) in enumerate(opts):
    row = 5 + i
    setc(wr, f"A{row}", m, BOLD if i == 0 else NORM); setc(wr, f"B{row}", fmt); setc(wr, f"C{row}", sp)
    setc(wr, f"D{row}", q, BLUE, "0"); setc(wr, f"E{row}", pr, BLUE, EUR); setc(wr, f"F{row}", f"=D{row}*E{row}", NORM, EUR)
    setc(wr, f"G{row}", src, wrap=True); setc(wr, f"H{row}", note, wrap=True); wr.row_dimensions[row].height = 45
    if i == 0:
        for j in range(1, 9): wr.cell(row=row, column=j).fill = SEL
wr["A9"] = "Costo al m²: OSB 18 ≈ 10 €/m² · lamellare 40 ≈ 49 €/m² · tavola OBI 14 ≈ 51 €/m²."; wr["A9"].font = NOTE

# --- taglio travi
wc = wb.create_sheet("Taglio travi")
wc["A1"] = "Taglio travi KVH 80×120 (barre da 4 m)"; wc["A1"].font = H1
header(wc, 3, ["Barra", "Tagli (mm)", "Usato (mm)", "Avanzo (mm)"], [10, 52, 12, 12])
for i, bar in enumerate(cf["kvh_bars"], 1):
    row = 3 + i
    setc(wc, f"A{row}", f"Barra {i}"); setc(wc, f"B{row}", " + ".join(map(str, bar)))
    setc(wc, f"C{row}", sum(bar) + 4 * len(bar) + 10, BLUE, "#,##0"); setc(wc, f"D{row}", f"=4000-C{row}", NORM, "#,##0")
wc["A9"] = "I 4 pezzi da 250 sono i montanti dell'alzatina: tagliali e conservali anche se l'alzatina la farai dopo."; wc["A9"].font = NOTE
wb.save("tavolo_base_costi.xlsx")

# ============================================================== 2. CASSETTIERA
cas = [p for p in parts if p["module"] == "cassettiera"]
pieces = {"multistrato 18": [], "multistrato 15": [], "HDF 4": []}
for p in cas:
    a, b, c = dims(p)
    if "(scatola)" in p["name"]:
        x0, y0, z0, x1, y1, z1 = p["box"]; wd, l, h = round(x1 - x0, 1), round(y1 - y0), round(z1 - z0)
        tag = "appeso" if "appeso" in p["name"] else p["name"].split(" (")[0].lower()
        pieces["multistrato 15"] += [(f"{tag}: fianco", l, h)] * 2 + [(f"{tag}: testata", round(wd - 30), h)] * 2
        pieces["HDF 4"] += [(f"{tag}: fondo", l, round(wd))]
    else:
        pieces[p["mat"]].append((p["name"], a, b))
json.dump(pieces, open("cassettiera_pezzi.json", "w"), indent=1)
wb = Workbook(); ws = wb.active; ws.title = "Distinta costi"
cas_items = [
    ("Legno", "Multistrato pioppo 18 mm, mezzo pannello 1250×1250", "scatola, frontali (taglio a pag. 'Taglio pannelli')", 1, "pz", 35.00, "stima", False),
    ("Legno", "Multistrato pioppo 15 mm, mezzo pannello 1250×1250", "scatole dei 4 cassetti", 1, "pz", 30.00, "stima", False),
    ("Legno", "HDF 4 mm, pannello 2500×1250", "fondi cassetti e schienale", 1, "pz", 15.00, "stima", False),
    ("Ferramenta", "Guide a sfera estrazione totale 500 mm (coppia)", "3 cassettiera + 1 appeso", 4, "cp", 12.00, "stima", False),
    ("Ferramenta", "Maniglie", "", 4, "pz", 4.00, "stima", False),
    ("Ferramenta", "Viti 4×45 (conf.)", "scatola cassettiera", 1, "conf", 4.00, "stima", False),
    ("Ferramenta", "Viti 3,5×30, 3,5×25, 3×16, 4×16, 4×30, 4×50 (assortimento)", "cassetti, frontali, guide, fissaggio al tavolo", 1, "set", 8.00, "stima", False),
    ("Ferramenta", "Colla vinilica D3 (quota)", "giunti", 1, "pz", 4.00, "stima", False),
    ("Finitura", "Vernice trasparente o olio 500 ml", "frontali e scatola", 1, "pz", 12.00, "stima", False),
]
distinta(ws, "Modulo 2 – Cassettiera: distinta e costi",
         "Cassettiera fissa per la campata sinistra (3 cassetti) + cassetto appeso sotto il piano. Celle gialle = stime.",
         cas_items, ["Legno", "Ferramenta", "Finitura"],
         ["Alternativa economica: scatola della cassettiera in OSB 18 ricavata dall'avanzo del pannello del tavolo base (0 €).",
          "Molti negozi tagliano il multistrato a misura: porta il foglio 'Taglio pannelli'."])
wp = wb.create_sheet("Taglio pannelli")
wp["A1"] = "Pezzi da tagliare"; wp["A1"].font = H1
header(wp, 3, ["Materiale", "Pezzo", "Lunghezza", "Larghezza", "Q.tà"], [18, 34, 12, 12, 8])
row = 4
for mat, lst in pieces.items():
    for (n, a, b), q in Counter(lst).items():
        setc(wp, f"A{row}", mat); setc(wp, f"B{row}", n); setc(wp, f"C{row}", a, BLUE, "0"); setc(wp, f"D{row}", b, BLUE, "0")
        setc(wp, f"E{row}", q, BLUE, "0"); row += 1
wb.save("cassettiera_costi.xlsx")

# ============================================================== 3. ALZATINA
wb = Workbook(); ws = wb.active; ws.title = "Distinta costi"
alz_items = [
    ("Legno", "Montanti KVH 80×120×250", "tagliati con le travi del tavolo base (barre 3 e 4)", 4, "pz", 0, "base", False),
    ("Legno", "Tavola lamellare abete OBI 800×200×14", "mensola: tagliate a 620, 780 e 600", 3, "pz", 8.19, "obi", False),
    ("Legno", "Listello abete 30×40, barra 2,4 m", "rinforzo sotto il bordo anteriore (2000)", 1, "pz", 5.00, "stima", False),
    ("Ferramenta", "Barra filettata M10 da 1 m", "4 spezzoni da 380", 2, "pz", 3.50, "stima", False),
    ("Ferramenta", "Dado cieco M10 + rondella Ø30", "sopra la mensola", 4, "set", 0.80, "stima", False),
    ("Ferramenta", "Dadi a tamburo M10 nelle gambe posteriori", "già montati con il tavolo base", 4, "pz", 0, "base", False),
    ("Ferramenta", "Viti 4×50 (conf.) + colla", "listello sotto le tavole", 1, "set", 6.00, "stima", False),
    ("Ferramenta", "Angolare a L 100×100 + tassello Ø8", "fissaggio a muro su M1 e M4", 2, "pz", 4.00, "stima", False),
    ("Finitura", "Olio/impregnante (quota)", "mensola e montanti", 1, "pz", 8.00, "stima", False),
]
distinta(ws, "Modulo 3 – Alzatina con mensola: distinta e costi",
         "Si monta sul tavolo base usando le predisposizioni (fori e dadi nelle gambe posteriori). Celle gialle = stime.",
         alz_items, ["Legno", "Ferramenta", "Finitura"],
         ["Se il tavolo base è già montato senza i 4 montanti, servono 1 m di KVH 80×120: una barra da 4 m costa 29,90 €.",
          "Tavole OBI: prezzo verificato il 18/10/2026 (articolo 2423135)."])
wb.save("alzatina_costi.xlsx")
print("ok")
