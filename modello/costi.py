"""Confronto travi + foglio costi (xlsx con formule) per il tavolo da lavoro."""
import json
from collections import Counter
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.comments import Comment
from openpyxl.utils import get_column_letter

KERF, TRIM = 4, 10       # taglio lama, rifilatura testate per barra
W, D, H, T_TOP, RISER = 2000, 800, 740, 40, 250
LEG_H = H - T_TOP

# ------------------------------------------------------------------ opzioni dal fornitore (dati utente)
OPTS = [
    # nome, b (larghezza X gamba), h (profondità Y gamba / altezza traversa), lungh barra, prezzo, KVH?
    ("Trave abete 120×120 – 6 m", 120, 120, 6000, 83.50, False),
    ("Trave abete 120×120 – 4 m", 120, 120, 4000, 55.90, False),
    ("Trave abete 90×90 – 4 m", 90, 90, 4000, 31.90, False),
    ("KVH giuntato 80×120 – 4 m", 80, 120, 4000, 29.90, True),
    ("KVH giuntato 100×120 – 4 m", 100, 120, 4000, 39.90, True),
]

def pieces_for(b, h):
    """distinta pezzi telaio a parità di schema (8 gambe, 3 campate, traverse dello stesso profilo)."""
    free = W - 4 * b                       # luce totale disponibile per le 3 campate
    seat, cass = 700, 500
    rel = max(free - seat - cass, 0)       # la campata ricarica prende il resto
    bays = [cass, seat, rel]
    pcs = [("Gamba", LEG_H, 8), ("Traversa laterale (profondità)", D - 2 * h, 8),
           ("Montante mensola", RISER, 4)]
    long_ = Counter()
    for i, L in enumerate(bays):
        long_[L] += 2                      # sup. + inf. posteriore
        if i == 2: long_[L] += 2           # ricarica: sup. + inf. anteriore
    for L, n in sorted(long_.items(), reverse=True):
        pcs.append((f"Traversa longitudinale {L}", L, n))
    return pcs, bays

def ffd(lengths, stock):
    bars = []
    for L in sorted(lengths, reverse=True):
        for bar in bars:
            if TRIM + sum(bar) + KERF * len(bar) + L <= stock:
                bar.append(L); break
        else:
            bars.append([L])
    return bars

import random
def best_pack(lengths, stock, tries=30000):
    best = ffd(lengths, stock)
    target = -(-(sum(lengths) + (KERF) * len(lengths)) // (stock - TRIM))   # minimo teorico
    s = 0
    while len(best) > target and s < tries:
        rnd = random.Random(s); l = lengths[:]; rnd.shuffle(l); bars = []
        for L in l:
            for bar in bars:
                if TRIM + sum(bar) + KERF * len(bar) + L <= stock:
                    bar.append(L); break
            else:
                bars.append([L])
        if len(bars) < len(best): best = bars
        s += 1
    # tra le soluzioni con lo stesso numero di barre, preferisci avanzi distribuiti (massimo avanzo minimo)
    def slack(bs): return min(stock - TRIM - sum(b) - KERF * len(b) for b in bs)
    for s2 in range(tries):
        rnd = random.Random(10**6 + s2); l = lengths[:]; rnd.shuffle(l); bars = []
        for L in l:
            for bar in bars:
                if TRIM + sum(bar) + KERF * len(bar) + L <= stock:
                    bar.append(L); break
            else:
                bars.append([L])
        if len(bars) == len(best) and slack(bars) > slack(best): best = bars
    return [sorted(b, reverse=True) for b in sorted(best, key=lambda b: -max(b))]

results = []
for name, b, h, stock, price, kvh in OPTS:
    pcs, bays = pieces_for(b, h)
    lens = [L for _, L, n in pcs for _ in range(n)]
    bars = best_pack(lens, stock)
    I_rel = (b * h ** 3) / (80 * 80 ** 3)   # rigidezza gamba avanti-indietro vs 8×8 iniziale
    results.append(dict(name=name, b=b, h=h, stock=stock, price=price, kvh=kvh, pcs=pcs, bays=bays,
                        need_mm=sum(lens), bars=bars, I_rel=I_rel))

# distinta reale dal modello KVH 80×120
mk = json.load(open("parts_kvh.json"))
beam_parts = [p for p in mk["parts"] if p["group"].startswith("Travi KVH")]
def plen(p):
    x0, y0, z0, x1, y1, z1 = p["box"]; return round(max(x1 - x0, y1 - y0, z1 - z0))
ROLE = {"gamba": "Gamba", "trav-lat": "Traversa laterale (profondità)", "trav-long": "Traversa longitudinale",
        "montante": "Montante mensola"}
kvh_rows = Counter((ROLE[p["role"]], plen(p)) for p in beam_parts)
kvh_lens = [plen(p) for p in beam_parts]
kvh_bars = best_pack(kvh_lens, 4000)
sel = next(r for r in results if r["name"].startswith("KVH giuntato 80"))
assert sorted(kvh_lens) == sorted(L for _, L, n in sel["pcs"] for _ in range(n)), "distinta modello ≠ confronto"

# ------------------------------------------------------------------ workbook
F = "Arial"
BLUE, GREEN = Font(name=F, color="0000FF"), Font(name=F, color="008000")
NORM, BOLD = Font(name=F), Font(name=F, bold=True)
H1 = Font(name=F, bold=True, size=14)
HEAD_FILL = PatternFill("solid", fgColor="E9DFCC")
YEL = PatternFill("solid", fgColor="FFF2A8")
SEL = PatternFill("solid", fgColor="DCEBD6")
thin = Side(style="thin", color="BBBBBB")
BOX = Border(top=thin, bottom=thin, left=thin, right=thin)
EUR = '#,##0.00 "€";-#,##0.00 "€";"-"'
EURM = '#,##0.00 "€/m"'

wb = Workbook()

def header(ws, row, cols, widths=None):
    for j, c in enumerate(cols, 1):
        cell = ws.cell(row=row, column=j, value=c)
        cell.font = BOLD; cell.fill = HEAD_FILL; cell.border = BOX
        cell.alignment = Alignment(wrap_text=True, vertical="center")
    if widths:
        for j, w_ in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(j)].width = w_

