"""
Tavolo da lavoro in TRAVI KVH 80x120 (abete C24, essiccato, piallato) - modello parametrico CadQuery
Unità mm. Origine: spigolo anteriore-sinistro a terra. X larghezza, Y profondità (fronte Y=0), Z altezza.

- 4 telai laterali (gamba ant. + gamba post. + traversa laterale alta e bassa, bulloni M10 + dadi a tamburo).
- Telai uniti da fasce a tutta lunghezza avvitate sulle facce delle gambe (viti strutturali Ø8):
  2 fasce posteriori 80x120 di coltello (alta e bassa) e 1 fascia anteriore alta 120x80 posata di piatto.
- Gambe 80 (X) x 120 (Y), arretrate dello spessore delle fasce: il piano 2000x800 copre tutto.
- Piano lamellare abete 2000x800x40 (pannello commerciale intero, nessun taglio).
Rilancia con: python tavolo_kvh.py
"""
import json
import cadquery as cq

P = dict(
    W=2000, D=800, H=740,
    Lx=80, Ly=120,          # sezione gambe (X, Y)
    Rt=80, Rh=120,          # traverse: spessore, altezza
    bays=[500, 700, 480],   # luci nette: cassetti (sx), seduta, ricarica (dx)
    T_top=40, T_dbl=36,
    lower_z=70,
    T_shelf=18, T_ply=18, rear_shelf_d=260,
    riser_h=250, riser_d=200, T_riser=18, mbat=(30, 40),   # mensola: tavole lamellari 1000×200×18 (Tecnomat) + listello sotto il bordo anteriore
    cleat=(30, 40),
    tray_w=100, tray_h=60, grommet_d=60, cable_hole=35,
    case_h=400, case_d=596, T_case=18, n_drawers=3, slide_len=500, slide_t=12.7,
    mount=(180, 180, 12), backer=(220, 220, 6),
    Fb=80, Ff_d=120, Ff_h=80, fascia_gap=5,   # fasce: post. 80 (Y) x 120 (Z); ant. 120 (Y) x 80 (Z); lunghe 1990 (2 per barra da 4 m), 5 mm per lato dai fianchi
)
BEAM = "Travi KVH 80x120"
parts = []

def add(name, group, mat, x0, y0, z0, x1, y1, z1, color, holes=None, tray=False, role=""):
    parts.append(dict(name=name, group=group, mat=mat, role=role,
                      box=[round(v, 2) for v in (x0, y0, z0, x1, y1, z1)],
                      color=color, holes=holes or [], tray=tray))

