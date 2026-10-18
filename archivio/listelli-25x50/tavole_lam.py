"""Tavole quotate + distinte per la versione in listelli 25x50 laminati -> tavolo_listelli_tavole.pdf"""
import json
from collections import Counter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle, Circle

d = json.load(open("parts_lam.json"))
P, parts, legs, bays, rail_x = d["params"], d["parts"], d["legs"], d["bays"], d["rail_x"]
W, D, H, t, w = P["W"], P["D"], P["H"], P["t"], P["w"]
A4 = (11.69, 8.27)
RED = "#c0392b"

def dims(p):
    x0, y0, z0, x1, y1, z1 = p["box"]
    return sorted([round(x1 - x0), round(y1 - y0), round(z1 - z0)], reverse=True)

# ------------------------------------------------ distinta listelli
ROLE = {"gamba": "Gamba – strato intero", "gamba-spezzone": "Gamba – spezzone strato centrale",
        "trav-lat-tenone": "Traversa laterale – strato tenone (passante)",
        "trav-lat-fianco": "Traversa laterale – 2° strato (tra le gambe)",
        "trav-long": "Traversa longitudinale – strato", "montante": "Montante mensola – strato"}
lam = [p for p in parts if p["group"] == "Listelli 25x50"]
rows = Counter((ROLE[p["role"]], dims(p)[0]) for p in lam)
lam_tab = sorted(rows.items(), key=lambda kv: (list(ROLE.values()).index(kv[0][0]), -kv[0][1]))
pieces = [L for (k, L), n in rows.items() for _ in range(n)]
tot = sum(pieces)

def ffd(pcs, stock, kerf=4):
    bars = []
    for L in sorted(pcs, reverse=True):
        for b in bars:
            if sum(b) + kerf * len(b) + L <= stock:
                b.append(L); break
        else:
            bars.append([L])
    return bars
opt = {st: ffd(pieces, st) for st in (2000, 2400, 3000, 4000)}

# ------------------------------------------------ pannelli
panel_rows = Counter()
for p in parts:
    if p["group"] in ("Pannelli", "Listelli reggiripiano") or (p["group"] == "Cassettiera" and "scatola" not in p["name"]):
        a, b, c = dims(p)
        base = p["name"]
        if p["group"] == "Listelli reggiripiano": base = "Listello reggiripiano"
        if base.startswith("Frontale cassetto ") and "appeso" not in base: base = "Frontale cassetto"
        if base.startswith("Pannello fianco"): base = "Pannello irrigidimento fianco"
        panel_rows[(base, p["mat"], a, b, c)] += 1
for p in parts:
    if "scatola" in p["name"]:
        x0, y0, z0, x1, y1, z1 = p["box"]
        wd, l, h = round(x1 - x0), round(y1 - y0), round(z1 - z0)
        tag = "appeso" if "appeso" in p["name"] else "cassettiera"
        panel_rows[(f"Cassetto {tag}: fianco", "multistrato 15", l, h, 15)] += 2
        panel_rows[(f"Cassetto {tag}: testata", "multistrato 15", wd - 30, h, 15)] += 2
        panel_rows[(f"Cassetto {tag}: fondo", "HDF 4", l, wd, 4)] += 1
panel_tab = sorted(panel_rows.items(), key=lambda kv: (kv[0][1], -kv[0][2]))