def setc(ws, ref, value, font=NORM, fmt=None, fill=None, border=True, wrap=False):
    c = ws[ref]; c.value = value; c.font = font
    if fmt: c.number_format = fmt
    if fill: c.fill = fill
    if border: c.border = BOX
    c.alignment = Alignment(wrap_text=wrap, vertical="center")
    return c

# ---------------- Foglio 1: Confronto travi
ws = wb.active; ws.title = "Confronto travi"
ws["A1"] = "Confronto travi per il telaio"; ws["A1"].font = H1
ws["A2"] = ("Stesso schema per tutte: 8 gambe, 3 campate (cassetti 500 · seduta 700 · ricarica = il resto), "
            "traverse dello stesso profilo, 4 montanti mensola. Taglio 4 mm + 10 mm di rifilatura per barra.")
ws["A2"].font = Font(name=F, italic=True, color="555555")
cols = ["Trave", "Sezione b×h (mm)", "Lungh. barra (m)", "Prezzo barra", "Prezzo al metro", "Sezione (cm²)",
        "Rigidezza gamba avanti-indietro (8×8 = 1)", "Metri necessari", "Barre necessarie",
        "Costo telaio", "Sfrido (m)", "Campata ricarica (mm)", "Essiccato / classificato", "Valutazione"]
header(ws, 4, cols, [30, 13, 11, 12, 13, 11, 18, 12, 11, 13, 10, 13, 22, 62])
ws.row_dimensions[4].height = 45
notes = {
    "Trave abete 120×120 – 6 m": "Molto robusta ma sovradimensionata: costa ~1,9× il KVH al metro, pesa il doppio e le gambe larghe 12 cm riducono la campata ricarica a 320 mm. Barre da 6 m difficili da trasportare.",
    "Trave abete 120×120 – 4 m": "Come sopra, senza il problema del trasporto ma con più sfrido.",
    "Trave abete 90×90 – 4 m": "Costa più del KVH 80×120 al metro con meno legno e meno rigidezza. Se non è essiccata in forno tende a fessurarsi e svergolare dopo il taglio.",
    "KVH giuntato 80×120 – 4 m": "SCELTA: il prezzo al metro più basso, la sezione più adatta (lato da 120 dove spingono le presse), legno essiccato al 15% e piallato: resta dritto. Le misure del progetto restano quelle concordate.",
    "KVH giuntato 100×120 – 4 m": "Stessa qualità del 80×120 ma +33% di prezzo per una rigidezza in più che qui non serve; le gambe più larghe tolgono 80 mm alla campata ricarica.",
}
r0 = 5
for i, r in enumerate(results):
    row = r0 + i
    setc(ws, f"A{row}", r["name"], BOLD if r["kvh"] and r["b"] == 80 else NORM)
    setc(ws, f"B{row}", f'{r["b"]}×{r["h"]}')
    setc(ws, f"C{row}", r["stock"] / 1000, BLUE, "0.0")
    setc(ws, f"D{row}", r["price"], BLUE, EUR)
    setc(ws, f"E{row}", f"=D{row}/C{row}", NORM, EURM)
    setc(ws, f"F{row}", f"=B{row}" if False else r["b"] * r["h"] / 100, BLUE, "0")
    setc(ws, f"G{row}", round(r["I_rel"], 2), BLUE, "0.0")
    setc(ws, f"H{row}", r["need_mm"] / 1000, BLUE, "0.00")
    setc(ws, f"I{row}", len(r["bars"]), BLUE, "0")
    setc(ws, f"J{row}", f"=I{row}*D{row}", NORM, EUR)
    setc(ws, f"K{row}", f"=I{row}*C{row}-H{row}", NORM, "0.00")
    setc(ws, f"L{row}", r["bays"][2], BLUE, "0")
    setc(ws, f"M{row}", "Sì – KVH, C24, umidità 15±3%" if r["kvh"] else "Da verificare col rivenditore")
    setc(ws, f"N{row}", notes[r["name"]], wrap=True)
    ws.row_dimensions[row].height = 48
    if r["kvh"] and r["b"] == 80:
        for j in range(1, 15): ws.cell(row=row, column=j).fill = SEL
