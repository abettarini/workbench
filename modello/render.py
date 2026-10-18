"""Render offscreen (VTK) del modello: python render.py"""
import sys, json
import vtk
import cadquery as cq
MODE = sys.argv[1] if len(sys.argv) > 1 else ""
LAM = MODE == "lam"
if MODE == "kvh":
    from tavolo_kvh import solid
    data = json.load(open("parts_kvh.json")); PFX = "kvh_"
elif LAM:
    from tavolo_lam import solid
    data = json.load(open("parts_lam.json")); PFX = "lam_"
else:
    from tavolo import solid
    data = json.load(open("parts.json")); PFX = ""

def hex2rgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))

def actor_for(p):
    s = solid(p).val()
    verts, tris = s.tessellate(0.5, 0.3)
    pts = vtk.vtkPoints()
    for v in verts: pts.InsertNextPoint(v.x, v.y, v.z)
    cells = vtk.vtkCellArray()
    for t in tris:
        c = vtk.vtkTriangle()
        for k in range(3): c.GetPointIds().SetId(k, t[k])
        cells.InsertNextCell(c)
    pd = vtk.vtkPolyData(); pd.SetPoints(pts); pd.SetPolys(cells)
    m = vtk.vtkPolyDataMapper(); m.SetInputData(pd)
    a = vtk.vtkActor(); a.SetMapper(m)
    a.GetProperty().SetColor(*hex2rgb(p["color"]))
    a.GetProperty().SetAmbient(0.35); a.GetProperty().SetDiffuse(0.7)
    # spigoli
    fe = vtk.vtkFeatureEdges(); fe.SetInputData(pd); fe.BoundaryEdgesOn(); fe.FeatureEdgesOn()
    fe.SetFeatureAngle(30); fe.ManifoldEdgesOff(); fe.NonManifoldEdgesOff()
    em = vtk.vtkPolyDataMapper(); em.SetInputConnection(fe.GetOutputPort()); em.ScalarVisibilityOff()
    ea = vtk.vtkActor(); ea.SetMapper(em); ea.GetProperty().SetColor(0.25, 0.2, 0.15)
    ea.GetProperty().SetLineWidth(1.2)
    return a, ea

def render(fname, az, el, hide=(), w=1600, h=1100):
    ren = vtk.vtkRenderer(); ren.SetBackground(1, 1, 1)
    for p in data["parts"]:
        if any(k in p["name"] for k in hide): continue
        for a in actor_for(p): ren.AddActor(a)
    win = vtk.vtkRenderWindow(); win.SetOffScreenRendering(1); win.SetSize(w, h); win.AddRenderer(ren)
    cam = ren.GetActiveCamera()
    cam.SetFocalPoint(1000, 400, 500); cam.SetPosition(1000, -3000, 500); cam.SetViewUp(0, 0, 1)
    cam.Azimuth(az); cam.Elevation(el); cam.OrthogonalizeViewUp()
    ren.ResetCamera(); cam.Zoom(1.25)
    win.Render()
    f = vtk.vtkWindowToImageFilter(); f.SetInput(win); f.Update()
    wr = vtk.vtkPNGWriter(); wr.SetFileName(fname); wr.SetInputConnection(f.GetOutputPort()); wr.Write()

if __name__ == "__main__":
    render(PFX + "vista_frontale_sx.png", -35, 22)
    render(PFX + "vista_frontale_dx.png", 35, 22)
    render(PFX + "vista_struttura.png", -35, 22,
           hide=("Piano di lavoro", "Mensola rialzata", "Base attacco", "Pannello fianco sx"))
    if LAM:
        render(PFX + "vista_retro.png", 180 + 35, 20)
    print("ok")