# ------------------------------------------------ ferramenta
long_rails = sorted({p["name"].rsplit(" - ", 1)[0] for p in lam if p["role"] == "trav-long"})
n_ends = 2 * len(long_rails)
shared = [n for n in long_rails if "post." in n]          # posteriori: continue su tutte le campate
n_rods = 2 * 2                                             # gambe 2 e 3, traversa sup. e inf. posteriore
n_single = n_ends - 2 * n_rods
n_lat = len({p["name"].rsplit(" - ", 1)[0] for p in lam if p["role"].startswith("trav-lat")})
n_drawers = sum(1 for p in parts if "scatola" in p["name"])
hardware = [
    ("Colla vinilica D3 (laminazione + incastri)", "2–3 kg", "incollare tutti gli strati a piena faccia"),
    ("Viti 4×50 per serraggio strati (oppure morsetti)", "~250", "ogni 15 cm, sfalsate; evitare le zone da forare"),
    ("Dadi a tamburo M8", f"{n_ends}", "uno per estremità di traversa longitudinale"),
    ("Barra filettata M8 (passante nelle gambe centrali)", f"{n_rods}",
     f"L≈{legs[1][1]-legs[1][0]+170:.0f} (gamba 2) e {legs[2][1]-legs[2][0]+170:.0f} (gamba 3) – unisce le traverse dei due lati"),
    ("Viti TCEI M8×150 / M8×180 + rondella", f"{n_single}", "estremità singole; testa incassata sotto i pannelli"),
    ("Spine in faggio Ø10", f"{4 * n_lat}", "2 per tenone passante, trasversali alla gamba, incollate"),
    ("Pannelli: viti 3,5×30 + colla", "~150", "ogni 15 cm su gambe e traverse"),
    ("Barra filettata M10 L≈400 + dado a tamburo + dado cieco", "4", "mensola → montante → piano → gamba post."),
    ("Inserti filettati M10 + piedini livellatori", "8", "base gambe"),
    ("Squadrette fissaggio piano + viti 4,5×30", "16", ""),
    ("Viti 5×70 + colla", "12", "rinforzo zona ricarica sotto il piano"),
    ("Viti 4×50", "24", "listelli reggiripiano"),
    ("Contropiastra acciaio 220×220×6 + 4 viti TSPEI M10×110 + dadi autobloccanti", "1 kit", "attacco piastre (vedi dettaglio)"),
    ("Angolari a L 100×100 + tasselli Ø10", "4", "fissaggio a muro (montanti mensola)"),
    ("Guide a sfera estrazione totale L=500", f"{n_drawers} cp", "3 cassettiera + 1 appeso"),
    ("Maniglie", f"{n_drawers}", ""),
    (f"Passacavi Ø{P['grommet_d']}", "3", "2 nel piano, 1 nel pannello posteriore"),
    ("Canalina sottoscrivania a misura", "3",
     " / ".join(str(round(p['box'][3] - p['box'][0])) for p in parts if p['name'].startswith('Canalina')) + " mm"),
    ("Ciabatta con interruttore", "1", "canalina campata seduta"),
]

# ------------------------------------------------ disegno
def dim(ax, x0, y0, x1, y1, off, text=None, vertical=False, fs=8):
    kw = dict(arrowprops=dict(arrowstyle="<->", lw=0.7, color=RED))
    if vertical:
        xo = x0 + off
        ax.annotate("", (xo, y0), (xo, y1), **kw)
        ax.plot([x0, xo], [y0, y0], lw=0.4, color=RED); ax.plot([x1, xo], [y1, y1], lw=0.4, color=RED)
        ax.text(xo + (14 if off > 0 else -14), (y0 + y1) / 2, text or f"{abs(y1 - y0):.0f}", rotation=90,
                ha="left" if off > 0 else "right", va="center", fontsize=fs, color=RED)
    else:
        yo = y0 + off
        ax.annotate("", (x0, yo), (x1, yo), **kw)
        ax.plot([x0, x0], [y0, yo], lw=0.4, color=RED); ax.plot([x1, x1], [y1, yo], lw=0.4, color=RED)
        ax.text((x0 + x1) / 2, yo + (12 if off > 0 else -12), text or f"{abs(x1 - x0):.0f}",
                ha="center", va="bottom" if off > 0 else "top", fontsize=fs, color=RED)

def elevation(ax, u, v, depth, sel=None, far_first_high=False):
    ps = [p for p in parts if sel is None or sel(p)]
    ps.sort(key=(lambda p: -p["box"][depth + 3]) if far_first_high else (lambda p: p["box"][depth]))
    for p in ps:
        b = p["box"]
        ax.add_patch(Rectangle((b[u], b[v]), b[u + 3] - b[u], b[v + 3] - b[v], fc=p["color"], ec="#3b2f22", lw=0.45))
    ax.set_aspect("equal"); ax.axis("off")

def header(fig, title, n):
    fig.text(0.04, 0.955, title, fontsize=15, weight="bold")
    fig.text(0.96, 0.955, f"Tavolo da lavoro 2000×800 – listelli 25×50 laminati – tav. {n}", fontsize=9,
             ha="right", color="#555")
    fig.text(0.04, 0.025, "Quote in mm. Listelli nominali 25×50: misurare il piallato reale e rigenerare il "
             "modello (parametri t, w in tavolo_lam.py).", fontsize=7.5, color="#555")

def table(ax, cells, cols, widths, fs=8.5, sc=1.3):
    tb = ax.table(cellText=cells, colLabels=cols, loc="upper left", cellLoc="left", colWidths=widths)
    tb.auto_set_font_size(False); tb.set_fontsize(fs); tb.scale(1, sc)
    for (r, c), cell in tb.get_celld().items():
        cell.set_edgecolor("#bbb")
        if r == 0: cell.set_facecolor("#efe6d6"); cell.set_text_props(weight="bold")

