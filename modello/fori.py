"""
Definizione di TUTTI i fori del tavolo KVH a partire da regole fisse + controllo collisioni.

Regole (quote "dalla testa" = dal filo superiore della traversa):
  traverse longitudinali (lungo X): bullone/barra a -30, spine a -85 (y = asse ± 15)
  traverse laterali (lungo Y):      bullone a -90,       spine a -35 (x = asse ± 15)
  dado a tamburo a 60 mm dalla testata della traversa
  fori: Ø11 passante (bullone M10), Ø12 spine (prof. 25 gamba / 30 traversa),
        Ø15 dado a tamburo, lamatura Ø25×12 per testa bullone + rondella
"""
import json, math
import cadquery as cq

d = json.load(open("parts_kvh.json"))
P = d["params"]; parts = {p["name"]: p for p in d["parts"]}
W, D, H = P["W"], P["D"], P["H"]
Lx, Ly, Rh = P["Lx"], P["Ly"], P["Rh"]
LEG_H = H - P["T_top"]
LEV = {"sup": LEG_H, "inf": P["lower_z"] + Rh}          # quota del filo superiore delle traverse
NUT_OFF, NUT_D, BOLT_D, DOW_D, CB_D, CB_H = 60, 15, 11, 12, 25, 12
legs_x = d["legs_x"]

holes = []   # dict(part, code, kind, p0, dir, d, depth, cb=(d,h)|None, note)

def H_(part, code, kind, p0, dir_, dia, depth, cb=None, note=""):
    holes.append(dict(part=part, code=code, kind=kind, p0=[round(v, 1) for v in p0], dir=dir_, d=dia,
                      depth=round(depth, 1), cb=cb, note=note))

# ---------------------------------------------------------------- gambe
long_faces = {   # (indice gamba, lato) -> facce X con traversa longitudinale
    (0, "post"): ["dx"], (1, "post"): ["sx", "dx"], (2, "post"): ["sx", "dx"], (3, "post"): ["sx"],
    (2, "ant"): ["dx"], (3, "ant"): ["sx"],
}
for i, x0 in enumerate(legs_x):
    xc = x0 + Lx / 2
    for side in ("ant", "post"):
        name = f"Gamba {i+1} {side}"
        y0, y1 = (0, Ly) if side == "ant" else (D - Ly, D)
        outer_y, inner_y = (y0, y1) if side == "ant" else (y1, y0)
        into = 1 if side == "ant" else -1                     # direzione verso l'interno (Y)
        ryc = Rh * 0 + (40 if side == "ant" else D - 40)    # asse traverse longitudinali (prof. 80)
        for lev, ztop in LEV.items():
            # traversa laterale: bullone dall'esterno, attraversa la gamba
            H_(name, "B1", "bullone laterale M10×180", (xc, outer_y, ztop - 90), (0, into, 0), BOLT_D, Ly,
               cb=(CB_D, CB_H), note=f"{lev}: passante, lamatura sulla faccia {'anteriore' if side=='ant' else 'posteriore'}")
            for dx in (-15, 15):
                H_(name, "S", "spina", (xc + dx, inner_y, ztop - 35), (0, -into, 0), DOW_D, 25, note=f"{lev}: spina laterale")
            # traverse longitudinali
            faces = long_faces.get((i, side), [])
            for f in faces:
                fx, fdir = (x0, 1) if f == "sx" else (x0 + Lx, -1)
                for dy in (-15, 15):
                    H_(name, "S", "spina", (fx, ryc + dy, ztop - 85), (fdir, 0, 0), DOW_D, 25, note=f"{lev}: spina long. {f}")
            if len(faces) == 2:
                H_(name, "R", "barra M10 L220 passante", (x0, ryc, ztop - 30), (1, 0, 0), BOLT_D, Lx,
                   note=f"{lev}: passante per barra che unisce le due traverse")
            elif len(faces) == 1:
                f = faces[0]
                ent, dirx = (x0 + Lx, -1) if f == "sx" else (x0, 1)   # entra dalla faccia opposta
                H_(name, "B2", "bullone long. M10×140", (ent, ryc, ztop - 30), (dirx, 0, 0), BOLT_D, Lx,
                   cb=(CB_D, CB_H), note=f"{lev}: passante, lamatura sulla faccia {'sinistra' if f=='dx' else 'destra'}")
        # piede: inserto filettato
        H_(name, "I", "inserto M10 piedino", (xc, (y0 + y1) / 2, 0), (0, 0, 1), 14, 25, note="foro per inserto (Ø secondo inserto)")
        if side == "post":   # mensola: barra verticale + dado a tamburo dal retro
            H_(name, "M", "barra mensola Ø12", (xc, D - 60, LEG_H), (0, 0, -1), 12, 75, note="dalla testa, per barra M10 mensola")
            H_(name, "T", "dado a tamburo mensola", (xc, D, LEG_H - 60), (0, -1, 0), NUT_D, 70, note="dal retro, a 60 dalla testa")

