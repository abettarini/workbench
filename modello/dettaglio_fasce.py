"""Dettaglio esploso del nodo: gamba 2 posteriore + traversa laterale L2s (bullone B1 + dado a tamburo + spine)
+ fascia posteriore alta FPa (viti 8×160) -> kvh_dettaglio_nodo.png"""
import json
import cadquery as cq
from piastre import render

d = json.load(open("parts_kvh.json")); holes = json.load(open("fori.json"))
parts = {p["name"]: p for p in d["parts"]}
g = parts["Gamba 2 post"]["box"]
cx, cy, cz = (g[0] + g[3]) / 2, (g[1] + g[4]) / 2, 600
EX = 190
P = []

def box(b, off=(0, 0, 0), clip=None):
    b = list(b)
    if clip:
        for k in range(6):
            if clip[k] is not None: b[k] = max(b[k], clip[k]) if k < 3 else min(b[k], clip[k])
    x0_, y0_, z0_, x1_, y1_, z1_ = b
    return cq.Workplane("XY").box(x1_ - x0_, y1_ - y0_, z1_ - z0_, centered=False).translate(
        (x0_ - cx + off[0], y0_ - cy + off[1], z0_ - cz + off[2]))

def cyl(L, dia, axis, at, sign=1):
    wp = {"x": "YZ", "y": "XZ", "z": "XY"}[axis]
    s = cq.Workplane(wp).circle(dia / 2).extrude(L)
    if axis == "y" and sign > 0: s = s.mirror("XZ")     # XZ estrude verso -y: specchia per andare verso +y
    return s.translate((at[0] - cx, at[1] - cy, at[2] - cz))

ZC = 470
P.append(("G2P", box(g, clip=(None, None, ZC, None, None, None)), parts["Gamba 2 post"]["color"]))
lb = parts["Trav. sup. lat. 2"]["box"]
P.append(("L2s", box(lb, (0, -EX, 0), clip=(None, lb[4] - 230, None, None, None, None)), parts["Trav. sup. lat. 2"]["color"]))
fb = parts["Fascia post. alta"]["box"]
EF = 420
P.append(("FPa", box(fb, (0, EF, 0), clip=(g[0] - 260, None, None, g[3] + 260, None, None)), parts["Fascia post. alta"]["color"]))
# bullone B1 (sfilato di 60 verso il retro), dado a tamburo nella traversa, spine
xc = (g[0] + g[3]) / 2
zb = lb[5] - 90
P.append(("B1", cyl(180, 10, "y", (xc, g[4] + 60, zb), sign=-1), "#b8bcc2"))
P.append(("B1 testa", cyl(10, 16, "y", (xc, g[4] + 70, zb), sign=-1), "#8f959b"))
P.append(("dado", cyl(45, 15, "z", (xc, lb[4] - 60 - EX, lb[2])), "#8f959b"))
for dx in (-15, 15):
    P.append(("spina", cyl(50, 12, "y", (xc + dx, lb[4] - 30 - EX, lb[5] - 35)), "#d4a017"))
# viti della fascia (si muovono con la fascia)
for h in holes:
    if h["part"] == "Gamba 2 post" and h["code"] == "V" and "alta" in h["note"]:
        x, _, z = h["p0"]
        P.append(("vite", cyl(160, 8, "y", (x, fb[4] + EF, z), sign=-1), "#c9a227"))
        P.append(("testa", cyl(5, 15, "y", (x, fb[4] + EF + 5, z), sign=-1), "#a8861c"))
L = [
    ((g[0], g[4], 540), "① Gamba G2P 80×120", "L", 800),
    ((xc, lb[4] - 120 - EX, lb[5]), "② Traversa laterale L2s:\n    2 spine Ø12 incollate +\n    dado a tamburo a 60 dalla testata", "L", 230),
    ((xc, g[4] + 40, zb), "③ Bullone B1 M10×180 dal retro della gamba,\n    nella lamatura Ø25: si stringe PRIMA della fascia", "R", 820),
    ((g[3] + 200, fb[4] + EF, fb[5]), "④ Fascia posteriore alta FPa 1990×80×120", "R", 170),
    ((xc + 16, fb[4] + EF, 640), "⑤ 2 viti 8×160 per gamba, perpendicolari:\n    80 nella fascia + 80 nella gamba (preforo Ø5)", "R", 520),
]
L = [((p[0] - cx, p[1] - cy, p[2] - cz),) + tuple(rest) for p, *rest in L]
render(P, "kvh_dettaglio_nodo.png", L, az=128, el=30, size=(1500, 1100), zoom=1.0)
print("ok")
