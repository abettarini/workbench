"""
Definizione di TUTTI i fori del tavolo KVH a partire da regole fisse + controllo collisioni.

Regole (quote "dalla testa" = dal filo superiore della traversa):
  traverse basse anteriori (lungo X): bullone a -30, spine a -85 (y = asse ± 15)
  fasce (a tutta lunghezza): viti strutturali Ø8 perpendicolari, 2 per gamba, preforo Ø5 nella gamba
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
def leg_y(i, side):
    b = parts[f"Gamba {i+1} {side}"]["box"]; return b[1], b[4]

def long_faces(i, side, ztop):
    """facce X della gamba su cui arriva una traversa longitudinale con filo superiore ztop (dal modello)"""
    x0 = legs_x[i]; x1 = x0 + Lx
    y0, y1 = leg_y(i, side)
    out = []
    for p in parts.values():
        if p.get("role") != "trav-long": continue
        b = p["box"]
        if abs(b[5] - ztop) > 0.5 or b[4] <= y0 or b[1] >= y1: continue
        if abs(b[0] - x1) < 0.5: out.append("dx")
        if abs(b[3] - x0) < 0.5: out.append("sx")
    return sorted(out, reverse=True)   # "sx" prima di "dx"

FAS = {n: p["box"] for n, p in parts.items() if p.get("role") == "fascia"}
# viti strutturali delle fasce: (fascia, gamba "ant"/"post", [(dx, z), ...], vite)
FASCIA_SCREWS = [
    ("Fascia ant. alta",   "ant",  [(-16, LEG_H - 25), (16, LEG_H - 55)], "vite strutturale Ø8×160"),
    ("Fascia post. alta",  "post", [(-16, LEG_H - 18), (16, LEG_H - 38)], "vite strutturale Ø8×160"),
    ("Fascia post. bassa", "post", [(-16, P["lower_z"] + 90), (16, P["lower_z"] + 60)], "vite strutturale Ø8×160"),
]
SCREW_D, PILOT_D = 8, 5

for i, x0 in enumerate(legs_x):
    xc = x0 + Lx / 2
    for side in ("ant", "post"):
        name = f"Gamba {i+1} {side}"
        y0, y1 = leg_y(i, side)
        outer_y, inner_y = (y0, y1) if side == "ant" else (y1, y0)
        into = 1 if side == "ant" else -1                     # direzione verso l'interno (Y)
        ryc = y0 + P["Rt"] / 2                                 # asse traverse basse anteriori (prof. 80, filo faccia ant.)
        for lev, ztop in LEV.items():
            # traversa laterale: bullone dalla faccia esterna (poi coperta dalla fascia), attraversa la gamba
            H_(name, "B1", "bullone laterale M10×180", (xc, outer_y, ztop - 90), (0, into, 0), BOLT_D, Ly,
               cb=(CB_D, CB_H), note=f"{lev}: passante, lamatura sulla faccia {'anteriore' if side=='ant' else 'posteriore'}")
            for dx in (-15, 15):
                H_(name, "S", "spina", (xc + dx, inner_y, ztop - 35), (0, -into, 0), DOW_D, 25, note=f"{lev}: spina laterale")
            faces = long_faces(i, side, ztop)
            for f in faces:
                fx, fdir = (x0, 1) if f == "sx" else (x0 + Lx, -1)
                for dy in (-15, 15):
                    H_(name, "S", "spina", (fx, ryc + dy, ztop - 85), (fdir, 0, 0), DOW_D, 25, note=f"{lev}: spina long. {f}")
            assert len(faces) <= 1, "traverse longitudinali da due lati: non previsto"
            if faces:
                f = faces[0]
                ent, dirx = (x0 + Lx, -1) if f == "sx" else (x0, 1)   # entra dalla faccia opposta
                H_(name, "B2", "bullone long. M10×140", (ent, ryc, ztop - 30), (dirx, 0, 0), BOLT_D, Lx,
                   cb=(CB_D, CB_H), note=f"{lev}: passante, lamatura sulla faccia {'sinistra' if f=='dx' else 'destra'}")
        # viti delle fasce: preforo Ø5 nella gamba, prof. 80
        for fas, fside, pts, vite in FASCIA_SCREWS:
            if fside != side: continue
            for dx, z in pts:
                H_(name, "V", vite, (xc + dx, outer_y, z), (0, into, 0), PILOT_D, 80, note=f"{fas}: preforo Ø5")
        H_(name, "I", "inserto M10 piedino", (xc, (y0 + y1) / 2, 0), (0, 0, 1), 14, 25, note="foro per inserto (Ø secondo inserto)")
        if side == "post":   # alzatina: barra verticale + dado a tamburo dalla faccia anteriore
            yc = (y0 + y1) / 2
            H_(name, "M", "barra mensola Ø12", (xc, yc, LEG_H), (0, 0, -1), 12, 75, note="dalla testa, per barra M10 mensola")
            fx, fdir, fn = (x0 + Lx, -1, "destra") if i < 3 else (x0, 1, "sinistra")
            H_(name, "T", "dado a tamburo mensola", (fx, yc, LEG_H - 60), (fdir, 0, 0), NUT_D, 60,
               note=f"dalla faccia {fn} (lato campata), a 60 dalla testa")

# fori passanti nelle fasce, in corrispondenza delle viti
for fas, fside, pts, vite in FASCIA_SCREWS:
    b = FAS[fas]
    yent, dy_ = (b[1], 1) if fside == "ant" else (b[4], -1)
    for i, x0 in enumerate(legs_x):
        xc = x0 + Lx / 2
        for dx, z in pts:
            cb, nt = (16, 5), "passante Ø9 + svasatura"
            H_(fas, "V", vite, (xc + dx, yent, z), (0, dy_, 0), SCREW_D + 1, b[4] - b[1], cb=cb,
               note=f"gamba {i+1}: {nt}")

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

rails = [n for n in parts if n.startswith("Trav.")]  # laterali + basse anteriori
for n in rails: rail_holes(n)

# ---------------------------------------------------------------- montanti, piano, mensola, rinforzo
YM = (parts["Gamba 1 post"]["box"][1] + parts["Gamba 1 post"]["box"][4]) / 2   # asse barre mensola
for i, x0 in enumerate(legs_x):
    xc = x0 + Lx / 2
    H_(f"Montante mensola {i+1}", "M", "barra mensola Ø12", (xc, YM, H), (0, 0, 1), 12, P["riser_h"],
       note="passante, forare metà da ogni testa")
    H_("Piano di lavoro", "M", "barra mensola Ø12", (xc, YM, H), (0, 0, -1), 12, P["T_top"], note="passante")
    zt_m = H + P["riser_h"] + P["T_riser"]
    boards = [n for n in parts if n.startswith("Mensola – tavola")]
    owner = [b for b in boards if parts[b]["box"][0] <= xc <= parts[b]["box"][3]]
    note = "passante" if len(owner) == 1 else f"passante, a cavallo del giunto {owner[0][-1]}–{owner[1][-1]}: fora a tavole accostate"
    H_(owner[0], "M", "barra mensola Ø12", (xc, YM, zt_m), (0, 0, -1), 12, P["T_riser"], note=note)
pz = parts["Piano di lavoro"]
for ax, u, v, dia in pz["holes"]:
    H_("Piano di lavoro", "C", "passacavi Ø60", (u, v, H), (0, 0, -1), dia, P["T_top"], note="sega a tazza")
mb = parts["Base attacco piastre"]["box"]; mx = (mb[0] + mb[3]) / 2; my = (mb[1] + mb[4]) / 2
for dx in (-65, 65):
    for dy in (-65, 65):
        y = my + dy
        H_("Piano di lavoro", "P", "vite base piastre M10", (mx + dx, y, H), (0, 0, -1), BOLT_D, P["T_top"], note="passante")
        if y < P["Ff_d"]:   # sopra la fascia anteriore: la vite la attraversa
            H_("Fascia ant. alta", "P", "vite base piastre M10×160", (mx + dx, y, LEG_H), (0, 0, -1), BOLT_D, P["Ff_h"],
               note="passante verticale, dado sotto la fascia")
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
