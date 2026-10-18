"""Manuale tavolo BASE – KVH 80×120 -> tavolo_base_manuale.pdf"""
from manlib import *
from manlib import PAGE, TOC, FOOTER
# ------------------------------------------------------------------ codici e quantità
legs = [n for n in parts if n.startswith("Gamba")]
rails = [n for n in parts if n.startswith("Trav.")]
risers = [n for n in parts if n.startswith("Montante")]
def length(n):
    x0, y0, z0, x1, y1, z1 = parts[n]["box"]; return round(max(x1 - x0, y1 - y0, z1 - z0))

# ------------------------------------------------------------------ disegni ferramenta
def draw_hw(ax, kind):
    ax.set_xlim(0, 100); ax.set_ylim(0, 40); ax.set_aspect("equal"); ax.axis("off")
    if kind in ("B1", "B2"):
        R(ax, 8, 14, 8, 12, STEEL); R(ax, 16, 17, 70 if kind == "B1" else 56, 6, STEEL)
        for x in range(30, 86 if kind == "B1" else 72, 3): ax.plot([x, x + 1.5], [17, 23], lw=0.4, color=INK)
        R(ax, 4, 12, 3, 16, "#c8cdd2")
    elif kind == "R":
        R(ax, 6, 17, 88, 6, STEEL)
        for x in range(7, 93, 3): ax.plot([x, x + 1.5], [17, 23], lw=0.4, color=INK)
    elif kind == "D":
        ax.add_patch(Circle((50, 20), 12, fc=STEEL, ec=INK)); ax.add_patch(Circle((50, 20), 4, fc="white", ec=INK))
        ax.plot([38, 62], [20, 20], lw=1.2, color=INK)
        ax.text(70, 20, "fessura per\ncacciavite", fontsize=6, va="center")
    elif kind == "S":
        R(ax, 25, 14, 50, 12, "#e8c77a")
        for x in range(28, 74, 4): ax.plot([x, x + 2], [14, 26], lw=0.4, color="#a07a2a")
    elif kind == "I":
        R(ax, 20, 13, 30, 14, "#c9a96e"); R(ax, 50, 18, 25, 4, STEEL); R(ax, 75, 10, 12, 20, "#333")
        ax.text(20, 4, "inserto + piedino", fontsize=6)
    elif kind == "M":
        R(ax, 6, 17, 80, 6, STEEL); ax.add_patch(Polygon([[86, 14], [94, 17], [94, 23], [86, 26]], fc="#c8cdd2", ec=INK))
        R(ax, 82, 12, 3, 16, "#c8cdd2")
    elif kind == "V":
        R(ax, 12, 17, 3, 6, STEEL); ax.add_patch(Polygon([[15, 18], [70, 19], [80, 20], [70, 21], [15, 22]], fc=STEEL, ec=INK))
        ax.add_patch(Polygon([[8, 14], [12, 17], [12, 23], [8, 26]], fc="#c8cdd2", ec=INK))
    elif kind == "Q":
        ax.add_patch(Polygon([[30, 8], [70, 8], [70, 12], [34, 12], [34, 34], [30, 34]], fc=STEEL, ec=INK))
        R(ax, 46, 9, 12, 2, "white", ec=INK, lw=0.5); R(ax, 31, 18, 2, 8, "white", ec=INK, lw=0.5)
        ax.text(60, 22, "asola", fontsize=6)
    elif kind == "X":
        R(ax, 10, 12, 30, 16, "#222"); R(ax, 40, 18, 20, 4, STEEL); R(ax, 60, 14, 5, 12, STEEL)

HW = [  # codice, nome, quantità, dove, disegno
    ("B1", "Bullone TCEI M10×180 + rondella Ø20", "16", "traverse laterali (L): dalla faccia esterna della gamba", "B1"),
    ("B2", "Bullone TCEI M10×140 + rondella Ø20", "8", "traverse longitudinali su gambe con una sola traversa", "B2"),
    ("R", "Barra filettata M10, spezzone 220 mm", "4", "gambe 2P e 3P: unisce le due traverse longitudinali", "R"),
    ("D", "Dado a tamburo M10 (Ø15 circa)", "36", "32 nelle traverse + 4 nelle gambe posteriori (predisposizione alzatina)", "D"),
    ("S", "Spina in faggio Ø12×50", "64", "2 per testata di traversa", "S"),
    ("I", "Inserto filettato M10 + piedino livellatore", "8", "sotto ogni gamba", "I"),
    ("Q", "Squadretta con asola + viti 4,5×25", "16", "fissaggio del piano alle traverse superiori", "Q"),
    ("V", "Viti legno: 5×60, 5×70, 4×45, 4×50, 3,5×25", "sfuse", "rinforzo, listelli, cassettiera, cassetti", "V"),
    ("X", "Viti TSPEI M10 + dadi autobloccanti", "2+2", "base piastre ricarica: 2 × M10×110 e 2 × M10×200", "X"),
]

# ------------------------------------------------------------------ foratura gambe
def leg_faces(n):
    x0, y0, z0, x1, y1, z1 = parts[n]["box"]
    return x0, x1, y0, y1

def face_uv(h, n):
    x0, x1, y0, y1 = leg_faces(n); x, y, z = h["p0"]; dx, dy, dz = h["dir"]
    t = 0.6
    if dy == 1 and abs(y - y0) < t: return "A", x - x0, z
    if dy == -1 and abs(y - y1) < t: return "P", x1 - x, z
    if dx == -1 and abs(x - x1) < t: return "D", y - y0, z
    if dx == 1 and abs(x - x0) < t: return "S", y1 - y, z
    if dz == -1: return "T", x - x0, y - y0
    if dz == 1: return "F", x - x0, y - y0
    raise ValueError(h)

def exit_uv(h, n):
    x0, x1, y0, y1 = leg_faces(n); x, y, z = h["p0"]; dx, dy, dz = h["dir"]; L = h["depth"]
    ex, ey, ez = x + dx * L, y + dy * L, z + dz * L
    if dy == 1: return "P", x1 - ex, ez
    if dy == -1: return "A", ex - x0, ez
    if dx == 1: return "D", ey - y0, ez
    if dx == -1: return "S", y1 - ey, ez

def through(h, n):
    x0, x1, y0, y1 = leg_faces(n); dx, dy, dz = h["dir"]
    return (dy and abs(h["depth"] - (y1 - y0)) < 0.5) or (dx and abs(h["depth"] - (x1 - x0)) < 0.5)

