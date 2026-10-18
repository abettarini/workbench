"""Dettaglio esploso del nodo KVH: gamba 2 posteriore + traversa laterale sup. + traverse longitudinali sup."""
import json
import cadquery as cq
from piastre import render

d = json.load(open("parts_kvh.json"))
x0, x1 = d["legs"][1]
cx, cy, cz = (x0 + x1) / 2, 740, 640
EX = 170
P = []

def box(b, off=(0, 0, 0), clip=None):
    b = list(b)
    if clip:
        for k in range(6):
            if clip[k] is not None: b[k] = max(b[k], clip[k]) if k < 3 else min(b[k], clip[k])
    x0_, y0_, z0_, x1_, y1_, z1_ = b
    return cq.Workplane("XY").box(x1_ - x0_, y1_ - y0_, z1_ - z0_, centered=False).translate(
        (x0_ - cx + off[0], y0_ - cy + off[1], z0_ - cz + off[2]))

def bolt(L, d, axis, at):
    wp = {"x": "YZ", "y": "XZ", "z": "XY"}[axis]
    s = cq.Workplane(wp).circle(d / 2).extrude(L)
    if axis == "y": s = s.mirror("XZ")
    return s.translate(at)

for p in d["parts"]:
    n, b = p["name"], p["box"]
    if n == "Gamba 2 post":
        P.append((n, box(b, clip=(None, None, 460, None, None, None)), p["color"]))
    elif n == "Trav. sup. lat. 2":
        P.append((n, box(b, (0, -EX, 0), clip=(None, 470, None, None, None, None)), p["color"]))
    elif n == "Trav. sup. post. cassetti":
        P.append((n, box(b, (-EX, 0, 0), clip=(x0 - 240, None, None, None, None, None)), p["color"]))
    elif n == "Trav. sup. post. seduta":
        P.append((n, box(b, (EX, 0, 0), clip=(None, None, None, x1 + 240, None, None)), p["color"]))

zt = 700 - cz           # testa gamba
yl = 800 - 40 - cy      # asse traverse longitudinali (Y centro = 760)
# bulloni longitudinali: attraversano la gamba in X a quota alta, sfalsati rispetto al laterale
zA, zB = zt - 30, zt - 30
P.append(("bullone L sx", bolt(160, 10, "x", (x0 - cx - 160 + 20 - EX * 0.5, yl, zA)), "#b8bcc2"))
P.append(("bullone L dx", bolt(160, 10, "x", (x1 - cx - 20 + EX * 0.5, yl, zB)), "#b8bcc2"))
# dadi a tamburo verticali nelle traverse longitudinali
P.append(("dado sx", bolt(60, 13, "z", (x0 - cx - 60 - EX, yl, zt + 60)), "#8f959b"))
P.append(("dado dx", bolt(60, 13, "z", (x1 - cx + 60 + EX, yl, zt + 60)), "#8f959b"))
# bullone laterale: attraversa la gamba in Y (dal retro) a quota intermedia
P.append(("bullone lat", bolt(180, 10, "y", (0, 800 - cy + 20, zt - 90)), "#b8bcc2"))
P.append(("dado lat", bolt(60, 15, "z", (0, 680 - 60 - cy - EX, zt + 60)), "#8f959b"))
# spine Ø12 sulle testate delle traverse
for dx in (-15, 15):
    P.append(("spina", bolt(40, 12, "y", (dx, 680 - cy - EX + 20, zt - 35)), "#d4a017"))

L = [
    ((x0 - cx + 40, 680 - cy, zt - 170), "① Gamba KVH 80×120 (120 in profondità)", "L", 700),
    ((x0 - cx - EX - 150, 800 - cy, zt - 60), "② Traverse longitudinali 80×120", "L", 600),
    ((20, 680 - cy - EX + 20, zt - 35), "③ 2 spine Ø12 in faggio per nodo, incollate", "L", 820),
    ((40, 560 - cy - EX, zt - 100), "④ Traversa laterale 80×120 di coltello", "R", 760),
    ((x1 - cx + EX * 0.5 + 100, yl, zB), "⑤ Gambe centrali: barra M10 L220 passante\n    a −30 dalla testa (estremità: bullone M10×140)", "R", 480),
    ((x1 - cx + 60 + EX, yl, zt + 90), "⑥ Dadi a tamburo M10 in fori Ø15 a 60 mm\n    dalla testata (qui estratti)", "R", 300),
    ((0, 800 - cy + 20 + 100, zt - 90), "⑦ Bullone M10×180 della traversa laterale\n    a −90: passa sotto la barra", "L", 380),
]
render(P, "kvh_dettaglio_nodo.png", L, az=-35, el=28, size=(1500, 1100), zoom=1.0)
print("ok")
