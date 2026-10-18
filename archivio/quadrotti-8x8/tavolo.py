"""
Tavolo da lavoro in quadrotti di abete 8x8 - modello parametrico (CadQuery)
Unità: millimetri. Origine: spigolo anteriore-sinistro a terra.
  X = larghezza (sinistra -> destra), Y = profondità (fronte -> retro), Z = altezza
Modifica i parametri in P e rilancia: python tavolo.py
"""
import json
import cadquery as cq

P = dict(
    W=2000,          # larghezza tavolo
    D=800,           # profondità tavolo
    H=740,           # altezza piano finito da terra
    S=80,            # sezione quadrotti (verificare la misura reale del piallato!)
    T_top=40,        # spessore piano (lamellare abete)
    bays=[500, 700, 480],   # luci nette campate: cassetti (sx), seduta, ricarica (dx)
    T_dbl=40,        # rinforzo piano (secondo strato) nella zona ricarica
    mount=(180, 180, 10),   # base attacco piastre intercambiabili (L, P, sp.) - adattare al sistema reale
    backer=(220, 220, 6),   # piastra acciaio di contrasto sotto il rinforzo
    upper_h=80,      # altezza traverse superiori (= S)
    lower_z=70,      # quota da terra del filo inferiore traverse basse
    T_shelf=18,      # spessore ripiani bassi (multistrato)
    rear_shelf_d=300,  # profondità ripiano posteriore nella campata seduta
    riser_h=250,     # altezza montanti mensola sopra il piano
    riser_d=260,     # profondità mensola
    T_riser=27,      # spessore mensola (lamellare abete)
    cleat=(20, 30),  # listelli reggi-ripiano (larghezza, altezza)
    tray_w=100, tray_h=60,  # canalina passacavi (profondità, altezza)
    grommet_d=60,    # passacavi nel piano
    case_h=420, case_d=600, T_case=18,   # cassettiera
    n_drawers=3, slide_len=500, slide_t=12.7,
    hang_front_h=97, hang_box_h=70,     # cassetto appeso
)

parts = []  # dict(name, group, mat, box=(x0,y0,z0,x1,y1,z1), color, holes)

def add(name, group, mat, x0, y0, z0, x1, y1, z1, color, holes=None, cut=False):
    parts.append(dict(name=name, group=group, mat=mat,
                      box=[round(v, 1) for v in (x0, y0, z0, x1, y1, z1)],
                      color=color, holes=holes or [], tray=cut))

