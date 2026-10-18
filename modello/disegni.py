"""Viste ortogonali quotate del tavolo base e schede quotate delle traverse."""
import json, re
from matplotlib.patches import Rectangle, Circle

d = json.load(open("parts_kvh.json")); holes = json.load(open("fori.json"))
P = d["params"]
ALL = d["parts"]
BASE = [p for p in ALL if p.get("module", "base") == "base"]
W, D, H, Lx, Ly, Rt, Rh = P["W"], P["D"], P["H"], P["Lx"], P["Ly"], P["Rt"], P["Rh"]
LEG_H = H - P["T_top"]
RED, INK, MUTE = "#c0392b", "#222222", "#666666"
COL = {"gamba": "#e3c79c", "trav-lat": "#cfa874", "trav-long": "#c39a63", "fascia": "#b98d55"}
Fb, Ffd, Ffh = P["Fb"], P["Ff_d"], P["Ff_h"]

def code(n):
    m = re.match(r"Gamba (\d) (ant|post)", n)
    if m: return f"G{m.group(1)}{'A' if m.group(2)=='ant' else 'P'}"
    m = re.match(r"Trav\. (sup|inf)\. lat\. (\d)", n)
    if m: return f"L{m.group(2)}{'s' if m.group(1)=='sup' else 'i'}"
    m = re.match(r"Trav\. (sup|inf)\. (post|ant)\. (\w+)", n)
    if m: return f"{'P' if m.group(2)=='post' else 'A'}{m.group(3)[0].upper()}{'s' if m.group(1)=='sup' else 'i'}"
    m = re.match(r"Fascia (post|ant)\. (alta|bassa)", n)
    if m: return "FA" if m.group(1) == "ant" else ("FPa" if m.group(2) == "alta" else "FPb")
    m = re.match(r"Montante mensola (\d)", n)
    if m: return f"M{m.group(1)}"
    return n

def length(p):
    x0, y0, z0, x1, y1, z1 = p["box"]; return round(max(x1 - x0, y1 - y0, z1 - z0))

# ------------------------------------------------------------------ quote
def chain(ax, vals, fixed, off, vertical=False, fs=6.5, total=True, color=RED):
    """catena di quote: vals = coordinate ordinate lungo l'asse; fixed = coordinata della linea di riferimento"""
    vals = sorted(set(round(v, 1) for v in vals))
    y = fixed + off
    for a, b in zip(vals[:-1], vals[1:]):
        if b - a < 0.5: continue
        if vertical:
            ax.annotate("", (y, a), (y, b), arrowprops=dict(arrowstyle="<->", lw=0.5, color=color, shrinkA=0, shrinkB=0))
            ax.text(y + (5 if off > 0 else -5), (a + b) / 2, f"{b - a:.0f}", rotation=90, fontsize=fs, color=color,
                    ha="left" if off > 0 else "right", va="center")
        else:
            ax.annotate("", (a, y), (b, y), arrowprops=dict(arrowstyle="<->", lw=0.5, color=color, shrinkA=0, shrinkB=0))
            ax.text((a + b) / 2, y + (4 if off > 0 else -4), f"{b - a:.0f}", fontsize=fs, color=color, ha="center",
                    va="bottom" if off > 0 else "top")
    for v in vals:
        if vertical: ax.plot([fixed, y], [v, v], lw=0.3, color=color)
        else: ax.plot([v, v], [fixed, y], lw=0.3, color=color)
    if total and len(vals) > 2:
        y2 = y + (off * 0.55 if off else 20)
        a, b = vals[0], vals[-1]
        if vertical:
            ax.annotate("", (y2, a), (y2, b), arrowprops=dict(arrowstyle="<->", lw=0.6, color=color, shrinkA=0, shrinkB=0))
            ax.text(y2 + (5 if off > 0 else -5), (a + b) / 2, f"{b - a:.0f}", rotation=90, fontsize=fs + 0.5,
                    color=color, weight="bold", ha="left" if off > 0 else "right", va="center")
        else:
            ax.annotate("", (a, y2), (b, y2), arrowprops=dict(arrowstyle="<->", lw=0.6, color=color, shrinkA=0, shrinkB=0))
            ax.text((a + b) / 2, y2 + (4 if off > 0 else -4), f"{b - a:.0f}", fontsize=fs + 0.5, color=color,
                    weight="bold", ha="center", va="bottom" if off > 0 else "top")

