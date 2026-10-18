"""Tavole quotate + distinta di taglio + ferramenta -> tavolo_tavole.pdf"""
import json
from collections import Counter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle, Circle

d = json.load(open("parts.json"))
P, parts, xs, bays = d["params"], d["parts"], d["legs_x"], d["bays"]
W, D, H, S = P["W"], P["D"], P["H"], P["S"]
A4 = (11.69, 8.27)

# ---------------------------------------------------------------- distinte
def dims(p):
    x0, y0, z0, x1, y1, z1 = p["box"]
    return sorted([round(x1 - x0), round(y1 - y0), round(z1 - z0)], reverse=True)

beams = [p for p in parts if p["group"] == "Quadrotti 8x8"]
beam_rows = Counter()
for p in beams:
    L = dims(p)[0]
    kind = ("Gamba" if p["name"].startswith("Gamba") else
            "Montante mensola" if p["name"].startswith("Montante") else
            "Traversa laterale (profondità)" if "lat." in p["name"] else
            "Traversa longitudinale")
    beam_rows[(kind, L)] += 1
beam_tab = sorted(beam_rows.items(), key=lambda kv: (-kv[0][1], kv[0][0]))
pieces = [L for (k, L), n in beam_rows.items() for _ in range(n)]
tot_beam = sum(pieces)

def ffd(pieces, stock, kerf=5):
    bars = []
    for L in sorted(pieces, reverse=True):
        for b in bars:
            if sum(b) + kerf * len(b) + L <= stock:
                b.append(L); break
        else:
            bars.append([L])
    return bars

opt = {st: ffd(pieces, st) for st in (2000, 3000, 4000)}

panel_rows = Counter()
for p in parts:
    if p["group"] in ("Pannelli", "Listelli") or (p["group"] == "Cassettiera" and "scatola" not in p["name"]):
        a, b, c = dims(p)
        base = p["name"].split(" - ")[0] if p["group"] == "Listelli" else p["name"]
        base = "Listello reggiripiano" if p["group"] == "Listelli" else base
        base = "Frontale cassetto" if base.startswith("Frontale cassetto ") and "appeso" not in base else base
        panel_rows[(base, p["mat"], a, b, c)] += 1
# scomposizione scatole cassetti (multistrato 15, fondo HDF 4)
T15 = 15
for p in parts:
    if "scatola" in p["name"]:
        x0, y0, z0, x1, y1, z1 = p["box"]
        w, l, h = round(x1 - x0), round(y1 - y0), round(z1 - z0)
        tag = "appeso" if "appeso" in p["name"] else "cassettiera"
        panel_rows[(f"Cassetto {tag}: fianco", "multistrato 15", l, h, T15)] += 2
        panel_rows[(f"Cassetto {tag}: testata", "multistrato 15", w - 2 * T15, h, T15)] += 2
        panel_rows[(f"Cassetto {tag}: fondo", "HDF 4", l, w, 4)] += 1
panel_tab = sorted(panel_rows.items(), key=lambda kv: (kv[0][1], -kv[0][2]))

