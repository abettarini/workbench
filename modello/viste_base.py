"""Viste d'insieme del solo tavolo base (base_vista_sx/dx.png)."""
import json
from tavolo_kvh import solid
from piastre import render
parts = [p for p in json.load(open("parts_kvh.json"))["parts"] if p["module"] == "base"]
P = [(p["name"], solid(p), p["color"]) for p in parts]
render(P, "base_vista_sx.png", [], az=-35, el=22, zoom=1.15)
render(P, "base_vista_dx.png", [], az=35, el=22, zoom=1.15)
print("ok")
