"""Dettaglio attacco a piastre intercambiabili: vista esplosa 3D + sezione quotata.
Origine: superficie del piano, centro della base; Y verso il retro (fronte a Y = -90)."""
import cadquery as cq
import vtk
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon

B = 180          # lato base e piastre
TB = 12          # spessore base acciaio
TP = 10          # spessore piastra attrezzo
TOP, DBL, CP = 40, 40, 6   # piano, rinforzo, contropiastra
BOLT = [(-65, -65), (65, -65), (-65, 65), (65, 65)]   # M10 svasati, base -> contropiastra
PINS = [(0, -60), (0, 60)]                            # spine Ø10 h8 sporgenti
KNOBS = [(-55, 0), (55, 0)]                           # filetti M12 nella base

def plate(t, z0, holes):
    w = cq.Workplane("XY").box(B, B, t, centered=(True, True, False)).translate((0, 0, z0))
    for (x, y), d in holes:
        w = w.cut(cq.Workplane("XY").circle(d / 2).extrude(t + 2).translate((x, y, z0 - 1)))
    return w

def cyl(d, h, x, y, z0):
    return cq.Workplane("XY").circle(d / 2).extrude(h).translate((x, y, z0))

def build(ex=0.0):
    """ex = fattore esploso (0 = montato)"""
    P = []
    zb = 0 + ex * 60       # base
    zt = TB + ex * 150     # piastra attrezzo
    zk = TB + TP + ex * 230
    zn = -(TOP + DBL + CP) - ex * 70
    # piano + rinforzo + contropiastra (porzione)
    P.append(("piano", cq.Workplane("XY").box(320, 260, TOP, centered=(True, False, False))
              .translate((0, -90, -TOP)), "#ecd3a8"))
    P.append(("rinforzo", cq.Workplane("XY").box(320, 230, DBL, centered=(True, False, False))
              .translate((0, -90 + 80, -TOP - DBL)), "#e0c08f"))
    P.append(("contropiastra", plate(CP, -TOP - DBL - CP - ex * 35, [(p, 11) for p in BOLT])
              .translate((0, 20, 0)), "#8d949c"))
    P.append(("base", plate(TB, zb, [(p, 11) for p in BOLT] + [(p, 10) for p in PINS] +
                            [(p, 10.2) for p in KNOBS]), "#3a3f45"))
    for x, y in BOLT:   # viti svasate M10 (testa a filo base) + dadi sotto
        P.append(("vite", cyl(10, TB + TOP + DBL + CP + 15, x, y, zb - TOP - DBL - CP - 15)
                  .union(cq.Workplane("XY").circle(10).workplane(offset=6).circle(5).loft()
                         .rotate((0, 0, 0), (1, 0, 0), 180).translate((x, y, zb + TB))), "#b8bcc2"))
        P.append(("dado", cq.Workplane("XY").polygon(6, 19).extrude(9)
                  .faces(">Z").workplane().hole(10).translate((x, y + 20 * 0, zn - 9)), "#b8bcc2"))
    for x, y in PINS:
        P.append(("spina", cyl(10, TB + 8, x, y, zb), "#d4a017"))
    P.append(("piastra", plate(TP, zt, [(p, 10.4) for p in PINS] + [(p, 13) for p in KNOBS] +
                               [((-40, 30), 13), ((40, 30), 13), ((0, -45), 13)]), "#9aa7b4"))
    for x, y in KNOBS:   # manopola a stella M12
        knob = cq.Workplane("XY").polygon(5, 50).extrude(18).edges("|Z").fillet(6).translate((x, y, zk))
        stud = cyl(12, TP + TB, x, y, zk - TP - TB)
        P.append(("manopola", knob.union(stud), "#c0392b"))
    return P