def draw_leg(fig, n, rect_draw, rect_tab):
    x0, x1, y0, y1 = leg_faces(n)
    gap = 45
    order = [("A", Lx), ("D", Ly), ("P", Lx), ("S", Ly)]
    offs, cur = {}, 0
    for f, w in order: offs[f] = (cur, w); cur += w + gap
    top_off = cur + 10
    ax = fig.add_axes(rect_draw); ax.set_aspect("equal"); ax.axis("off")
    for f, (o, w) in offs.items():
        R(ax, o, 0, w, LEG_H, WOOD, lw=0.7)
        ax.text(o + w / 2, LEG_H + 18, FACE_NAME[f].upper(), ha="center", fontsize=6.3, weight="bold")
        ax.text(o + w / 2, -22, f"{w}", ha="center", fontsize=6, color=MUTE)
    # testa e piede (viste dall'alto, fronte in basso)
    R(ax, top_off, LEG_H - Ly, Lx, Ly, "#f1dfbf", lw=0.7); ax.text(top_off + Lx / 2, LEG_H + 18, "TESTA", ha="center", fontsize=6.3, weight="bold")
    ax.text(top_off + Lx / 2, LEG_H - Ly - 14, "fronte ↓", ha="center", fontsize=5.5, color=MUTE)
    R(ax, top_off, 0, Lx, Ly, "#f1dfbf", lw=0.7); ax.text(top_off + Lx / 2, Ly + 8, "PIEDE", ha="center", fontsize=6.3, weight="bold")
    hs = [h for h in holes if h["part"] == n]
    zs = sorted({round(face_uv(h, n)[2]) for h in hs if face_uv(h, n)[0] in "ADPS"}, reverse=True)
    ly = []
    for z in zs:
        y = z if not ly or ly[-1] - z >= 16 else ly[-1] - 16
        ly.append(y)
        ax.plot([-15, cur - gap], [z, z], lw=0.3, ls=(0, (3, 3)), color="#888", zorder=0)
        ax.plot([-40, -15], [y, z], lw=0.3, color=RED)
        ax.text(-44, y, f"{LEG_H - z:.0f}", ha="right", va="center", fontsize=6.5, color=RED)
    ax.text(-44, LEG_H + 45, "quote\ndalla testa", ha="right", va="center", fontsize=6, color=RED)
    rows, rcol = [], []
    # ordina: per faccia, poi dall'alto
    hs.sort(key=lambda h: ("ADPSTF".index(face_uv(h, n)[0]), -face_uv(h, n)[2]))
    for k, h in enumerate(hs, 1):
        f, u, v = face_uv(h, n); col = HCOL.get(h["code"], INK)
        if f in "ADPS":
            o, w = offs[f]; cx, cy = o + u, v
        elif f == "T":
            cx, cy = top_off + u, LEG_H - Ly + v
        else:
            cx, cy = top_off + u, v
        if h["cb"]: ax.add_patch(Circle((cx, cy), h["cb"][0] / 2, fc="white", ec=col, lw=0.6, ls="--", zorder=3))
        ax.add_patch(Circle((cx, cy), h["d"] / 2, fc=col, ec=INK, lw=0.4, zorder=4))
        ax.text(cx + max(h["d"], (h["cb"] or [0])[0]) / 2 + 3, cy + 6, str(k), fontsize=5.6, color=col, weight="bold", zorder=5)
        if through(h, n):
            ef, eu, ev = exit_uv(h, n); o, w = offs[ef]
            ax.add_patch(Circle((o + eu, ev), h["d"] / 2, fc="white", ec=col, lw=0.7, zorder=4))
            ax.text(o + eu + h["d"] / 2 + 3, ev - 10, f"{k}'", fontsize=5.4, color=col, zorder=5)
        if f in "ADPS":
            pos = f"{LEG_H - v:.0f}"; hor = f"{u:.0f}"
        else:
            pos = "—"; hor = f"{u:.0f} da sx, {('%.0f' % (Ly - v))} dal retro" if f == "T" else f"centro"
        depth = "passante" if through(h, n) else f"{h['depth']:.0f}"
        note = {"B1": "bullone laterale B1", "B2": "bullone longit. B2", "R": "barra R", "S": "spina S", "I": "inserto I",
                "M": "predisp. alzatina: foro barra M", "T": "predisp. alzatina: dado D"}.get(h["code"], h["kind"])
        if h["cb"]: note += f", lamatura Ø{h['cb'][0]}×{h['cb'][1]}"
        if f == "T": note += " – punta lunga"
        lev = "sup." if (v > 400 and f in "ADPS") else ("inf." if f in "ADPS" else "")
        rows.append([str(k), FACE_NAME[f], pos, hor, f"Ø{h['d']:.0f}", depth, (lev + " " + note).strip()])
        rcol.append(None)
    ax.set_xlim(-95, top_off + Lx + 10); ax.set_ylim(-35, LEG_H + 70)
    at = fig.add_axes(rect_tab)
    table(at, rows, ["n°", "faccia", "dalla testa", "da sinistra", "Ø", "prof.", "cosa"],
          [0.05, 0.11, 0.10, 0.20, 0.06, 0.10, 0.42], fs=7, sc=1.45)
    return hs

# ------------------------------------------------------------------ sezioni
def sec_nodo_estremita(ax):
    """vista dall'alto: gamba 1P + traversa PC (bullone B2)"""
    ax.set_aspect("equal"); ax.axis("off")
    R(ax, 0, 0, 80, 120, WOOD); R(ax, 80, 40, 220, 80, WOOD2)
    # bullone: lamatura da sinistra
    R(ax, 0, 80 - 12.5, 12, 25, "white", ls="--"); R(ax, 12, 80 - 5.5, 68 + 70, 11, "white", ec=INK, ls="--", lw=0.6)
    R(ax, 2, 80 - 8, 10, 16, STEEL); R(ax, 12, 80 - 5, 128, 10, STEEL)
    ax.add_patch(Circle((140, 80), 7.5, fc=STEEL, ec=INK)); ax.plot([133, 147], [80, 80], lw=1, color=INK)
    for dy in (-15, 15): R(ax, 55, 80 + dy - 6, 55, 12, "#e8c77a", ec=INK, lw=0.5, ls=":")
    dim(ax, 80, 120, 140, 120, 18, "60"); dim(ax, 0, 0, 80, 0, -14, "80")
    ax.text(150, 112, "dado a tamburo D\n(foro Ø15 dall'alto,\nprof. 45)", fontsize=6.3, va="top")
    ax.text(2, 135, "lamatura Ø25×12", fontsize=6.3)
    ax.text(170, 60, "traversa\nlongitudinale", fontsize=6.3)
    ax.text(5, 20, "gamba", fontsize=6.3)
    ax.text(57, 50, "spine S (quota diversa)", fontsize=5.5, color="#8a6a20")
    ax.set_xlim(-10, 310); ax.set_ylim(-35, 150)
    ax.set_title("A · gamba d'estremità: bullone B2 M10×140 (vista dall'alto)", fontsize=8, loc="left")

def sec_nodo_centrale(ax):
    ax.set_aspect("equal"); ax.axis("off")
    R(ax, -220, 40, 220, 80, WOOD2); R(ax, 0, 0, 80, 120, WOOD); R(ax, 80, 40, 220, 80, WOOD2)
    R(ax, -75, 75, 230, 10, STEEL)
    for x in (-60, 140): ax.add_patch(Circle((x, 80), 7.5, fc=STEEL, ec=INK)); ax.plot([x - 7, x + 7], [80, 80], lw=1, color=INK)
    dim(ax, -60, 120, 140, 120, 18, "barra R 220: 60 + 80 + 60 + 2×10")
    ax.text(-210, 60, "traversa sinistra", fontsize=6.3); ax.text(170, 60, "traversa destra", fontsize=6.3)
    ax.text(5, 20, "gamba\n2P / 3P", fontsize=6.3)
    ax.text(-215, -10, "Avvita la barra a metà nel dado della prima traversa, accosta l'altra e stringi\n"
            "ruotando i dadi a tamburo con un cacciavite largo: le traverse si tirano contro la gamba.",
            fontsize=6.3, va="top")
    ax.set_xlim(-230, 310); ax.set_ylim(-45, 150)
    ax.set_title("B · gambe centrali posteriori: barra passante R (vista dall'alto)", fontsize=8, loc="left")

def sec_nodo_laterale(ax):
    ax.set_aspect("equal"); ax.axis("off")
    # vista dall'alto: gamba anteriore (y 0..120 in verticale) e traversa laterale verso il retro
    R(ax, 0, 0, 80, 120, WOOD); R(ax, 0, 120, 80, 200, WOOD2)
    R(ax, 40 - 12.5, 0, 25, 12, "white", ls="--"); R(ax, 40 - 8, 2, 16, 10, STEEL); R(ax, 35, 12, 10, 108 + 70, STEEL)
    ax.add_patch(Circle((40, 180), 7.5, fc=STEEL, ec=INK)); ax.plot([40, 40], [173, 187], lw=1, color=INK)
    for dx in (-15, 15): R(ax, 40 + dx - 6, 95, 12, 55, "#e8c77a", ec=INK, lw=0.5, ls=":")
    dim(ax, 80, 120, 80, 180, 18, "60", vertical=True); dim(ax, 80, 0, 80, 120, 18, "120", vertical=True)
    ax.text(110, 200, "dado D dal basso\n(foro Ø15, prof. 45)", fontsize=6.3)
    ax.text(-70, 6, "fronte", fontsize=6.3, color=MUTE); ax.text(-70, 250, "retro", fontsize=6.3, color=MUTE)
    ax.text(-75, 60, "gamba\nanteriore", fontsize=6.3); ax.text(-75, 220, "traversa\nlaterale", fontsize=6.3)
    ax.set_xlim(-90, 220); ax.set_ylim(-20, 330)
    ax.set_title("C · traversa laterale: bullone B1 M10×180", fontsize=8, loc="left")