def box2d(ax, p, u, v, fc=None, ls="-", lw=0.7, label=True, fs=6, alpha=1, z=2):
    b = p["box"]
    fc = fc or COL.get(p.get("role"), p["color"])
    ax.add_patch(Rectangle((b[u], b[v]), b[u + 3] - b[u], b[v + 3] - b[v], fc=fc, ec=INK, lw=lw, ls=ls, alpha=alpha, zorder=z))
    if label and (p["name"].startswith(("Gamba", "Trav.", "Montante", "Fascia"))):
        w, h = b[u + 3] - b[u], b[v + 3] - b[v]
        txt = code(p["name"]) + ("" if p["name"].startswith("Gamba") else f"\n{length(p)}")
        ax.text(b[u] + w / 2, b[v] + h / 2, txt, ha="center", va="center", fontsize=fs, zorder=z + 1,
                rotation=90 if h > 2.2 * w and not p["name"].startswith("Gamba") else 0)

def frame_parts(include_top=False):
    keep = [p for p in BASE if p["name"].startswith(("Gamba", "Trav.", "Fascia"))]
    return keep

# ------------------------------------------------------------------ viste
def pianta_telaio(ax):
    """vista dall'alto del telaio senza piano. Traverse superiori piene, solo inferiori tratteggiate."""
    ax.set_aspect("equal"); ax.axis("off")
    fr = frame_parts()
    sup = [p for p in fr if "sup." in p["name"] or "alta" in p["name"]]
    inf = [p for p in fr if "inf." in p["name"] or "bassa" in p["name"]]
    sup_keys = {tuple(p["box"][:2] + p["box"][3:5]) for p in sup}
    for p in inf:   # solo inferiori (non coperte da una superiore)
        if tuple(p["box"][:2] + p["box"][3:5]) not in sup_keys:
            box2d(ax, p, 0, 1, fc="white", ls="--", z=1)
    for p in sup: box2d(ax, p, 0, 1, z=2)
    for p in fr:
        if p["name"].startswith("Gamba"): box2d(ax, p, 0, 1, z=3)
    xs = [0, W] + [v for p in fr if p["name"].startswith("Gamba") for v in (p["box"][0], p["box"][3])]
    chain(ax, xs, 0, -60); chain(ax, xs, D, 60, total=False)
    ys = [0, D, Ffd, Ffd + Rt, Ffd + Ly, D - Fb - Ly, D - Fb]
    chain(ax, ys, 0, -70, vertical=True); chain(ax, ys, W, 70, vertical=True, total=False)
    ax.text(W / 2, -175, "FRONTE", ha="center", fontsize=8, color=MUTE); ax.text(W / 2, D + 120, "RETRO (muro)", ha="center", fontsize=8, color=MUTE)
    for (a, c), lab in zip(d["bays"], ["campata cassetti", "campata seduta", "campata ricarica"]):
        ax.text((a + c) / 2, D / 2, lab, ha="center", va="center", fontsize=7.5, color=MUTE, style="italic")
    ax.set_xlim(-200, W + 200); ax.set_ylim(-220, D + 170)

