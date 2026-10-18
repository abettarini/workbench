"""
Tavolo da lavoro in LISTELLI 25x50 LAMINATI - modello parametrico (CadQuery)
Unità mm. Origine: spigolo anteriore-sinistro a terra. X larghezza, Y profondità (fronte Y=0), Z altezza.

Costruzione:
- Gambe: 3 strati di listello (75x50); 4 strati (100x50) nella zona ricarica.
  Gli strati centrali sono interrotti alle quote delle traverse laterali -> mortase "da laminazione".
- Traverse laterali (in profondità): 2 strati; lo strato centrale attraversa la gamba (tenone passante).
  Nelle gambe a 4 strati passano entrambi gli strati.
- Traverse longitudinali: 2 strati, tra le facce delle gambe, bullone M8 + dado a tamburo.
- Pannelli di irrigidimento in multistrato 12 su retro e fianchi.
Rilancia con: python tavolo_lam.py
"""
import json
import cadquery as cq

P = dict(
    W=2000, D=800, H=740,
    t=25, w=50,            # listello: spessore, larghezza (verificare il piallato reale!)
    legs_n=[3, 3, 4, 4],   # strati per coppia di gambe (sx -> dx)
    second_side=[2, 0, None, None],  # gambe a 3 strati: dove sta il 2° strato della traversa laterale
    bays=[500, 680, 446],  # luci nette: cassetti (sx), seduta, ricarica (dx)
    T_top=40, T_dbl=40, T_pan=12, T_shelf=18,
    lower_z=70,
    rear_shelf_d=300,
    riser_h=250, riser_d=260, T_riser=27,
    cleat=(20, 30),
    tray_w=100, tray_h=60, grommet_d=60, cable_hole=30,
    case_h=450, case_d=600, T_case=18, n_drawers=3, slide_len=500, slide_t=12.7,
    hang_front_h=97, hang_box_h=70,
    mount=(180, 180, 12), backer=(220, 220, 6),
)

parts = []

def add(name, group, mat, x0, y0, z0, x1, y1, z1, color, holes=None, tray=False, role=""):
    parts.append(dict(name=name, group=group, mat=mat, role=role,
                      box=[round(v, 2) for v in (x0, y0, z0, x1, y1, z1)],
                      color=color, holes=holes or [], tray=tray))

L1, L2 = "#dcb684", "#c9a06c"   # colori alternati degli strati

