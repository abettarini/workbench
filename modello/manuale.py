"""Manuale tavolo BASE – KVH 80×120, 4 telai laterali + 3 fasce -> tavolo_base_manuale.pdf"""
from manlib import *
from manlib import PAGE, TOC, FOOTER
from openpyxl import load_workbook
from osb import OSB_CUTS, STRIP
import disegni
# ------------------------------------------------------------------ codici, misure dal modello
legs = [n for n in parts if n.startswith("Gamba")]
rails = [n for n in parts if n.startswith("Trav.")]
fasce = [n for n in parts if n.startswith("Fascia")]
risers = [n for n in parts if n.startswith("Montante")]
def length(n):
    x0, y0, z0, x1, y1, z1 = parts[n]["box"]; return round(max(x1 - x0, y1 - y0, z1 - z0))
Fb, Ffd, Ffh = P["Fb"], P["Ff_d"], P["Ff_h"]
yF0, yB1 = Ffd, D - Fb                       # facce esterne delle gambe
yF1, yB0 = yF0 + Ly, yB1 - Ly                # testate delle traverse laterali
LAT = yB0 - yF1                               # lunghezza traverse laterali
FAS = length("Fascia ant. alta")
YM = (yB0 + yB1) / 2                          # asse barre alzatina
XM = [x + Lx / 2 for x in d["legs_x"]]
cable = next(h for h in holes if h["code"] == "C" and h["part"].startswith("Trav."))
CAB_Y, CAB_Z = cable["p0"][1] - yF1, LEG_H - cable["p0"][2]
tray = parts["Canalina seduta"]["box"]
rinf = parts["Rinforzo piano ricarica"]["box"]
NB = len(cf["kvh_bars"])

def screws_of(fas):
    return sorted({(round(h["p0"][0] - (parts[fas]["box"][0])), round(h["p0"][2])) for h in holes if h["part"] == fas and h["code"] == "V"})

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
        ax.add_patch(Polygon([[6, 12], [12, 16], [12, 24], [6, 28]], fc="#d8b84a", ec=INK))
        R(ax, 12, 16.5, 78, 7, "#d8b84a")
        for x in range(40, 88, 3): ax.plot([x, x + 1.5], [16.5, 23.5], lw=0.4, color=INK)
        ax.add_patch(Polygon([[90, 16.5], [96, 20], [90, 23.5]], fc="#d8b84a", ec=INK))
    elif kind == "W":
        R(ax, 12, 17, 3, 6, STEEL); ax.add_patch(Polygon([[15, 18], [70, 19], [80, 20], [70, 21], [15, 22]], fc=STEEL, ec=INK))
        ax.add_patch(Polygon([[8, 14], [12, 17], [12, 23], [8, 26]], fc="#c8cdd2", ec=INK))
    elif kind == "K":
        R(ax, 10, 14, 70, 12, "#bfbfbf"); R(ax, 6, 12, 4, 16, "#999")
        for x in range(20, 78, 6): ax.plot([x, x], [14, 26], lw=0.5, color="#666")
    elif kind == "Q":
        ax.add_patch(Polygon([[30, 8], [70, 8], [70, 12], [34, 12], [34, 34], [30, 34]], fc=STEEL, ec=INK))
        R(ax, 46, 9, 12, 2, "white", ec=INK, lw=0.5); R(ax, 31, 18, 2, 8, "white", ec=INK, lw=0.5)
        ax.text(60, 22, "asola", fontsize=6)
    elif kind == "X":
        R(ax, 10, 12, 30, 16, "#222"); R(ax, 40, 18, 20, 4, STEEL); R(ax, 60, 14, 5, 12, STEEL)