def pianta_piano(ax):
    ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(Rectangle((0, 0), W, D, fc="#efe0c2", ec=INK, lw=0.8))
    for p in BASE:
        if p["name"] == "Base attacco piastre":
            b = p["box"]; ax.add_patch(Rectangle((b[0], b[1]), b[3] - b[0], b[4] - b[1], fc="#3a3f45", ec=INK, alpha=0.85))
        if p["name"].startswith("Gamba"):
            b = p["box"]; ax.add_patch(Rectangle((b[0], b[1]), b[3] - b[0], b[4] - b[1], fill=False, ec=MUTE, ls=":", lw=0.6))
    hs = [h for h in holes if h["part"] == "Piano di lavoro"]
    col = {"C": "#555", "P": "#34495e", "M": "#2c6fbb"}
    for h in hs:
        ax.add_patch(Circle(h["p0"][:2], max(h["d"], 16) / 2, fc=col[h["code"]], ec=INK, lw=0.4, zorder=4))
    xs = [0, W] + [h["p0"][0] for h in hs if h["code"] in ("C", "M")]
    chain(ax, xs, D, 60, fs=6)
    xs2 = [0, W] + [h["p0"][0] for h in hs if h["code"] == "P"]
    chain(ax, xs2, 0, -60, fs=6)
    ys = [0, D] + [h["p0"][1] for h in hs]
    chain(ax, ys, W, 70, vertical=True, fs=6)
    ax.text(W / 2, -170, "FRONTE · blu: fori barra alzatina (solo con il modulo 3) · grigio: passacavi Ø60 · scuro: base piastre (4 fori Ø11) · puntinato: gambe sotto",
            ha="center", fontsize=6.8, color=MUTE)
    ax.set_xlim(-60, W + 200); ax.set_ylim(-200, D + 170)

def prospetto(ax, side="front"):
    """front: guardando da davanti (x→destra); back: da dietro (x specchiato)."""
    ax.set_aspect("equal"); ax.axis("off")
    ps = [p for p in BASE if p["name"].startswith(("Gamba", "Trav.", "Fascia", "Piano", "Ripiano", "Base attacco", "Rinforzo", "Listello"))]
    if side == "front":
        ps.sort(key=lambda p: -p["box"][4]); X = lambda x: x
    else:
        ps.sort(key=lambda p: p["box"][1]); X = lambda x: W - x
    for p in ps:
        b = p["box"]; x0, x1 = sorted((X(b[0]), X(b[3])))
        fc = COL.get(p.get("role"), p["color"])
        ax.add_patch(Rectangle((x0, b[2]), x1 - x0, b[5] - b[2], fc=fc, ec=INK, lw=0.6))
        vis = (b[1] < Ffd + 1) if side == "front" else (b[4] > D - Fb - 1)
        if p["name"].startswith(("Gamba", "Trav.", "Fascia")) and (vis or p["name"].startswith("Gamba")):
            txt = code(p["name"]) + ("" if p["name"].startswith("Gamba") else f" · {length(p)}")
            rot = 90 if p["name"].startswith("Gamba") else 0
            ax.text((x0 + x1) / 2, (b[2] + b[5]) / 2 + (0 if rot == 0 else 120), txt, ha="center", va="center", fontsize=6, rotation=rot)
    legs = [p for p in BASE if p["name"].startswith("Gamba")]
    xs = [0, W] + [X(v) for p in legs for v in (p["box"][0], p["box"][3])]
    chain(ax, xs, 0, -60)
    zs = [0, P["lower_z"], P["lower_z"] + Rh, LEG_H - Rh, LEG_H, H] + ([LEG_H - Ffh] if side == "front" else [])
    chain(ax, zs, 0 if side == "front" else W, -80 if side == "front" else 80, vertical=True)
    base_p = next(p for p in BASE if p["name"] == "Base attacco piastre")
    chain(ax, [H, base_p["box"][5]], W if side == "front" else 0, 80 if side == "front" else -80, vertical=True, total=False)
    ax.text(W / 2, -190, "vista da DAVANTI" if side == "front" else "vista da DIETRO (lato muro)", ha="center", fontsize=8, color=MUTE)
    ax.set_xlim(-240, W + 240); ax.set_ylim(-230, H + 80)

