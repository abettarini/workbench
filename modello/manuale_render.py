"""Viste 3D delle fasi di montaggio (KVH) per il manuale."""
import json
from tavolo_kvh import solid
from piastre import render

d = json.load(open("parts_kvh.json"))
ALL = d["parts"]
parts = [p for p in ALL if p.get("module", "base") == "base"]

def code(n):
    import re
    m = re.match(r"Gamba (\d) (ant|post)", n)
    if m: return f"G{m.group(1)}{'A' if m.group(2)=='ant' else 'P'}"
    m = re.match(r"Trav\. (sup|inf)\. lat\. (\d)", n)
    if m: return f"L{m.group(2)}{'s' if m.group(1)=='sup' else 'i'}"
    m = re.match(r"Trav\. (sup|inf)\. (post|ant)\. (\w+)", n)
    if m: return f"{'P' if m.group(2)=='post' else 'A'}{m.group(3)[0].upper()}{'s' if m.group(1)=='sup' else 'i'}"
    m = re.match(r"Montante mensola (\d)", n)
    if m: return f"M{m.group(1)}"
    return n

def stage(fname, inc, off=lambda p: (0, 0, 0), labels=(), az=-35, el=24, zoom=1.0, size=(1500, 1000), ghost=None):
    P = []
    for p in parts:
        if inc(p):
            dx, dy, dz = off(p)
            col = p["color"]
            if ghost and ghost(p): col = "#e9e4dc"
            P.append((p["name"], solid(p).translate((dx, dy, dz)), col))
    L = []
    for item in labels:
        name, where, txt, side, ty = item
        p = next(q for q in parts if q["name"] == name)
        x0, y0, z0, x1, y1, z1 = p["box"]; dx, dy, dz = off(p)
        pt = {"c": ((x0+x1)/2, (y0+y1)/2, (z0+z1)/2), "top": ((x0+x1)/2, (y0+y1)/2, z1),
              "front": ((x0+x1)/2, y0, (z0+z1)/2)}[where]
        L.append(((pt[0]+dx, pt[1]+dy, pt[2]+dz), txt, side, ty))
    render(P, fname, L, az=az, el=el, size=size, zoom=zoom)

is_leg = lambda p: p["name"].startswith("Gamba")
is_lat = lambda p: ". lat." in p["name"]
is_long = lambda p: p["name"].startswith("Trav.") and not is_lat(p)
frame = lambda p: is_leg(p) or p["role"] in ("trav-lat", "trav-long")

