"""Viste 3D dei moduli cassettiera e alzatina."""
import json, copy
from tavolo_kvh import solid
from piastre import render

ALL = json.load(open("parts_kvh.json"))["parts"]
GHOST = "#e9e4dc"

def stage(fname, parts, off=lambda p: (0, 0, 0), color=lambda p: p["color"], labels=(), az=-35, el=24, zoom=1.0,
          size=(1500, 1000)):
    P = [(p["name"], solid(p).translate(off(p)), color(p)) for p in parts]
    L = []
    for name, where, txt, side, ty in labels:
        p = next(q for q in parts if q["name"] == name)
        x0, y0, z0, x1, y1, z1 = p["box"]; dx, dy, dz = off(p)
        pt = {"c": ((x0+x1)/2, (y0+y1)/2, (z0+z1)/2), "top": ((x0+x1)/2, (y0+y1)/2, z1),
              "front": ((x0+x1)/2, y0, (z0+z1)/2), "bottom": ((x0+x1)/2, (y0+y1)/2, z0)}[where]
        L.append(((pt[0]+dx, pt[1]+dy, pt[2]+dz), txt, side, ty))
    render(P, fname, L, az=az, el=el, size=size, zoom=zoom)

base = [p for p in ALL if p["module"] == "base"]
cas = [p for p in ALL if p["module"] == "cassettiera"]
alz = [p for p in ALL if p["module"] == "alzatina"]

# tavolo completo
stage("tavolo_completo.png", ALL, az=-35, el=22, zoom=1.15)

# --- cassettiera: installazione (porzione sinistra del tavolo)
left = [p for p in base if p["box"][0] < 700]
def off_ci(p):
    n = p["name"]
    if p["module"] != "cassettiera": return (0, 0, 0)
    return (0, -420, 0)
stage("cas_installazione.png", left + cas, off_ci, color=lambda p: p["color"] if p["module"] == "cassettiera" else GHOST,
      labels=[("Cassettiera fianco dx", "c", "La cassettiera completa entra dal fronte\ne appoggia sul ripiano OSB", "R", 760),
              ("Frontale cassetto appeso", "front", "Cassetto appeso: guide su L1s/G1A e L2s/G2A", "L", 240),
              ("Ripiano basso cassetti", "front", "Ripiano della campata cassetti (tavolo base)", "L", 860)],
      az=-38, el=20, zoom=1.0)

# --- cassettiera: esploso della scatola
def off_ce(p):
    n = p["name"]
    if n == "Cassettiera fianco sx": return (-160, 0, 0)
    if n == "Cassettiera fianco dx": return (160, 0, 0)
    if n == "Cassettiera cielo": return (0, 0, 140)
    if n == "Cassettiera fondo": return (0, 0, -120)
    if n == "Cassettiera schienale": return (0, 180, 0)
    if n.startswith("Frontale cassetto ") and "appeso" not in n: return (0, -380, 0)
    if "(scatola)" in n and "appeso" not in n: return (0, -200, 0)
    return (0, 0, 0)
box_parts = [p for p in cas if "appeso" not in p["name"]]
stage("cas_esploso.png", box_parts, off_ce, labels=[
    ("Cassettiera fianco sx", "c", "Fianchi 582×400 (multistrato 18)", "L", 520),
    ("Cassettiera cielo", "top", "Cielo e fondo TRA i fianchi", "L", 200),
    ("Cassettiera schienale", "c", "Schienale HDF 4", "R", 200),
    ("Cassetto 3 (scatola)", "c", "Scatole dei cassetti (multistrato 15)", "R", 520),
    ("Frontale cassetto 1", "front", "Frontali 496×131 (multistrato 18)", "R", 800),
], az=-35, el=22, zoom=1.0)

# --- alzatina: installazione
right_back = [p for p in base if p["box"][4] > 600]
def off_ai(p):
    if p["group"] == "Alzatina": return (0, 0, 260)
    if p["name"].startswith("Montante"): return (0, 0, 120)
    return (0, 0, 0)
stage("alz_installazione.png", base + alz, off_ai, color=lambda p: p["color"] if p["module"] == "alzatina" else GHOST,
      labels=[("Mensola – tavola 2", "top", "Mensola: 3 tavole lamellari 1000×200×18\n(tagliate a 620 + 780 + 600)", "L", 140),
              ("Listello mensola", "front", "Listello 30×40 incollato sotto\nil bordo anteriore", "L", 320),
              ("Montante mensola 1", "c", "4 montanti KVH 80×120×250\n(tagliati con il tavolo base)", "L", 560),
              ("Montante mensola 4", "bottom", "Barre M10 nei dadi a tamburo\npredisposti nelle gambe posteriori", "R", 640)],
      az=-25, el=22, zoom=1.1)

# --- alzatina: mensola vista da sotto
stage("alz_mensola_sotto.png", alz, lambda p: (0, 0, 0) if not p["name"].startswith("Montante") else (0, 0, -60),
      labels=[("Listello mensola", "bottom", "Listello 30×40 unico da 2000:\nunisce le tre tavole", "L", 760),
              ("Mensola – tavola 2", "bottom", "Giunti in asse ai montanti 2 e 3", "R", 250),
              ("Montante mensola 2", "bottom", "Montanti", "R", 820)],
      az=-30, el=-25, zoom=1.0)
print("ok")