def build():
    W, D, H, S = P["W"], P["D"], P["H"], P["S"]
    leg_h = H - P["T_top"]
    b = P["bays"]
    assert abs(sum(b) + 4 * S - W) < 0.5, "campate + 4 gambe != larghezza"
    xs = [0, S + b[0], 2 * S + b[0] + b[1], W - S]    # x inizio gambe
    bay_x = [(xs[i] + S, xs[i + 1]) for i in range(3)]  # luci nette campate
    yF, yB = (0, S), (D - S, D)
    WOOD, RAIL, PLY = "#d9b382", "#c99a62", "#e8cfa0"

    # --- gambe
    for i, x in enumerate(xs):
        for side, (y0, y1) in (("ant", yF), ("post", yB)):
            add(f"Gamba {i+1} {side}", "Quadrotti 8x8", "abete 8x8", x, y0, 0, x + S, y1, leg_h, WOOD)

    zu = (leg_h - P["upper_h"], leg_h)
    zl = (P["lower_z"], P["lower_z"] + S)
    names = ["cassetti", "seduta", "ricarica"]
    # --- traverse
    for i, (a, c) in enumerate(bay_x):
        add(f"Trav. sup. post. {names[i]}", "Quadrotti 8x8", "abete 8x8", a, *yB[:1], zu[0], c, yB[1], zu[1], RAIL)
        add(f"Trav. inf. post. {names[i]}", "Quadrotti 8x8", "abete 8x8", a, yB[0], zl[0], c, yB[1], zl[1], RAIL)
        if names[i] == "ricarica":
            add(f"Trav. sup. ant. {names[i]}", "Quadrotti 8x8", "abete 8x8", a, yF[0], zu[0], c, yF[1], zu[1], RAIL)
        if names[i] in ("cassetti", "ricarica"):
            add(f"Trav. inf. ant. {names[i]}", "Quadrotti 8x8", "abete 8x8", a, yF[0], zl[0], c, yF[1], zl[1], RAIL)
    for i, x in enumerate(xs):
        # fori passacavi Ø35 nelle traverse sup. laterali interne (passaggio canalina)
        holes = []
        if i in (1, 2):
            holes = [("x", D - S - P["tray_w"] / 2 - 5, zu[0] + 40, 35)]
        add(f"Trav. sup. lat. {i+1}", "Quadrotti 8x8", "abete 8x8", x, S, zu[0], x + S, D - S, zu[1], RAIL, holes)
        add(f"Trav. inf. lat. {i+1}", "Quadrotti 8x8", "abete 8x8", x, S, zl[0], x + S, D - S, zl[1], RAIL)

    # --- piano con passacavi
    gy = D - S - P["tray_w"] / 2 - 5
    gh = [("z", (bay_x[1][0] + bay_x[1][1]) / 2, gy, P["grommet_d"]),
          ("z", (bay_x[2][0] + bay_x[2][1]) / 2, gy, P["grommet_d"])]
    add("Piano di lavoro", "Pannelli", "lamellare abete 40", 0, 0, leg_h, W, D, H, "#ecd3a8", gh)

    # --- zona ricarica: rinforzo piano + attacco piastre + contropiastra acciaio
    a, c = bay_x[2]; mx = (a + c) / 2
    add("Rinforzo piano ricarica", "Pannelli", "lamellare abete 40", a, S, leg_h - P["T_dbl"], c,
        D - S - P["tray_w"] - 15, leg_h, "#e0c08f")
    bw, bd, bt = P["backer"]
    add("Contropiastra acciaio", "Ricarica", "acciaio S235", mx - bw / 2, S, leg_h - P["T_dbl"] - bt,
        mx + bw / 2, S + bd, leg_h - P["T_dbl"], "#7d848c")
    mw, md, mt = P["mount"]
    add("Base attacco piastre", "Ricarica", "acciaio", mx - mw / 2, 0, H, mx + mw / 2, md, H + mt, "#3a3f45")

    # --- ripiani bassi su listelli
    zs1 = zl[1]; zs0 = zs1 - P["T_shelf"]
    cw, ch = P["cleat"]
    def shelf(name, x0, x1, y0, y1):
        add(name, "Pannelli", "multistrato 18", x0, y0, zs0, x1, y1, zs1, PLY)
        add(f"Listello sx - {name}", "Listelli", "abete 20x30", x0, y0, zs0 - ch, x0 + cw, y1, zs0, WOOD)
        add(f"Listello dx - {name}", "Listelli", "abete 20x30", x1 - cw, y0, zs0 - ch, x1, y1, zs0, WOOD)
    shelf("Ripiano basso cassetti", *bay_x[0], S, D - S)
    shelf("Ripiano basso ricarica", *bay_x[2], S, D - S)
    shelf("Ripiano basso post. seduta", *bay_x[1], D - S - P["rear_shelf_d"], D - S)

    # --- mensola rialzata: montanti sopra le gambe posteriori
    for i, x in enumerate(xs):
        add(f"Montante mensola {i+1}", "Quadrotti 8x8", "abete 8x8", x, yB[0], H, x + S, yB[1], H + P["riser_h"], WOOD)
    zr = H + P["riser_h"]
    add("Mensola rialzata", "Pannelli", "lamellare abete 27", 0, D - P["riser_d"], zr, W, D, zr + P["T_riser"], "#ecd3a8")

    # --- canaline passacavi (una per campata) appese alla traversa sup. posteriore
    for i, (a, c) in enumerate(bay_x):
        add(f"Canalina {names[i]}", "Elettrico", "canalina acciaio", a + 5, D - S - P["tray_w"] - 5,
            leg_h - P["tray_h"] - 10, c - 5, D - S - 5, leg_h - 10, "#555b63", cut=True)
    a, c = bay_x[1]; mid = (a + c) / 2
    add("Ciabatta", "Elettrico", "ciabatta 6 prese", mid - 200, D - S - 85, leg_h - 60, mid + 200, D - S - 30,
        leg_h - 20, "#f2f2f2")

    # --- cassettiera (campata sinistra), appoggiata sul ripiano basso
    a, c = bay_x[0]; gap = 2
    x0, x1 = a + gap, c - gap
    T, ch_, cd = P["T_case"], P["case_h"], P["case_d"]
    z0, z1 = zs1, zs1 + ch_
    CASE, FRONT = "#f0e2c4", "#5f7a8c"
    add("Cassettiera fianco sx", "Cassettiera", "multistrato 18", x0, T, z0, x0 + T, cd, z1, CASE)
    add("Cassettiera fianco dx", "Cassettiera", "multistrato 18", x1 - T, T, z0, x1, cd, z1, CASE)
    add("Cassettiera cielo", "Cassettiera", "multistrato 18", x0 + T, T, z1 - T, x1 - T, cd, z1, CASE)
    add("Cassettiera fondo", "Cassettiera", "multistrato 18", x0 + T, T, z0, x1 - T, cd, z0 + T, CASE)
    add("Cassettiera schienale", "Cassettiera", "HDF 4", x0, cd, z0, x1, cd + 4, z1, CASE)
    n, g = P["n_drawers"], 3
    fh = (ch_ - (n - 1) * g) / n
    inner_w = (x1 - x0) - 2 * T
    box_w = inner_w - 2 * P["slide_t"]
    for k in range(n):
        fz0 = z0 + k * (fh + g)
        add(f"Frontale cassetto {k+1}", "Cassettiera", "multistrato 18", x0, 0, fz0, x1, T, fz0 + fh, FRONT)
        bz0 = fz0 + 20
        add(f"Cassetto {k+1} (scatola)", "Cassettiera", "multistrato 15", x0 + T + P["slide_t"], T, bz0,
            x0 + T + P["slide_t"] + box_w, T + P["slide_len"], bz0 + 100, "#e2c79a")
    # --- cassetto appeso sotto il piano, guide sulle traverse sup. laterali
    hz1 = leg_h - 3; hz0 = hz1 - P["hang_front_h"]
    add("Frontale cassetto appeso", "Cassettiera", "multistrato 18", x0, 0, hz0, x1, T, hz1, FRONT)
    hb_w = (c - a) - 2 * P["slide_t"]
    add("Cassetto appeso (scatola)", "Cassettiera", "multistrato 15", a + P["slide_t"], T, zu[0] - 5,
        a + P["slide_t"] + hb_w, T + P["slide_len"], zu[0] - 5 + P["hang_box_h"], "#e2c79a")
    return xs, bay_x