last = r0 + len(results) - 1
ws[f"I{r0}"].comment = Comment("Barre calcolate con ottimizzazione First-Fit-Decreasing sui pezzi dello schema "
                               "(vedi foglio 'Taglio travi' per l'opzione scelta).", "Claude")
ws[f"G{r0}"].comment = Comment("Rapporto b·h³ rispetto alla gamba 8×8 della prima versione: misura quanto la "
                               "gamba resiste a flettersi avanti-indietro (la direzione della leva delle presse).", "Claude")
n = last + 2
ws[f"A{n}"] = "Legenda"; ws[f"A{n}"].font = BOLD
ws[f"A{n+1}"] = "Testo blu = dato modificabile (prezzi e lunghezze forniti da te, quantità dall'ottimizzazione). Testo nero = formula."
ws[f"A{n+2}"] = "Riga verde = trave scelta per il progetto."
for k in (n + 1, n + 2): ws[f"A{k}"].font = Font(name=F, color="555555")
ws.freeze_panes = "B5"

# ---------------- Foglio 2: Distinta costi
wc = wb.create_sheet("Distinta costi")
wc["A1"] = "Distinta e costi – tavolo in KVH 80×120"; wc["A1"].font = H1
wc["A2"] = ("Celle gialle = prezzo stimato da verificare: sostituiscilo con il prezzo reale e i totali si aggiornano. "
            "Prezzi senza giallo = forniti da te.")
wc["A2"].font = Font(name=F, italic=True, color="555555")
header(wc, 4, ["Categoria", "Articolo", "Uso", "Q.tà", "Unità", "Prezzo unitario", "Totale", "Fonte prezzo"],
       [16, 46, 46, 8, 8, 14, 13, 22])