def build():
    W, D, H = P["W"], P["D"], P["H"]
    Lx, Ly, Rt, Rh = P["Lx"], P["Ly"], P["Rt"], P["Rh"]
    b = P["bays"]
    assert abs(sum(b) + 4 * Lx - W) < 0.5, "campate + gambe != larghezza"
    leg_h = H - P["T_top"]
    xs = [0, Lx + b[0], 2 * Lx + b[0] + b[1], W - Lx]
    legs = [(x, x + Lx) for x in xs]
    bays = [(xs[i] + Lx, xs[i + 1]) for i in range(3)]
    zu, zl = (leg_h - Rh, leg_h), (P["lower_z"], P["lower_z"] + Rh)
    names = ["cassetti", "seduta", "ricarica"]
    LEG, RAIL, RAIL2 = "#d9b382", "#c99a62", "#bd8d55"

    yF0 = P["Ff_d"]                 # faccia anteriore gambe anteriori
    yB1 = D - P["Fb"]               # faccia posteriore gambe posteriori
    yF1, yB0 = yF0 + Ly, yB1 - Ly   # testate delle traverse laterali
    for i, x in enumerate(xs):
        for side, (y0, y1) in (("ant", (yF0, yF1)), ("post", (yB0, yB1))):
            add(f"Gamba {i+1} {side}", BEAM, "KVH 80x120", x, y0, 0, x + Lx, y1, leg_h, LEG, role="gamba")

    tray_y = yB1 - 5 - P["tray_w"] / 2
    ymid = (yF1 + yB0) / 2
    for i, x in enumerate(xs):   # traverse laterali tra gamba ant. e post.
        holes = [("x", ymid, zu[0] + 70, P["cable_hole"])] if i in (1, 2) else []
        add(f"Trav. sup. lat. {i+1}", BEAM, "KVH 80x120", x, yF1, zu[0], x + Lx, yB0, zu[1], RAIL, holes, role="trav-lat")
        add(f"Trav. inf. lat. {i+1}", BEAM, "KVH 80x120", x, yF1, zl[0], x + Lx, yB0, zl[1], RAIL, role="trav-lat")
    g = P["fascia_gap"]
    add("Fascia post. alta", BEAM, "KVH 80x120", g, yB1, zu[0], W - g, D, zu[1], RAIL2, role="fascia")
    add("Fascia post. bassa", BEAM, "KVH 80x120", g, yB1, zl[0], W - g, D, zl[1], RAIL2, role="fascia")
    add("Fascia ant. alta", BEAM, "KVH 80x120 (di piatto)", g, 0, leg_h - P["Ff_h"], W - g, yF0, leg_h, RAIL2, role="fascia")
    for i, (a, c) in enumerate(bays):  # traverse basse anteriori, filo faccia anteriore gambe
        if names[i] in ("cassetti", "ricarica"):
            add(f"Trav. inf. ant. {names[i]}", BEAM, "KVH 80x120", a, yF0, zl[0], c, yF0 + Rt, zl[1], RAIL2, role="trav-long")

    gh = [("z", (bb[0] + bb[1]) / 2, tray_y, P["grommet_d"]) for bb in bays[1:]]
    add("Piano di lavoro", "Pannelli", "lamellare abete 40 – pannello 1", 0, 0, leg_h, W, D, H, "#ecd3a8", gh)

    # zona ricarica
    a, c = bays[2]; mx = (a + c) / 2
    add("Rinforzo piano ricarica", "Pannelli", "OSB/3 18 ×2 incollati", a, yF0, leg_h - P["T_dbl"], c,
        tray_y - P["tray_w"] / 2 - 15, leg_h, "#e0c08f")
    bw, bd, bt = P["backer"]
    add("Contropiastra acciaio", "Ricarica", "acciaio S235", mx - bw / 2, yF0, leg_h - P["T_dbl"] - bt,
        mx + bw / 2, yF0 + bd, leg_h - P["T_dbl"], "#7d848c")
    mw, md, mt = P["mount"]
    add("Base attacco piastre", "Ricarica", "acciaio", mx - mw / 2, 0, H, mx + mw / 2, md, H + mt, "#3a3f45")

    # ripiani bassi su listelli avvitati alle traverse laterali inferiori
    zs1 = zl[1]; cw, ch = P["cleat"]
    def shelf(name, i, y0, y1, T, mat, col):
        x0, x1 = bays[i]; zs0 = zs1 - T
        add(name, "Pannelli", mat, x0, y0, zs0, x1, y1, zs1, col)
        for s, xa in (("sx", x0), ("dx", x1 - cw)):
            add(f"Listello reggiripiano – {name} {s}", "Listelli reggiripiano", "abete 30x40",
                xa, y0, zs0 - ch, xa + cw, y1, zs0, "#d4ae7c")
    shelf("Ripiano basso cassetti", 0, yF0 + Rt, yB1, P["T_shelf"], "OSB/3 18", "#d9c08a")
    shelf("Ripiano basso ricarica", 2, yF0 + Rt, yB1, P["T_shelf"], "OSB/3 18", "#d9c08a")
    shelf("Ripiano basso post. seduta", 1, yB1 - P["rear_shelf_d"], yB1, P["T_shelf"], "OSB/3 18", "#d9c08a")

    # mensola rialzata
    for i, x in enumerate(xs):
        add(f"Montante mensola {i+1}", BEAM, "KVH 80x120", x, yB0, H, x + Lx, yB1, H + P["riser_h"], LEG, role="montante")
    zr = H + P["riser_h"]
    joints = [0] + [x + Lx / 2 for x in xs[1:3]] + [W]      # giunti in asse ai montanti 2 e 3
    for k in range(3):
        add(f"Mensola – tavola {k+1}", "Alzatina", "tavola lamellare abete 1000×200×18", joints[k], D - P["riser_d"], zr,
            joints[k + 1], D, zr + P["T_riser"], "#ecd3a8" if k % 2 == 0 else "#e4c99a")
    bw_, bh_ = P["mbat"]
    for k, (la, lc) in enumerate(bays):   # listello sotto il bordo anteriore, in 3 pezzi tra i montanti
        add(f"Listello mensola {k+1}", "Alzatina", "abete 30×40", la, D - P["riser_d"], zr - bh_, lc, D - P["riser_d"] + bw_, zr, "#d4ae7c")

    # canaline e ciabatta
    for i, (a, c) in enumerate(bays):
        add(f"Canalina {names[i]}", "Elettrico", "canalina acciaio", a + 5, tray_y - P["tray_w"] / 2,
            leg_h - P["tray_h"] - 10, c - 5, tray_y + P["tray_w"] / 2, leg_h - 10, "#555b63", tray=True)
    a, c = bays[1]; m = (a + c) / 2
    add("Ciabatta", "Elettrico", "ciabatta 6 prese", m - 200, tray_y - 30, leg_h - 60, m + 200, tray_y + 25,
        leg_h - 20, "#f2f2f2")

    # cassettiera (frontali a filo della faccia anteriore delle gambe)
    a, c = bays[0]; x0, x1 = a + 2, c - 2
    T, chh, cd = P["T_case"], P["case_h"], P["case_d"]
    y0c = yF0
    z0, z1 = zs1, zs1 + chh
    CASE, FRONT = "#f0e2c4", "#5f7a8c"
    add("Cassettiera fianco sx", "Cassettiera", "multistrato 18", x0, y0c + T, z0, x0 + T, y0c + cd, z1, CASE)
    add("Cassettiera fianco dx", "Cassettiera", "multistrato 18", x1 - T, y0c + T, z0, x1, y0c + cd, z1, CASE)
    add("Cassettiera cielo", "Cassettiera", "multistrato 18", x0 + T, y0c + T, z1 - T, x1 - T, y0c + cd, z1, CASE)
    add("Cassettiera fondo", "Cassettiera", "multistrato 18", x0 + T, y0c + T, z0, x1 - T, y0c + cd, z0 + T, CASE)
    add("Cassettiera schienale", "Cassettiera", "pannello di fibra 3", x0, y0c + cd, z0, x1, y0c + cd + 3, z1, CASE)
    nd, g = P["n_drawers"], 3
    fh = (chh - (nd - 1) * g) / nd
    box_w = (x1 - x0) - 2 * T - 2 * P["slide_t"]
    for k in range(nd):
        fz0 = z0 + k * (fh + g)
        add(f"Frontale cassetto {k+1}", "Cassettiera", "multistrato 18", x0, y0c, fz0, x1, y0c + T, fz0 + fh, FRONT)
        add(f"Cassetto {k+1} (scatola)", "Cassettiera", "multistrato 15", x0 + T + P["slide_t"], y0c + T, fz0 + 22,
            x0 + T + P["slide_t"] + box_w, y0c + T + P["slide_len"], fz0 + 22 + 85, "#e2c79a")
    for p in parts:
        n = p["name"]
        p["module"] = ("cassettiera" if p["group"] == "Cassettiera" else
                       "alzatina" if (p["group"] == "Alzatina" or n.startswith("Montante")) else "base")
    return xs, legs, bays

