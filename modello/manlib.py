"""Funzioni comuni per i manuali (impaginazione, disegni, tabelle)."""
import json, re, textwrap
from collections import Counter, OrderedDict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle, Circle, Polygon, FancyBboxPatch

def code(n):
    m = re.match(r"Gamba (\d) (ant|post)", n)
    if m: return f"G{m.group(1)}{'A' if m.group(2)=='ant' else 'P'}"
    m = re.match(r"Trav\. (sup|inf)\. lat\. (\d)", n)
    if m: return f"L{m.group(2)}{'s' if m.group(1)=='sup' else 'i'}"
    m = re.match(r"Trav\. (sup|inf)\. (post|ant)\. (\w+)", n)
    if m: return f"{'P' if m.group(2)=='post' else 'A'}{m.group(3)[0].upper()}{'s' if m.group(1)=='sup' else 'i'}"
    m = re.match(r"Fascia (post|ant)\. (alta|bassa)", n)
    if m: return "FA" if m.group(1) == "ant" else ("FPa" if m.group(2) == "alta" else "FPb")
    m = re.match(r"Montante mensola (\d)", n)
    if m: return f"M{m.group(1)}"
    return n

d = json.load(open("parts_kvh.json")); holes = json.load(open("fori.json")); cf = json.load(open("confronto.json"))
P = d["params"]; parts = {p["name"]: p for p in d["parts"]}
W, D, H, Lx, Ly, Rt, Rh = P["W"], P["D"], P["H"], P["Lx"], P["Ly"], P["Rt"], P["Rh"]
LEG_H = H - P["T_top"]
A4 = (11.69, 8.27)
INK, RED, MUTE = "#222222", "#c0392b", "#666666"
WOOD, WOOD2, STEEL, PLY = "#e3c79c", "#cfa874", "#9aa3ab", "#efdcb8"
HCOL = {"B1": "#c0392b", "B2": "#e67e22", "R": "#8e44ad", "S": "#d4a017", "I": "#7f8c8d", "M": "#2c6fbb",
        "T": "#16a085", "A": "#c0392b", "C": "#555555", "P": "#34495e", "V": "#7d3c98"}
FACE_NAME = {"A": "anteriore", "D": "destra", "P": "posteriore", "S": "sinistra", "T": "testa", "F": "piede"}
plt.rcParams["font.family"] = "DejaVu Sans"
PAGE = [0]
FOOTER = ["Tavolo da lavoro KVH 80×120 – manuale di lavorazione e montaggio"]
TOC = []

# ------------------------------------------------------------------ utilità pagina
def page(title, phase=None):
    PAGE[0] += 1
    fig = plt.figure(figsize=A4)
    fig.patches.append(Rectangle((0, 0.93), 1, 0.07, transform=fig.transFigure, fc="#2f3b45", ec="none"))
    fig.text(0.035, 0.955, title, fontsize=15, weight="bold", color="white", va="center")
    if phase: fig.text(0.965, 0.955, phase, fontsize=10, color="#d9e1e7", va="center", ha="right")
    fig.text(0.035, 0.02, FOOTER[0], fontsize=7.5, color=MUTE)
    fig.text(0.965, 0.02, f"pag. {PAGE[0]}", fontsize=7.5, color=MUTE, ha="right")
    TOC.append((PAGE[0], title))
    return fig

def para(fig, x, y, text, width=60, fs=9, lh=1.45, color=INK, weight="normal"):
    """testo con a capo automatico; ritorna la y finale"""
    lines = []
    for block in text.split("\n"):
        if not block.strip(): lines.append(""); continue
        ind = len(block) - len(block.lstrip())
        sub = textwrap.wrap(block.strip(), width=width - ind) or [""]
        bullet = block.strip()[:2] in ("• ", "– ") or re.match(r"^\d+\.", block.strip())
        lines.append(" " * ind + sub[0])
        for s in sub[1:]: lines.append(" " * (ind + (3 if bullet else 0)) + s)
    fig.text(x, y, "\n".join(lines), fontsize=fs, va="top", color=color, linespacing=lh, weight=weight)
    return y - len(lines) * fs * lh / 72 / A4[1]

def box_note(fig, x, y, w, h, title, text, fs=8.3, color="#fff6e0", edge="#e0b25c", width=None):
    fig.patches.append(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.006", transform=fig.transFigure,
                                      fc=color, ec=edge, lw=0.8))
    fig.text(x + 0.01, y + h - 0.012, title, fontsize=fs + 0.5, weight="bold", va="top")
    para(fig, x + 0.01, y + h - 0.04, text, width=width or int(w * 150), fs=fs)

def dim(ax, x0, y0, x1, y1, off, text=None, vertical=False, fs=7.5):
    kw = dict(arrowprops=dict(arrowstyle="<->", lw=0.6, color=RED, shrinkA=0, shrinkB=0))
    if vertical:
        xo = x0 + off
        ax.annotate("", (xo, y0), (xo, y1), **kw)
        ax.plot([x0, xo], [y0, y0], lw=0.35, color=RED); ax.plot([x1, xo], [y1, y1], lw=0.35, color=RED)
        ax.text(xo + (4 if off > 0 else -4), (y0 + y1) / 2, text or f"{abs(y1 - y0):.0f}", rotation=90,
                ha="left" if off > 0 else "right", va="center", fontsize=fs, color=RED)
    else:
        yo = y0 + off
        ax.annotate("", (x0, yo), (x1, yo), **kw)
        ax.plot([x0, x0], [y0, yo], lw=0.35, color=RED); ax.plot([x1, x1], [y1, yo], lw=0.35, color=RED)
        ax.text((x0 + x1) / 2, yo + (3 if off > 0 else -3), text or f"{abs(x1 - x0):.0f}",
                ha="center", va="bottom" if off > 0 else "top", fontsize=fs, color=RED)

def R(ax, x, y, w, h, fc=WOOD, ec=INK, lw=0.8, hatch=None, ls="-", z=1, alpha=1):
    ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, hatch=hatch, ls=ls, zorder=z, alpha=alpha))

def label(ax, xy, xytext, text, fs=7.5, ha="left"):
    ax.annotate(text, xy, xytext, fontsize=fs, ha=ha, va="center",
                arrowprops=dict(arrowstyle="-", lw=0.6, color=INK, shrinkB=0),
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#aaa", lw=0.5))

def img(fig, path, rect, crop=None):
    a = fig.add_axes(rect); im = plt.imread(path)
    if crop: im = im[crop[0]:crop[1], crop[2]:crop[3]]
    a.imshow(im); a.axis("off"); return a

def table(ax, cells, cols, widths, fs=7.5, sc=1.25, colors=None):
    tb = ax.table(cellText=cells, colLabels=cols, loc="upper left", cellLoc="left", colWidths=widths)
    tb.auto_set_font_size(False); tb.set_fontsize(fs); tb.scale(1, sc)
    for (r, c), cell in tb.get_celld().items():
        cell.set_edgecolor("#bbb"); cell.set_linewidth(0.5)
        if r == 0: cell.set_facecolor("#e8edf1"); cell.set_text_props(weight="bold")
        elif colors and colors[r - 1]: cell.set_facecolor(colors[r - 1])
    ax.axis("off"); return tb