def fianco(ax, which="sx"):
    """vista laterale: sx = guardando la faccia sinistra (fronte a sinistra? no: da sinistra il fronte è a destra)."""
    ax.set_aspect("equal"); ax.axis("off")
    if which == "sx":   # osservatore a sinistra guarda verso +x: fronte a destra
        ps = [p for p in BASE if p["box"][0] < Lx + 1]; Y = lambda y: D - y; ps.sort(key=lambda p: -p["box"][0])
    else:               # osservatore a destra guarda verso -x: fronte a sinistra
        ps = [p for p in BASE if p["box"][3] > W - Lx - 1]; Y = lambda y: y; ps.sort(key=lambda p: p["box"][3])
    ps = [p for p in ps if p["name"].startswith(("Gamba", "Trav.", "Fascia", "Piano", "Ripiano", "Base", "Rinforzo"))]
    for p in ps:
        b = p["box"]; y0, y1 = sorted((Y(b[1]), Y(b[4])))
        ax.add_patch(Rectangle((y0, b[2]), y1 - y0, b[5] - b[2], fc=COL.get(p.get("role"), p["color"]), ec=INK, lw=0.6))
        if p["name"].startswith(("Gamba", "Trav. sup. lat", "Trav. inf. lat", "Fascia")):
            txt = code(p["name"]) + ("" if p["name"].startswith("Gamba") else f" · {length(p)}")
            if p["name"].startswith("Fascia"): txt = code(p["name"])
            ax.text((y0 + y1) / 2, (b[2] + b[5]) / 2 + (120 if p["name"].startswith("Gamba") else 0), txt, ha="center",
                    va="center", fontsize=6 if not p["name"].startswith("Fascia") else 5.5,
                    rotation=90 if p["name"].startswith(("Gamba", "Fascia post")) else 0)
    ys = [0, D, Ffd, Ffd + Ly, D - Fb - Ly, D - Fb]
    chain(ax, [Y(v) for v in ys], 0, -60)
    zs = [0, P["lower_z"], P["lower_z"] + Rh, LEG_H - Ffh, LEG_H - Rh, LEG_H, H]
    chain(ax, zs, D, 70, vertical=True)
    ax.text(D / 2, -170, ("fianco SINISTRO (fronte a destra)" if which == "sx" else "fianco DESTRO (fronte a sinistra)"),
            ha="center", fontsize=8, color=MUTE)
    ax.set_xlim(-60, D + 260); ax.set_ylim(-210, H + 80)