sel_row = r0 + [i for i, r in enumerate(results) if r["kvh"] and r["b"] == 80][0]
pan_cnt = Counter()
items = [
    ("Legno", "Trave KVH giuntato 80×120, barra 4 m", "gambe, traverse, montanti mensola (schema senza margine: +1 barra se temi errori di taglio)",
     f"='Confronto travi'!I{sel_row}", "pz", f"='Confronto travi'!D{sel_row}", "fornito", True),
    ("Legno", "Tavola abete lamellare 2000×800×40", "pannello 1: piano di lavoro (intero, senza tagli)",
     1, "pz", 79.00, "fornito", False),
    ("Legno", "Tavola abete lamellare 2000×800×40", "pannello 2: mensola, rinforzo ricarica, 2 ripiani bassi",
     1, "pz", 79.00, "fornito", False),
    ("Legno", "Multistrato pioppo 18 mm, pannello 2500×1250", "cassettiera, frontali, ripiano posteriore seduta",
     1, "pz", 60.00, "stima", False),
    ("Legno", "Multistrato 15 mm, mezzo pannello 1250×1250", "scatole dei 4 cassetti", 1, "pz", 35.00, "stima", False),
    ("Legno", "HDF 4 mm, mezzo pannello", "fondi cassetti, schienale cassettiera", 1, "pz", 10.00, "stima", False),
    ("Legno", "Listello abete 30×40, barra 2,4 m", "reggiripiano (4 × 560 + 2 × 300)", 2, "pz", 5.00, "stima", False),
    ("Ferramenta telaio", "Bullone TCEI M10×180 + rondella Ø20 (B1)", "traverse laterali, 16 testate",
     16, "pz", 1.20, "stima", False),
    ("Ferramenta telaio", "Bullone TCEI M10×140 + rondella Ø20 (B2)", "traverse longitudinali sulle gambe con una sola traversa",
     8, "pz", 1.00, "stima", False),
    ("Ferramenta telaio", "Dado a tamburo M10 (D)", "32 testate di traversa + 4 mensola", 36, "pz", 0.80, "stima", False),
    ("Ferramenta telaio", "Barra filettata M10 da 1 m (R, M) + 4 dadi ciechi + 4 rondelle", "4 spezzoni 220 (gambe centrali) + 4 spezzoni 400 (mensola)",
     3, "pz", 3.50, "stima", False),
    ("Ferramenta telaio", "Spine in faggio Ø12×50 (conf. 100)", "2 per nodo, antirotazione", 1, "conf", 6.00, "stima", False),
    ("Ferramenta telaio", "Colla vinilica D3 750 g", "spine, rinforzo, cassetti", 1, "pz", 9.00, "stima", False),
    ("Ferramenta telaio", "Inserto filettato M10 + piedino livellatore", "base gambe", 8, "pz", 3.00, "stima", False),
    ("Ferramenta telaio", "Squadrette fissaggio piano", "piano su traverse", 16, "pz", 0.60, "stima", False),
    ("Ferramenta telaio", "Viti assortite (5×60, 5×70, 4×45, 4×50, 3,5×30, 4,5×25)", "rinforzo, listelli, cassettiera, squadrette", 1, "set", 20.00, "stima", False),
    ("Ferramenta telaio", "Angolare a L 100×100 + tassello Ø10", "fissaggio a muro", 4, "pz", 4.00, "stima", False),
    ("Zona ricarica", "Piastre acciaio tagliate e forate (base 180×180×12, contropiastra 220×220×6, 3 piastre 180×180×10)",
     "attacco presse e morsa", 1, "lotto", 90.00, "stima", False),
    ("Zona ricarica", "Viti TSPEI M10×110 + rondella larga + dado autobloccante", "base attacco, 2 posteriori (contropiastra)", 2, "set", 1.50, "stima", False),
    ("Zona ricarica", "Viti TSPEI M10×200 + rondella larga + dado autobloccante", "base attacco, 2 anteriori (attraversano la traversa)", 2, "set", 2.00, "stima", False),
    ("Zona ricarica", "Manopole a stella M12 + 2 spine Ø10 h8", "bloccaggio piastre", 1, "kit", 10.00, "stima", False),
    ("Cassetti", "Guide a sfera estrazione totale 500 mm (coppia)", "3 cassettiera + 1 appeso", 4, "cp", 12.00, "stima", False),
    ("Cassetti", "Maniglie", "", 4, "pz", 4.00, "stima", False),
    ("Elettrico", "Canalina passacavi sottoscrivania", "una per campata", 3, "pz", 15.00, "stima", False),
    ("Elettrico", "Passacavi Ø60 da incasso", "piano", 2, "pz", 4.00, "stima", False),
    ("Elettrico", "Ciabatta 6 prese con interruttore", "campata seduta", 1, "pz", 20.00, "stima", False),
    ("Finitura", "Olio/impregnante per legno 750 ml + abrasivi", "piano e telaio", 1, "set", 30.00, "stima", False),
]
row = 5
for cat, art, use, q, u, pr, src, linked in items:
    setc(wc, f"A{row}", cat); setc(wc, f"B{row}", art, wrap=True); setc(wc, f"C{row}", use, wrap=True)
    setc(wc, f"D{row}", q, GREEN if linked else BLUE, "0")
    setc(wc, f"E{row}", u)
    setc(wc, f"F{row}", pr, GREEN if linked else BLUE, EUR, fill=YEL if src == "stima" else None)
    setc(wc, f"G{row}", f"=D{row}*F{row}", NORM, EUR)
    setc(wc, f"H{row}", "fornito da te" if src == "fornito" else "stima – da verificare")
    row += 1
first, lastr = 5, row - 1
row += 1
def total(label, formula, bold=False):
    global row
    setc(wc, f"F{row}", label, BOLD if bold else NORM, border=False)
    setc(wc, f"G{row}", formula, BOLD if bold else NORM, EUR)
    row += 1
