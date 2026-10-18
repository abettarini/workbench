"""Dettaglio esploso del nodo laminato: gamba 2 posteriore (3 strati) + traversa laterale sup. + traverse longitudinali."""
import json
import cadquery as cq
from piastre import render

d = json.load(open("parts_lam.json"))
leg = d["legs"][1]; t = d["params"]["t"]; w = d["params"]["w"]
cx, cy, cz = (leg[0] + leg[1]) / 2, 763, 640
Z0 = 470                       # taglio inferiore del dettaglio
P = []

def box(b, col, off=(0, 0, 0), clip=None):
    x0, y0, z0, x1, y1, z1 = b
    if clip: x0, y0, z0, x1, y1, z1 = [max(v, c) if i < 3 else min(v, c) for i, (v, c) in enumerate(zip(b, clip))]
    s = cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate(
        (x0 - cx + off[0], y0 - cy + off[1], z0 - cz + off[2]))
    return s

clip_leg = (-1e9, -1e9, Z0, 1e9, 1e9, 1e9)
for p in d["parts"]:
    n, b = p["name"], p["box"]
    if n.startswith("Gamba 2 post"):
        if b[5] <= Z0: continue
        P.append((n, box(b, p["color"], clip=clip_leg), p["color"]))
    elif n.startswith("Trav. sup. lat. 2"):
        P.append((n, box(b, p["color"], (0, 0, 230), clip=(-1e9, 520, -1e9, 1e9, 1e9, 1e9)), p["color"]))
    elif n.startswith("Trav. sup. post. cassetti"):
        P.append((n, box(b, p["color"], (-190, 0, 0), clip=(leg[0] - 200, -1e9, -1e9, 1e9, 1e9, 1e9)), p["color"]))
    elif n.startswith("Trav. sup. post. seduta"):
        P.append((n, box(b, p["color"], (190, 0, 0), clip=(-1e9, -1e9, -1e9, leg[1] + 200, 1e9, 1e9)), p["color"]))
# barra filettata M8 passante + dadi a tamburo (nelle traverse longitudinali, a 35 mm dalla gamba)
zr = 675 - cz
rod = cq.Workplane("YZ").circle(4).extrude(leg[1] - leg[0] + 2 * 60).translate((leg[0] - 60 - cx, 0, zr))
P.append(("barra", rod, "#b8bcc2"))
for sx, xo in ((-1, leg[0] - 35), (1, leg[1] + 35)):
    nut = cq.Workplane("XY").circle(6.5).extrude(44).translate((xo - cx + sx * 190, 0, zr - 22 + 110))
    P.append(("dado", nut, "#9aa0a6"))

L = [
    ((leg[0] - cx + 12, -25, 700 - cz - 5), "① Strati esterni della gamba: interi", "L"),
    ((leg[0] - cx + t + 12, -25, 640 - cz), "② Strato centrale interrotto:\n    forma la mortasa aperta in testa", "L"),
    ((leg[0] - cx + t + 12, -240, 240 + 25), "③ Traversa laterale – strato centrale\n    lungo 788: tenone passante", "R"),
    ((leg[0] - cx + 5, -200, 240 + 25), "④ Traversa laterale – 2° strato\n    tra le gambe (688)", "L"),
    ((leg[0] - cx - 190 - 120, -25, 30), "⑤ Traverse longitudinali (2 strati)", "L"),
    ((leg[1] - cx + 190 + 35, 0, zr + 110 + 22), "⑥ Dadi a tamburo M8 (in sedi verticali\n    nelle traverse)", "R"),
    ((leg[1] - cx + 50, 0, zr), "⑦ Barra M8 passante: serra traverse,\n    gamba e tenone", "R"),
]
render(P, "lam_dettaglio_incastro.png", L, az=-28, el=30, size=(1500, 1100), zoom=1.05)
print("ok")