# ------------------------------------------------------------------ schede traverse
def scheda_traversa(ax, name, title=None):
    """fianco (lunghezza × 120) a sinistra e vista dall'alto (lunghezza × 80) a destra, con tutti i fori."""
    p = next(q for q in ALL if q["name"] == name); b = p["box"]
    lat = ". lat." in name
    L = length(p)
    if lat: u0, ui, tt0, ti = b[1], 1, b[0], 0
    else: u0, ui, tt0, ti = b[0], 0, b[1], 1
    z0 = b[2]
    ax.set_aspect("equal"); ax.axis("off")
    OX = L + 170          # origine della vista dall'alto
    col_ = COL[p["role"]]
    ax.add_patch(Rectangle((0, 0), L, Rh, fc=col_, ec=INK, lw=0.7))
    ax.add_patch(Rectangle((OX, 20), L, 80, fc=col_, ec=INK, lw=0.7))
    hs = [h for h in holes if h["part"] == name]
    for h in hs:
        (x, y, z), dv = h["p0"], h["dir"]
        u = (x, y, z)[ui] - u0; t = (x, y, z)[ti] - tt0; zz = z - z0
        col = {"A": RED, "T": "#16a085", "S": "#d4a017", "C": "#555", "P": "#34495e"}[h["code"]]
        if h["code"] in ("A", "S"):
            du = h["depth"] * (1 if dv[ui] > 0 else -1); ua, ub = sorted((u, u + du))
            ax.add_patch(Rectangle((ua, zz - h["d"] / 2), ub - ua, h["d"], fill=False, ec=col, ls="--", lw=0.7))
            ax.add_patch(Rectangle((OX + ua, 20 + t - h["d"] / 2), ub - ua, h["d"], fill=False, ec=col, ls="--", lw=0.7))
        elif h["code"] in ("T", "P"):
            dz = h["depth"] * (1 if dv[2] > 0 else -1); za, zb = sorted((zz, zz + dz))
            ax.add_patch(Rectangle((u - h["d"] / 2, za), h["d"], zb - za, fill=False, ec=col, ls="--", lw=0.7))
            ax.add_patch(Circle((OX + u, 20 + t), h["d"] / 2, fc=col, ec=INK, lw=0.4))
        elif h["code"] == "C":
            ax.add_patch(Circle((u, zz), h["d"] / 2, fc="white", ec=col, lw=0.8))
            ax.add_patch(Rectangle((OX + u - h["d"] / 2, 20), h["d"], 80, fill=False, ec=col, ls="--", lw=0.7))
    us = sorted({0, L} | {round((h["p0"][ui] - u0), 1) for h in hs if h["code"] in ("T", "C", "P")})
    chain(ax, us, Rh, 22, fs=6.5)
    chain(ax, [OX + v for v in us], 100, 22, fs=6.5)
    zs = sorted({0, Rh} | {round(h["p0"][2] - z0, 1) for h in hs if h["code"] in ("A", "S", "C")})
    chain(ax, zs, L, 22, vertical=True, fs=6.5, total=False)
    ts = sorted({0, 80} | {round(h["p0"][ti] - tt0, 1) for h in hs if h["code"] in ("A", "S", "T", "P")})
    chain(ax, [20 + v for v in ts], OX + L, 22, vertical=True, fs=6.5, total=False)
    ax.text(L / 2, -18, "fianco (filo superiore in alto)", ha="center", fontsize=6.5, color=MUTE)
    ax.text(OX + L / 2, 2, "vista dall'alto (" + ("fronte in basso)" if not lat else "faccia sinistra in basso)"), ha="center", fontsize=6.5, color=MUTE)
    ax.set_xlim(-20, OX + L + 80); ax.set_ylim(-35, Rh + 75)
    ax.set_title(title or name, fontsize=8.5, loc="left")

def gruppi_traverse():
    """raggruppa le traverse con stessa lunghezza e stessa foratura (coordinate locali)."""
    groups = {}
    for p in BASE:
        if not p["name"].startswith("Trav."): continue
        b = p["box"]; lat = ". lat." in p["name"]
        u0, ui, t0, ti = (b[1], 1, b[0], 0) if lat else (b[0], 0, b[1], 1)
        sig = [length(p), lat]
        for h in sorted(holes, key=lambda h: h["p0"]):
            if h["part"] != p["name"]: continue
            x = h["p0"]; sig.append((h["code"], round(x[ui] - u0), round(x[ti] - t0), round(x[2] - b[2]), h["d"]))
        groups.setdefault(tuple(sorted(map(str, sig))), []).append(p["name"])
    out = []
    for names in groups.values():
        p = next(q for q in BASE if q["name"] == names[0])
        out.append((names[0], [code(n) for n in names], length(p), ". lat." in names[0]))
    out.sort(key=lambda g: (not g[3], -g[2], len(g[1]) * -1))
    return out