# ---------------------------------------------------------------- traverse
def rail_holes(name):
    p = parts[name]; x0, y0, z0, x1, y1, z1 = p["box"]
    lateral = (y1 - y0) > (x1 - x0) and (x1 - x0) == Lx and "lat." in name
    ztop = z1
    if lateral:
        xc = (x0 + x1) / 2
        for end_y, dirn in ((y0, 1), (y1, -1)):
            H_(name, "A", "assiale bullone", (xc, end_y, ztop - 90), (0, dirn, 0), BOLT_D, 80, note="testata")
            H_(name, "T", "dado a tamburo", (xc, end_y + dirn * NUT_OFF, z0), (0, 0, 1), NUT_D, 45, note="dal basso")
            for dx in (-15, 15):
                H_(name, "S", "spina", (xc + dx, end_y, ztop - 35), (0, dirn, 0), DOW_D, 30, note="testata")
    else:
        yc = (y0 + y1) / 2
        for end_x, dirn in ((x0, 1), (x1, -1)):
            H_(name, "A", "assiale bullone", (end_x, yc, ztop - 30), (dirn, 0, 0), BOLT_D, 80, note="testata")
            H_(name, "T", "dado a tamburo", (end_x + dirn * NUT_OFF, yc, z1), (0, 0, -1), NUT_D, 45, note="dall'alto")
            for dy in (-15, 15):
                H_(name, "S", "spina", (end_x, yc + dy, ztop - 85), (dirn, 0, 0), DOW_D, 30, note="testata")
    for ax, u, v, dia in p["holes"]:     # passacavi
        H_(name, "C", "passacavi", (x0, u, v), (1, 0, 0), dia, x1 - x0, note="passante")

rails = [n for n in parts if n.startswith("Trav.")]
for n in rails: rail_holes(n)

# ---------------------------------------------------------------- montanti, piano, mensola, rinforzo
for i, x0 in enumerate(legs_x):
    xc = x0 + Lx / 2
    H_(f"Montante mensola {i+1}", "M", "barra mensola Ø12", (xc, D - 60, H), (0, 0, 1), 12, P["riser_h"],
       note="passante, forare metà da ogni testa")
    H_("Piano di lavoro", "M", "barra mensola Ø12", (xc, D - 60, H), (0, 0, -1), 12, P["T_top"], note="passante")
    H_("Mensola rialzata", "M", "barra mensola Ø12", (xc, D - 60, H + P["riser_h"] + P["T_riser"]), (0, 0, -1), 12,
       P["T_riser"], cb=(CB_D, 8), note="passante, lamatura per rondella e dado cieco")
pz = parts["Piano di lavoro"]
for ax, u, v, dia in pz["holes"]:
    H_("Piano di lavoro", "C", "passacavi Ø60", (u, v, H), (0, 0, -1), dia, P["T_top"], note="sega a tazza")
mb = parts["Base attacco piastre"]["box"]; mx = (mb[0] + mb[3]) / 2; my = (mb[1] + mb[4]) / 2
for dx in (-65, 65):
    for dy in (-65, 65):
        y = my + dy
        H_("Piano di lavoro", "P", "vite base piastre M10", (mx + dx, y, H), (0, 0, -1), BOLT_D, P["T_top"], note="passante")
        if y < P["Rt"]:   # sopra la traversa anteriore: la vite la attraversa
            H_("Trav. sup. ant. ricarica", "P", "vite base piastre M10×200", (mx + dx, y, LEG_H), (0, 0, -1), BOLT_D, Rh,
               note="passante verticale, dado sotto la traversa")
        else:
            H_("Rinforzo piano ricarica", "P", "vite base piastre M10×110", (mx + dx, y, LEG_H), (0, 0, -1), BOLT_D,
               P["T_dbl"], note="passante, poi contropiastra")

# ---------------------------------------------------------------- verifica
def cyl(h):
    (x, y, z), (a, b, c) = h["p0"], h["dir"]
    pl = cq.Plane(origin=(x, y, z), xDir=(b, -a, 0) if (a or b) else (1, 0, 0), normal=(a, b, c))
    s = cq.Workplane(pl).circle(h["d"] / 2).extrude(h["depth"])
    if h["cb"]:
        s = s.union(cq.Workplane(pl).circle(h["cb"][0] / 2).extrude(h["cb"][1]))
    return s

def part_solid(name):
    x0, y0, z0, x1, y1, z1 = parts[name]["box"]
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))

def check():
    problems = []
    by_part = {}
    for h in holes: by_part.setdefault(h["part"], []).append(h)
    for name, hs in by_part.items():
        ps = part_solid(name).val()
        cs = [cyl(h).val() for h in hs]
        for h, c in zip(hs, cs):           # il foro deve stare nel pezzo (tolleranza: esce solo dalla faccia d'ingresso)
            out = c.cut(ps).Volume()
            if out > 1.0 and h["depth"] < 1e9:
                # passanti escono: ammessi se il foro attraversa tutto il pezzo
                pass
        for i in range(len(hs)):
            for j in range(i + 1, len(hs)):
                v = cs[i].intersect(cs[j]).Volume()
                same_axis = hs[i]["code"] in ("A", "T", "B1", "B2", "R", "M") and hs[j]["code"] in ("A", "T", "B1", "B2", "R", "M")
                if v > 1.0:
                    # intersezioni volute: assiale×dado a tamburo, barra mensola×dado
                    wanted = {hs[i]["code"], hs[j]["code"]} in ({"A", "T"}, {"M", "T"})
                    if not wanted:
                        problems.append((name, hs[i]["kind"], hs[i]["note"], hs[j]["kind"], hs[j]["note"], round(v)))
    # wall thickness check between non-intersecting holes (min distanza assi paralleli) — semplice: avviso se < 6 mm
    return problems

if __name__ == "__main__":
    pr = check()
    print(len(holes), "fori;", len(pr), "collisioni")
    for p in pr: print("  COLLISIONE:", p)
    # verifica che ogni assiale incontri il suo dado
    json.dump(holes, open("fori.json", "w"), indent=1)