n_rails = sum(1 for p in beams if p["name"].startswith("Trav."))
n_drawers = sum(1 for p in parts if "scatola" in p["name"])
rod_L = round(P["T_riser"] + P["riser_h"] + P["T_top"] + 70)
hardware = [
    ("Bulloni M10×150 TE/TCEI + rondella + dado a tamburo M10", 2 * n_rails, "giunzioni traverse-gambe (1 per estremità)"),
    ("Spine in faggio Ø10×40", 4 * n_rails, "2 per giunzione, antirotazione (con colla)"),
    (f"Barra filettata M10, L≈{rod_L + 30} mm + dado a tamburo + dado cieco + rondella", 4,
     "mensola → montante → piano → gamba posteriore"),
    ("Inserti filettati M10 + piedini livellatori M10", 8, "base gambe, compensano il pavimento"),
    ("Squadrette/piastrine fissaggio piano + viti 4,5×30", 16, "piano su traverse superiori"),
    ("Viti 5×70 + colla vinilica D3", 12, "rinforzo zona ricarica incollato e avvitato sotto il piano"),
    ("Viti 4×50", 24, "listelli reggiripiano"),
    ("Contropiastra acciaio 220×220×6 (S235)", 1, "sotto il rinforzo, forata come la base attacco"),
    ("Bulloni M10×120 TCEI + rondelle larghe + dadi autobloccanti", 4,
     "base attacco piastre (numero/foratura secondo il sistema)"),
    ("Angolari rinforzati a L 100×100 + tasselli Ø10 adatti al muro", 4,
     "2 su montanti mensola, 2 su traversa sup. posteriore"),
    ("Guide a sfera estrazione totale L=500 (≥45 kg)", n_drawers, "coppie: 3 cassettiera + 1 cassetto appeso"),
    ("Maniglie / pomoli", n_drawers, ""),
    (f"Passacavi Ø{P['grommet_d']} da incasso", 2, "piano, sopra le canaline"),
    ("Canalina passacavi sottoscrivania (tagliata a misura)", 3,
     " / ".join(str(round(p['box'][3] - p['box'][0])) for p in parts if p['name'].startswith('Canalina')) + " mm"),
    ("Ciabatta con interruttore", 1, "nella canalina della campata seduta"),
]

# ---------------------------------------------------------------- disegno
def dim(ax, x0, y0, x1, y1, off, text=None, vertical=False, fs=8):
    if vertical:
        xo = x0 + off
        ax.annotate("", (xo, y0), (xo, y1), arrowprops=dict(arrowstyle="<->", lw=0.7, color="#c0392b"))
        ax.plot([x0, xo], [y0, y0], lw=0.4, color="#c0392b"); ax.plot([x1, xo], [y1, y1], lw=0.4, color="#c0392b")
        ax.text(xo + (14 if off > 0 else -14), (y0 + y1) / 2, text or f"{abs(y1 - y0):.0f}", rotation=90,
                ha="left" if off > 0 else "right", va="center", fontsize=fs, color="#c0392b")
    else:
        yo = y0 + off
        ax.annotate("", (x0, yo), (x1, yo), arrowprops=dict(arrowstyle="<->", lw=0.7, color="#c0392b"))
        ax.plot([x0, x0], [y0, yo], lw=0.4, color="#c0392b"); ax.plot([x1, x1], [y1, yo], lw=0.4, color="#c0392b")
        ax.text((x0 + x1) / 2, yo + (12 if off > 0 else -12), text or f"{abs(x1 - x0):.0f}",
                ha="center", va="bottom" if off > 0 else "top", fontsize=fs, color="#c0392b")

def elevation(ax, u, v, depth, sel=None):
    """u,v,depth: indici asse (0=x,1=y,2=z). Painter: prima i pezzi lontani."""
    ps = [p for p in parts if (sel is None or sel(p))]
    ps.sort(key=lambda p: -p["box"][depth + 3] if depth == 1 else p["box"][depth])
    for p in ps:
        b = p["box"]
        ax.add_patch(Rectangle((b[u], b[v]), b[u + 3] - b[u], b[v + 3] - b[v],
                               fc=p["color"], ec="#3b2f22", lw=0.5))
    ax.set_aspect("equal"); ax.axis("off")

def header(fig, title, n):
    fig.text(0.04, 0.955, title, fontsize=15, weight="bold")
    fig.text(0.96, 0.955, f"Tavolo da lavoro 2000×800 – tav. {n}", fontsize=9, ha="right", color="#555")
    fig.text(0.04, 0.025, "Quote in mm. Quadrotti abete 8×8 – verificare la sezione reale del piallato e "
             "rigenerare il modello se diversa.", fontsize=7.5, color="#555")