HW = [  # codice, nome, quantità, dove, disegno
    ("B1", "Vite M10×180 testa cilindrica (TCEI) + rondella Ø20", "16", "traverse laterali (L) dei 4 telai: dalla faccia esterna della gamba", "B1"),
    ("B2", "Vite M10×140 testa cilindrica (M10×180 accorciata) + rondella", "4", "traverse basse anteriori ACi e ARi", "B2"),
    ("D", "Dado a tamburo M10 (Ø15 circa)", "24", "20 nelle testate delle traverse + 4 nelle gambe posteriori (predisposizione alzatina)", "D"),
    ("S", "Spina in faggio Ø12×50", "40", "2 per testata di traversa", "S"),
    ("V", "Vite strutturale per legno 8×160 (Rothoblaas TPS)", "24", "fasce FA, FPa, FPb: 2 per gamba, perpendicolari", "V"),
    ("I", "Dado ragno M10 (o inserto filettato) + piedino M10", "8", "sotto ogni gamba", "I"),
    ("Q", "Squadretta con asola + viti 4,5×25", "16", "fissaggio del piano a fasce e traverse laterali alte", "Q"),
    ("W", "Viti legno: 5×60, 5×70, 4×35, 4,5×25", "sfuse", "rinforzo ricarica, listelli, ripiani, squadrette", "W"),
    ("X", "Viti TSPEI M10 + dadi autobloccanti + rondelle larghe", "2+2", "base piastre ricarica: 2 × M10×160 (anteriori) e 2 × M10×110", "X"),
    ("K", "Tassello per telai Ø10 L 160 con vite", "4", "fissaggio a muro attraverso la fascia posteriore alta", "K"),
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
        note = {"B1": "bullone laterale B1", "B2": "bullone traversa bassa B2", "S": "spina S", "I": "dado ragno I",
                "M": "predisp. alzatina: foro barra", "T": "predisp. alzatina: dado D",
                "V": "preforo vite fascia V"}.get(h["code"], h["kind"])
        if h["cb"]: note += f", lamatura Ø{h['cb'][0]}×{h['cb'][1]}"
        if f == "T": note += " – punta lunga"
        if h["code"] == "V": note += " (" + h["note"].split(":")[0] + ")"
        lev = "sup." if (v > 400 and f in "ADPS") else ("inf." if f in "ADPS" else "")
        rows.append([str(k), FACE_NAME[f], pos, hor, f"Ø{h['d']:.0f}", depth, (lev + " " + note).strip()])
        rcol.append(None)
    ax.set_xlim(-95, top_off + Lx + 10); ax.set_ylim(-35, LEG_H + 70)
    at = fig.add_axes(rect_tab)
    table(at, rows, ["n°", "faccia", "dalla testa", "da sinistra", "Ø", "prof.", "cosa"],
          [0.045, 0.10, 0.09, 0.16, 0.05, 0.085, 0.43], fs=6.6, sc=1.45)
    return hs

# ------------------------------------------------------------------ sezioni
def sec_nodo_bassa(ax):
    """vista dall'alto: gamba G1A + traversa bassa ACi (bullone B2 dalla faccia opposta)"""
    ax.set_aspect("equal"); ax.axis("off")
    R(ax, 0, 0, 80, 120, WOOD); R(ax, 80, 0, 220, 80, WOOD2)
    R(ax, 0, 40 - 12.5, 12, 25, "white", ls="--"); R(ax, 12, 40 - 5.5, 68 + 70, 11, "white", ec=INK, ls="--", lw=0.6)
    R(ax, 2, 40 - 8, 10, 16, STEEL); R(ax, 12, 40 - 5, 128, 10, STEEL)
    ax.add_patch(Circle((140, 40), 7.5, fc=STEEL, ec=INK)); ax.plot([133, 147], [40, 40], lw=1, color=INK)
    for dy in (-15, 15): R(ax, 55, 40 + dy - 6, 55, 12, "#e8c77a", ec=INK, lw=0.5, ls=":")
    dim(ax, 80, 80, 140, 80, 18, "60"); dim(ax, 0, 120, 80, 120, 14, "80")
    dim(ax, 300, 0, 300, 40, 12, "40", vertical=True)
    ax.text(150, 125, "dado a tamburo D\n(Ø15 dall'alto, prof. 45)", fontsize=6.3, va="bottom")
    ax.text(2, -14, "lamatura Ø25×12", fontsize=6.3, va="top")
    ax.text(175, 25, "ACi / ARi", fontsize=6.3)
    ax.text(5, 95, "gamba\nanteriore", fontsize=6.3)
    ax.text(-8, -40, "← fronte (sotto la fascia FA)", fontsize=6, color=MUTE)
    ax.set_xlim(-15, 330); ax.set_ylim(-55, 175)
    ax.set_title("A · traversa bassa: bullone B2 (dall'alto)", fontsize=8, loc="left")

def sec_laterale(ax):
    """sezione verticale lungo la profondità, sull'asse di una gamba: telaio laterale + fasce + viti"""
    ax.set_aspect("equal"); ax.axis("off")
    zc = 470
    R(ax, yF0, zc, Ly, LEG_H - zc, WOOD); R(ax, yB0, zc, Ly, LEG_H - zc, WOOD)
    R(ax, yF1, LEG_H - Rh, LAT, Rh, WOOD2)
    R(ax, 0, LEG_H - Ffh, Ffd, Ffh, "#b98d55"); R(ax, yB1, LEG_H - Rh, Fb, Rh, "#b98d55")
    R(ax, 0, LEG_H, D, P["T_top"], "#efe0c2", hatch="///")
    ax.plot([D + 3, D + 3], [zc - 20, H + 30], color="#555", lw=2.5); ax.text(D + 10, zc, "muro", fontsize=6.3, rotation=90)
    for x in (zc,): ax.plot([yF0 - 5, yF1 + 5], [x, x], color=INK, lw=0.6, ls=(0, (4, 3)))
    ax.plot([yB0 - 5, yB1 + 5], [zc, zc], color=INK, lw=0.6, ls=(0, (4, 3)))
    # viti fascia anteriore (lamatura Ø20 prof. 40)
    for (u, z) in screws_of("Fascia ant. alta")[:2]:
        R(ax, 0, z - 10, 40, 20, "white", ec=HCOL["V"], ls="--", lw=0.6)
        R(ax, 40, z - 3.5, 160, 7, "#d8b84a", lw=0.5); R(ax, 37, z - 7.5, 3, 15, "#a8861c", lw=0.4)
    for (u, z) in screws_of("Fascia post. alta")[:2]:
        R(ax, D - 160, z - 3.5, 160, 7, "#d8b84a", lw=0.5); R(ax, D - 3, z - 7.5, 3, 15, "#a8861c", lw=0.4)
    # bulloni laterali
    zb = LEG_H - 90
    R(ax, yF0, zb - 12.5, 12, 25, "white", ls="--", lw=0.5); R(ax, yF0 + 2, zb - 5, 178, 10, STEEL, lw=0.5)
    R(ax, yB1 - 12, zb - 12.5, 12, 25, "white", ls="--", lw=0.5); R(ax, yB1 - 180, zb - 5, 178, 10, STEEL, lw=0.5)
    for yy in (yF1 + 60, yB0 - 60):
        R(ax, yy - 7.5, LEG_H - Rh, 15, 45, "#9aa3ab", lw=0.5)
    dim(ax, 0, H, Ffd, H, 22, f"{Ffd}", fs=6.3); dim(ax, Ffd, H, yF1, H, 22, f"{Ly}", fs=6.3)
    dim(ax, yF1, H, yB0, H, 22, f"{LAT}", fs=6.3); dim(ax, yB0, H, yB1, H, 22, f"{Ly}", fs=6.3)
    dim(ax, yB1, H, D, H, 22, f"{Fb}", fs=6.3)
    dim(ax, 0, LEG_H - Ffh, 0, LEG_H, -14, f"{Ffh}", vertical=True, fs=6.3)
    dim(ax, D, LEG_H - Rh, D, LEG_H, 30, f"{Rh}", vertical=True, fs=6.3)
    ax.text(-30, LEG_H - Ffh - 22, "FA (di piatto)", fontsize=6.2)
    ax.text(yB1 + 4, LEG_H - Rh - 22, "FPa", fontsize=6.2)
    ax.text(yF1 + 120, LEG_H - Rh / 2, "traversa laterale alta", fontsize=6.2, va="center")
    ax.text(yF0 + 4, zc + 40, "gamba\nant.", fontsize=6.2); ax.text(yB0 + 4, zc + 40, "gamba\npost.", fontsize=6.2)
    ax.text(-30, LEG_H - Ffh - 70, "vite 8×160 in lamatura\nØ20 prof. 40 (tappo)", fontsize=5.6, color=HCOL["V"])
    ax.text(yB0 - 10, LEG_H - Rh - 40, "viti 8×160", fontsize=5.6, color=HCOL["V"], ha="right")
    ax.text(yF0 + 14, zb - 22, "B1", fontsize=6, color=RED); ax.text(yB1 - 30, zb - 22, "B1", fontsize=6, color=RED)
    ax.set_xlim(-50, D + 60); ax.set_ylim(zc - 30, H + 70)
    ax.set_title("B · sezione sull'asse di una gamba (fronte a sinistra, muro a destra)", fontsize=8, loc="left")

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
        bz, sz, nut_from, title = 90, 35, "alto", "Traversa BASSA ANTERIORE (ACi, ARi): testata e fianco"
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
pal = {FAS: "#b98d55", 700: "#d9b382", LAT: "#c99a62", 500: "#bd8d55", 480: "#b07f4a", 250: "#e6caa0"}
with PdfPages("tavolo_base_manuale.pdf") as pdf:
    # ================= copertina
    fig = plt.figure(figsize=A4); PAGE[0] += 1
    fig.text(0.05, 0.9, "Tavolo da lavoro", fontsize=30, weight="bold")
    fig.text(0.05, 0.85, "Modulo 1 · Tavolo base – manuale di lavorazione e montaggio", fontsize=14, color=MUTE)
    img(fig, "man_f9_base.png", [0.36, 0.10, 0.62, 0.72], crop=(150, 900, 40, 1480))
    fases = ["Prima di iniziare · Ferramenta · Distinta materiali (BOM)", "Codici dei pezzi · Viste quotate",
             "Fase 1 · Taglio", "Fase 2 · Foratura (gambe, traverse, fasce, piano)", "Fase 3 · Levigatura e finitura",
             "Fase 4 · Telai laterali", "Fase 5 · Traverse basse e fasce", "Fase 6 · Listelli e ripiani bassi",
             "Fase 7 · Piano", "Fase 8 · Zona ricarica", "Fase 9 · Piedini, fissaggio a muro, predisposizioni",
             "Fase 10 · Canaline, elettrico e controlli finali", "",
             "Moduli aggiuntivi (manuali separati):", "  Modulo 2 · Cassettiera", "  Modulo 3 · Alzatina con mensola"]
    fig.text(0.05, 0.76, "Contenuto", fontsize=11, weight="bold")
    fig.text(0.05, 0.735, "\n".join(fases), fontsize=9, va="top", linespacing=1.9)
    fig.text(0.05, 0.08, "Struttura: 4 telai laterali imbullonati uniti da 3 fasce a tutta lunghezza avvitate.\n"
             "Quote in mm. Ogni foro è stato verificato sul modello 3D: nessun foro ne interseca un altro\n"
             "(minimo 7,5 mm di legno tra due fori).", fontsize=8, color=MUTE)
    pdf.savefig(fig); plt.close(fig)

    # ================= prima di iniziare
    fig = page("Prima di iniziare")
    para(fig, 0.04, 0.89, "Attrezzi", fs=11, weight="bold")
    para(fig, 0.04, 0.86, (
        "• Troncatrice o sega circolare con guida (tagli a 90° precisi; le fasce sono lunghe 1990)\n"
        "• Trapano a colonna oppure guida per trapano (fori perpendicolari)\n"
        "• Punte legno: Ø3, Ø5, Ø9, Ø11, Ø12; punta lunga Ø12 da 300 mm; punta Ø5 da almeno 120 mm\n"
        "• Punte Forstner: Ø15, Ø20, Ø25, Ø35; sega a tazza Ø60; svasatore\n"
        "• Avvitatore con inserto TX40 (viti 8×160), chiave a brugola 8 (TCEI M10), chiave 17\n"
        "• Cacciavite piatto largo (per orientare i dadi a tamburo)\n"
        "• 4 morsetti da almeno 600 mm + 2 morsetti lunghi o cinghie per le fasce\n"
        "• Squadra, metro, matita, livella\n"
        "• Levigatrice orbitale con carte 80 – 120 – 180\n"
        "• Colla vinilica D3, pennello, stracci"), width=62, fs=8.6)
    para(fig, 0.52, 0.89, "Verifica prima di tagliare e forare", fs=11, weight="bold")
    para(fig, 0.52, 0.86, (
        "1. Sezione reale delle travi: devono essere 80×120. Se misurano 78×118 le quote dei fori restano valide "
        "(sono riferite alla testa e all'asse dei pezzi), ma ricontrolla campate e profondità.\n"
        "2. Lunghezza delle barre: le fasce sono 1990 perché da una barra da 4000 ne escono due (taglio 4 mm + "
        "rifilatura 10). Se le barre sono più corte di 4000, accorcia tutte e tre le fasce della stessa misura.\n"
        "3. Dado a tamburo: non lo vendono Tecnomat, OBI e Leroy Merlin (ferramenta o online). Il manuale usa Ø15: "
        "se il tuo è Ø14 o Ø16 usa la Forstner dello stesso diametro.\n"
        "4. Piedini: le gambe sono da 700 mm e il piano finito è a 740 senza piedini. Per restare a 740 con i piedini, "
        "accorcia tutte le gambe dal lato del PIEDE: le quote dei fori 'dalla testa' non cambiano.\n"
        "5. Il muro: tipo (pieno, forato, cartongesso) e battiscopa, che può allontanare il tavolo dal muro."),
        width=60, fs=8.4)
    para(fig, 0.04, 0.5, "Convenzioni del manuale", fs=11, weight="bold")
    para(fig, 0.04, 0.47, (
        "• Fronte = lato dove ti siedi. Sinistra/destra viste stando seduto davanti al tavolo.\n"
        "• Gambe numerate da 1 (sinistra) a 4 (destra); A = anteriore, P = posteriore: G1A … G4P.\n"
        "• Traverse laterali L1s…L4i (s = alta, i = bassa); traverse basse anteriori ACi e ARi; fasce FA, FPa, FPb.\n"
        "• Quote dei fori nelle gambe 'dalla testa' (estremità alta) e 'da sinistra' guardando quella faccia da fuori.\n"
        "• Nelle traverse le quote sono dal filo superiore del pezzo e dalla testata.\n"
        "• Passante = il foro attraversa tutto il pezzo; il punto di uscita è indicato con l'apice (es. 3')."),
        width=62, fs=8.6)
    box_note(fig, 0.52, 0.10, 0.44, 0.38, "Come sta in piedi il tavolo",
             "• 4 TELAI LATERALI: gamba anteriore + gamba posteriore + traversa laterale alta e bassa. Nodi con "
             "bullone M10 + dado a tamburo + 2 spine Ø12 (bullone a 90 dalla testa della traversa, spine a 35).\n"
             "• 3 FASCE a tutta lunghezza li uniscono: FPa e FPb dietro, di coltello, contro il muro; FA davanti, "
             "posata di piatto sotto il bordo del piano. Ogni fascia si avvita a ogni gamba con 2 viti 8×160 "
             "perpendicolari: lavorano nel legno di fianco, tengono molto e si possono togliere e rimettere.\n"
             "• 2 traverse basse anteriori ACi e ARi chiudono le campate dei ripiani.\n"
             "• Il piano avvitato e il fissaggio a muro completano la rigidezza: indispensabili per le presse.",
             fs=8.1, width=66)
    pdf.savefig(fig); plt.close(fig)

    # ================= ferramenta
    fig = page("Ferramenta – codici usati nel manuale")
    for i, (c, name, q, where, k) in enumerate(HW):
        col, row = i % 2, i // 2
        x = 0.04 + col * 0.48; y = 0.80 - row * 0.15
        a = fig.add_axes([x, y, 0.13, 0.10]); draw_hw(a, k)
        fig.text(x + 0.14, y + 0.08, f"{c}", fontsize=13, weight="bold", color=HCOL.get(c, INK))
        fig.text(x + 0.18, y + 0.083, name, fontsize=8.3, weight="bold", va="center")
        fig.text(x + 0.18, y + 0.055, f"Quantità: {q}", fontsize=8)
        para(fig, x + 0.18, y + 0.042, where, width=44, fs=7.6, color=MUTE)
    fig.text(0.04, 0.04, "Colla vinilica D3 per spine, rinforzo e listelli. Prezzi e negozi nella distinta materiali (pagina seguente) "
             "e nel foglio tavolo_base_costi.xlsx.", fontsize=8, color=MUTE)
    pdf.savefig(fig); plt.close(fig)

    # ================= distinta materiali (BOM)
    ws = load_workbook("tavolo_base_costi.xlsx", data_only=True)["Distinta costi"]
    bom, tot, ver = [], 0, 0
    for r in ws.iter_rows(min_row=5, values_only=True):
        if not r[0] or not r[1]: break
        cat, art, use, q, u, pr, t, src, shop = r[:9]
        tot += t or 0; ver += (t or 0) if str(src).startswith("verificato") else 0
        bom.append([cat, "\n".join(textwrap.wrap(art, 46)), "\n".join(textwrap.wrap(str(use), 44)), f"{q:g} {u}",
                    shop, f"{pr:.2f}", f"{t:.2f}", "sì" if str(src).startswith("verificato") else "stima"])
    for part_, rows_ in (("1/2", bom[:15]), ("2/2", bom[15:])):
        fig = page(f"Distinta materiali e costi (BOM) {part_}")
        at = fig.add_axes([0.03, 0.10, 0.94, 0.80])
        tb = table(at, rows_, ["categoria", "articolo", "uso", "q.tà", "negozio", "€ cad.", "€ tot.", "verificato"],
                   [0.10, 0.27, 0.26, 0.06, 0.10, 0.06, 0.07, 0.08], fs=6.6, sc=2.25,
                   colors=[None if r[7] == "sì" else "#fff6c8" for r in rows_])
        if part_ == "2/2":
            fig.text(0.97, 0.07, f"TOTALE modulo 1: {tot:.2f} €   (prezzi verificati {ver:.2f} € · stime {tot - ver:.2f} €)",
                     fontsize=9.5, weight="bold", ha="right")
        fig.text(0.03, 0.04, "Prezzi letti sui siti di Tecnomat, OBI e Leroy Merlin il 18/10/2026 (negozio di riferimento Tecnomat Roma "
                 "Prenestina). Righe gialle = stime. Link ai prodotti nel file tavolo_base_costi.xlsx.", fontsize=7.2, color=MUTE)
        pdf.savefig(fig); plt.close(fig)

    # ================= codici pezzi
    fig = page("Codici dei pezzi")
    ax = fig.add_axes([0.03, 0.42, 0.50, 0.47]); ax.set_aspect("equal"); ax.axis("off")
    for n in legs + rails + fasce:
        if n == "Fascia post. bassa": continue
        x0, y0, z0, x1, y1, z1 = parts[n]["box"]
        fc = WOOD if n.startswith("Gamba") else ("#b98d55" if n.startswith("Fascia") else WOOD2)
        R(ax, x0, y0, x1 - x0, y1 - y0, fc, lw=0.6, ls="--" if n.startswith("Trav. inf. ant") else "-",
          alpha=0.55 if n.startswith("Trav. inf. ant") else 1)
        c = code(n)
        if n.startswith("Trav. sup. lat"): c = c[:-1] + "s/i"
        if n == "Fascia post. alta": c = "FPa / FPb"
        if n.startswith("Trav. inf. lat"): continue
        ax.text((x0 + x1) / 2, (y0 + y1) / 2, c, ha="center", va="center", fontsize=6.5, weight="bold",
                rotation=90 if (y1 - y0) > (x1 - x0) * 2 and not n.startswith("Gamba") else 0)
    ax.text(1000, -70, "FRONTE (seduta)", ha="center", fontsize=8, color=MUTE)
    ax.text(1000, 850, "RETRO (muro)", ha="center", fontsize=8, color=MUTE)
    for (a, c), lab in zip(d["bays"], ["cassetti", "seduta", "ricarica"]):
        ax.text((a + c) / 2, 420, lab, ha="center", fontsize=8, color=MUTE, style="italic")
    ax.set_xlim(-40, 2040); ax.set_ylim(-110, 900)
    ax.set_title("Pianta del telaio (vista dall'alto) – ACi e ARi tratteggiate (sono in basso)", fontsize=8.5, loc="left")
    rows = []; groups = OrderedDict()
    for n in legs + fasce + rails + risers:
        c = code(n); L = length(n)
        typ = ("gamba" if n.startswith("Gamba") else "fascia (tutta lunghezza)" if n.startswith("Fascia") else
               "traversa laterale" if ". lat." in n else "montante alzatina (conservare)" if n.startswith("Mont") else
               "traversa bassa anteriore")
        groups.setdefault((typ, L), []).append(c)
    for (typ, L), cs in groups.items():
        rows.append([typ, f"{L}", str(len(cs)), "\n".join(", ".join(cs[k:k + 4]) for k in range(0, len(cs), 4))])
    at = fig.add_axes([0.55, 0.40, 0.42, 0.49])
    table(at, rows, ["pezzo", "lungh.", "n°", "codici"], [0.40, 0.11, 0.07, 0.42], fs=7.2, sc=2.6)
    para(fig, 0.04, 0.36, (
        "Appena tagliato ogni pezzo, scrivi il codice a matita su una faccia che resterà nascosta (gambe: la testa; "
        "traverse: la faccia inferiore; fasce: la faccia verso l'interno) e una freccia verso il FRONTE.\n\n"
        "Sezioni: gambe e traverse laterali 80 (largh.) × 120 (prof./altezza); fasce posteriori 80 × 120 di coltello; fascia "
        "anteriore 120 × 80 posata di piatto (stessa trave, ruotata); ACi e ARi 80 × 120 di coltello.\n\n"
        "Gli altri pezzi hanno il loro nome: Piano (lamellare), Rinforzo, Ripiano cassetti, Ripiano ricarica, Ripiano seduta "
        "(tutti in OSB), Listelli reggiripiano. I 4 montanti M1–M4 non servono al tavolo base: tagliali, marcali e "
        "conservali per l'alzatina (modulo 3)."), width=112, fs=8.6)
    pdf.savefig(fig); plt.close(fig)

    # ================= viste quotate
    disegni.pagine_viste(page, pdf, plt)

    # ================= fase 1 taglio
    fig = page("Taglio delle travi e dei pannelli", "Fase 1")
    ax = fig.add_axes([0.04, 0.50, 0.92, 0.38]); ax.axis("off")
    pool = {}
    for n in legs + fasce + rails + risers: pool.setdefault(length(n), []).append(code(n))
    for k in pool: pool[k] = sorted(pool[k], key=lambda c: (c[0] != "G", c))
    bars = cf["kvh_bars"]
    ax.set_xlim(-300, 4250); ax.set_ylim(len(bars) * 1.5 + 0.2, -0.8)
    for i, bar in enumerate(bars):
        y = i * 1.5; x = 10
        R(ax, 0, y, 4000, 1.0, "#f4f1ec", ec="#999", lw=0.6)
        ax.text(-40, y + 0.5, f"Barra {i+1}", ha="right", va="center", fontsize=8.5, weight="bold")
        R(ax, 0, y, 10, 1.0, "#bbb", ec="none")
        for L in bar:
            c = pool[L].pop(0)
            R(ax, x, y, L, 1.0, pal.get(L, WOOD), lw=0.6)
            ax.text(x + L / 2, y + 0.33, c, ha="center", va="center", fontsize=7.5 if L > 300 else 6.5, weight="bold")
            ax.text(x + L / 2, y + 0.72, str(L), ha="center", va="center", fontsize=6.8)
            x += L + 4
        ax.text(4020, y + 0.5, f"avanzo {4000 - x:.0f}", va="center", fontsize=7.5, color=MUTE)
    ax.text(0, -0.45, f"Travi KVH 80×120 da 4 m ({NB} barre) – grigio: 10 mm di rifilatura della testa; taglio 4 mm", fontsize=8.5)
    para(fig, 0.04, 0.46, (
        "1. Rifila 10 mm a una testa di ogni barra per avere un'estremità a 90° pulita.\n"
        f"2. Le fasce da {FAS} per prime: due sulla barra 1 (la seconda è quello che resta: misurala, deve essere ≥ {FAS}). "
        "Le tre fasce devono essere identiche: segna la prima e usala come campione.\n"
        "3. Gambe (700) e traverse laterali (" + f"{LAT}" + "): tagliale con un fermo (battuta) sulla troncatrice, non misurandole una a una.\n"
        "4. Controlla ogni taglio con la squadra su due facce. Una testata storta apre il nodo.\n"
        "5. Tieni un avanzo di ~100 mm: serve per la dima di foratura.\n"
        "6. Marca subito il codice su ogni pezzo. Tecnomat taglia in negozio (1° taglio gratis, poi 1 €)."), width=66, fs=8.4)
    ax2 = fig.add_axes([0.56, 0.08, 0.40, 0.32]); ax2.set_aspect("equal"); ax2.axis("off")
    R(ax2, 0, 0, 2500, 1250, "#efe3c4")
    for (x, y), w_, h_, t in OSB_CUTS:
        R(ax2, x, y, w_, h_, "#d9c08a", lw=0.6); ax2.text(x + w_ / 2, y + h_ / 2, t, ha="center", va="center", fontsize=6)
    ax2.text(1800, 900, "avanzo ≈ 1,7 m²\n(utile per la cassettiera)", ha="center", va="center", fontsize=6.5, color=MUTE)
    ax2.set_xlim(-20, 2520); ax2.set_ylim(-20, 1270)
    ax2.set_title("Pannello OSB/3 2500×1250×18 (il piano lamellare resta intero)", fontsize=8, loc="left")
    para(fig, 0.04, 0.17, (
        f"OSB: taglia prima la striscia da {STRIP} su tutta la lunghezza, poi i pezzi. Lato liscio dei ripiani verso "
        "l'alto. I due rinforzi si incollano uno sull'altro e formano 36 mm."), width=66, fs=8.4)
    pdf.savefig(fig); plt.close(fig)

    # ================= fase 2 regole e sezioni
    fig = page("Foratura: regole e sezioni dei nodi", "Fase 2")
    a = fig.add_axes([0.03, 0.56, 0.46, 0.32]); testata(a, "lat")
    a = fig.add_axes([0.51, 0.56, 0.46, 0.32]); testata(a, "long")
    a = fig.add_axes([0.02, 0.06, 0.30, 0.42]); sec_nodo_bassa(a)
    a = fig.add_axes([0.32, 0.06, 0.46, 0.44]); sec_laterale(a)
    a = fig.add_axes([0.78, 0.06, 0.21, 0.42]); sec_nodo_laterale(a)
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
    ax.set_xlim(-50, 130); ax.set_ylim(-40, 150)
    ax.set_title("Dima: avanzo di KVH 80×120×100 forato al trapano a colonna", fontsize=8.5, loc="left")
    para(fig, 0.42, 0.88, (
        "Come si costruisce\n"
        "Prendi un avanzo di trave lungo ~100 mm e fora i 3 fori passanti al trapano a colonna, perfettamente "
        "perpendicolari. Scrivi 'BASSO' sulla faccia corta di riferimento.\n\n"
        "Come si usa\n"
        "Accosta la dima alla faccia da forare, a filo del bordo di riferimento, e stringila con un morsetto. La punta "
        "segue il foro della dima e resta dritta anche col trapano a mano. Nastro sulla punta alla profondità giusta "
        "(profondità + 100 mm di dima).\n\n"
        "Orientamento\n"
        "• Traverse LATERALI (L) e relative facce delle gambe: dima con 'BASSO' verso il basso del pezzo → bullone a 90 "
        "dalla testa, spine a 35.\n"
        "• Traverse BASSE ANTERIORI (ACi, ARi) e facce laterali delle gambe anteriori 1, 2, 3, 4: dima capovolta → bullone "
        "a 30 dalla testa della traversa, spine a 85; sulla gamba la dima va a filo del bordo ANTERIORE (asse a 40).\n\n"
        "Fasce (senza dima)\n"
        "• Fori Ø9 passanti nella fascia al trapano a colonna (o con guida), poi svasatura (FPa, FPb) o lamatura Ø20 "
        "prof. 40 (FA).\n"
        "• Il preforo Ø5 nella gamba si fa a fascia montata, passando dal foro Ø9 (fase 5): così i fori coincidono.\n\n"
        "Ordine dei fori in ogni pezzo\n"
        "1. Fori Ø11 (bulloni) e Ø12 (spine) con la dima.  2. Lamature Ø25×12 con la Forstner, centrate sul Ø11.\n"
        "3. Nelle traverse: Ø15 per il dado a tamburo a 60 dalla testata, prof. 45; deve incontrare il Ø11.\n"
        "4. Smussa leggermente gli spigoli di tutti i fori."), width=78, fs=8.1)
    box_note(fig, 0.04, 0.08, 0.35, 0.30, "Profondità",
             "• Ø11 nella testata della traversa: 80 mm\n• Ø12 spine: 30 nella traversa, 25 nella gamba\n"
             "• Ø15 dado a tamburo: 45 mm (60 nelle gambe post.)\n• Ø11 nelle gambe: passante (80 o 120)\n"
             "• Lamatura bulloni: Ø25, 12 mm\n• Fasce: Ø9 passante; preforo Ø5 prof. 80 nella gamba\n\n"
             "Foro Ø11 nella testata: punta lunga almeno 200 mm (100 di dima + 80 + margine).", fs=8.2, width=58)
    pdf.savefig(fig); plt.close(fig)

    # ================= foratura gambe
    order = ["Gamba 1 ant", "Gamba 1 post", "Gamba 2 ant", "Gamba 2 post", "Gamba 3 ant", "Gamba 3 post",
             "Gamba 4 ant", "Gamba 4 post"]
    for n in order:
        fig = page(f"Foratura gamba {code(n)} – {n.lower()}", "Fase 2")
        draw_leg(fig, n, [0.02, 0.09, 0.42, 0.80], [0.46, 0.12, 0.52, 0.76])
        fig.text(0.03, 0.06, "Facce viste da fuori, testa in alto · cerchio pieno = ingresso · cerchio vuoto con apice = uscita "
                 "del foro passante · tratteggio = lamatura Ø25 · viola = preforo Ø5 delle viti delle fasce (da fare a fascia "
                 "montata) · i numeri rimandano alla tabella", fontsize=6.8, color=MUTE)
        pdf.savefig(fig); plt.close(fig)

    # ================= traverse e montanti
    fig = page("Foratura traverse e montanti", "Fase 2")
    rows = []
    for n in sorted(rails, key=lambda n: (". lat." not in n, code(n))):
        c = code(n); L = length(n); lat = ". lat." in n
        extra = []
        for h in holes:
            if h["part"] == n and h["code"] == "C":
                extra.append(f"passacavi Ø35 a {h['p0'][1] - parts[n]['box'][1]:.0f} dalla testata anteriore, "
                             f"{parts[n]['box'][5] - h['p0'][2]:.0f} dalla testa (vedi sotto)")
        rows.append([c, "laterale" if lat else "bassa anteriore", f"{L}",
                     "bullone −90 · spine −35 · dado dal BASSO" if lat else "bullone −30 · spine −85 · dado dall'ALTO",
                     "; ".join(dict.fromkeys(extra)) or "—"])
    at = fig.add_axes([0.03, 0.48, 0.94, 0.40])
    table(at, rows, ["codice", "tipo", "lungh.", "entrambe le testate (quote dal filo superiore)", "fori aggiuntivi"],
          [0.07, 0.12, 0.07, 0.32, 0.42], fs=7, sc=1.3)
    ax = fig.add_axes([0.04, 0.07, 0.42, 0.30]); ax.set_aspect("equal"); ax.axis("off")
    R(ax, 0, 0, LAT, 120, WOOD)
    zz = 120 - CAB_Z + (LEG_H - 120) - (LEG_H - 120)   # dal basso della traversa
    zz = 120 - CAB_Z
    ax.add_patch(Circle((CAB_Y, zz), 17.5, fc="white", ec=INK))
    for end in (60, LAT - 60): R(ax, end - 7.5, 0, 15, 45, "white", ec=HCOL["T"], ls="--", lw=0.7)
    dim(ax, 0, 120, CAB_Y, 120, 12, f"{CAB_Y:.0f}"); dim(ax, LAT, 120 - CAB_Z, LAT, 120, 14, f"{CAB_Z:.0f}", vertical=True)
    ax.text(0, -25, "fronte", fontsize=6.5, color=MUTE); ax.text(LAT, -25, "retro", fontsize=6.5, color=MUTE, ha="right")
    ax.set_xlim(-20, LAT + 70); ax.set_ylim(-40, 150)
    ax.set_title("L2s e L3s: foro passacavi Ø35 (Forstner), vista dal fianco", fontsize=8, loc="left")
    ax = fig.add_axes([0.52, 0.07, 0.44, 0.30]); ax.set_aspect("equal"); ax.axis("off")
    R(ax, 0, 0, 250, 120, WOOD); R(ax, 0, 60 - 6, 250, 12, "white", ec=HCOL["M"], ls="--", lw=0.8)
    dim(ax, 0, 0, 0, 60, -12, "60", vertical=True); dim(ax, 0, 120, 250, 120, 12, "250")
    ax.text(270, 60, "Ø12 passante, in asse\nlungo tutto il montante\n(60 dal filo posteriore).\n"
            "Fora 125 mm da ogni\ntesta con la punta lunga.", fontsize=7, va="center")
    ax.text(0, -25, "retro (muro)", fontsize=6.5, color=MUTE)
    ax.set_xlim(-30, 420); ax.set_ylim(-40, 150)
    ax.set_title("Montanti M1–M4 (80×120×250) per l'alzatina, vista dal fianco", fontsize=8, loc="left")
    pdf.savefig(fig); plt.close(fig)

    disegni.pagine_traverse(page, pdf, plt, "Fase 2")
    disegni.pagine_fasce(page, pdf, plt, "Fase 2")

    # ================= pannelli
    fig = page("Foratura di piano, rinforzo e contropiastra", "Fase 2")
    ax = fig.add_axes([0.03, 0.42, 0.62, 0.46]); ax.set_aspect("equal"); ax.axis("off")
    R(ax, 0, 0, 2000, 800, "#efe0c2")
    prow = []
    for h in [h for h in holes if h["part"] == "Piano di lavoro"]:
        x, y = h["p0"][0], h["p0"][1]
        ax.add_patch(Circle((x, y), max(h["d"], 14) / 2, fc=HCOL.get(h["code"], INK), ec=INK, lw=0.4))
        prow.append((h["code"], x, y, h["d"]))
    for xx in sorted({round(p[1]) for p in prow if p[0] == "M"}):
        ax.text(xx, YM - 55, f"{xx}", fontsize=6, ha="center", color=RED)
    ax.text(-30, YM, f"{YM:.0f}", fontsize=6, ha="right", va="center", color=RED); ax.plot([-20, 0], [YM, YM], color=RED, lw=0.4)
    for p in prow:
        if p[0] == "C": ax.text(p[1], p[2] - 110, f"x {p[1]:.0f}\ny {p[2]:.0f}", fontsize=6, ha="center", color=RED)
    ps_ = sorted({(round(p[1]), round(p[2])) for p in prow if p[0] == "P"})
    ax.text(1680, 250, f"4 fori Ø11:\nx {ps_[0][0]} e {ps_[-1][0]}\ny {ps_[0][1]} e {ps_[-1][1]}", fontsize=6, ha="center", color=RED)
    ax.text(1000, -60, "FRONTE – quote da sinistra (x) e dal bordo anteriore (y)", ha="center", fontsize=7.5, color=MUTE)
    ax.set_xlim(-60, 2040); ax.set_ylim(-110, 820)
    ax.set_title("PIANO 2000×800×40 visto dall'alto", fontsize=8.5, loc="left")
    para(fig, 0.67, 0.88, (
        "Piano\n• 2 fori Ø60 passacavi con la sega a tazza: metà da sopra e metà da sotto per non scheggiare.\n"
        "• 4 fori Ø11 della base piastre: falli in fase 8, usando la base d'acciaio come dima.\n"
        f"• 4 fori Ø12 (in blu) a {YM:.0f} dal fronte, x = {', '.join(str(round(x)) for x in XM)}: servono SOLO per l'alzatina "
        "(modulo 3). Non farli ora: si forano dal basso passando la punta nel foro della gamba, quando monti l'alzatina.\n\n"
        f"Rinforzo (OSB 2×18) e contropiastra 220×220×6\n• Rinforzo {round(rinf[3]-rinf[0])}×{round(rinf[4]-rinf[1])}: "
        "2 fori Ø11 per le viti posteriori della base, in fase 8 insieme al piano, dopo l'incollaggio."), width=48, fs=8.1)
    pdf.savefig(fig); plt.close(fig)

    # ================= fase 3 + 4
    fig = page("Levigatura e finitura · Telai laterali", "Fasi 3 e 4")
    para(fig, 0.04, 0.89, "Fase 3 · Levigatura e finitura (prima del montaggio)", fs=10.5, weight="bold")
    para(fig, 0.04, 0.86, (
        "1. Leviga tutti i pezzi con grana 120 e poi 180. Il KVH è già piallato: basta togliere segni e matita.\n"
        "2. Smussa tutti gli spigoli vivi di 2 mm (la fascia FA è sotto le mani: smussala bene).\n"
        "3. Olio o impregnante su gambe, traverse, fasce e montanti; vernice trasparente sui ripiani OSB.\n"
        "4. NON trattare testate delle traverse e zone da incollare (sotto il piano dove va il rinforzo).\n"
        "5. Il piano si tratta per ultimo, a tavolo montato, con 2–3 mani."), width=58, fs=8.5)
    para(fig, 0.04, 0.62, "Fase 4 · Telai laterali (4 telai)", fs=10.5, weight="bold")
    para(fig, 0.04, 0.59, (
        "Ogni telaio = gamba anteriore + gamba posteriore + traversa laterale alta e bassa (es. G1A + G1P + L1s + L1i).\n\n"
        "1. Predisposizione alzatina: in ogni gamba posteriore infila un dado a tamburo D nel foro Ø15 della faccia "
        "laterale (lato campata), con il foro filettato in verticale. Prova avvitando di qualche giro una barra M10 dal "
        "foro Ø12 in testa, poi sfilala.\n"
        "2. Dadi a tamburo D nelle traverse L (dal basso), fessura verso la testata, foro filettato allineato al Ø11.\n"
        "3. Incolla le spine S nelle testate delle traverse (solo lì), sporgenti 20 mm.\n"
        "4. Gambe a terra, faccia interna in alto. Infila le traverse sulle spine della gamba anteriore.\n"
        "5. Bulloni B1 con rondella dalla faccia anteriore della gamba anteriore, avvitali nel dado. Stringi poco.\n"
        "6. Ripeti con la gamba posteriore (bulloni dalla faccia posteriore).\n"
        "7. Diagonali del telaio uguali entro 2 mm, poi stringi a fondo. I bulloni B1 restano coperti dalle fasce: "
        "stringili bene adesso.\n8. Pulisci subito la colla uscita."), width=58, fs=8.3)
    img(fig, "man_f4_telai.png", [0.47, 0.12, 0.52, 0.78], crop=(100, 900, 40, 1480))
    pdf.savefig(fig); plt.close(fig)

    # ================= fase 5
    fig = page("Traverse basse anteriori e fasce", "Fase 5")
    img(fig, "man_f5_collegamento.png", [0.43, 0.36, 0.56, 0.56], crop=(80, 940, 40, 1480))
    sv = {f: screws_of(f) for f in fasce}
    para(fig, 0.04, 0.89, (
        "Serve un aiutante. Tavolo in piedi, sul pavimento piano, vicino al muro dove andrà.\n\n"
        "1. Metti in piedi i 4 telai alle distanze giuste (campate nette 500 · 700 · 480).\n"
        "2. ACi tra G1A e G2A e ARi tra G3A e G4A: dadi D e spine come nei telai; bulloni B2 dalla faccia della gamba "
        "opposta alla traversa (G1A sinistra, G2A destra, G3A sinistra, G4A destra).\n"
        f"3. Fascia posteriore bassa FPb: appoggiala sul retro delle gambe posteriori, a filo sotto (quota 70–190) e con "
        "5 mm di margine ai due fianchi. Morsetti su G1P e G4P.\n"
        "4. Controlla la squadra in pianta (diagonali del rettangolo delle gambe uguali entro 3 mm) e che le gambe siano a piombo.\n"
        "5. Passando dai fori Ø9 della fascia, fai il preforo Ø5 profondo 80 nella gamba, poi avvita le viti V 8×160 "
        "fino a portare la testa a filo. Una gamba alla volta, partendo dal centro (G2P, G3P).\n"
        "6. Fascia posteriore alta FPa allo stesso modo, a filo della testa delle gambe (quota 580–700).\n"
        "7. Fascia anteriore FA, di piatto, davanti alle gambe anteriori e a filo della loro testa: viti dentro le "
        "lamature Ø20. Poi incolla i tappi Ø20 e rasali.\n"
        "8. Ricontrolla diagonali e piombo: con le fasce il telaio è rigido."), width=52, fs=8.2)
    a = fig.add_axes([0.45, 0.04, 0.52, 0.30]); sec_laterale(a)
    pdf.savefig(fig); plt.close(fig)

    # ================= fase 6
    fig = page("Listelli e ripiani bassi", "Fase 6")
    img(fig, "man_f6_ripiani.png", [0.40, 0.10, 0.59, 0.80], crop=(90, 920, 40, 1480))
    lc = parts["Listello reggiripiano – Ripiano basso cassetti sx"]["box"]; ls_ = parts["Listello reggiripiano – Ripiano basso post. seduta sx"]["box"]
    Lc, Ls = round(lc[4] - lc[1]), round(ls_[4] - ls_[1])
    para(fig, 0.04, 0.89, (
        f"Listelli reggiripiano 30×40 (6 pezzi): avvitati sulle facce interne di gambe e traverse laterali basse, con il "
        f"filo superiore 18 mm sotto il filo della traversa (i ripiani OSB restano a filo).\n\n"
        f"• Campate cassetti e ricarica: listelli da {Lc}, da dietro la traversa bassa anteriore (y {round(lc[1])}) fino alla "
        f"fascia posteriore bassa (y {round(lc[4])}).\n"
        f"• Campata seduta: listelli da {Ls} contro la fascia posteriore bassa.\n\n"
        "Viti 5×70, preforo Ø3, svasate, più colla. Listelli lunghi: 3 viti, una nella gamba anteriore, una al centro "
        "della traversa laterale e una nella gamba posteriore. Listelli corti: 2 viti (traversa e gamba posteriore).\n"
        "NON avvitare entro 40 mm dalle testate delle traverse (spine).\n\n"
        "Ripiani OSB 18: appoggiali sui listelli, lato liscio in alto, e fissa ciascuno con 2 viti 4×35 per lato, preforo Ø3. "
        "Carico consigliato: fino a 30 kg sui ripiani da 500, fino a 15 kg su quello della seduta (luce 700)."), width=55, fs=8.3)
    ax = fig.add_axes([0.04, 0.08, 0.32, 0.25]); ax.set_aspect("equal"); ax.axis("off")
    R(ax, 0, 0, 80, 120, WOOD2); R(ax, 80, 62, 30, 40, WOOD); R(ax, 80, 102, 160, 18, "#d9c08a")
    R(ax, 20, 79.5, 90, 5, STEEL)
    ax.text(5, 82, "vite 5×70", fontsize=6.3, va="center", color="white")
    ax.text(120, 111, "ripiano OSB 18", fontsize=6.5, va="center"); ax.text(115, 75, "listello 30×40", fontsize=6.5)
    ax.text(5, 20, "traversa\nlaterale bassa", fontsize=6.3)
    dim(ax, 240, 102, 240, 120, 10, "18", vertical=True)
    ax.set_xlim(-10, 290); ax.set_ylim(-15, 140)
    ax.set_title("Sezione: ripiano sul listello", fontsize=8, loc="left")
    pdf.savefig(fig); plt.close(fig)

    # ================= fase 7 piano
    fig = page("Piano di lavoro", "Fase 7")
    img(fig, "man_f7_piano.png", [0.42, 0.40, 0.57, 0.52], crop=(110, 950, 40, 1480))
    para(fig, 0.04, 0.89, (
        "1. Fai i 2 fori passacavi Ø60. Incolla tra loro i due rinforzi OSB (36 mm) e poi incollali sotto il piano: "
        f"x {round(rinf[0])}–{round(rinf[3])}, y {round(rinf[1])}–{round(rinf[4])} (dietro la fascia FA, tra le traverse L3s e L4s). "
        "Colla su tutta la superficie + 12 viti 5×60 dal basso, preforo Ø3, svasate, lontane almeno 40 mm dai fori della "
        f"base piastre (x {ps_[0][0]} e {ps_[-1][0]}, y {ps_[-1][1]}).\n"
        "2. Appoggia il piano sul telaio: a filo della fascia FA davanti e della fascia FPa dietro, sporgenza 5 mm "
        "oltre le fasce sui fianchi (a filo delle gambe).\n"
        "3. Fissalo con le squadrette Q avvitate sulle facce interne di FA, FPa e delle traverse laterali alte: asola sotto il "
        "piano e vite 4,5×25 al centro dell'asola, così il legno può muoversi con l'umidità.\n"
        "4. Se monterai l'alzatina, le sue barre bloccheranno il piano anche sul retro."), width=56, fs=8.2)
    rows = [["FA (faccia interna)", "2 per campata, a 100 dalle gambe", "6"],
            ["FPa (faccia interna)", "2 per campata, a 100 dalle gambe", "6"],
            ["L1s e L4s", "1 al centro, faccia interna", "2"],
            ["L2s e L3s", "1 al centro, lato seduta", "2"],
            ["totale", "", "16"]]
    at = fig.add_axes([0.04, 0.32, 0.37, 0.16]); table(at, rows, ["dove", "posizione", "n°"], [0.36, 0.52, 0.12], fs=6.8, sc=1.3)
    ax = fig.add_axes([0.44, 0.06, 0.52, 0.30]); ax.set_aspect("equal"); ax.axis("off")
    R(ax, 0, 0, 80, 120, WOOD2); R(ax, -200, 120, 380, 40, "#efe0c2")
    ax.add_patch(Polygon([[-4, 75], [0, 75], [0, 116], [-40, 116], [-40, 120], [-4, 120]], fc=STEEL, ec=INK, lw=0.6))
    R(ax, -26, 120, 4, 25, STEEL, lw=0.4); R(ax, -2, 92, 25, 4, STEEL, lw=0.4)
    ax.text(-190, 100, "squadretta Q", fontsize=6.5); ax.text(30, 60, "fascia o\ntraversa alta", fontsize=6.5)
    ax.text(-190, 140, "piano 40", fontsize=6.5)
    ax.text(100, 100, "vite 4,5×25 nell'asola\n(il piano può muoversi)", fontsize=6.5)
    ax.set_xlim(-210, 300); ax.set_ylim(40, 170)
    ax.set_title("Sezione: squadretta di fissaggio del piano", fontsize=8, loc="left")
    pdf.savefig(fig); plt.close(fig)

    # ================= fase 8 ricarica
    fig = page("Zona ricarica: base delle piastre", "Fase 8")
    img(fig, "man_f8_ricarica.png", [0.52, 0.42, 0.47, 0.50], crop=(110, 900, 40, 1480))
    ax = fig.add_axes([0.03, 0.06, 0.62, 0.40]); ax.set_aspect("equal"); ax.axis("off")
    R(ax, 0, LEG_H - Ffh, Ffd, Ffh, "#b98d55")                      # FA
    R(ax, 0, LEG_H, 640, 40, "#efe0c2", hatch="///")                 # piano
    R(ax, Ffd, LEG_H - 36, 480, 36, "#d9c08a", hatch="\\\\")          # rinforzo
    R(ax, Ffd, LEG_H - 42, 220, 6, STEEL)                            # contropiastra
    R(ax, 0, H, 180, 12, "#3a3f45"); R(ax, 0, H + 12, 180, 10, "#9aa7b4")
    for y, zb, lab_ in ((25, LEG_H - Ffh, "M10×160"), (155, LEG_H - 42, "M10×110")):
        R(ax, y - 5, zb - 14, 10, H + 12 - zb + 14, STEEL, lw=0.5)
        ax.add_patch(Polygon([[y - 9, H + 12], [y + 9, H + 12], [y + 5, H + 6], [y - 5, H + 6]], fc=STEEL, ec=INK, lw=0.5))
        R(ax, y - 9, zb - 9, 18, 9, "#7f8890", lw=0.5)
        ax.text(y, zb - 30, lab_, ha="center", fontsize=6.5)
    for y in (380, 520): R(ax, y - 2.5, LEG_H - 40, 5, 60, "#666", lw=0.3)
    ax.text(440, LEG_H - 60, "viti 5×60 + colla", fontsize=6.5)
    ax.text(5, LEG_H - Ffh + 30, "FA", fontsize=6.5)
    ax.text(330, H - 20 + 40 - 18, "piano 40", fontsize=6.5); ax.text(330, LEG_H - 23, "rinforzo OSB 36", fontsize=6.5)
    ax.text(250, LEG_H - 52, "contropiastra 6", fontsize=6.5)
    ax.text(190, H + 20, "base 12 + piastra attrezzo 10", fontsize=6.5)
    dim(ax, 0, H + 22, 25, H + 22, 14, "25", fs=6.5); dim(ax, 0, H + 50, 155, H + 50, 10, "155", fs=6.5)
    ax.text(0, LEG_H - Ffh - 50, "← fronte", fontsize=6.5, color=MUTE)
    ax.set_xlim(-20, 660); ax.set_ylim(LEG_H - Ffh - 70, H + 80)
    ax.set_title(f"Sezione verticale in corrispondenza delle viti (x {ps_[0][0]} e {ps_[-1][0]})", fontsize=8, loc="left")
    para(fig, 0.04, 0.89, (
        "1. Appoggia la base d'acciaio sul piano: bordo anteriore a filo del piano, centrata nella campata "
        "(centro a x = 1680, cioè 240 mm dalla gamba destra). Bloccala con due morsetti.\n"
        "2. Usa i suoi fori come dima: fora Ø11 verticale.\n"
        f"   – 2 fori ANTERIORI (25 dal fronte): attraversano piano e fascia FA ({P['T_top'] + Ffh} mm). Punta lunga, "
        "fora metà da sopra; finisci da sotto se serve.\n"
        "   – 2 fori POSTERIORI (155 dal fronte): attraversano piano e rinforzo.\n"
        "3. Da sotto, presenta la contropiastra sui 2 fori posteriori e segnala/forala se non è già forata.\n"
        "4. Viti TSPEI dall'alto (testa svasata a filo della base):\n"
        "   – anteriori M10×160: rondella larga + dado autobloccante sotto la fascia FA;\n"
        "   – posteriori M10×110: dado autobloccante sotto la contropiastra.\n"
        "5. Stringi in croce. Le piastre degli attrezzi si bloccano poi con le 2 manopole M12."), width=62, fs=8.2)
    pdf.savefig(fig); plt.close(fig)

    # ================= fase 9
    fig = page("Piedini, fissaggio a muro e predisposizioni", "Fase 9")
    img(fig, "man_f9_base.png", [0.50, 0.40, 0.49, 0.52], crop=(150, 900, 40, 1480))
    ax = fig.add_axes([0.53, 0.04, 0.34, 0.34]); ax.set_aspect("equal"); ax.axis("off")
    R(ax, yB0, 450, Ly, LEG_H - 450, WOOD); R(ax, yB1, LEG_H - Rh, Fb, Rh, "#b98d55")
    R(ax, yB0 - 60, LEG_H, 260, 40, "#efe0c2", hatch="///")
    R(ax, YM - 6, LEG_H - 75, 12, 75, "white", ec=HCOL["M"], ls="--")
    ax.add_patch(Circle((YM, LEG_H - 60), 7.5, fc=STEEL, ec=INK)); ax.plot([YM - 6, YM + 6], [LEG_H - 60, LEG_H - 60], color=INK, lw=0.8)
    R(ax, D - 70, LEG_H - Rh / 2 - 5, 70, 10, "#bfbfbf", lw=0.4)
    ax.plot([D + 2, D + 2], [430, 760], color="#555", lw=2); ax.text(D + 8, 450, "muro", fontsize=6.5, rotation=90)
    ax.text(yB0 - 55, LEG_H + 15, "piano (non forato)", fontsize=6.3); ax.text(yB0 + 10, 540, "gamba\nposteriore", fontsize=6.3)
    ax.text(yB0 + 5, LEG_H - 45, "D", fontsize=6.3, color=HCOL["T"]); ax.text(YM + 8, LEG_H - 20, "Ø12", fontsize=6, color=HCOL["M"])
    ax.text(yB1 + 4, LEG_H - Rh - 18, "FPa + tassello", fontsize=6)
    dim(ax, yB0, 450, yB1, 450, -20, f"{Ly}", fs=6.3); dim(ax, YM, LEG_H + 40, yB1, LEG_H + 40, 12, f"{yB1 - YM:.0f}", fs=6.3)
    ax.set_xlim(yB0 - 70, D + 30); ax.set_ylim(400, H + 80)
    ax.set_title("Gamba posteriore: dado D (visto di testa) e tassello nella fascia", fontsize=7.5, loc="left")
    para(fig, 0.04, 0.89, (
        "Piedini\n1. Inclina il tavolo, avvita i dadi ragno I nei fori sotto le gambe e poi i piedini.\n"
        "2. Porta il tavolo al muro e livellalo agendo sui piedini.\n\n"
        "Fissaggio a muro (indispensabile per le presse)\n"
        "3. 4 tasselli per telai Ø10 L 160 attraverso la fascia posteriore alta FPa, alla sua mezzeria (quota 640): uno in "
        "ogni campata e uno in più nella campata ricarica, a ~150 mm dalle gambe (lontano dalle viti V). Fora Ø10 la fascia, "
        "segna il muro, fora il muro con la punta adatta, inserisci e avvita. Se c'è il battiscopa, metti uno spessore "
        "dietro la fascia all'altezza dei tasselli. Su cartongesso: cerca i montanti metallici o usa tasselli a espansione "
        "specifici.\n\n"
        "Predisposizioni per i moduli\n"
        "• Alzatina (modulo 3): in ogni gamba posteriore c'è il dado D inserito in fase 4 (dalla faccia laterale, lato "
        "campata) e il foro Ø12 in testa. I fori nel piano si fanno solo quando monti l'alzatina. Conserva i montanti M1–M4.\n"
        "• Cassettiera (modulo 2): nessuna lavorazione. La campata sinistra con il suo ripiano è già pronta."), width=62, fs=8.1)
    pdf.savefig(fig); plt.close(fig)

    # ================= fase 10
    fig = page("Canaline, elettrico e controlli finali", "Fase 10")
    img(fig, "man_f7_piano.png", [0.50, 0.40, 0.49, 0.52], crop=(110, 950, 40, 1480))
    para(fig, 0.04, 0.89, (
        "Canaline e ciabatta\n"
        f"1. Una canalina per campata, sotto il piano, davanti alla fascia FPa: fascia y {round(tray[1])}–{round(tray[4])} dal fronte. "
        "Fissala sotto il piano con viti 4×25 (il piano è spesso 40: non usare viti più lunghe).\n"
        "2. La ciabatta va dentro la canalina della campata seduta, con l'interruttore raggiungibile dal fronte.\n"
        f"3. I cavi passano da una campata all'altra nei fori Ø35 delle traverse L2s e L3s ({CAB_Y + yF1:.0f} dal fronte "
        "del tavolo). Salgono sul piano dai passacavi Ø60.\n"
        "4. Fascette e cavi alti, lontani dai cassetti della campata sinistra.\n"
        "5. Un solo cavo di alimentazione scende a muro, lungo la gamba G2P o G3P."), width=60, fs=8.3)
    checks = ["Il tavolo appoggia su 8 piedini senza dondolare (livella sul piano in due direzioni)",
              "Telai: 20 nodi imbullonati stretti; dopo 2–3 settimane ristringi ACi e ARi (gli altri sono sotto le fasce)",
              "Fasce: 24 viti 8×160 a fondo, nessuna fessura tra fascia e gamba",
              "Nessun gioco spingendo il piano avanti-indietro e di lato",
              "Tasselli a muro serrati: prova con la pressa in calibratura, il tavolo non deve muoversi",
              "Base piastre: le 4 viti stringono, le manopole bloccano la piastra senza gioco",
              "Campata cassetti libera e ripiano fissato: pronta per la cassettiera (modulo 2)",
              "Finitura del piano: 2–3 mani di olio, leggera carteggiatura 240 tra una mano e l'altra"]
    para(fig, 0.04, 0.46, "Controlli finali", fs=10.5, weight="bold")
    y = 0.43
    for c in checks:
        fig.patches.append(Rectangle((0.045, y - 0.016), 0.012, 0.016, transform=fig.transFigure, fc="white", ec=INK, lw=0.7))
        para(fig, 0.065, y, c, width=110, fs=8.5); y -= 0.042
    pdf.savefig(fig); plt.close(fig)

print("pagine:", PAGE[0])