if __name__ == "__main__":
    # 1. telai laterali: telaio 1 esploso, altri montati e distanziati
    def off1(p):
        import re
        i = int(re.search(r"(\d)", p["name"]).group(1)) - 1
        base = (i * 260, 0, 0)
        if i == 0:
            if "ant" in p["name"]: return (base[0], -260, 0)
            if "post" in p["name"]: return (base[0], 260, 0)
        return base
    stage("man_f4_telai.png", lambda p: is_leg(p) or is_lat(p), off1, labels=[
        ("Gamba 1 ant", "front", "G1A – gamba anteriore", "L", 640),
        ("Trav. sup. lat. 1", "top", "L1s – traversa laterale superiore", "L", 300),
        ("Trav. inf. lat. 1", "c", "L1i – traversa laterale inferiore", "L", 820),
        ("Gamba 1 post", "top", "G1P – gamba posteriore", "L", 180),
        ("Gamba 4 ant", "front", "Telai 2, 3 e 4 già montati", "R", 700),
    ], az=-40, el=22, zoom=1.15)

    # 2. collegamento telai
    def off2(p):
        return (0, 0, 220) if is_long(p) else (0, 0, 0)
    stage("man_f5_collegamento.png", frame, off2, labels=[
        ("Trav. sup. post. cassetti", "top", "PCs / PCi – posteriori cassetti", "L", 220),
        ("Trav. sup. post. seduta", "top", "PSs / PSi – posteriori seduta", "L", 120),
        ("Trav. sup. post. ricarica", "top", "PRs / PRi – posteriori ricarica", "R", 120),
        ("Trav. sup. ant. ricarica", "top", "ARs / ARi – anteriori ricarica", "R", 300),
        ("Gamba 2 post", "c", "Gambe 2P e 3P: barra passante\nche unisce le due traverse", "L", 700),
    ], az=-30, el=26, zoom=1.1)

    # 3. listelli e ripiani bassi
    shelf = lambda p: p["name"].startswith("Ripiano") or p["group"] == "Listelli reggiripiano"
    def off3(p):
        if p["name"].startswith("Ripiano"): return (0, 0, 260)
        return (0, 0, 0)
    stage("man_f6_ripiani.png", lambda p: frame(p) or shelf(p), off3, labels=[
        ("Ripiano basso cassetti", "top", "Ripiano cassetti – OSB 18", "L", 250),
        ("Ripiano basso post. seduta", "top", "Ripiano posteriore seduta – OSB 18", "L", 140),
        ("Ripiano basso ricarica", "top", "Ripiano ricarica – OSB 18", "R", 250),
        ("Listello reggiripiano – Ripiano basso ricarica dx", "c", "Listelli 30×40 avvitati\nalle traverse inferiori", "R", 700),
    ], az=-30, el=30, zoom=1.1, ghost=frame)

    # 4. piano
    top = lambda p: p["name"] in ("Piano di lavoro", "Rinforzo piano ricarica")
    stage("man_f7_piano.png", lambda p: frame(p) or shelf(p) or top(p),
          lambda p: (0, 0, 300) if top(p) else (0, 0, 0), labels=[
        ("Piano di lavoro", "top", "Piano lamellare 2000×800×40\n(fori passacavi e fori mensola già fatti)", "L", 160),
        ("Rinforzo piano ricarica", "c", "Rinforzo OSB 2×18 (36 mm) incollato\ne avvitato sotto il piano", "R", 380),
    ], az=-30, el=28, zoom=1.1, ghost=lambda p: not top(p))

    # 5. zona ricarica (porzione destra, vista da sotto)
    import copy
    def clip_parts():
        out = []
        for p in parts:
            n = p["name"]
            if n in ("Piano di lavoro",):
                q = copy.deepcopy(p); q["box"][0] = 1360; q["holes"] = [h for h in q["holes"] if h[1] > 1360]; out.append(q)
            elif n in ("Rinforzo piano ricarica", "Contropiastra acciaio", "Base attacco piastre", "Trav. sup. ant. ricarica",
                       "Trav. sup. post. ricarica", "Trav. sup. lat. 3", "Trav. sup. lat. 4"):
                out.append(p)
            elif n in ("Gamba 3 ant", "Gamba 4 ant", "Gamba 3 post", "Gamba 4 post"):
                q = copy.deepcopy(p); q["box"][2] = 450; out.append(q)
        return out
    def off5(p):
        n = p["name"]
        if n == "Base attacco piastre": return (0, 0, 140)
        if n == "Contropiastra acciaio": return (0, 0, -140)
        return (0, 0, 0)
    _saved = parts[:]
    parts[:] = clip_parts()
    stage("man_f8_ricarica.png", lambda p: True, off5, labels=[
        ("Contropiastra acciaio", "c", "Contropiastra 220×220×6: 2 viti posteriori M10×110", "L", 860),
        ("Rinforzo piano ricarica", "c", "Rinforzo OSB 36 mm incollato + 12 viti 5×60", "L", 640),
        ("Trav. sup. ant. ricarica", "c", "ARs: le 2 viti anteriori M10×200\nla attraversano, dado sotto", "R", 820),
        ("Base attacco piastre", "c", "Base 180×180×12 (sopra il piano)", "R", 300),
    ], az=-35, el=-28, zoom=1.0)
    parts[:] = _saved

    # 6. vista finale del tavolo base
    stage("man_f9_base.png", lambda p: True, labels=[
        ("Ripiano basso cassetti", "front", "Campata cassetti: ripiano pronto\nper la cassettiera (modulo 2)", "L", 700),
        ("Gamba 2 post", "top", "Gambe posteriori: predisposte\nper l'alzatina (modulo 3)", "L", 250),
        ("Base attacco piastre", "top", "Zona ricarica", "R", 300),
    ], az=-28, el=22, zoom=1.1)
    print("ok")