with PdfPages("tavolo_tavole.pdf") as pdf:
    # 1 - vista d'insieme
    fig = plt.figure(figsize=A4); header(fig, "Vista d'insieme", 1)
    for i, f in enumerate(["vista_frontale_sx.png", "vista_frontale_dx.png"]):
        a = fig.add_axes([0.02 + i * 0.49, 0.30, 0.47, 0.60]); a.imshow(plt.imread(f)); a.axis("off")
    txt = (f"Piano a {H} mm da terra (seduto, statura 174 cm) – lamellare abete {P['T_top']} mm\n"
           f"8 gambe 8×8 – campate nette: cassetti {bays[0][1]-bays[0][0]:.0f} (sx) · "
           f"seduta {bays[1][1]-bays[1][0]:.0f} · ricarica {bays[2][1]-bays[2][0]:.0f} (dx)\n"
           f"Ripiani bassi: cassetti e ricarica a tutta profondità, seduta solo posteriore "
           f"({P['rear_shelf_d']} mm) per lasciare spazio ai piedi\n"
           f"Mensola rialzata {P['riser_d']}×{P['T_riser']} a +{P['riser_h']} mm sul piano, "
           f"montanti allineati alle gambe posteriori (barra filettata passante)\n"
           f"Zona ricarica: base per piastre intercambiabili (Rock Chucker / Dillon 550 / morsa) sul bordo anteriore, "
           f"piano raddoppiato (+{P['T_dbl']} mm) e contropiastra in acciaio\n"
           "Canaline passacavi sotto il bordo posteriore in ogni campata, fori Ø35 nelle traverse per il passaggio "
           "cavi, ciabatta nella campata seduta\nTavolo da fissare a muro (angolari su montanti mensola e traversa posteriore)")
    fig.text(0.05, 0.07, txt, fontsize=9, va="bottom", linespacing=1.6)
    pdf.savefig(fig); plt.close(fig)

    # 2 - prospetto frontale
    fig = plt.figure(figsize=A4); header(fig, "Prospetto frontale", 2)
    ax = fig.add_axes([0.05, 0.08, 0.9, 0.84])
    elevation(ax, 0, 2, 1, sel=lambda p: "scatola" not in p["name"])
    top_z = H + P["riser_h"] + P["T_riser"]
    dim(ax, 0, top_z, W, top_z, 90, f"{W}")
    for x in xs:  # gambe
        pass
    for (a, c) in bays:
        dim(ax, a, 0, c, 0, -70)
    for x in xs:
        dim(ax, x, 0, x + S, 0, -70, f"{S}", fs=6.5)
    dim(ax, W, 0, W, H, 110, vertical=True)
    dim(ax, W, 0, W, top_z, 260, vertical=True)
    dim(ax, 0, 0, 0, P["lower_z"] + S, -110, vertical=True)
    dim(ax, 0, H - P["T_top"] - P["upper_h"], 0, H - P["T_top"], -110, vertical=True)
    ax.set_xlim(-300, W + 380); ax.set_ylim(-260, top_z + 220)
    for (a, c), lab in zip(bays, ["CASSETTI", "SEDUTA", "RICARICA"]):
        ax.text((a + c) / 2, -200, lab, ha="center", fontsize=9, weight="bold", color="#333")
    pdf.savefig(fig); plt.close(fig)

    # 3 - vista laterale (da destra) + pianta zona ricarica
    fig = plt.figure(figsize=A4); header(fig, "Vista laterale da destra · pianta zona ricarica", 3)
    ax = fig.add_axes([0.03, 0.08, 0.50, 0.84])
    elevation(ax, 1, 2, 0, sel=lambda p: p["box"][0] >= bays[1][1] - 1 or p["box"][3] > bays[2][0])
    dim(ax, 0, top_z, D, top_z, 80, f"{D}")
    dim(ax, D - P["riser_d"], H + P["riser_h"], D, H + P["riser_h"], -60, f"{P['riser_d']}", fs=7)
    dim(ax, 0, 0, S, 0, -60, f"{S}", fs=7); dim(ax, S, 0, D - S, 0, -60)
    dim(ax, D, 0, D, H, 100, vertical=True)
    dim(ax, D, H, D, H + P["riser_h"], 100, vertical=True)
    dim(ax, 0, H - P["T_top"] - P["T_dbl"], 0, H, -90, f"{P['T_top']}+{P['T_dbl']}", vertical=True, fs=7)
    ax.set_xlim(-250, D + 330); ax.set_ylim(-180, top_z + 200)
    ax.text(D / 2, -150, "fronte ←            → muro", ha="center", fontsize=8, color="#555")

    ax = fig.add_axes([0.56, 0.18, 0.41, 0.66])
    a, c = bays[2]; x0 = xs[2]
    ax.add_patch(Rectangle((x0, 0), W - x0, D, fc="#ecd3a8", ec="#3b2f22", lw=0.8))
    for p in parts:
        if p["name"] in ("Rinforzo piano ricarica", "Contropiastra acciaio"):
            b = p["box"]; ax.add_patch(Rectangle((b[0], b[1]), b[3] - b[0], b[4] - b[1], fill=False,
                                                 ec=p["color"], ls="--", lw=1))
        if p["name"] == "Base attacco piastre":
            b = p["box"]; ax.add_patch(Rectangle((b[0], b[1]), b[3] - b[0], b[4] - b[1], fc=p["color"]))
            mb = b
    for x in (xs[2], xs[3]):
        for y in (0, D - S):
            ax.add_patch(Rectangle((x, y), S, S, fill=False, ec="#8a6a45", ls=":", lw=0.8))
    ax.add_patch(Rectangle((a, 0), c - a, S, fill=False, ec="#8a6a45", ls=":", lw=0.8))
    for h in parts[[p["name"] for p in parts].index("Piano di lavoro")]["holes"]:
        if h[1] > x0: ax.add_patch(Circle((h[1], h[2]), h[3] / 2, fc="white", ec="#333"))
    ax.set_xlim(x0 - 60, W + 160); ax.set_ylim(D + 60, -150); ax.set_aspect("equal"); ax.axis("off")
    mx = (mb[0] + mb[3]) / 2
    dim(ax, x0, 0, mx, 0, -60, f"{mx - x0:.0f}", fs=7)
    dim(ax, mx, 0, W, 0, -60, f"{W - mx:.0f}", fs=7)
    dim(ax, W, 0, W, mb[4], 50, f"{mb[4] - mb[1]:.0f}", vertical=True, fs=7)
    ax.set_title("Pianta zona ricarica (dall'alto, fronte in alto)", fontsize=9)
    fig.text(0.56, 0.08, "Pieno: base attacco piastre (sul piano, a filo del bordo anteriore)\n"
             "Tratteggio: rinforzo 40 mm e contropiastra acciaio (sotto il piano)\n"
             "Puntinato: gambe e traversa superiore anteriore (sotto il piano)",
             fontsize=7.5, color="#333", linespacing=1.5)
    pdf.savefig(fig); plt.close(fig)

    # 4 - distinta quadrotti + ottimizzazione
    fig = plt.figure(figsize=A4); header(fig, "Distinta di taglio – quadrotti abete 8×8", 4)
    ax = fig.add_axes([0.04, 0.45, 0.50, 0.45]); ax.axis("off")
    rows = [[k, f"{L}", f"{n}", f"{L*n}"] for (k, L), n in beam_tab]
    rows.append(["TOTALE", "", f"{len(pieces)}", f"{tot_beam}"])
    t = ax.table(cellText=rows, colLabels=["Pezzo", "Lungh.", "Q.tà", "Tot. mm"], loc="upper left", cellLoc="left",
                 colWidths=[0.55, 0.15, 0.12, 0.18]); t.auto_set_font_size(False); t.set_fontsize(8.5); t.scale(1, 1.35)
    ax = fig.add_axes([0.58, 0.45, 0.38, 0.45]); ax.axis("off")
    lines = ["Ottimizzazione barre (taglio 5 mm incl. squadratura)", ""]
    for st, bars in opt.items():
        waste = st * len(bars) - tot_beam
        lines.append(f"Barre da {st/1000:.0f} m: {len(bars)} pz  (sfrido {waste/1000:.2f} m)")
        for i, b in enumerate(bars):
            lines.append(f"   {i+1}: " + " + ".join(map(str, b)))
        lines.append("")
    ax.text(0, 1, "\n".join(lines), va="top", fontsize=7.6, family="monospace")
    fig.text(0.04, 0.12, "Note\n"
             "• Gambe: tutte uguali, piano appoggiato in testa. Traverse tra le gambe (luce netta = lunghezza).\n"
             "• Ogni giunzione: 1 bullone M10 passante nella gamba + dado a tamburo nella traversa + 2 spine Ø10.\n"
             "  Dove due traverse entrano nella stessa gamba alla stessa quota, sfalsare i bulloni di ±18 mm in altezza.\n"
             "• Traverse superiori laterali interne: foro Ø35 per il passaggio dei cavi lungo le canaline.\n"
             "• Montanti mensola: foro passante Ø11 in asse per la barra filettata che scende nella gamba posteriore.",
             fontsize=8, va="bottom", linespacing=1.55)
    pdf.savefig(fig); plt.close(fig)

    # 5 - pannelli
    fig = plt.figure(figsize=A4); header(fig, "Distinta pannelli e listelli", 5)
    ax = fig.add_axes([0.04, 0.08, 0.92, 0.84]); ax.axis("off")
    rows = [[n_, m, f"{a}×{b}", f"{c}", f"{q}"] for (n_, m, a, b, c), q in panel_tab]
    t = ax.table(cellText=rows, colLabels=["Pezzo", "Materiale", "Dimensioni (L×l)", "Sp.", "Q.tà"],
                 loc="upper left", cellLoc="left", colWidths=[0.40, 0.22, 0.18, 0.08, 0.08])
    t.auto_set_font_size(False); t.set_fontsize(8.5); t.scale(1, 1.3)
    pdf.savefig(fig); plt.close(fig)

    # 6 - ferramenta
    fig = plt.figure(figsize=A4); header(fig, "Ferramenta e note zona ricarica", 6)
    ax = fig.add_axes([0.04, 0.38, 0.92, 0.54]); ax.axis("off")
    t = ax.table(cellText=[[a, str(b), c] for a, b, c in hardware], colLabels=["Articolo", "Q.tà", "Uso"],
                 loc="upper left", cellLoc="left", colWidths=[0.48, 0.06, 0.46])
    t.auto_set_font_size(False); t.set_fontsize(8); t.scale(1, 1.35)
    fig.text(0.04, 0.06, "Zona ricarica\n"
             "• La base delle piastre va a filo del bordo anteriore, sopra la traversa superiore anteriore: la leva "
             "delle presse scende davanti al piano.\n"
             "• Pacchetto serrato dai bulloni: base acciaio + piano 40 + rinforzo 40 + contropiastra 6 mm. "
             "Rinforzo incollato e avvitato al piano prima di forare.\n"
             "• Foratura e dimensioni della base vanno adattate al sistema di piastre che usi già: nel modello è un "
             "segnaposto 180×180×10 mm.\n"
             "• Uso da seduto a 74 cm: Rock Chucker e Dillon 550 direttamente sulla piastra, senza rialzo.\n"
             "• Fissaggio a muro obbligatorio: le presse tendono a far ribaltare e 'camminare' il tavolo. "
             "Il ripiano basso della campata ricarica (componenti, piombo) fa anche da zavorra.",
             fontsize=8.3, va="bottom", linespacing=1.6)
    pdf.savefig(fig); plt.close(fig)
print("PDF ok", len(pieces), "pezzi 8x8", tot_beam, "mm")