def render(P, fname, labels, az=-35, el=28, size=(1500, 1100), zoom=1.5):
    ren = vtk.vtkRenderer(); ren.SetBackground(1, 1, 1)
    for name, w, col in P:
        verts, tris = w.val().tessellate(0.2, 0.2)
        pts = vtk.vtkPoints(); [pts.InsertNextPoint(v.x, v.y, v.z) for v in verts]
        cells = vtk.vtkCellArray()
        for t in tris:
            c = vtk.vtkTriangle(); [c.GetPointIds().SetId(k, t[k]) for k in range(3)]; cells.InsertNextCell(c)
        pd = vtk.vtkPolyData(); pd.SetPoints(pts); pd.SetPolys(cells)
        nm = vtk.vtkPolyDataNormals(); nm.SetInputData(pd); nm.SetFeatureAngle(35)
        m = vtk.vtkPolyDataMapper(); m.SetInputConnection(nm.GetOutputPort())
        a = vtk.vtkActor(); a.SetMapper(m)
        h = col.lstrip("#"); a.GetProperty().SetColor(*[int(h[i:i+2], 16) / 255 for i in (0, 2, 4)])
        a.GetProperty().SetAmbient(0.3); a.GetProperty().SetDiffuse(0.75)
        a.GetProperty().SetSpecular(0.2 if col != "#ecd3a8" else 0)
        ren.AddActor(a)
        fe = vtk.vtkFeatureEdges(); fe.SetInputData(pd); fe.BoundaryEdgesOn(); fe.FeatureEdgesOn()
        fe.SetFeatureAngle(40); fe.ManifoldEdgesOff(); fe.NonManifoldEdgesOff()
        em = vtk.vtkPolyDataMapper(); em.SetInputConnection(fe.GetOutputPort()); em.ScalarVisibilityOff()
        ea = vtk.vtkActor(); ea.SetMapper(em); ea.GetProperty().SetColor(0.2, 0.2, 0.2); ren.AddActor(ea)
    win = vtk.vtkRenderWindow(); win.SetOffScreenRendering(1); win.SetSize(*size); win.AddRenderer(ren)
    cam = ren.GetActiveCamera()
    cam.SetFocalPoint(0, 30, 0); cam.SetPosition(0, -1500, 0); cam.SetViewUp(0, 0, 1)
    cam.Azimuth(az); cam.Elevation(el); cam.OrthogonalizeViewUp(); ren.ResetCamera(); cam.Zoom(zoom)
    win.Render()
    f = vtk.vtkWindowToImageFilter(); f.SetInput(win); f.Update()
    wr = vtk.vtkPNGWriter(); wr.SetFileName(fname + ".raw.png"); wr.SetInputConnection(f.GetOutputPort()); wr.Write()
    # proiezione etichette
    co = vtk.vtkCoordinate(); co.SetCoordinateSystemToWorld()
    pts2 = []
    for item in labels:
        (x, y, z), txt, side = item[:3]
        co.SetValue(x, y, z); u, v = co.GetComputedDoubleDisplayValue(ren)
        pts2.append((u, size[1] - v, txt, side, item[3] if len(item) > 3 else None))
    img = plt.imread(fname + ".raw.png")
    fig = plt.figure(figsize=(size[0] / 100, size[1] / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1]); ax.imshow(img); ax.axis("off")
    for u, v, txt, side, ty in pts2:
        tx = 60 if side == "L" else size[0] - 60
        ax.annotate(txt, (u, v), (tx, v if ty is None else ty), fontsize=13, ha="left" if side == "L" else "right", va="center",
                    arrowprops=dict(arrowstyle="-", lw=0.9, color="#333", shrinkB=0),
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#999", lw=0.6))
    fig.savefig(fname); plt.close(fig)

if __name__ == "__main__":
    E = build(1.0)
    render(E, "piastre_esploso.png", [
        ((55, 0, TB + TP + 230 + 18), "① Manopole a stella M12 (2)", "R"),
        ((90, 60, TB + 150 + TP), "② Piastra attrezzo 180×180×10 –\n    una per Rock Chucker, Dillon 550, morsa", "R"),
        ((0, 60, 60 + TB + 8), "③ Spine di centraggio Ø10 (2)", "L"),
        ((-90, -30, 60 + TB / 2), "④ Base fissa acciaio 180×180×12\n    fori M12 filettati + viti svasate M10", "L"),
        ((-160, 50, -TOP / 2), "⑤ Piano 40 mm", "L"),
        ((-160, 60, -TOP - DBL / 2), "⑥ Rinforzo 40 mm (sotto il piano)", "L"),
        ((40, -90, -TOP - DBL - CP - 36), "⑦ Contropiastra 220×220×6", "R"),
        ((-65, 65, -(TOP + DBL + CP) - 70 - 5), "⑧ Dadi autobloccanti M10 (4)", "L"),
    ], az=-30, el=24, zoom=1.35)
    render(build(0.0), "piastre_montato.png", [], az=-30, el=30, size=(1000, 750), zoom=1.6)

    # ---- sezione quotata (piano YZ attraverso le manopole: taglio a X=55)
    fig, ax = plt.subplots(figsize=(11, 7.5))
    def r(x0, z0, w, h, fc, hatch=None, ec="#222"):
        ax.add_patch(Rectangle((x0, z0), w, h, fc=fc, ec=ec, lw=0.9, hatch=hatch))
    tot = TOP + DBL + CP
    r(-160, -TOP, 320, TOP, "#ecd3a8", "//"); r(-160, -TOP - DBL, 320, DBL, "#e0c08f", "\\\\")
    r(-110, -tot, 220, CP, "#8d949c")
    r(-90, 0, B, TB, "#3a3f45"); r(-90, TB, B, TP, "#9aa7b4")
    # foro bullone M10 svasato a x=-65 e manopola a x=+55 (sezione rappresentativa)
    for x in (-65,):
        r(x - 5, -tot - 15, 10, tot + TB + 15, "#b8bcc2")
        ax.add_patch(Polygon([(x - 10, TB), (x + 10, TB), (x + 5, TB - 6), (x - 5, TB - 6)], fc="#b8bcc2", ec="#222"))
        r(x - 9.5, -tot - 9, 19, 9, "#b8bcc2")
    x = 55
    r(x - 6, 0, 12, TB + TP, "#c0392b"); r(x - 25, TB + TP, 50, 18, "#c0392b")
    r(0 - 5, 0, 10, TB + 8, "#d4a017")  # spina (proiettata)
    def q(z0, z1, txt, xx=175):
        ax.annotate("", (xx, z0), (xx, z1), arrowprops=dict(arrowstyle="<->", color="#c0392b", lw=0.8))
        ax.text(xx + 6, (z0 + z1) / 2, txt, va="center", fontsize=9, color="#c0392b")
    q(TB, TB + TP, "piastra attrezzo 10"); q(0, TB, "base 12"); q(-TOP, 0, "piano 40")
    q(-TOP - DBL, -TOP, "rinforzo 40"); q(-tot, -TOP - DBL, "contropiastra 6")
    ax.annotate("", (-90, 50), (90, 50), arrowprops=dict(arrowstyle="<->", color="#c0392b", lw=0.8))
    ax.text(0, 54, "180", ha="center", fontsize=9, color="#c0392b")
    notes = [(-65, -tot - 30, "vite TSPEI M10×110\n+ dado autobloccante"),
             (130, TB + TP + 9, "manopola M12\n(stringe piastra su base)"),
             (0, TB + 18, "spina Ø10")]
    for xx, zz, t in notes:
        ax.text(xx, zz, t, ha="center", va="center", fontsize=8.5)
    ax.text(-160, 70, "SEZIONE DEL PACCHETTO (scala indicativa, quote in mm)", fontsize=11, weight="bold")
    ax.text(-160, -150,
            "Come funziona\n"
            "• La base ④ resta sempre sul tavolo: 4 viti svasate M10 la serrano, attraverso piano e rinforzo, "
            "sulla contropiastra ⑦.\n"
            "• Ogni attrezzo è avvitato in modo permanente sulla propria piastra ②, forata con il suo schema.\n"
            "• Cambio attrezzo: sviti le 2 manopole ①, sollevi la piastra, infili la nuova sulle spine ③ "
            "(centraggio e taglio), riavviti.\n"
            "• Le spine assorbono le forze orizzontali, le manopole lo strappo verso l'alto della leva; "
            "la contropiastra distribuisce il carico sul legno.",
            fontsize=9.5, va="top", linespacing=1.6)
    ax.set_xlim(-170, 340); ax.set_ylim(-240, 85); ax.set_aspect("equal"); ax.axis("off")
    fig.savefig("piastre_sezione.png", dpi=130, bbox_inches="tight"); plt.close(fig)
    print("ok")