def solid(p):
    x0, y0, z0, x1, y1, z1 = p["box"]
    s = cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))
    if p["tray"]:
        th = 2
        s = s.cut(cq.Workplane("XY").box(x1 - x0, y1 - y0 - 2 * th, z1 - z0 - th, centered=False)
                  .translate((x0, y0 + th, z0 + th)))
    for ax, u, v, d in p["holes"]:
        if ax == "z":
            s = s.cut(cq.Workplane("XY").circle(d / 2).extrude(z1 - z0 + 2).translate((u, v, z0 - 1)))
        else:
            s = s.cut(cq.Workplane("YZ").circle(d / 2).extrude(x1 - x0 + 2).translate((x0 - 1, u, v)))
    return s

def overlaps():
    bad = []
    for i in range(len(parts)):
        for j in range(i + 1, len(parts)):
            a, b = parts[i]["box"], parts[j]["box"]
            if all(min(a[k + 3], b[k + 3]) - max(a[k], b[k]) > 0.5 for k in range(3)):
                bad.append((parts[i]["name"], parts[j]["name"]))
    return bad

if __name__ == "__main__":
    xs, legs, bays = build()
    for b in overlaps(): print("INTERFERENZA:", b)
    assy = cq.Assembly(name="tavolo_kvh")
    for i, p in enumerate(parts):
        assy.add(solid(p), name=f"{i:03d}_{p['name']}".replace(" ", "_").replace(".", "").replace("–", "-"),
                 color=cq.Color(p["color"]))
    assy.export("tavolo_kvh.step")
    json.dump(dict(params=P, legs_x=xs, legs=legs, bays=bays, parts=parts), open("parts_kvh.json", "w"), indent=1)
    print(len(parts), "parti")
