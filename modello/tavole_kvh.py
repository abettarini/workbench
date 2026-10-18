"""Tavole quotate del tavolo base (modulo 1) -> tavolo_base_tavole.pdf"""
import json
from collections import Counter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle, Circle

d = json.load(open("parts_kvh.json")); cf = json.load(open("confronto.json"))
P, legs, bays = d["params"], d["legs"], d["bays"]
parts = [p for p in d["parts"] if p.get("module", "base") == "base"]
W, D, H, Lx, Ly, Rt, Rh = P["W"], P["D"], P["H"], P["Lx"], P["Ly"], P["Rt"], P["Rh"]
A4 = (11.69, 8.27); RED = "#c0392b"
top_z = H

def dims(p):
    x0, y0, z0, x1, y1, z1 = p["box"]
    return sorted([round(x1 - x0), round(y1 - y0), round(z1 - z0)], reverse=True)

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

NUM = [0]
def header(fig, title, n=None):
    NUM[0] += 1; n = NUM[0]
    fig.text(0.04, 0.955, title, fontsize=15, weight="bold")
    fig.text(0.96, 0.955, f"Tavolo da lavoro 2000×800 – travi KVH 80×120 – tav. {n}", fontsize=9, ha="right", color="#555")
    fig.text(0.04, 0.025, "Quote in mm. KVH 80×120 abete C24 giuntato, piallato. Costi nel file tavolo_base_costi.xlsx.",
             fontsize=7.5, color="#555")

def table(ax, cells, cols, widths, fs=8.5, sc=1.3):
    tb = ax.table(cellText=cells, colLabels=cols, loc="upper left", cellLoc="left", colWidths=widths)
    tb.auto_set_font_size(False); tb.set_fontsize(fs); tb.scale(1, sc)
    for (r, c), cell in tb.get_celld().items():
        cell.set_edgecolor("#bbb")
        if r == 0: cell.set_facecolor("#efe6d6"); cell.set_text_props(weight="bold")