def testata(ax, kind):
    """vista di testa + vista laterale di una traversa"""
    ax.set_aspect("equal"); ax.axis("off")
    # testata 80×120
    R(ax, 0, 0, 80, 120, WOOD)
    if kind == "lat":
        bz, sz, nut_from, title = 30, 85, "basso", "Traversa LATERALE (L): testata e fianco"
    else:
        bz, sz, nut_from, title = 90, 35, "alto", "Traversa LONGITUDINALE (P, A): testata e fianco"
    ax.add_patch(Circle((40, bz), 5.5, fc=HCOL["A"], ec=INK)); ax.text(48, bz - 2, "Ø11 prof. 80", fontsize=6.2)
    for dx in (-15, 15): ax.add_patch(Circle((40 + dx, sz), 6, fc=HCOL["S"], ec=INK))
    ax.text(62, sz + 8, "Ø12 prof. 30", fontsize=6.2)
    dim(ax, 0, 0, 0, bz, -10, f"{bz}", vertical=True, fs=6.5); dim(ax, 0, 0, 0, sz, -32, f"{sz}", vertical=True, fs=6.5)
    dim(ax, 0, 120, 25, 120, 10, "25", fs=6.5); dim(ax, 25, 120, 55, 120, 10, "30", fs=6.5)
    ax.text(40, -22, "testata (vista di fronte)", ha="center", fontsize=6.5, color=MUTE)
    # fianco
    ox = 150
    R(ax, ox, 0, 230, 120, WOOD); ax.plot([ox + 230, ox + 230], [0, 120], color="white", lw=3)
    R(ax, ox, bz - 5.5, 80, 11, "white", ec=HCOL["A"], ls="--", lw=0.8)
    R(ax, ox, sz - 6, 30, 12, "white", ec="#a07a2a", ls="--", lw=0.8)
    ny0 = 0 if nut_from == "basso" else 120 - 45
    R(ax, ox + 60 - 7.5, ny0, 15, 45, "white", ec=HCOL["T"], ls="--", lw=0.8)
    dim(ax, ox, 120, ox + 60, 120, 12, "60", fs=6.5); dim(ax, ox, 0, ox + 80, 0, -12, "80", fs=6.5)
    ax.text(ox + 75, (ny0 + 22) if nut_from == "basso" else 60, f"Ø15 dal{'l' if nut_from=='alto' else ''} {nut_from}\nprof. 45",
            fontsize=6.2, color=HCOL["T"])
    ax.text(ox + 115, -22, "fianco (testata a sinistra)", ha="center", fontsize=6.5, color=MUTE)
    ax.set_xlim(-50, ox + 240); ax.set_ylim(-45, 150)
    ax.set_title(title, fontsize=8, loc="left")