top_z = H + P["riser_h"] + P["T_riser"]
with PdfPages("tavolo_listelli_tavole.pdf") as pdf:
    # 1 insieme
    fig = plt.figure(figsize=A4); header(fig, "Vista d'insieme", 1)
    for i, f in enumerate(["lam_vista_frontale_sx.png", "lam_vista_frontale_dx.png"]):
        a = fig.add_axes([0.02 + i * 0.49, 0.33, 0.47, 0.57]); a.imshow(plt.imread(f)); a.axis("off")
    txt = (f"Telaio in listelli {t}×{w} incollati a strati: gambe 3 strati ({3*t}×{w}), 4 strati ({4*t}×{w}) "
           f"nella zona ricarica; traverse 2 strati ({2*t}×{w})\n"
           "Incastri ricavati nella laminazione: lo strato centrale della gamba è interrotto e accoglie il tenone "
           "passante della traversa laterale (vedi tav. 3)\n"
           f"Pannelli di irrigidimento multistrato {P['T_pan']} mm su retro e fianchi, incollati e avvitati: "
           "danno la rigidezza che la sezione ridotta non ha\n"
           f"Piano a {H} mm (seduto) – lamellare abete {P['T_top']} mm · campate nette: cassetti "
           f"{bays[0][1]-bays[0][0]:.0f} · seduta {bays[1][1]-bays[1][0]:.0f} · ricarica {bays[2][1]-bays[2][0]:.0f}\n"
           f"Zona ricarica: piano raddoppiato +{P['T_dbl']} mm, contropiastra acciaio, base per piastre "
           "intercambiabili (Rock Chucker / Dillon 550 / morsa)\n"
           "Mensola rialzata su montanti a 2 strati sopra le gambe posteriori · canaline passacavi e ciabatta · "
           "fissaggio a muro obbligatorio")
    fig.text(0.05, 0.075, txt, fontsize=8.8, va="bottom", linespacing=1.65)
    pdf.savefig(fig); plt.close(fig)

    # 2 prospetto frontale (senza pannelli fianchi, che coprirebbero le gambe estreme)
    fig = plt.figure(figsize=A4); header(fig, "Prospetto frontale", 2)
    ax = fig.add_axes([0.05, 0.08, 0.9, 0.84])
    elevation(ax, 0, 2, 1, sel=lambda p: "scatola" not in p["name"] and "fianco s" not in p["name"]
              and "fianco d" not in p["name"], far_first_high=True)
    dim(ax, 0, top_z, W, top_z, 90, f"{W}")
    for a, c in bays: dim(ax, a, 0, c, 0, -70)
    for a, c in legs: dim(ax, a, 0, c, 0, -70, f"{c-a:.0f}", fs=6.5)
    dim(ax, 0, 0, P["T_pan"], 0, -150, f"{P['T_pan']}", fs=6.5)
    dim(ax, W, 0, W, H, 110, vertical=True); dim(ax, W, 0, W, top_z, 260, vertical=True)
    dim(ax, 0, 0, 0, P["lower_z"] + w, -110, vertical=True)
    dim(ax, 0, H - P["T_top"] - w, 0, H - P["T_top"], -110, vertical=True)
    for (a, c), lab in zip(bays, ["CASSETTI", "SEDUTA", "RICARICA"]):
        ax.text((a + c) / 2, -210, lab, ha="center", fontsize=9, weight="bold", color="#333")
    ax.set_xlim(-300, W + 380); ax.set_ylim(-270, top_z + 220)
    pdf.savefig(fig); plt.close(fig)

    # 3 laterale + dettaglio incastro
    fig = plt.figure(figsize=A4); header(fig, "Vista laterale da destra (senza pannello) · dettaglio incastro", 3)
    ax = fig.add_axes([0.02, 0.10, 0.42, 0.80])
    elevation(ax, 1, 2, 0, sel=lambda p: p["box"][0] >= bays[1][1] - 1 and "fianco dx" not in p["name"])
    dim(ax, 0, top_z, D, top_z, 80, f"{D}")
    dim(ax, 0, 0, w, 0, -60, f"{w}", fs=7); dim(ax, w, 0, D - P["T_pan"] - w, 0, -60)
    dim(ax, D - P["T_pan"], 0, D, 0, -130, f"{P['T_pan']}", fs=7)
    dim(ax, D, 0, D, H, 100, vertical=True); dim(ax, D, H, D, H + P["riser_h"], 100, vertical=True)
    dim(ax, 0, H - P["T_top"] - P["T_dbl"], 0, H, -90, f"{P['T_top']}+{P['T_dbl']}", vertical=True, fs=7)
    ax.set_xlim(-250, D + 330); ax.set_ylim(-200, top_z + 200)
    ax.text(D / 2, -175, "fronte ←            → muro", ha="center", fontsize=8, color="#555")
    a = fig.add_axes([0.40, 0.15, 0.60, 0.78]); a.imshow(plt.imread("lam_dettaglio_incastro.png")[230:790, 40:1460]); a.axis("off")
    fig.text(0.47, 0.07, "Lo strato centrale della gamba si interrompe alle quote delle traverse laterali: la mortasa "
             "nasce già in laminazione.\nIl tenone passante si incastra dall'alto, si incolla e si blocca con 2 spine; "
             "la barra M8 delle traverse\nlongitudinali lo attraversa e chiude il nodo.", fontsize=8, linespacing=1.5)
    pdf.savefig(fig); plt.close(fig)

    # 4 distinta listelli
    fig = plt.figure(figsize=A4); header(fig, f"Distinta di taglio – listelli {t}×{w}", 4)
    ax = fig.add_axes([0.04, 0.40, 0.52, 0.50]); ax.axis("off")
    cells = [[k, f"{L}", f"{n}", f"{L*n}"] for (k, L), n in lam_tab] + [["TOTALE", "", f"{len(pieces)}", f"{tot}"]]
    table(ax, cells, ["Pezzo", "Lungh.", "Q.tà", "Tot. mm"], [0.62, 0.12, 0.10, 0.16], fs=8)
    ax = fig.add_axes([0.59, 0.10, 0.38, 0.80]); ax.axis("off")
    lines = [f"Ottimizzazione barre (taglio 4 mm)", ""]
    for st, bars in opt.items():
        waste = st * len(bars) - tot
        lines.append(f"Barre da {st/1000:.1f} m: {len(bars)} pz (sfrido {waste/1000:.1f} m)")
        if st in (2400, 3000):
            for i, b in enumerate(bars):
                lines.append(f"  {i+1:2d}: " + "+".join(map(str, b)))
        lines.append("")
    ax.text(0, 1, "\n".join(lines), va="top", fontsize=6.6, family="monospace")
    fig.text(0.04, 0.09, "Note di laminazione\n"
             "• Scegliere listelli dritti e senza nodi passanti; incollare a piena faccia con D3 e serrare (morsetti o viti).\n"
             "• Gambe: incollare gli strati esterni sugli spezzoni centrali usando un ritaglio di listello come distanziale "
             "nelle mortase,\n  così la luce viene esatta; togliere il distanziale prima che la colla tiri.\n"
             "• Dopo l'incollaggio, rifilare e squadrare le testate; forare per barre e spine a colla indurita.\n"
             f"• Totale: {len(pieces)} pezzi, {tot/1000:.1f} m di listello (più sfrido).",
             fontsize=8, va="bottom", linespacing=1.55)
    pdf.savefig(fig); plt.close(fig)

    # 5 pannelli
    fig = plt.figure(figsize=A4); header(fig, "Distinta pannelli e listelli reggiripiano", 5)
    ax = fig.add_axes([0.04, 0.08, 0.92, 0.84]); ax.axis("off")
    table(ax, [[n_, m, f"{a}×{b}", f"{c}", f"{q}"] for (n_, m, a, b, c), q in panel_tab],
          ["Pezzo", "Materiale", "Dimensioni", "Sp.", "Q.tà"], [0.40, 0.22, 0.18, 0.08, 0.08], fs=8.3, sc=1.25)
    pdf.savefig(fig); plt.close(fig)

    # 6 ferramenta
    fig = plt.figure(figsize=A4); header(fig, "Ferramenta e note", 6)
    ax = fig.add_axes([0.04, 0.30, 0.92, 0.62]); ax.axis("off")
    table(ax, [list(h) for h in hardware], ["Articolo", "Q.tà", "Uso"], [0.45, 0.08, 0.47], fs=7.8, sc=1.3)
    fig.text(0.04, 0.06, "Sequenza di montaggio consigliata\n"
             "1. Laminare gambe, traverse e montanti; a colla indurita rifilare e forare.\n"
             "2. Montare i telai laterali (gamba ant. + gamba post. + traverse laterali): tenone dall'alto, colla, spine.\n"
             "3. Collegare i telai con le traverse longitudinali (barre M8 e dadi a tamburo), verificare la squadra sulle diagonali.\n"
             "4. Incollare e avvitare i pannelli di irrigidimento: da qui il telaio non si deforma più.\n"
             "5. Piano, rinforzo e attacco ricarica; mensola con barre M10; fissaggio a muro; cassettiera e canaline.",
             fontsize=8.3, va="bottom", linespacing=1.6)
    pdf.savefig(fig); plt.close(fig)
print("PDF ok:", len(pieces), "pezzi listello,", tot, "mm;", {k: len(v) for k, v in opt.items()})