with PdfPages("tavolo_base_tavole.pdf") as pdf:
    # 1
    fig = plt.figure(figsize=A4); header(fig, "Vista d'insieme", 1)
    for i, f in enumerate(["base_vista_sx.png", "base_vista_dx.png"]):
        a = fig.add_axes([0.02 + i * 0.49, 0.33, 0.47, 0.57]); a.imshow(plt.imread(f)); a.axis("off")
    txt = (f"Telaio in travi KVH 80×120: gambe con il lato da 120 in profondità (verso la leva delle presse), traverse di coltello (120 in altezza)\n"
           f"Piano a {H} mm (seduto) – tavola lamellare abete 2000×800×40 intera · campate nette: cassetti 500 · seduta 700 · ricarica 480\n"
           "Ripiani bassi e rinforzo della ricarica (2 strati) da un pannello OSB/3 2500×1250×18\n"
           "Nodi: bullone M10 passante + dado a tamburo + 2 spine Ø12; bulloni sfalsati in altezza dove due traverse entrano nella stessa gamba\n"
           "Telaio da 5 barre KVH da 4 m (29 pezzi, ~2,6 m di scorta). Fissaggio a muro obbligatorio per l'uso delle presse\n"
           "Moduli separati: cassettiera (modulo 2) e alzatina con mensola (modulo 3), con i propri manuali e costi")
    fig.text(0.05, 0.075, txt, fontsize=8.8, va="bottom", linespacing=1.65)
    pdf.savefig(fig); plt.close(fig)

    # 2 viste ortogonali quotate + schede traverse
    import disegni
    def new_page(title, phase=None):
        f = plt.figure(figsize=A4); header(f, title); return f
    disegni.pagine_viste(new_page, pdf, plt)
    disegni.pagine_traverse(new_page, pdf, plt)

    # 3 laterale + nodo
    fig = plt.figure(figsize=A4); header(fig, "Vista laterale da destra · dettaglio nodo")
    ax = fig.add_axes([0.02, 0.10, 0.40, 0.80])
    elevation(ax, 1, 2, 0, sel=lambda p: p["box"][0] >= bays[1][1] - 1)
    dim(ax, 0, top_z, D, top_z, 80, f"{D}")
    dim(ax, 0, 0, Ly, 0, -60, f"{Ly}", fs=7); dim(ax, Ly, 0, D - Ly, 0, -60); dim(ax, D - Ly, 0, D, 0, -60, f"{Ly}", fs=7)
    dim(ax, D, 0, D, H, 100, vertical=True)
    dim(ax, 0, H - P["T_top"] - P["T_dbl"], 0, H, -90, f"{P['T_top']}+{P['T_dbl']}", vertical=True, fs=7)
    ax.set_xlim(-250, D + 330); ax.set_ylim(-200, top_z + 200)
    ax.text(D / 2, -175, "fronte ←            → muro", ha="center", fontsize=8, color="#555")
    a = fig.add_axes([0.40, 0.14, 0.60, 0.80]); a.imshow(plt.imread("kvh_dettaglio_nodo.png")[240:880, 30:1470]); a.axis("off")
    fig.text(0.44, 0.07, "Foratura: Ø11 passante nella gamba, Ø11 in asse nella testata della traversa (prof. 80), Ø15 per il dado a tamburo\n"
             "a 60 mm dalla testata. Schemi completi di ogni pezzo nel manuale di lavorazione.", fontsize=8, linespacing=1.5)
    pdf.savefig(fig); plt.close(fig)

    # 4 travi + schema di taglio
    fig = plt.figure(figsize=A4); header(fig, "Travi KVH 80×120 – distinta e schema di taglio", 4)
    ax = fig.add_axes([0.04, 0.50, 0.50, 0.40]); ax.axis("off")
    rows = sorted([[k.replace("Montante mensola", "Montante alzatina (conservare)"), L, q] for k, L, q in cf["kvh_rows"]], key=lambda r: -r[1])
    tot = sum(L * q for _, L, q in rows)
    table(ax, [[k, f"{L}", f"{q}", f"{L*q}"] for k, L, q in rows] + [["TOTALE", "", f"{sum(q for *_, q in rows)}", f"{tot}"]],
          ["Pezzo", "Lungh.", "Q.tà", "Tot. mm"], [0.58, 0.14, 0.10, 0.18])
    ax = fig.add_axes([0.04, 0.10, 0.92, 0.36]); ax.axis("off")
    ax.set_xlim(-250, 4100); ax.set_ylim(len(cf["kvh_bars"]) * 1.4 + 0.4, -0.6)
    pal = {700: "#d9b382", 560: "#c99a62", 500: "#bd8d55", 480: "#b07f4a", 250: "#e6caa0"}
    for i, bar in enumerate(cf["kvh_bars"]):
        y = i * 1.4; x = 10
        ax.add_patch(Rectangle((0, y), 4000, 0.9, fc="#f4f1ec", ec="#999", lw=0.6))
        ax.text(-40, y + 0.45, f"Barra {i+1}", ha="right", va="center", fontsize=8.5, weight="bold")
        for L in bar:
            ax.add_patch(Rectangle((x, y), L, 0.9, fc=pal.get(L, "#d9b382"), ec="#3b2f22", lw=0.6))
            ax.text(x + L / 2, y + 0.45, str(L), ha="center", va="center", fontsize=8)
            x += L + 4
        ax.text(4020, y + 0.45, f"avanzo {4000 - x:.0f}", va="center", fontsize=7.5, color="#555")
    ax.text(0, -0.35, "Schema di taglio (barre da 4000 mm, taglio 4 mm, 10 mm di rifilatura in testa)", fontsize=9)
    fig.text(0.58, 0.62, "Note\n• La 5ª barra lascia ~2,6 m di scorta per errori di taglio.\n"
             "• Se il rivenditore taglia a misura, porta questa pagina.\n"
             "• Taglia prima i pezzi lunghi (700) e controlla la squadra.\n"
             "• Le gambe sono tutte uguali: puoi tagliarle in pacco.", fontsize=8.5, va="top", linespacing=1.6)
    pdf.savefig(fig); plt.close(fig)

    # 5 pannelli
    fig = plt.figure(figsize=A4); header(fig, "Pannelli, listelli e taglio del pannello OSB", 5)
    prow = Counter()
    for p in parts:
        if p["group"] in ("Pannelli", "Listelli reggiripiano") or (p["group"] == "Cassettiera" and "scatola" not in p["name"]):
            a, b, c = dims(p); nm = p["name"]
            if p["group"] == "Listelli reggiripiano": nm = "Listello reggiripiano"
            if nm.startswith("Frontale cassetto ") and "appeso" not in nm: nm = "Frontale cassetto"
            prow[(nm, p["mat"], a, b, c)] += 1
    for p in parts:
        if "scatola" in p["name"]:
            x0, y0, z0, x1, y1, z1 = p["box"]; wd, l, h = round(x1 - x0), round(y1 - y0), round(z1 - z0)
            tag = "appeso" if "appeso" in p["name"] else "cassettiera"
            prow[(f"Cassetto {tag}: fianco", "multistrato 15", l, h, 15)] += 2
            prow[(f"Cassetto {tag}: testata", "multistrato 15", wd - 30, h, 15)] += 2
            prow[(f"Cassetto {tag}: fondo", "HDF 4", l, wd, 4)] += 1
    ax = fig.add_axes([0.04, 0.34, 0.92, 0.58]); ax.axis("off")
    table(ax, [[n_, m, f"{a}×{b}", f"{c}", f"{q}"] for (n_, m, a, b, c), q in sorted(prow.items(), key=lambda kv: (kv[0][1], -kv[0][2]))],
          ["Pezzo", "Materiale", "Dimensioni", "Sp.", "Q.tà"], [0.34, 0.30, 0.16, 0.08, 0.08], fs=7.6, sc=1.18)
    ax = fig.add_axes([0.10, 0.07, 0.80, 0.22]); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 2000, 800, fc="#f4ead8", ec="#333"))
    ax.add_patch(Rectangle((0, 0), 2500, 1250, fc="#f4ead8", ec="#333"))
    cuts = [((0, 0), 500, 560, "Ripiano cassetti\n500×560"), ((504, 0), 480, 560, "Ripiano ricarica\n480×560"),
            ((988, 0), 480, 520, "Rinforzo A\n480×520"), ((1472, 0), 480, 520, "Rinforzo B\n480×520"),
            ((0, 564), 700, 260, "Ripiano seduta 700×260")]
    for (x, y), w_, h_, t in cuts:
        ax.add_patch(Rectangle((x, y), w_, h_, fc="#d9c08a", ec="#3b2f22")); ax.text(x + w_ / 2, y + h_ / 2, t, ha="center", va="center", fontsize=7)
    ax.text(1700, 900, "avanzo", ha="center", va="center", fontsize=7, color="#777")
    ax.set_xlim(-20, 2520); ax.set_ylim(-20, 1270)
    ax.set_title("Pannello OSB/3 2500×1250×18", fontsize=8.5)
    pdf.savefig(fig); plt.close(fig)

    # 6 ferramenta e montaggio
    fig = plt.figure(figsize=A4); header(fig, "Ferramenta e montaggio", 6)
    hw = [("Bullone TCEI M10×180 + rondella (B1)", "16", "traverse laterali"),
          ("Bullone TCEI M10×140 + rondella (B2)", "10", "traverse longitudinali su gambe con una sola traversa"),
          ("Barra filettata M10 L 220 (R)", "4", "gambe posteriori centrali: unisce le due traverse"),
          ("Dado a tamburo M10 (D)", "38", "34 testate di traversa + 4 predisposizione alzatina"),
          ("Spine in faggio Ø12×50", "68", "2 per nodo, incollate"),
          ("Inserti filettati M10 + piedini livellatori", "8", "base gambe"),
          ("Squadrette fissaggio piano + viti 4,5×30", "16", "piano sulle traverse superiori"),
          ("Viti 5×60 + colla", "12", "rinforzo zona ricarica sotto il piano"),
          ("Listello 30×40 + viti 5×70", "6 pz", "reggiripiano su traverse laterali inferiori"),
          ("Kit attacco piastre (acciaio, viti M10 svasate, manopole M12)", "1", "vedi dettaglio piastre"),
          ("Angolari a L 100×100 + tasselli Ø10", "4", "fissaggio a muro (G1P e G4P, 2 per gamba)"),
          ("Canaline, passacavi Ø60, ciabatta", "3+2+1", "")]
    ax = fig.add_axes([0.04, 0.45, 0.92, 0.47]); ax.axis("off")
    table(ax, [list(h) for h in hw], ["Articolo", "Q.tà", "Uso"], [0.47, 0.08, 0.45], fs=8.2, sc=1.35)
    fig.text(0.04, 0.07, "Montaggio\n"
             "1. Taglia i pezzi secondo lo schema; fora tutti i nodi con una dima (gamba: Ø11 passante; traversa: Ø11 in testa + Ø13 verticale).\n"
             "2. Monta i 4 telai laterali (gamba ant. + gamba post. + traversa laterale sup. e inf.) con spine incollate e bulloni.\n"
             "3. Collega i telai con le traverse longitudinali posteriori e con quelle anteriori della campata ricarica; controlla le diagonali.\n"
             "4. Avvita i listelli, posa i ripiani bassi; fissa il piano con le squadrette (asole per il movimento del legno).\n"
             "5. Rinforzo ricarica incollato e avvitato sotto il piano, poi base piastre e contropiastra con le viti M10 passanti.\n"
             "6. Piedini, fissaggio a muro, canaline e ciabatta. Moduli 2 e 3: vedi i loro manuali.",
             fontsize=8.3, va="bottom", linespacing=1.6)
    pdf.savefig(fig); plt.close(fig)
print("ok")
