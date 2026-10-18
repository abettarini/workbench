"""Esporta un file STEP per modulo (base, cassettiera, alzatina) dal modello completo."""
import json
import cadquery as cq
from tavolo_kvh import solid
parts = json.load(open("parts_kvh.json"))["parts"]
for mod, fname in (("base", "tavolo_base.step"), ("cassettiera", "cassettiera.step"), ("alzatina", "alzatina.step")):
    a = cq.Assembly(name=mod)
    for i, p in enumerate([p for p in parts if p["module"] == mod]):
        a.add(solid(p), name=f"{i:03d}_{p['name']}".replace(" ", "_").replace(".", "").replace("–", "-"), color=cq.Color(p["color"]))
    a.export(fname); print(fname)