# ------------------------------------------------------------------ PDF
FOOTER[0] = "Modulo 1 – Tavolo base KVH 80×120 – manuale di lavorazione e montaggio"
with PdfPages("tavolo_base_manuale.pdf") as pdf:
    # ================= 1. copertina
    fig = plt.figure(figsize=A4); PAGE[0] += 1
    fig.text(0.05, 0.9, "Tavolo da lavoro", fontsize=30, weight="bold")
    fig.text(0.05, 0.85, "Modulo 1 · Tavolo base – manuale di lavorazione e montaggio", fontsize=14, color=MUTE)
    img(fig, "man_f9_base.png", [0.36, 0.10, 0.62, 0.72], crop=(150, 900, 40, 1480))
    fases = ["Prima di iniziare", "Ferramenta e codici dei pezzi", "Fase 1 · Taglio",
             "Fase 2 · Foratura (gambe, traverse, pannelli)", "Fase 3 · Levigatura e finitura",
             "Fase 4 · Telai laterali", "Fase 5 · Collegamento dei telai", "Fase 6 · Listelli e ripiani bassi",
             "Fase 7 · Piano", "Fase 8 · Zona ricarica", "Fase 9 · Piedini, fissaggio a muro, predisposizioni",
             "Fase 10 · Canaline, elettrico e controlli finali", "",
             "Moduli aggiuntivi (manuali separati):", "  Modulo 2 · Cassettiera", "  Modulo 3 · Alzatina con mensola"]
    fig.text(0.05, 0.76, "Contenuto", fontsize=11, weight="bold")
    fig.text(0.05, 0.735, "\n".join(fases), fontsize=9, va="top", linespacing=1.9)
    fig.text(0.05, 0.08, "Quote in mm. Ogni foro è stato verificato sul modello 3D: nessun foro\n"
             "ne interseca un altro (minimo 7,7 mm di legno tra due fori).", fontsize=8, color=MUTE)
    pdf.savefig(fig); plt.close(fig)

    # ================= 2. prima di iniziare
    fig = page("Prima di iniziare")
    para(fig, 0.04, 0.89, "Attrezzi", fs=11, weight="bold")
    para(fig, 0.04, 0.86, (
        "• Troncatrice o sega circolare con guida (tagli a 90° precisi)\n"
        "• Trapano a colonna oppure guida per trapano (fori perpendicolari)\n"
        "• Punte legno a lancia/elicoidali: Ø3, Ø4, Ø8, Ø11, Ø12; punta lunga Ø12 da 300 mm\n"
        "• Punte Forstner: Ø15, Ø25, Ø35; sega a tazza Ø60\n"
        "• Svasatore, avvitatore, chiave a brugola 8 (TCEI M10), chiave 17\n"
        "• Cacciavite piatto largo (per ruotare i dadi a tamburo)\n"
        "• 4 morsetti da almeno 600 mm, squadra, metro, matita, livella\n"
        "• Levigatrice orbitale con carte 80 – 120 – 180\n"
        "• Colla vinilica D3, pennello, stracci"), width=62, fs=8.6)
    para(fig, 0.52, 0.89, "Verifica prima di tagliare e forare", fs=11, weight="bold")
    para(fig, 0.52, 0.86, (
        "1. Sezione reale delle travi: devono essere 80×120. Se misurano 78×118 (capita) le quote dei fori "
        "restano valide perché sono riferite alla testa e all'asse dei pezzi, ma rifai i conti delle campate.\n"
        "2. Diametro del dado a tamburo acquistato: il manuale usa Ø15. Se il tuo è Ø14 o Ø16 usa la Forstner "
        "dello stesso diametro.\n"
        "3. Inserto per i piedini: il foro Ø14 è indicativo, usa quello indicato sulla confezione.\n"
        "4. Altezza del piedino: le gambe sono da 700 mm e il piano finito è a 740 mm senza piedini. "
        "Se vuoi restare a 740 con i piedini, accorcia tutte le gambe dell'altezza del piedino dal lato "
        "del PIEDE: le quote dei fori, date 'dalla testa', non cambiano.\n"
        "5. Il muro: tipo (mattone pieno, forato, cartongesso) e presenza del battiscopa, che può "
        "allontanare il tavolo dal muro."), width=60, fs=8.6)
    para(fig, 0.04, 0.5, "Convenzioni del manuale", fs=11, weight="bold")
    para(fig, 0.04, 0.47, (
        "• Fronte = lato dove ti siedi. Sinistra/destra viste stando seduto davanti al tavolo.\n"
        "• Le gambe si numerano da 1 (sinistra) a 4 (destra); A = anteriore, P = posteriore: G1A … G4P.\n"
        "• Le quote dei fori nelle gambe sono 'dalla testa' (dall'estremità alta) e 'da sinistra' guardando "
        "quella faccia da fuori.\n"
        "• Nelle traverse le quote sono dal filo superiore del pezzo e dalla testata.\n"
        "• Passante = il foro attraversa tutto il pezzo; il punto di uscita è indicato con l'apice (es. 3').\n"
        "• Lamatura = allargamento poco profondo (Ø25×12) dove entra la testa del bullone con la rondella."),
        width=62, fs=8.6)
    box_note(fig, 0.52, 0.12, 0.44, 0.36, "Regola d'oro dei nodi",
             "Tutti i nodi telaio sono uguali: bullone (o barra) M10 + dado a tamburo + 2 spine Ø12.\n\n"
             "• Traverse longitudinali: bullone a 30 mm dalla testa, spine a 85.\n"
             "• Traverse laterali: bullone a 90 mm dalla testa, spine a 35.\n"
             "• Spine a ±15 mm dall'asse del pezzo.\n"
             "• Dado a tamburo a 60 mm dalla testata della traversa.\n\n"
             "Le due regole sono una lo specchio dell'altra: con UNA sola dima (pag. 7) fori tutti i nodi, "
             "basta girarla.\n\n"
             "Spine incollate solo nella traversa: nella gamba entrano a secco, così il tavolo resta smontabile.",
             fs=8.3, width=64)
    pdf.savefig(fig); plt.close(fig)

    # ================= 3. ferramenta
    fig = page("Ferramenta – codici usati nel manuale")
    for i, (c, name, q, where, k) in enumerate(HW):
        col, row = i % 2, i // 2
        x = 0.04 + col * 0.48; y = 0.80 - row * 0.155
        a = fig.add_axes([x, y, 0.13, 0.11]); draw_hw(a, k)
        fig.text(x + 0.14, y + 0.085, f"{c}", fontsize=13, weight="bold", color=HCOL.get(c, INK))
        fig.text(x + 0.18, y + 0.088, name, fontsize=8.5, weight="bold", va="center")
        fig.text(x + 0.18, y + 0.058, f"Quantità: {q}", fontsize=8)
        para(fig, x + 0.18, y + 0.045, where, width=44, fs=7.8, color=MUTE)
    fig.text(0.04, 0.05, "Colla vinilica D3 per spine, rinforzo e cassetti. Prezzi e quantità nel foglio tavolo_costi.xlsx.",
             fontsize=8, color=MUTE)
    pdf.savefig(fig); plt.close(fig)

    # ================= 4. codici pezzi
    fig = page("Codici dei pezzi")
    ax = fig.add_axes([0.03, 0.42, 0.50, 0.47]); ax.set_aspect("equal"); ax.axis("off")
    for n in legs + rails:
        x0, y0, z0, x1, y1, z1 = parts[n]["box"]
        if z0 > 300 or n.startswith("Gamba"):
            R(ax, x0, y0, x1 - x0, y1 - y0, WOOD if n.startswith("Gamba") else WOOD2, lw=0.6)
            ax.text((x0 + x1) / 2, (y0 + y1) / 2, code(n).replace("s", "s/i") if not n.startswith("Gamba") else code(n),
                    ha="center", va="center", fontsize=6.5, weight="bold", rotation=90 if (y1 - y0) > (x1 - x0) * 2 and not n.startswith("Gamba") else 0)
    ax.text(1000, -60, "FRONTE (seduta)", ha="center", fontsize=8, color=MUTE)
    ax.text(1000, 860, "RETRO (muro)", ha="center", fontsize=8, color=MUTE)
    for (a, c), lab in zip(d["bays"], ["cassetti", "seduta", "ricarica"]):
        ax.text((a + c) / 2, 400, lab, ha="center", fontsize=8, color=MUTE, style="italic")
    ax.set_xlim(-40, 2040); ax.set_ylim(-110, 900)
    ax.set_title("Pianta del telaio (vista dall'alto) – s = superiore, i = inferiore", fontsize=8.5, loc="left")
    rows = []
    groups = OrderedDict()
    for n in legs + rails + risers:
        c = code(n); L = length(n)
        typ = "gamba" if n.startswith("Gamba") else ("traversa laterale" if ". lat." in n else
               ("montante alzatina (conservare)" if n.startswith("Mont") else "traversa longitudinale"))
        groups.setdefault((typ, L), []).append(c)
    for (typ, L), cs in groups.items():
        rows.append([typ, f"{L}", str(len(cs)), "\n".join(", ".join(cs[k:k + 4]) for k in range(0, len(cs), 4))])
    at = fig.add_axes([0.55, 0.40, 0.42, 0.49])
    table(at, rows, ["pezzo", "lungh.", "n°", "codici"], [0.38, 0.12, 0.07, 0.43], fs=7.2, sc=2.6)
    para(fig, 0.04, 0.36, (
        "Appena tagliato ogni pezzo, scrivi il codice a matita su una faccia che resterà nascosta "
        "(per le gambe: la testa; per le traverse: la faccia inferiore). Segna anche una freccia verso il FRONTE: "
        "evita di montare un pezzo girato.\n\n"
        "Gli altri pezzi hanno il loro nome: Piano (lamellare), Rinforzo, Ripiano cassetti, Ripiano ricarica, "
        "Ripiano seduta (tutti in OSB), Listelli reggiripiano. I 4 montanti M1–M4 non servono al tavolo base: "
        "tagliali, marcali e conservali per l'alzatina (modulo 3)."), width=110, fs=8.8)
    pdf.savefig(fig); plt.close(fig)

    # ================= 5. taglio
    fig = page("Taglio delle travi e dei pannelli", "Fase 1")
    ax = fig.add_axes([0.04, 0.50, 0.92, 0.38]); ax.axis("off")
    # assegna codici ai tagli
    pool = {}
    for n in legs + rails + risers: pool.setdefault(length(n), []).append(code(n))
    for k in pool: pool[k] = sorted(pool[k], key=lambda c: (c[0] != "G", c))
    bars = cf["kvh_bars"]
    ax.set_xlim(-300, 4250); ax.set_ylim(len(bars) * 1.5 + 0.2, -0.8)
    pal = {700: "#d9b382", 560: "#c99a62", 500: "#bd8d55", 480: "#b07f4a", 250: "#e6caa0"}
    for i, bar in enumerate(bars):
        y = i * 1.5; x = 10
        R(ax, 0, y, 4000, 1.0, "#f4f1ec", ec="#999", lw=0.6)
        ax.text(-40, y + 0.5, f"Barra {i+1}", ha="right", va="center", fontsize=8.5, weight="bold")
        R(ax, 0, y, 10, 1.0, "#bbb", ec="none")
        for L in bar:
            c = pool[L].pop(0)
            R(ax, x, y, L, 1.0, pal.get(L, WOOD), lw=0.6)
            ax.text(x + L / 2, y + 0.33, c, ha="center", va="center", fontsize=8, weight="bold")
            ax.text(x + L / 2, y + 0.72, str(L), ha="center", va="center", fontsize=7)
            x += L + 4
        ax.text(4020, y + 0.5, f"avanzo {4000 - x:.0f}", va="center", fontsize=7.5, color=MUTE)
    ax.text(0, -0.45, "Travi KVH 80×120 da 4 m – grigio: 10 mm di rifilatura della testa; taglio 4 mm", fontsize=8.5)
    para(fig, 0.04, 0.46, (
        "1. Rifila 10 mm a una testa di ogni barra per avere un'estremità a 90° pulita.\n"
        "2. Taglia nell'ordine indicato, misurando sempre dalla testa appena tagliata. Le 8 gambe devono essere "
        "identiche: tagliale con un fermo (battuta) sulla troncatrice, non misurandole una a una.\n"
        "3. Stessa cosa per le 8 traverse laterali da 560: una sola battuta per tutte.\n"
        "4. Controlla ogni taglio con la squadra su due facce. Una testata storta apre il nodo.\n"
        "5. Tieni gli avanzi da ~100 mm: uno serve per la dima di foratura.\n"
        "6. Marca subito il codice su ogni pezzo."), width=66, fs=8.5)
    ax2 = fig.add_axes([0.56, 0.08, 0.40, 0.32]); ax2.set_aspect("equal"); ax2.axis("off")
    R(ax2, 0, 0, 2500, 1250, "#efe3c4")
    for (x, y), w_, h_, t in [((0, 0), 500, 560, "Ripiano\ncassetti\n500×560"), ((504, 0), 480, 560, "Ripiano\nricarica\n480×560"),
                              ((988, 0), 480, 520, "Rinforzo A\n480×520"), ((1472, 0), 480, 520, "Rinforzo B\n480×520"),
                              ((0, 564), 700, 260, "Ripiano seduta 700×260")]:
        R(ax2, x, y, w_, h_, "#d9c08a", lw=0.6); ax2.text(x + w_ / 2, y + h_ / 2, t, ha="center", va="center", fontsize=6.3)
    ax2.text(1600, 900, "avanzo ≈ 1,8 m²\n(utile per la cassettiera)", ha="center", va="center", fontsize=6.5, color=MUTE)
    ax2.set_xlim(-20, 2520); ax2.set_ylim(-20, 1270)
    ax2.set_title("Pannello OSB/3 2500×1250×18 (il piano lamellare resta intero)", fontsize=8, loc="left")
    para(fig, 0.04, 0.17, (
        "OSB: taglia prima la striscia da 560 su tutta la lunghezza, poi i pezzi. Lato liscio dei ripiani verso "
        "l'alto. I due rinforzi si incollano uno sull'altro e formano 36 mm."),
        width=66, fs=8.5)
    pdf.savefig(fig); plt.close(fig)

    # ================= 6. dima e regole foratura
    fig = page("Foratura: regole, dima e sezioni dei nodi", "Fase 2")
    a = fig.add_axes([0.03, 0.55, 0.46, 0.33]); testata(a, "lat")
    a = fig.add_axes([0.51, 0.55, 0.46, 0.33]); testata(a, "long")
    a = fig.add_axes([0.03, 0.08, 0.32, 0.40]); sec_nodo_estremita(a)
    a = fig.add_axes([0.36, 0.08, 0.36, 0.40]); sec_nodo_centrale(a)
    a = fig.add_axes([0.74, 0.08, 0.24, 0.40]); sec_nodo_laterale(a)
    pdf.savefig(fig); plt.close(fig)

    fig = page("Foratura: la dima e come forare", "Fase 2")
    ax = fig.add_axes([0.04, 0.45, 0.35, 0.42]); ax.set_aspect("equal"); ax.axis("off")
    R(ax, 0, 0, 80, 120, "#f1dfbf")
    ax.add_patch(Circle((40, 30), 5.5, fc=HCOL["A"], ec=INK)); ax.text(48, 30, "Ø11", fontsize=7, va="center")
    for dx in (-15, 15): ax.add_patch(Circle((40 + dx, 85), 6, fc=HCOL["S"], ec=INK))
    ax.text(62, 95, "Ø12", fontsize=7)
    dim(ax, 0, 0, 0, 30, -10, "30", vertical=True); dim(ax, 0, 0, 0, 85, -30, "85", vertical=True)
    dim(ax, 0, 120, 25, 120, 10, "25"); dim(ax, 25, 120, 55, 120, 10, "30")
    ax.text(40, -20, "faccia di riferimento (BASSO)", ha="center", fontsize=7, color=RED)
    ax.annotate("", (95, 30), (95, 85), arrowprops=dict(arrowstyle="<->", color=MUTE))
    ax.set_xlim(-50, 130); ax.set_ylim(-40, 150)
    ax.set_title("Dima: avanzo di KVH 80×120×100 forato al trapano a colonna", fontsize=8.5, loc="left")
    para(fig, 0.42, 0.88, (
        "Come si costruisce\n"
        "Prendi un avanzo di trave lungo ~100 mm e fora i 3 fori passanti al trapano a colonna, "
        "perfettamente perpendicolari. Scrivi 'BASSO' sulla faccia corta di riferimento.\n\n"
        "Come si usa\n"
        "Accosta la dima alla faccia da forare, a filo con il bordo di riferimento, e stringila con un morsetto. "
        "La punta segue il foro della dima e resta dritta anche col trapano a mano. Metti un nastro sulla "
        "punta alla profondità giusta (profondità + 100 mm di dima).\n\n"
        "Orientamento\n"
        "• Traverse LATERALI (L) e gambe per le L: dima con 'BASSO' verso il basso del pezzo → bullone a 90 "
        "dalla testa, spine a 35.\n"
        "• Traverse LONGITUDINALI (P, A) e gambe per le P/A: dima capovolta, 'BASSO' verso l'alto → bullone "
        "a 30 dalla testa, spine a 85.\n"
        "• Sulle facce laterali delle gambe posteriori (larghe 120) la dima va a filo del bordo POSTERIORE; "
        "sulle gambe anteriori a filo del bordo ANTERIORE: l'asse delle traverse longitudinali è a 40 mm dal filo esterno.\n\n"
        "Ordine dei fori in ogni pezzo\n"
        "1. Fori Ø11 (bulloni) e Ø12 (spine) con la dima.\n"
        "2. Lamature Ø25×12 con la Forstner, centrate sul foro Ø11 già fatto.\n"
        "3. Nelle traverse: foro Ø15 per il dado a tamburo, a 60 dalla testata, profondo 45. Deve incontrare "
        "il foro Ø11: verifica infilando un chiodo nel Ø11.\n"
        "4. Smussa leggermente gli spigoli di tutti i fori."), width=78, fs=8.4)
    box_note(fig, 0.04, 0.08, 0.35, 0.3, "Profondità",
             "• Ø11 nella testata della traversa: 80 mm\n• Ø12 spine: 30 nella traversa, 25 nella gamba\n"
             "• Ø15 dado a tamburo: 45 mm\n• Ø11 nelle gambe: passante (80 o 120)\n"
             "• Lamatura: Ø25, 12 mm\n\nForo Ø11 nella testata: punta lunga almeno 200 mm (100 di dima + 80 + margine).",
             fs=8.3, width=58)
    pdf.savefig(fig); plt.close(fig)

    # ================= foratura gambe (2 per pagina)
    order = ["Gamba 1 ant", "Gamba 1 post", "Gamba 2 ant", "Gamba 2 post", "Gamba 3 ant", "Gamba 3 post",
             "Gamba 4 ant", "Gamba 4 post"]
    for n in order:
        fig = page(f"Foratura gamba {code(n)} – {n.lower()}", "Fase 2")
        draw_leg(fig, n, [0.02, 0.09, 0.42, 0.80], [0.46, 0.12, 0.52, 0.76])
        fig.text(0.03, 0.06, "Facce viste da fuori, testa in alto · cerchio pieno = ingresso · cerchio vuoto con apice = uscita "
                 "del foro passante · tratteggio = lamatura Ø25 · i numeri rimandano alla tabella", fontsize=7, color=MUTE)
        pdf.savefig(fig); plt.close(fig)

    # ================= traverse e montanti
    fig = page("Foratura traverse e montanti", "Fase 2")
    rows, cols = [], []
    for n in sorted(rails, key=lambda n: (". lat." not in n, code(n))):
        c = code(n); L = length(n); lat = ". lat." in n
        extra = []
        for h in holes:
            if h["part"] == n and h["code"] == "C":
                extra.append(f"passacavi Ø35 a {h['p0'][1] - parts[n]['box'][1]:.0f} dalla testata anteriore, "
                             f"{parts[n]['box'][5] - h['p0'][2]:.0f} dalla testa (vedi sotto)")
            if h["part"] == n and h["code"] == "P":
                extra.append(f"Ø11 verticale a {h['p0'][0] - parts[n]['box'][0]:.0f}")
        extra = [e for e in dict.fromkeys(extra)]
        if any(e.startswith("Ø11 verticale") for e in extra):
            xs_ = [e.split(" a ")[1] for e in extra if e.startswith("Ø11")]
            extra = [f"2 fori Ø11 verticali passanti a {' e '.join(xs_)} da sx, 25 dal fronte (fase 8)"]
        rows.append([c, "laterale" if lat else "longitudinale", f"{L}",
                     "bullone −90 · spine −35 · dado dal BASSO" if lat else "bullone −30 · spine −85 · dado dall'ALTO",
                     "; ".join(dict.fromkeys(extra)) or "—"])
    at = fig.add_axes([0.03, 0.43, 0.94, 0.45])
    table(at, rows, ["codice", "tipo", "lungh.", "entrambe le testate (quote dal filo superiore)", "fori aggiuntivi"],
          [0.07, 0.11, 0.07, 0.32, 0.43], fs=7, sc=1.25)
    # dettaglio passacavi e montante
    ax = fig.add_axes([0.04, 0.07, 0.42, 0.30]); ax.set_aspect("equal"); ax.axis("off")
    R(ax, 0, 0, 560, 120, WOOD)
    hc = next(h for h in holes if h["code"] == "C" and h["part"].startswith("Trav."))
    yy = hc["p0"][1] - 120; zz = hc["p0"][2] - 580
    ax.add_patch(Circle((yy, zz), 17.5, fc="white", ec=INK))
    for end in (60, 500): R(ax, end - 7.5, 0, 15, 45, "white", ec=HCOL["T"], ls="--", lw=0.7)
    dim(ax, 0, 120, yy, 120, 12, f"{yy:.0f}"); dim(ax, 560, 0, 560, zz, 14, f"{zz:.0f}", vertical=True)
    ax.text(0, -25, "fronte", fontsize=6.5, color=MUTE); ax.text(560, -25, "retro", fontsize=6.5, color=MUTE, ha="right")
    ax.set_xlim(-20, 620); ax.set_ylim(-40, 150)
    ax.set_title("L2s e L3s: foro passacavi Ø35 (Forstner), vista dal fianco", fontsize=8, loc="left")
    ax = fig.add_axes([0.52, 0.07, 0.44, 0.30]); ax.set_aspect("equal"); ax.axis("off")
    R(ax, 0, 0, 250, 120, WOOD); R(ax, 0, 60 - 6, 250, 12, "white", ec=HCOL["M"], ls="--", lw=0.8)
    dim(ax, 0, 0, 0, 60, -12, "60", vertical=True); dim(ax, 0, 120, 250, 120, 12, "250")
    ax.text(270, 60, "Ø12 passante, in asse\nlungo tutto il montante,\na 60 mm dal filo\nposteriore.\n"
            "Fora 125 mm da ogni\ntesta con la punta lunga.", fontsize=7, va="center")
    ax.text(0, -25, "retro (muro)", fontsize=6.5, color=MUTE)
    ax.set_xlim(-30, 420); ax.set_ylim(-40, 150)
    ax.set_title("Montanti M1–M4 (80×120×250) per l'alzatina, vista dal fianco", fontsize=8, loc="left")
    pdf.savefig(fig); plt.close(fig)

    # ================= pannelli
    fig = page("Foratura di piano, rinforzo e contropiastra", "Fase 2")
    ax = fig.add_axes([0.03, 0.42, 0.62, 0.46]); ax.set_aspect("equal"); ax.axis("off")
    R(ax, 0, 0, 2000, 800, "#efe0c2")
    lab = {"M": "barra mensola Ø12", "C": "passacavi Ø60", "P": "base piastre Ø11"}
    prow = []
    for h in [h for h in holes if h["part"] == "Piano di lavoro"]:
        x, y = h["p0"][0], h["p0"][1]
        ax.add_patch(Circle((x, y), max(h["d"], 14) / 2, fc=HCOL.get(h["code"], INK), ec=INK, lw=0.4))
        prow.append((h["code"], x, y, h["d"]))
    for xx in sorted({round(p[1]) for p in prow if p[0] == "M"}):
        ax.text(xx, 770 - 60, f"{xx}", fontsize=6, ha="center", color=RED)
    ax.text(-30, 740, "740", fontsize=6, ha="right", color=RED); ax.plot([-20, 0], [740, 740], color=RED, lw=0.4)
    for p in prow:
        if p[0] == "C": ax.text(p[1], p[2] - 110, f"x {p[1]:.0f}\ny {p[2]:.0f}", fontsize=6, ha="center", color=RED)
    ax.text(1680, 230, "4 fori Ø11:\nx 1615 e 1745\ny 25 e 155", fontsize=6, ha="center", color=RED)
    ax.text(1000, -60, "FRONTE – quote da sinistra (x) e dal bordo anteriore (y)", ha="center", fontsize=7.5, color=MUTE)
    ax.set_xlim(-60, 2040); ax.set_ylim(-110, 820)
    ax.set_title("PIANO 2000×800×40 visto dall'alto", fontsize=8.5, loc="left")
    para(fig, 0.67, 0.88, (
        "Piano\n• 2 fori Ø60 passacavi con la sega a tazza: fora metà da sopra e metà da sotto per non scheggiare.\n"
        "• 4 fori Ø11 della base piastre: falli in fase 8, usando la base d'acciaio come dima.\n"
        "• 4 fori Ø12 (in blu) a 740 dal fronte, x = 40, 620, 1400, 1960: servono SOLO per l'alzatina "
        "(modulo 3). Non farli ora: si forano dall'alto passando la punta nel foro già fatto nella gamba.\n\n"
        "Rinforzo (OSB 2×18) e contropiastra 220×220×6\n• 2 fori Ø11 per le viti posteriori della base: "
        "falli in fase 8 insieme al piano, dopo l'incollaggio del rinforzo."), width=48, fs=8.2)
    pdf.savefig(fig); plt.close(fig)

    # ================= fase 3 finitura + fase 4 telai
    fig = page("Levigatura e finitura · Telai laterali", "Fasi 3 e 4")
    para(fig, 0.04, 0.89, "Fase 3 · Levigatura e finitura (prima del montaggio)", fs=10.5, weight="bold")
    para(fig, 0.04, 0.86, (
        "1. Leviga tutti i pezzi con grana 120 e poi 180. Il KVH è già piallato: basta togliere segni e matita.\n"
        "2. Smussa tutti gli spigoli vivi di 2 mm.\n"
        "3. Stendi olio o impregnante su gambe, traverse e montanti; vernice trasparente sui ripiani OSB "
        "(l'OSB grezzo trattiene polvere e sporco).\n"
        "4. NON trattare le testate delle traverse e le zone dove andrà la colla (sotto il piano dove si incolla "
        "il rinforzo): la colla non attacca sull'olio. Coprile con nastro di carta.\n"
        "5. Il piano si tratta per ultimo, a tavolo montato, con 2–3 mani."), width=58, fs=8.6)
    para(fig, 0.04, 0.58, "Fase 4 · Telai laterali (4 telai)", fs=10.5, weight="bold")
    para(fig, 0.04, 0.55, (
        "Ogni telaio = gamba anteriore + gamba posteriore + traversa laterale superiore e inferiore "
        "(es. G1A + G1P + L1s + L1i).\n\n"
        "1. Inserisci i dadi a tamburo D nelle traverse L, con la fessura verso la testata e il foro filettato "
        "allineato al foro Ø11.\n"
        "2. Incolla le spine S nelle testate delle traverse (solo lì). Lascia sporgere 20 mm.\n"
        "3. Appoggia le due gambe sul pavimento, faccia interna in alto. Infila le traverse sulle spine della gamba "
        "anteriore.\n"
        "4. Dalla faccia anteriore della gamba infila i bulloni B1 con rondella e avvitali nel dado a tamburo. "
        "Stringi con moderazione.\n"
        "5. Ripeti con la gamba posteriore (bulloni dalla faccia posteriore).\n"
        "6. Controlla la squadra misurando le diagonali del telaio: devono essere uguali entro 2 mm. "
        "Poi stringi a fondo.\n"
        "7. Pulisci subito la colla uscita."), width=58, fs=8.6)
    img(fig, "man_f4_telai.png", [0.47, 0.12, 0.52, 0.78], crop=(100, 900, 40, 1480))
    pdf.savefig(fig); plt.close(fig)

    # ================= fase 5
    fig = page("Collegamento dei telai", "Fase 5")
    img(fig, "man_f5_collegamento.png", [0.36, 0.08, 0.63, 0.84], crop=(80, 940, 40, 1480))
    para(fig, 0.04, 0.89, (
        "Serve un aiutante. Lavora con il tavolo in piedi, sul pavimento piano.\n\n"
        "1. Prepara le traverse longitudinali: dadi a tamburo D e spine S incollate in entrambe le testate.\n"
        "2. Telaio 1 + telaio 2 con le traverse posteriori dei cassetti PCs e PCi:\n"
        "   – lato gamba 1: bullone B2 dalla faccia sinistra di G1P (lamatura);\n"
        "   – lato gamba 2: avvita a metà una barra R nel dado della PCs passando dal foro di G2P. Fai lo stesso "
        "con la PCi.\n"
        "3. Aggiungi il telaio 3 con le traverse posteriori della seduta PSs e PSi: la barra R che sporge da G2P "
        "entra nel loro dado. Ruota i dadi a tamburo con il cacciavite per tirare le traverse contro la gamba.\n"
        "4. Telaio 4 con le traverse posteriori della ricarica PRs e PRi: barre R in G3P, bulloni B2 dalla "
        "faccia destra di G4P.\n"
        "5. Traverse anteriori della ricarica ARs e ARi tra G3A e G4A: bulloni B2 dalla faccia sinistra di G3A "
        "(lato seduta) e dalla faccia destra di G4A.\n"
        "6. Prima di stringere tutto: controlla che il tavolo appoggi su tutte le 8 gambe e misura le "
        "diagonali di ogni campata, viste dall'alto (uguali entro 3 mm).\n"
        "7. Stringi tutti i nodi partendo dal centro verso le estremità."), width=52, fs=8.4)
    a = fig.add_axes([0.04, 0.08, 0.30, 0.20]); sec_nodo_centrale(a)
    pdf.savefig(fig); plt.close(fig)

    # ================= fase 6
    fig = page("Listelli e ripiani bassi", "Fase 6")
    img(fig, "man_f6_ripiani.png", [0.40, 0.10, 0.59, 0.80], crop=(90, 920, 40, 1480))
    para(fig, 0.04, 0.89, (
        "Listelli reggiripiano 30×40 (6 pezzi): avvitati sulle facce interne delle traverse laterali inferiori, "
        "con il filo superiore a 18 mm sotto il filo della traversa (i ripiani OSB restano a filo).\n\n"
        "• Campate cassetti e ricarica: listelli da 560, per tutta la profondità.\n"
        "• Campata seduta: listelli da 260 contro la traversa posteriore.\n\n"
        "Viti: 5×70, preforo Ø3 nella traversa, Ø5 svasato nel listello, più colla.\n"
        "• Listelli da 560: 3 viti a 130, 280 e 430 dalla testata anteriore.\n"
        "• Listelli da 260: 2 viti a 50 e 130 dall'inizio del listello.\n"
        "NON avvitare entro 100 mm dalle testate delle traverse: lì ci sono bullone e dado a tamburo.\n\n"
        "Ripiani OSB 18: appoggiali sui listelli, lato liscio in alto, e fissa ciascuno con 2 viti 4×35 per lato, "
        "preforo Ø3. Carico consigliato: fino a 30 kg sui ripiani da 500, fino a 15 kg su quello della seduta "
        "(luce 700)."), width=55, fs=8.4)
    ax = fig.add_axes([0.04, 0.08, 0.32, 0.25]); ax.set_aspect("equal"); ax.axis("off")
    R(ax, 0, 0, 80, 120, WOOD2); R(ax, 80, 62, 30, 40, WOOD); R(ax, 80, 102, 160, 18, "#d9c08a")
    for y in (82,): R(ax, 20, y - 2.5, 90, 5, STEEL)
    ax.text(5, 82, "vite 5×70", fontsize=6.3, va="center", color="white")
    ax.text(120, 111, "ripiano OSB 18", fontsize=6.5, va="center"); ax.text(115, 75, "listello 30×40", fontsize=6.5)
    ax.text(5, 20, "traversa\nlaterale inf.", fontsize=6.3)
    dim(ax, 240, 102, 240, 120, 10, "18", vertical=True)
    ax.set_xlim(-10, 290); ax.set_ylim(-15, 140)
    ax.set_title("Sezione: ripiano sul listello", fontsize=8, loc="left")
    pdf.savefig(fig); plt.close(fig)

    # ================= fase 7 piano
    fig = page("Piano di lavoro", "Fase 7")
    img(fig, "man_f7_piano.png", [0.42, 0.40, 0.57, 0.52], crop=(110, 950, 40, 1480))
    para(fig, 0.04, 0.89, (
        "1. Fai i 2 fori passacavi Ø60. Incolla tra loro i due rinforzi OSB (36 mm) e poi incollali sotto il piano: "
        "posizione x 1440–1920, y 80–600 (a filo della traversa ARs e tra le traverse L3s e L4s). Colla su tutta "
        "la superficie + 12 viti 5×60 dal basso, preforo Ø3, svasate. Le viti non devono stare entro 40 mm "
        "dai 4 fori della base piastre (x 1615 e 1745, y 155).\n"
        "2. Appoggia il piano sul telaio, a filo dietro e sui lati (sporgenza zero).\n"
        "3. Fissalo con le squadrette Q avvitate all'interno delle traverse superiori: l'asola va sotto il piano "
        "e la vite 4,5×25 al centro dell'asola, così il legno può muoversi con l'umidità.\n"
        "4. Se monterai l'alzatina, le sue barre bloccheranno il piano anche sul retro."), width=56, fs=8.4)
    rows = [["traverse posteriori PCs, PSs, PRs", "2 per traversa, a 100 dalle gambe", "6"],
            ["L1s (faccia destra)", "a 200 e 450 dal fronte", "2"],
            ["L2s (faccia sinistra e destra)", "1 a sinistra, 2 a destra", "3"],
            ["L3s (faccia sinistra)", "a 200 e 450 dal fronte", "2"],
            ["campata ricarica", "nessuna (vedi fase 8)", "–"],
            ["totale", "", "13 (+3 di scorta)"]]
    at = fig.add_axes([0.04, 0.32, 0.37, 0.18]); table(at, rows, ["dove", "posizione", "n°"], [0.42, 0.45, 0.13], fs=6.8, sc=1.3)
    ax = fig.add_axes([0.44, 0.06, 0.52, 0.30]); ax.set_aspect("equal"); ax.axis("off")
    R(ax, 0, 0, 80, 120, WOOD2); R(ax, -200, 120, 380, 40, "#efe0c2")
    ax.add_patch(Polygon([[-4, 75], [0, 75], [0, 116], [-40, 116], [-40, 120], [-4, 120]], fc=STEEL, ec=INK, lw=0.6))
    ax.add_patch(Polygon([[-4, 75], [-4, 120], [-40, 120], [-40, 116], [0, 116]], fc=STEEL, ec=INK, lw=0.6))
    R(ax, -26, 120, 4, 25, STEEL, lw=0.4); R(ax, -2, 92, 25, 4, STEEL, lw=0.4)
    ax.text(-190, 100, "squadretta Q", fontsize=6.5); ax.text(30, 60, "traversa\nsuperiore", fontsize=6.5)
    ax.text(-190, 140, "piano 40", fontsize=6.5)
    ax.text(100, 100, "vite 4,5×25 nell'asola\n(il piano può muoversi)", fontsize=6.5)
    ax.set_xlim(-210, 300); ax.set_ylim(40, 170)
    ax.set_title("Sezione: squadretta di fissaggio del piano", fontsize=8, loc="left")
    pdf.savefig(fig); plt.close(fig)

    # ================= fase 8 ricarica
    fig = page("Zona ricarica: base delle piastre", "Fase 8")
    img(fig, "man_f8_ricarica.png", [0.52, 0.42, 0.47, 0.50], crop=(110, 900, 40, 1480))
    ax = fig.add_axes([0.03, 0.06, 0.62, 0.40]); ax.set_aspect("equal"); ax.axis("off")
    R(ax, 0, 580, 80, 120, WOOD2)                         # ARs
    R(ax, 0, 700, 640, 40, "#efe0c2", hatch="///")        # piano
    R(ax, 80, 664, 520, 36, "#d9c08a", hatch="\\\\")       # rinforzo
    R(ax, 80, 658, 220, 6, STEEL)                          # contropiastra
    R(ax, 0, 740, 180, 12, "#3a3f45"); R(ax, 0, 752, 180, 10, "#9aa7b4")
    for y, zb, lab_ in ((25, 580, "M10×200"), (155, 658, "M10×110")):
        R(ax, y - 5, zb - 14, 10, 752 - zb + 14, STEEL, lw=0.5)
        ax.add_patch(Polygon([[y - 9, 752], [y + 9, 752], [y + 5, 746], [y - 5, 746]], fc=STEEL, ec=INK, lw=0.5))
        R(ax, y - 9, zb - 9, 18, 9, "#7f8890", lw=0.5)
        ax.text(y, zb - 30, lab_, ha="center", fontsize=6.5)
    for y in (380, 520): R(ax, y - 2.5, 660, 5, 60, "#666", lw=0.3)
    ax.text(440, 640, "viti 5×60 + colla", fontsize=6.5)
    ax.text(200, 590, "traversa ARs", fontsize=6.5) if False else ax.text(5, 610, "ARs", fontsize=6.5)
    ax.text(330, 720, "piano 40", fontsize=6.5); ax.text(330, 677, "rinforzo OSB 36", fontsize=6.5)
    ax.text(310, 650, "contropiastra 6", fontsize=6.5)
    ax.text(190, 760, "base 12 + piastra attrezzo 10", fontsize=6.5)
    dim(ax, 0, 762, 25, 762, 14, "25", fs=6.5); dim(ax, 0, 790, 155, 790, 10, "155", fs=6.5)
    ax.text(0, 540, "← fronte", fontsize=6.5, color=MUTE)
    ax.set_xlim(-20, 660); ax.set_ylim(520, 820)
    ax.set_title("Sezione verticale in corrispondenza delle viti (x 1615 e 1745)", fontsize=8, loc="left")
    para(fig, 0.04, 0.89, (
        "1. Appoggia la base d'acciaio sul piano: bordo anteriore a filo del piano, centrata nella campata "
        "(centro a x = 1680, cioè 240 mm dalla gamba destra). Bloccala con due morsetti.\n"
        "2. Usa i suoi fori come dima: fora Ø11 verticale.\n"
        "   – 2 fori ANTERIORI (25 dal fronte): attraversano piano e traversa ARs (160 mm). Punta lunga, "
        "fora metà da sopra; finisci da sotto se serve.\n"
        "   – 2 fori POSTERIORI (155 dal fronte): attraversano piano e rinforzo.\n"
        "3. Da sotto, presenta la contropiastra sui 2 fori posteriori e segna/foralo se non è già forata.\n"
        "4. Viti TSPEI dall'alto (testa svasata a filo della base):\n"
        "   – anteriori M10×200: rondella larga + dado autobloccante sotto la traversa ARs;\n"
        "   – posteriori M10×110: dado autobloccante sotto la contropiastra.\n"
        "5. Stringi in croce. Le piastre degli attrezzi si bloccano poi con le 2 manopole M12."), width=62, fs=8.3)
    pdf.savefig(fig); plt.close(fig)

    # ================= fase 9 piedini, muro, predisposizioni
    fig = page("Piedini, fissaggio a muro e predisposizioni", "Fase 9")
    img(fig, "man_f9_base.png", [0.50, 0.40, 0.49, 0.52], crop=(150, 900, 40, 1480))
    ax = fig.add_axes([0.55, 0.04, 0.30, 0.34]); ax.set_aspect("equal"); ax.axis("off")
    R(ax, 680, 450, 120, 250, WOOD); R(ax, 560, 700, 260, 40, "#efe0c2", hatch="///")
    R(ax, 734, 625, 12, 75, "white", ec=HCOL["M"], ls="--")
    R(ax, 730, 632.5, 70, 15, "white", ec=HCOL["T"], ls="--"); ax.add_patch(Circle((740, 640), 7.5, fc=STEEL, ec=INK))
    ax.plot([800, 800], [430, 760], color="#555", lw=2); ax.text(806, 450, "muro", fontsize=6.5, rotation=90)
    ax.text(570, 715, "piano (non forato)", fontsize=6.3); ax.text(600, 560, "gamba\nposteriore", fontsize=6.3)
    ax.text(600, 660, "dado D\ngià inserito", fontsize=6.3, color=HCOL["T"]); ax.text(690, 680, "Ø12", fontsize=6, color=HCOL["M"])
    dim(ax, 680, 450, 800, 450, -20, "120", fs=6.3); dim(ax, 740, 760, 800, 760, 10, "60", fs=6.3)
    ax.set_xlim(540, 840); ax.set_ylim(400, 790)
    ax.set_title("Predisposizione alzatina nelle gambe posteriori", fontsize=8, loc="left")
    para(fig, 0.04, 0.89, (
        "Piedini\n1. Inclina il tavolo, avvita gli inserti I nei fori Ø14 sotto le gambe (con una vite M10 e "
        "controdado) e poi i piedini.\n2. Porta il tavolo al muro e livellalo agendo sui piedini.\n\n"
        "Fissaggio a muro (indispensabile per le presse)\n"
        "3. 4 angolari a L: 2 sulla faccia esterna di G1P e 2 su quella di G4P, a 300 e 450 da terra. Viti 5×40 "
        "nella gamba, tasselli Ø8 nel muro (nylon per mattone pieno, specifici per forato; su cartongesso "
        "cerca il montante metallico). Se c'è il battiscopa, metti uno spessore dietro le gambe.\n\n"
        "Predisposizioni per i moduli\n"
        "• Alzatina (modulo 3): in ogni gamba posteriore il foro Ø12 in testa e il dado a tamburo D inserito "
        "dal retro (fase 4), con il foro filettato in verticale: PROVA avvitando di qualche giro una barra M10 "
        "dal foro in testa, poi sfilala. Fallo ADESSO, prima del piano: dopo non si raggiungono più. I fori nel piano si "
        "fanno solo quando monti l'alzatina. Conserva i 4 montanti M1–M4.\n"
        "• Cassettiera (modulo 2): nessuna lavorazione. La campata sinistra con il suo ripiano è già pronta; "
        "le guide del cassetto appeso si avvitano direttamente su L1s e L2s."), width=62, fs=8.2)
    pdf.savefig(fig); plt.close(fig)

    # ================= fase 11
    fig = page("Canaline, elettrico e controlli finali", "Fase 10")
    img(fig, "man_f7_piano.png", [0.50, 0.40, 0.49, 0.52], crop=(110, 950, 40, 1480))
    para(fig, 0.04, 0.89, (
        "Canaline e ciabatta\n"
        "1. Una canalina per campata, sotto il piano, tra la traversa posteriore e i passacavi: "
        "fascia y 615–715 dal fronte. Fissala sotto il piano con viti 4×25 (il piano è spesso 40: non usare viti più lunghe).\n"
        "2. La ciabatta va dentro la canalina della campata seduta, con l'interruttore raggiungibile dal fronte.\n"
        "3. I cavi passano da una campata all'altra nei fori Ø35 delle traverse L2s e L3s (560 dal fronte "
        "del tavolo). Salgono sul piano dai passacavi Ø60.\n"
        "4. Usa fascette e tieni i cavi alti, lontani dalla zona del futuro cassetto appeso (campata sinistra).\n"
        "5. Un solo cavo di alimentazione scende a muro, fissato alla gamba G2P o G3P."), width=60, fs=8.4)
    checks = ["Il tavolo appoggia su 8 piedini senza dondolare (livella sul piano in due direzioni)",
              "Tutti i 32 nodi stretti; dopo 2–3 settimane ristringi (il legno si assesta)",
              "Diagonali delle campate uguali: nessun gioco spingendo il piano avanti-indietro",
              "Fissaggi a muro serrati: prova con la pressa in calibratura, il tavolo non deve muoversi",
              "Base piastre: le 4 viti stringono, le manopole bloccano la piastra senza gioco",
              "Campata cassetti libera e ripiano fissato: pronta per la cassettiera (modulo 2)",
              "Nessun cavo schiacciato tra cassetti, guide o traverse",
              "Finitura del piano: 2–3 mani di olio, leggera carteggiatura 240 tra una mano e l'altra"]
    para(fig, 0.04, 0.46, "Controlli finali", fs=10.5, weight="bold")
    y = 0.43
    for c in checks:
        fig.patches.append(Rectangle((0.045, y - 0.016), 0.012, 0.016, transform=fig.transFigure, fc="white", ec=INK, lw=0.7))
        para(fig, 0.065, y, c, width=110, fs=8.6); y -= 0.042
    pdf.savefig(fig); plt.close(fig)

print("pagine:", PAGE[0])