def solid(p):
    x0, y0, z0, x1, y1, z1 = p["box"]
    s = cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))
    if p["tray"]:
        t = 2
        s = s.cut(cq.Workplane("XY").box(x1 - x0, y1 - y0 - 2 * t, z1 - z0 - t, centered=False)
                  .translate((x0, y0 + t, z0 + t)))
    for ax, u, v, d in p["holes"]:
        if ax == "z":
            s = s.cut(cq.Workplane("XY").circle(d / 2).extrude(z1 - z0 + 2).translate((u, v, z0 - 1)))
        else:  # foro lungo X: (y, z)
            s = s.cut(cq.Workplane("YZ").circle(d / 2).extrude(x1 - x0 + 2).translate((x0 - 1, u, v)))
    return s

if __name__ == "__main__":
    xs, bay_x = build()
    assy = cq.Assembly(name="tavolo")
    for i, p in enumerate(parts):
        assy.add(solid(p), name=f"{i:02d}_{p['name']}".replace(" ", "_").replace(".", ""),
                 color=cq.Color(p["color"]))
    assy.export("tavolo.step")
    json.dump(dict(params=P, legs_x=xs, bays=bay_x, parts=parts), open("parts.json", "w"), indent=1)
    print(len(parts), "parti; STEP esportato")