def scheda_fascia(ax, name, title=None):
    """fascia a tutta lunghezza: faccia vista (lunghezza × altezza) sopra, vista dall'alto (lunghezza × profondità) sotto."""
    p = next(q for q in ALL if q["name"] == name); b = p["box"]
    L = round(b[3] - b[0]); hh = round(b[5] - b[2]); dd = round(b[4] - b[1])
    ant = "ant." in name
    ax.set_aspect("equal"); ax.axis("off")
    GAP = 70; OY = -(dd + GAP)          # vista dall'alto sotto la faccia
    col_ = COL["fascia"]
    ax.add_patch(Rectangle((0, 0), L, hh, fc=col_, ec=INK, lw=0.7))
    ax.add_patch(Rectangle((0, OY), L, dd, fc=col_, ec=INK, lw=0.7))
    hs = [h for h in holes if h["part"] == name]
    for h in hs:
        x, y, z = h["p0"]; u = x - b[0]; zz = z - b[2]
        # in pianta: y misurata dalla faccia vista (anteriore per FA, posteriore per FP)
        t = (y - b[1]) if ant else (b[4] - y)
        if h["code"] == "V":
            if h["cb"]: ax.add_patch(Circle((u, zz), h["cb"][0] / 2, fc="white", ec="#7d3c98", lw=0.5, ls="--"))
            ax.add_patch(Circle((u, zz), h["d"] / 2, fc="#7d3c98", ec=INK, lw=0.4))
            ax.add_patch(Rectangle((u - h["d"] / 2, OY), h["d"], dd, fill=False, ec="#7d3c98", ls="--", lw=0.6))
        elif h["code"] == "P":
            ax.add_patch(Rectangle((u - h["d"] / 2, 0), h["d"], hh, fill=False, ec="#34495e", ls="--", lw=0.6))
            ax.add_patch(Circle((u, OY + dd - t), h["d"] / 2, fc="#34495e", ec=INK, lw=0.4))
    axes_ = [x + Lx / 2 - b[0] for x in d["legs_x"]]
    us = sorted({0, L} | {round(v, 1) for v in axes_} | {round(h["p0"][0] - b[0], 1) for h in hs if h["code"] == "P"})
    chain(ax, us, hh, 24, fs=6)
    for v in axes_:
        ax.plot([v, v], [-8, hh + 8], lw=0.4, ls="-.", color=RED)
        ax.text(v, -10, "asse\ngamba", ha="center", va="top", fontsize=4.8, color=RED)
        ax.annotate("", (v - 16, hh + 6), (v + 16, hh + 6), arrowprops=dict(arrowstyle="<->", lw=0.4, color=RED, shrinkA=0, shrinkB=0))
    ax.text(axes_[1] + 30, hh + 4, "±16", fontsize=5, color=RED, va="bottom")
    zs = sorted({0, hh} | {round(h["p0"][2] - b[2], 1) for h in hs if h["code"] == "V"})
    chain(ax, zs, L, 24, vertical=True, fs=5.5, total=False)
    ts = sorted({0, dd} | {round(dd - ((h["p0"][1] - b[1]) if ant else (b[4] - h["p0"][1])), 1) for h in hs if h["code"] == "P"})
    chain(ax, [OY + v for v in ts], L, 24, vertical=True, fs=5.5, total=False)
    ax.text(-15, hh / 2, "faccia\nvista", ha="right", va="center", fontsize=6, color=MUTE)
    ax.text(-15, OY + dd / 2, "dall'alto", ha="right", va="center", fontsize=6, color=MUTE)
    ax.text(L / 2, OY - 18, ("fronte in basso" if ant else "muro in alto") + f" · {L} × {dd} × {hh}", ha="center", va="top", fontsize=6, color=MUTE)
    ax.set_xlim(-110, L + 110); ax.set_ylim(OY - 45, hh + 95)
    ax.set_title(title or name, fontsize=8.5, loc="left")