def build():
    W, D, H, t, w = P["W"], P["D"], P["H"], P["t"], P["w"]
    Tp = P["T_pan"]
    Dy = D - Tp                       # retro del telaio (davanti al pannello posteriore)
    leg_h = H - P["T_top"]
    zu = (leg_h - w, leg_h)
    zl = (P["lower_z"], P["lower_z"] + w)
    n = P["legs_n"]
    # posizioni gambe
    legs, x = [], Tp
    for i in range(4):
        legs.append((x, x + n[i] * t))
        if i < 3: x += n[i] * t + P["bays"][i]
    assert abs(legs[3][1] - (W - Tp)) < 0.5, f"somma campate errata: {legs[3][1]} vs {W - Tp}"
    bays = [(legs[i][1], legs[i + 1][0]) for i in range(3)]
    names = ["cassetti", "seduta", "ricarica"]

    # ---------------- gambe laminate
    for i, (x0, x1) in enumerate(legs):
        gapped = [1] if n[i] == 3 else [1, 2]
        for side, (y0, y1) in (("ant", (0, w)), ("post", (Dy - w, Dy))):
            for k in range(n[i]):
                xa = x0 + k * t
                c = L1 if k % 2 == 0 else L2
                nm = f"Gamba {i+1} {side} - strato {k+1}"
                if k in gapped:
                    add(nm + " (piede)", "Listelli 25x50", "listello 25x50", xa, y0, 0, xa + t, y1, zl[0], c,
                        role="gamba-spezzone")
                    add(nm + " (centro)", "Listelli 25x50", "listello 25x50", xa, y0, zl[1], xa + t, y1, zu[0], c,
                        role="gamba-spezzone")
                else:
                    add(nm, "Listelli 25x50", "listello 25x50", xa, y0, 0, xa + t, y1, leg_h, c, role="gamba")

    # ---------------- traverse laterali (tenone passante nella gamba)
    tray_y = Dy - w - 5 - P["tray_w"] / 2
    rail_x = []
    for i, (x0, x1) in enumerate(legs):
        if n[i] == 3:
            layers = [(1, "tenone"), (P["second_side"][i], "fianco")]
        else:
            layers = [(1, "tenone"), (2, "tenone")]
        xs_ = [x0 + k * t for k, _ in layers]
        rail_x.append((min(xs_), max(xs_) + t))
        for lev, (za, zb) in (("sup", zu), ("inf", zl)):
            for k, kind in layers:
                xa = x0 + k * t
                y0, y1 = (0, Dy) if kind == "tenone" else (w, Dy - w)
                holes = []
                if lev == "sup" and i in (1, 2):
                    holes = [("x", tray_y, (za + zb) / 2, P["cable_hole"])]
                add(f"Trav. {lev}. lat. {i+1} - {kind}", "Listelli 25x50", "listello 25x50",
                    xa, y0, za, xa + t, y1, zb, "#b98e5c" if kind == "tenone" else L1, holes,
                    role="trav-lat-" + kind)

    # ---------------- traverse longitudinali (2 strati in Y)
    def long_rail(name, a, c, yfront, z):
        for k in range(2):
            ya = yfront + k * t
            add(f"{name} - strato {k+1}", "Listelli 25x50", "listello 25x50", a, ya, z[0], c, ya + t, z[1],
                "#c08f58" if k == 0 else "#b07f4a", role="trav-long")
    for i, (a, c) in enumerate(bays):
        long_rail(f"Trav. sup. post. {names[i]}", a, c, Dy - w, zu)
        long_rail(f"Trav. inf. post. {names[i]}", a, c, Dy - w, zl)
        if names[i] == "ricarica":
            long_rail(f"Trav. sup. ant. {names[i]}", a, c, 0, zu)
        if names[i] in ("cassetti", "ricarica"):
            long_rail(f"Trav. inf. ant. {names[i]}", a, c, 0, zl)

    # ---------------- pannelli di irrigidimento
    pc = "#e9d8b4"
    sx = (bays[1][0] + bays[1][1]) / 2
    add("Pannello posteriore", "Pannelli", "multistrato 12", 0, Dy, zl[0], W, D, leg_h, pc,
        [("y", sx, leg_h - 120, 60)])
    add("Pannello fianco sx", "Pannelli", "multistrato 12", 0, 0, zl[0], Tp, Dy, leg_h, pc)
    add("Pannello fianco dx", "Pannelli", "multistrato 12", W - Tp, 0, zl[0], W, Dy, leg_h, pc)

    # ---------------- piano con passacavi
    gh = [("z", (b[0] + b[1]) / 2, tray_y, P["grommet_d"]) for b in bays[1:]]
    add("Piano di lavoro", "Pannelli", "lamellare abete 40", 0, 0, leg_h, W, D, H, "#ecd3a8", gh)

    # ---------------- zona ricarica
    a, c = rail_x[2][1], rail_x[3][0]
    mx = (bays[2][0] + bays[2][1]) / 2
    add("Rinforzo piano ricarica", "Pannelli", "lamellare abete 40", a, w, leg_h - P["T_dbl"], c,
        tray_y - P["tray_w"] / 2 - 13, leg_h, "#e0c08f")
    bw, bd, bt = P["backer"]
    add("Contropiastra acciaio", "Ricarica", "acciaio S235", mx - bw / 2, w, leg_h - P["T_dbl"] - bt,
        mx + bw / 2, w + bd, leg_h - P["T_dbl"], "#7d848c")
    mw, md, mt = P["mount"]
    add("Base attacco piastre", "Ricarica", "acciaio", mx - mw / 2, 0, H, mx + mw / 2, md, H + mt, "#3a3f45")

    # ---------------- ripiani bassi su listelli, tra le facce delle traverse laterali
    zs1 = zl[1]; zs0 = zs1 - P["T_shelf"]; cw, ch = P["cleat"]
    def shelf(name, i, y0, y1):
        x0, x1 = rail_x[i][1], rail_x[i + 1][0]
        add(name, "Pannelli", "multistrato 18", x0, y0, zs0, x1, y1, zs1, "#e8cfa0")
        add(f"Listello reggiripiano - {name} sx", "Listelli reggiripiano", "abete 20x30",
            x0, y0, zs0 - ch, x0 + cw, y1, zs0, L1)
        add(f"Listello reggiripiano - {name} dx", "Listelli reggiripiano", "abete 20x30",
            x1 - cw, y0, zs0 - ch, x1, y1, zs0, L1)
    shelf("Ripiano basso cassetti", 0, w, Dy - w)
    shelf("Ripiano basso post. seduta", 1, Dy - w - P["rear_shelf_d"], Dy - w)
    shelf("Ripiano basso ricarica", 2, w, Dy - w)

    # ---------------- mensola rialzata: montanti 2 strati sopra le gambe posteriori
    for i, (x0, x1) in enumerate(legs):
        cx = (x0 + x1) / 2
        for k in range(2):
            add(f"Montante mensola {i+1} - strato {k+1}", "Listelli 25x50", "listello 25x50",
                cx - w / 2 + k * t, Dy - w, H, cx - w / 2 + (k + 1) * t, Dy, H + P["riser_h"],
                L1 if k == 0 else L2, role="montante")
    zr = H + P["riser_h"]
    add("Mensola rialzata", "Pannelli", "lamellare abete 27", 0, D - P["riser_d"], zr, W, D,
        zr + P["T_riser"], "#ecd3a8")

    # ---------------- canaline + ciabatta
    for i, (a, c) in enumerate(bays):
        add(f"Canalina {names[i]}", "Elettrico", "canalina acciaio", a + 5, tray_y - P["tray_w"] / 2,
            leg_h - P["tray_h"] - 10, c - 5, tray_y + P["tray_w"] / 2, leg_h - 10, "#555b63", tray=True)
    a, c = bays[1]; m = (a + c) / 2
    add("Ciabatta", "Elettrico", "ciabatta 6 prese", m - 200, tray_y - 30, leg_h - 60, m + 200, tray_y + 25,
        leg_h - 20, "#f2f2f2")

    # ---------------- cassettiera + cassetto appeso (campata sx)
    a, c = bays[0]; x0, x1 = a + 2, c - 2
    T, chh, cd = P["T_case"], P["case_h"], P["case_d"]
    z0, z1 = zs1, zs1 + chh
    CASE, FRONT = "#f0e2c4", "#5f7a8c"
    add("Cassettiera fianco sx", "Cassettiera", "multistrato 18", x0, T, z0, x0 + T, cd, z1, CASE)
    add("Cassettiera fianco dx", "Cassettiera", "multistrato 18", x1 - T, T, z0, x1, cd, z1, CASE)
    add("Cassettiera cielo", "Cassettiera", "multistrato 18", x0 + T, T, z1 - T, x1 - T, cd, z1, CASE)
    add("Cassettiera fondo", "Cassettiera", "multistrato 18", x0 + T, T, z0, x1 - T, cd, z0 + T, CASE)
    add("Cassettiera schienale", "Cassettiera", "HDF 4", x0, cd, z0, x1, cd + 4, z1, CASE)
    nd, g = P["n_drawers"], 3
    fh = (chh - (nd - 1) * g) / nd
    box_w = (x1 - x0) - 2 * T - 2 * P["slide_t"]
    for k in range(nd):
        fz0 = z0 + k * (fh + g)
        add(f"Frontale cassetto {k+1}", "Cassettiera", "multistrato 18", x0, 0, fz0, x1, T, fz0 + fh, FRONT)
        add(f"Cassetto {k+1} (scatola)", "Cassettiera", "multistrato 15", x0 + T + P["slide_t"], T, fz0 + 20,
            x0 + T + P["slide_t"] + box_w, T + P["slide_len"], fz0 + 20 + 100, "#e2c79a")
    ra, rc = rail_x[0][1], rail_x[1][0]          # facce traverse sup. laterali (guide)
    hz1 = leg_h - 3
    add("Frontale cassetto appeso", "Cassettiera", "multistrato 18", x0, 0, hz1 - P["hang_front_h"], x1, T, hz1, FRONT)
    add("Cassetto appeso (scatola)", "Cassettiera", "multistrato 15", ra + P["slide_t"], T, zu[0] - 25,
        rc - P["slide_t"], T + P["slide_len"], zu[0] - 25 + P["hang_box_h"], "#e2c79a")
    return legs, bays, rail_x

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
        elif ax == "x":
            s = s.cut(cq.Workplane("YZ").circle(d / 2).extrude(x1 - x0 + 2).translate((x0 - 1, u, v)))
        else:  # "y": (x, z)
            s = s.cut(cq.Workplane("XZ").circle(d / 2).extrude(-(y1 - y0 + 2)).translate((u, y0 - 1, v)))
    return s

def overlaps():
    """controllo interferenze tra pezzi (box), esclusi contatti di faccia"""
    bad = []
    for i in range(len(parts)):
        for j in range(i + 1, len(parts)):
            a, b = parts[i]["box"], parts[j]["box"]
            ov = [min(a[k + 3], b[k + 3]) - max(a[k], b[k]) for k in range(3)]
            if all(o > 0.5 for o in ov):
                bad.append((parts[i]["name"], parts[j]["name"], [round(o, 1) for o in ov]))
    return bad

if __name__ == "__main__":
    legs, bays, rail_x = build()
    bad = overlaps()
    for b in bad: print("INTERFERENZA:", b)
    assy = cq.Assembly(name="tavolo_listelli")
    for i, p in enumerate(parts):
        assy.add(solid(p), name=f"{i:03d}_{p['name']}".replace(" ", "_").replace(".", ""), color=cq.Color(p["color"]))
    assy.export("tavolo_listelli.step")
    json.dump(dict(params=P, legs=legs, bays=bays, rail_x=rail_x, parts=parts),
              open("parts_lam.json", "w"), indent=1)
    print(len(parts), "parti; interferenze:", len(bad))