total("Prezzi forniti", f'=SUMIFS(G{first}:G{lastr},H{first}:H{lastr},"fornito da te")')
total("Stime", f'=SUMIFS(G{first}:G{lastr},H{first}:H{lastr},"stima – da verificare")')
total("TOTALE", f"=SUM(G{first}:G{lastr})", True)
row += 1
for cat in ["Legno", "Ferramenta telaio", "Zona ricarica", "Cassetti", "Elettrico", "Finitura"]:
    total(f"di cui {cat.lower()}", f'=SUMIFS(G{first}:G{lastr},A{first}:A{lastr},"{cat}")')
row += 1
wc[f"A{row}"] = ("Prezzo travi e lamellare: forniti da te. Tutte le altre voci sono stime di prezzo medio al dettaglio, "
                 "da sostituire con preventivi reali; le piastre d'acciaio dipendono molto dall'officina.")
wc[f"A{row}"].font = Font(name=F, italic=True, color="555555")
wc.freeze_panes = "A5"
wc.column_dimensions["F"].width = 18

# ---------------- Foglio 3: Taglio travi
wt = wb.create_sheet("Taglio travi")
wt["A1"] = "Taglio travi KVH 80×120 (barre da 4 m)"; wt["A1"].font = H1
header(wt, 3, ["Pezzo", "Lunghezza (mm)", "Q.tà", "Totale (mm)"], [36, 15, 8, 14])
row = 4
for (k, L), q in sorted(kvh_rows.items(), key=lambda kv: (-kv[0][1])):
    setc(wt, f"A{row}", k); setc(wt, f"B{row}", L, BLUE, "0"); setc(wt, f"C{row}", q, BLUE, "0")
    setc(wt, f"D{row}", f"=B{row}*C{row}", NORM, "#,##0"); row += 1
setc(wt, f"A{row}", "TOTALE", BOLD); setc(wt, f"C{row}", f"=SUM(C4:C{row-1})", BOLD, "0")
setc(wt, f"D{row}", f"=SUM(D4:D{row-1})", BOLD, "#,##0")
row += 2
header_row = row
for j, c in enumerate(["Barra", "Tagli (mm, nell'ordine)", "Usato (mm)", "Avanzo (mm)"], 1):
    cell = wt.cell(row=row, column=j, value=c); cell.font = BOLD; cell.fill = HEAD_FILL; cell.border = BOX
row += 1
for i, bar in enumerate(kvh_bars, 1):
    used = sum(bar) + KERF * len(bar) + TRIM
    setc(wt, f"A{row}", f"Barra {i}"); setc(wt, f"B{row}", " + ".join(map(str, bar)))
    setc(wt, f"C{row}", used, BLUE, "#,##0"); setc(wt, f"D{row}", f"=4000-C{row}", NORM, "#,##0"); row += 1
wt.column_dimensions["B"].width = 46
row += 1
wt[f"A{row}"] = (f"Utilizzati: taglio {KERF} mm e {TRIM} mm di rifilatura testate per barra. "
                 "Lo schema usa 4 barre con pochi cm di avanzo: misura e taglia con attenzione, oppure prendi una barra in più come scorta. "
                 "Se il rivenditore taglia a misura, porta questa lista: i pezzi sono facili da trasportare.")
wt[f"A{row}"].font = Font(name=F, italic=True, color="555555")
row += 2
wt[f"A{row}"] = "Pannello lamellare 2 (2000×800×40) – schema di taglio"; wt[f"A{row}"].font = BOLD; row += 1
for txt in ["1. Striscia 2000×260 → mensola rialzata",
            "2. Dalla striscia restante (2000×536): rinforzo ricarica 480×520",
            "3. Ripiano basso cassetti 560×500 (560 lungo la tavola)",
            "4. Ripiano basso ricarica 560×480 (560 lungo la tavola)",
            "Avanzo ≈ 390×536: tienilo per riparazioni o una mensolina."]:
    wt[f"A{row}"] = txt; wt[f"A{row}"].font = NORM; row += 1

wb.save("tavolo_costi.xlsx")
json.dump(dict(results=[{k: v for k, v in r.items() if k != "pcs"} for r in results],
               kvh_bars=kvh_bars, kvh_rows=[[k, L, q] for (k, L), q in kvh_rows.items()]),
          open("confronto.json", "w"), indent=1)
for r in results:
    print(f'{r["name"]:30s} {r["price"]/(r["stock"]/1000):6.2f} €/m  barre {len(r["bars"])}  '
          f'telaio {len(r["bars"])*r["price"]:7.2f} €  rig {r["I_rel"]:.1f}  ricarica {r["bays"][2]}')
print("KVH barre modello:", kvh_bars)