def pagine_fasce(new_page, pdf, plt, phase=None):
    fig = new_page("Fasce a tutta lunghezza: misure e fori", phase)
    specs = [("Fascia post. alta", "FPa · fascia posteriore alta – di coltello, 80 × 120"),
             ("Fascia post. bassa", "FPb · fascia posteriore bassa – di coltello, 80 × 120"),
             ("Fascia ant. alta", "FA · fascia anteriore – posata di piatto, 120 × 80")]
    for j, (n, t) in enumerate(specs):
        scheda_fascia(fig.add_axes([0.03, 0.635 - j * 0.28, 0.94, 0.26]), n, t)
    fig.text(0.04, 0.05, "Viola: fori Ø9 passanti per le viti 8×160 (svasatura sulle fasce posteriori; lamatura Ø20 prof. 40 sulla fascia "
             "anteriore, da chiudere con un tappo) · blu scuro: 2 fori Ø11 verticali della base piastre (fase 8). In ogni asse gamba 2 fori "
             "a ±16 mm dall'asse, alle quote dal basso indicate a destra. Quote sempre dalla testata lato G1 (sinistra guardando il tavolo "
             "dal fronte): sulle fasce posteriori, che si forano dal lato muro, segna le quote dalla stessa testata.", fontsize=6.6, color=MUTE, wrap=True)
    pdf.savefig(fig); plt.close(fig)

def pagine_viste(new_page, pdf, plt, phase=None):
    """aggiunge al pdf le pagine delle viste quotate. new_page(title, phase) -> fig"""
    fig = new_page("Pianta del telaio quotata (senza piano)", phase)
    pianta_telaio(fig.add_axes([0.02, 0.06, 0.96, 0.84]))
    fig.text(0.04, 0.05, "Pezzi alti pieni, pezzi solo bassi (ACi, ARi) tratteggiati. FA = fascia anteriore (di piatto), FPa/FPb = fasce "
             "posteriori alta e bassa (sovrapposte in pianta). Codice e lunghezza su ogni pezzo.", fontsize=7.5, color=MUTE)
    pdf.savefig(fig); plt.close(fig)
    fig = new_page("Prospetto anteriore quotato", phase)
    prospetto(fig.add_axes([0.02, 0.05, 0.96, 0.86]), "front"); pdf.savefig(fig); plt.close(fig)
    fig = new_page("Prospetto posteriore quotato", phase)
    prospetto(fig.add_axes([0.02, 0.05, 0.96, 0.86]), "back"); pdf.savefig(fig); plt.close(fig)
    fig = new_page("Fianchi quotati", phase)
    fianco(fig.add_axes([0.02, 0.06, 0.47, 0.84]), "sx"); fianco(fig.add_axes([0.51, 0.06, 0.47, 0.84]), "dx")
    pdf.savefig(fig); plt.close(fig)
    fig = new_page("Pianta del piano quotata", phase)
    pianta_piano(fig.add_axes([0.02, 0.06, 0.96, 0.84])); pdf.savefig(fig); plt.close(fig)

def pagine_traverse(new_page, pdf, plt, phase=None):
    g = gruppi_traverse()
    for k in range(0, len(g), 3):
        fig = new_page("Traverse quotate: lunghezze e fori", phase)
        for j, (name, codes, L, lat) in enumerate(g[k:k + 3]):
            ax = fig.add_axes([0.03, 0.635 - j * 0.28, 0.94, 0.24])
            scheda_traversa(ax, name, f"{'Laterale' if lat else 'Bassa anteriore'} {L} mm – {len(codes)} pz: {', '.join(codes)}")
        fig.text(0.04, 0.058, "Rosso: foro Ø11 del bullone (prof. 80) · verde: foro Ø15 del dado a tamburo (prof. 45) · giallo: spine Ø12 "
                 "(prof. 30) · grigio: passacavi Ø35 · blu scuro: fori Ø11 verticali della base piastre. Quote in mm dalla testata "
                 "sinistra, dal basso (fianco) e dal lato anteriore/sinistro (sopra).", fontsize=6.6, color=MUTE, wrap=True)
        pdf.savefig(fig); plt.close(fig)
