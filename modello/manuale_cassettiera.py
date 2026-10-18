"""Manuale modulo 2 – Cassettiera -> cassettiera_manuale.pdf"""
import json
from collections import Counter
from manlib import *
from manlib import PAGE, FOOTER

d = json.load(open("parts_kvh.json")); P = d["params"]
parts = {p["name"]: p for p in d["parts"]}
pieces = json.load(open("cassettiera_pezzi.json"))
FOOTER[0] = "Modulo 2 – Cassettiera per il tavolo da lavoro – manuale"
B = lambda n: parts[n]["box"]

# ---------------------------------------------------------------- impaginazione tagli (a ripiani)
def pack(items, W=1250, H=1250, k=4):
    items = sorted(items, key=lambda it: (-max(it[1], it[2]), -min(it[1], it[2])))
    rows, placed = [], []
    for name, a, b in items:
        L, w = max(a, b), min(a, b)
        ok = False
        for r in rows:
            if r["x"] + L <= W and w <= r["h"]:
                placed.append((name, r["x"], r["y"], L, w)); r["x"] += L + k; ok = True; break
        if not ok:
            y = (rows[-1]["y"] + rows[-1]["h"] + k) if rows else 0
            if y + w > H: raise ValueError(f"non entra: {name}")
            rows.append({"y": y, "h": w, "x": L + k}); placed.append((name, 0, y, L, w))
    return placed, (rows[-1]["y"] + rows[-1]["h"]) if rows else 0

def pack_multi(items, W, H, k=4):
    """riempie più pannelli W×H: ritorna lista di (placed, altezza usata)"""
    rest = sorted(items, key=lambda it: (-max(it[1], it[2]), -min(it[1], it[2])))
    sheets = []
    while rest:
        rows, placed, left = [], [], []
        for name, a, b in rest:
            L, w = max(a, b), min(a, b)
            ok = False
            for r in rows:
                if r["x"] + L <= W and w <= r["h"]:
                    placed.append((name, r["x"], r["y"], L, w)); r["x"] += L + k; ok = True; break
            if not ok:
                y = (rows[-1]["y"] + rows[-1]["h"] + k) if rows else 0
                if y + w <= H and L <= W:
                    rows.append({"y": y, "h": w, "x": L + k}); placed.append((name, 0, y, L, w))
                else:
                    left.append((name, a, b))
        if not placed: raise ValueError("pezzo più grande del pannello")
        sheets.append(placed); rest = left
    return sheets

def draw_sheet(ax, title, placed, W=1250, H=1250, col="#efdcb8"):
    ax.set_aspect("equal"); ax.axis("off")
    R(ax, 0, 0, W, H, "#f6f1e7")
    for name, x, y, L, w in placed:
        R(ax, x, y, L, w, col, lw=0.6)
        ax.text(x + L / 2, y + w / 2, f"{name}\n{L:.0f}×{w:.0f}", ha="center", va="center", fontsize=5.6)
    ax.set_xlim(-20, W + 20); ax.set_ylim(-20, H + 20)
    ax.set_title(title, fontsize=8, loc="left")

with PdfPages("cassettiera_manuale.pdf") as pdf:
    # ---------- copertina
    fig = plt.figure(figsize=A4); PAGE[0] += 1
    fig.text(0.05, 0.9, "Cassettiera", fontsize=30, weight="bold")
    fig.text(0.05, 0.85, "Modulo 2 del tavolo da lavoro – manuale di costruzione e montaggio", fontsize=14, color=MUTE)
    img(fig, "cas_installazione.png", [0.36, 0.08, 0.62, 0.74], crop=(60, 900, 0, 1500))
    fig.text(0.05, 0.76, "Contenuto", fontsize=11, weight="bold")
    fig.text(0.05, 0.735, "\n".join(["Cosa serve", "Fase 1 · Taglio dei pannelli", "Fase 2 · Scatola della cassettiera",
                                     "Fase 3 · Guide e cassetti", "Fase 4 · Installazione nel tavolo",
                                     "Controlli finali"]), fontsize=9, va="top", linespacing=1.9)
    box_note(fig, 0.05, 0.12, 0.28, 0.32, "In breve",
             "Cassettiera fissa con 3 cassetti per la campata sinistra del tavolo (luce 500 mm), sotto la fascia "
             "anteriore del piano.\n\nSi monta quando vuoi, anche dopo il tavolo: non servono fori o modifiche "
             "al telaio.\n\nCosti nel file cassettiera_costi.xlsx.", fs=8.3, width=44)
    pdf.savefig(fig); plt.close(fig)

    # ---------- cosa serve
    fig = page("Cosa serve")
    para(fig, 0.04, 0.89, "Materiali", fs=11, weight="bold")
    para(fig, 0.04, 0.86, (
        "• Multistrato pioppo 18 mm: 2 pannelli 1200×600 (scatola e frontali)\n"
        "• Multistrato pioppo 15 mm: 1 pannello 1200×600 (scatole dei cassetti)\n"
        "• Fibra grezza 3 mm: pannello 2500×1250 (fondi e schienale)\n"
        "• 3 coppie di guide a sfera a estrazione totale, lunghezza 500 mm, spessore 12,7 mm\n"
        "• 3 maniglie\n"
        "• Viti: 4×45 (scatola), 3,5×30 (cassetti), 3×16 (fondi e schienale), 3,5×25 (frontali), "
        "4×16 (guide), 4×30 e 4×50 (fissaggio al tavolo)\n"
        "• Colla vinilica D3, nastro biadesivo, 4 spessori da 2 mm"), width=62, fs=8.6)
    para(fig, 0.04, 0.55, "Attrezzi", fs=11, weight="bold")
    para(fig, 0.04, 0.52, (
        "• Sega circolare con guida (o taglio a misura in negozio)\n• Avvitatore, punte Ø2,5, Ø3, svasatore\n"
        "• Morsetti, squadra, metro\n• Levigatrice, carta 120–180"), width=62, fs=8.6)
    para(fig, 0.04, 0.38, "Prerequisiti dal tavolo base", fs=11, weight="bold")
    para(fig, 0.04, 0.35, (
        "• Ripiano OSB della campata cassetti montato e avvitato ai listelli.\n"
        "• Nessuna lavorazione sul telaio: la cassettiera si avvita al ripiano e alle gambe anteriori G1A e G2A."),
        width=62, fs=8.6)
    rows = []
    for mat, lst in pieces.items():
        for (n, a, b), q in Counter(map(tuple, lst)).items():
            rows.append([mat, n.replace("Cassettiera ", "").replace("cassetto", "cass."), f"{a:.0f}×{b:.0f}", str(q)])
    at = fig.add_axes([0.53, 0.20, 0.44, 0.68])
    table(at, rows, ["materiale", "pezzo", "misure", "n°"], [0.25, 0.45, 0.2, 0.08], fs=7, sc=1.35)
    fig.text(0.53, 0.89, "Elenco dei pezzi", fontsize=11, weight="bold")
    pdf.savefig(fig); plt.close(fig)

    # ---------- taglio
    fig = page("Taglio dei pannelli", "Fase 1")
    s18 = pack_multi([(n.replace("Cassettiera ", "").replace("Frontale cassetto", "Frontale"), a, b) for n, a, b in pieces["multistrato 18"]], 1200, 600)
    s15 = pack_multi([(n.replace("cassetto ", "c."), a, b) for n, a, b in pieces["multistrato 15"]], 1200, 600)
    s4 = pack_multi([(n, a, b) for n, a, b in pieces["pannello di fibra 3"]], 2500, 1250)
    for k, pl in enumerate(s18):
        draw_sheet(fig.add_axes([0.03 + k * 0.32, 0.66, 0.30, 0.23]), f"Multistrato 18 – 1200×600 (n. {k+1})", pl, W=1200, H=600)
    for k, pl in enumerate(s15):
        draw_sheet(fig.add_axes([0.03 + k * 0.32, 0.40, 0.30, 0.23]), f"Multistrato 15 – 1200×600 (n. {k+1})", pl, W=1200, H=600, col="#e8d3a6")
    draw_sheet(fig.add_axes([0.67, 0.42, 0.31, 0.40]), "Fibra grezza 3 – 2500×1250", s4[0], W=2500, H=1250, col="#d8cbb5")
    h18 = h15 = 0
    para(fig, 0.04, 0.36, (
        "• Le venature esterne del multistrato vanno in verticale su fianchi e frontali: tieni conto del verso quando tagli.\n"
        "• I frontali dei cassetti sono affiancati sullo stesso pannello: le venature restano continue.\n"
        "• Tolleranza ±0,5 mm. Se il negozio taglia a misura, porta questa pagina.\n"
        f"• Pannelli pretagliati Tecnomat 1200×600: servono {len(s18)} da 18 mm e {len(s15)} da 15 mm. Tecnomat taglia in negozio (1° taglio gratis, poi 1 €).\n"
        "• Fondi in fibra da 3 mm: per carichi fino a ~15 kg per cassetto; per carichi maggiori usa MDF/HDF da 4–5 mm."),
        width=150, fs=8.4)
    pdf.savefig(fig); plt.close(fig)

    # ---------- scatola
    fig = page("Scatola della cassettiera", "Fase 2")
    img(fig, "cas_esploso.png", [0.45, 0.30, 0.54, 0.62], crop=(60, 900, 0, 1500))
    fs_ = B("Cassettiera fianco sx"); fd = B("Cassettiera fianco dx"); W_ = fd[3] - fs_[0]; H_ = fs_[5] - fs_[2]; D_ = fs_[4] - fs_[1]
    para(fig, 0.04, 0.89, (
        f"Misure finite: {W_:.0f} (largh.) × {H_:.0f} (alt.) × {D_ + 18:.0f} (prof. con frontali).\n\n"
        "1. Segna su fianchi, cielo e fondo i punti delle viti: a 9 mm dal bordo (metà spessore), ogni 150 mm, "
        "4 viti per giunto.\n"
        "2. Cielo e fondo vanno TRA i due fianchi. Colla sulle testate, accosta, stringi con i morsetti.\n"
        "3. Preforo Ø3 attraverso il fianco e dentro il cielo/fondo per 30 mm, svasa, avvita 4×45.\n"
        "4. Controlla la squadra (diagonali uguali) e appoggia lo schienale in fibra: avvitalo con 3×16 ogni 120 mm. "
        "Lo schienale tiene in squadra la scatola: fissalo prima che la colla tiri.\n"
        "5. Leviga gli spigoli e tratta la scatola (vernice o olio)."), width=62, fs=8.5)
    ax = fig.add_axes([0.04, 0.06, 0.38, 0.40]); ax.set_aspect("equal"); ax.axis("off")
    x0 = fs_[0]
    for n in ("Cassettiera fianco sx", "Cassettiera fianco dx", "Cassettiera cielo", "Cassettiera fondo"):
        b = B(n); R(ax, b[0] - x0, b[2] - fs_[2], b[3] - b[0], b[5] - b[2], "#efdcb8")
    for zz in (9, H_ - 9):
        for xx in (9, W_ - 9):
            ax.plot([xx - 16, xx + 16], [zz, zz], color=STEEL, lw=2.2)
    guide = []
    for k in range(3):
        bb = B(f"Cassetto {k+1} (scatola)"); zc = (bb[2] + bb[5]) / 2 - fs_[2] - 18
        guide.append(zc)
        ax.plot([18, W_ - 18], [zc + 18, zc + 18], ls="--", color=HCOL["M"], lw=0.8)
        ax.text(W_ + 8, zc + 18, f"{zc:.0f}", fontsize=6.5, color=HCOL["M"], va="center")
    dim(ax, 0, 0, W_, 0, -18, f"{W_:.0f}"); dim(ax, 0, 0, 0, H_, -18, f"{H_:.0f}", vertical=True)
    ax.text(W_ + 8, H_ + 10, "asse guide\ndal fondo int.", fontsize=6, color=HCOL["M"])
    ax.set_xlim(-60, W_ + 90); ax.set_ylim(-50, H_ + 40)
    ax.set_title("Vista di fronte (senza frontali): viti 4×45 e asse delle guide", fontsize=8, loc="left")
    pdf.savefig(fig); plt.close(fig)

    # ---------- guide e cassetti
    fig = page("Guide e cassetti", "Fase 3")
    bb = B("Cassetto 1 (scatola)"); bw = bb[3] - bb[0]; bl = bb[4] - bb[1]; bh = bb[5] - bb[2]
    para(fig, 0.04, 0.89, (
        "Guide sui fianchi (prima di inserire la cassettiera nel tavolo)\n"
        f"1. Traccia sui fianchi interni le linee dell'asse delle guide: {guide[0]:.0f}, {guide[1]:.0f} e "
        f"{guide[2]:.0f} mm dal piano del fondo interno.\n"
        "2. Separa le guide (parte fissa e parte mobile). Avvita la parte fissa sul fianco, arretrata di 2 mm dal "
        "bordo anteriore, con viti 4×16 nelle asole: regolerai dopo.\n\n"
        f"Scatole dei cassetti (multistrato 15) – {bw:.0f} × {bl:.0f} × alt. {bh:.0f}\n"
        "3. Le testate vanno TRA i fianchi. Colla + 2 viti 3,5×30 per giunto, preforo Ø2,5, svasatura.\n"
        "4. Controlla la squadra e avvita sotto il fondo in fibra con 3×16 ogni 100 mm: blocca la squadra.\n"
        "5. Avvita la parte mobile delle guide sui fianchi della scatola, a metà altezza, a filo davanti.\n"
        f"6. Larghezza della scatola = luce interna − 2 × 12,7 = {bw:.1f} mm. Se le tue guide hanno uno spessore "
        "diverso, ricalcola prima di tagliare le testate.\n\n"
        "Frontali\n"
        "7. Inserisci i cassetti. Appoggia i frontali con biadesivo: il primo a filo del fondo, fughe di 3 mm tra "
        "un frontale e l'altro (usa 2 monete o spessori).\n"
        "8. Apri il cassetto e fissa ogni frontale dall'interno con 4 viti 3,5×25. Togli il biadesivo se dà fastidio.\n"
        "9. Fora per le maniglie dall'esterno, con un pezzo di scarto dietro per non scheggiare."), width=66, fs=8.4)
    ax = fig.add_axes([0.56, 0.32, 0.40, 0.55]); ax.set_aspect("equal"); ax.axis("off")
    t = 15
    R(ax, 0, 0, t, bl, "#e8d3a6"); R(ax, bw - t, 0, t, bl, "#e8d3a6")
    R(ax, t, 0, bw - 2 * t, t, "#dcc28f"); R(ax, t, bl - t, bw - 2 * t, t, "#dcc28f")
    R(ax, -40, 0, 12.7, bl, STEEL, alpha=0.6); R(ax, bw + 27.3, 0, 12.7, bl, STEEL, alpha=0.6)
    for yy in (7.5, bl - 7.5):
        for xx in (-12, bw + 12): ax.plot([xx - 14 * (1 if xx < 0 else -1), xx + 10 * (1 if xx < 0 else -1)], [yy, yy], color=INK, lw=1.4)
    dim(ax, 0, bl, bw, bl, 18, f"{bw:.1f}"); dim(ax, bw, 0, bw, bl, 60, f"{bl:.0f}", vertical=True)
    ax.text(bw / 2, bl / 2, "fondo in fibra\navvitato sotto", ha="center", va="center", fontsize=7)
    ax.text(-45, -25, "guida 12,7", fontsize=6.5); ax.text(bw / 2, -25, "fronte", ha="center", fontsize=6.5, color=MUTE)
    ax.set_xlim(-70, bw + 110); ax.set_ylim(-45, bl + 50)
    ax.set_title("Scatola del cassetto vista dall'alto", fontsize=8, loc="left")
    pdf.savefig(fig); plt.close(fig)

    # ---------- installazione
    fig = page("Installazione nel tavolo", "Fase 4")
    img(fig, "cas_installazione.png", [0.48, 0.38, 0.51, 0.54], crop=(60, 900, 0, 1500))
    yF0 = P["Ff_d"]; zFA = P["H"] - P["T_top"] - P["Ff_h"]
    cs = B("Cassettiera cielo")
    para(fig, 0.04, 0.89, (
        "1. Togli i cassetti. Infila la scatola nella campata sinistra dal fronte, sotto la fascia anteriore FA, "
        "appoggiata sul ripiano OSB.\n"
        f"2. Frontali a filo della faccia anteriore delle gambe G1A e G2A ({yF0:.0f} mm dietro il bordo del piano): "
        "la fascia FA sporge sopra i cassetti come una visiera.\n"
        "3. Centra la scatola: 2 mm di gioco per lato. Metti gli spessori da 2 mm tra fianco e gamba.\n"
        "4. Fissala: 4 viti 4×30 dall'interno del fondo nel ripiano (preforo Ø3) e 2 viti 4×50 per fianco "
        "dentro le gambe anteriori, a 250 e 500 da terra e 60 mm dalla faccia anteriore della gamba (preforo Ø3).\n"
        "5. Rimetti i cassetti e regola le guide nelle asole finché le fughe sono uniformi; poi aggiungi le viti "
        "nei fori tondi.\n\n"
        f"Spazio libero: tra il cielo della cassettiera (quota {cs[5]:.0f}) e la fascia FA (quota {zFA:.0f}) restano "
        f"{zFA - cs[5]:.0f} mm; i cassetti si aprono senza toccarla."), width=64, fs=8.4)
    ax = fig.add_axes([0.52, 0.05, 0.44, 0.28]); ax.set_aspect("equal"); ax.axis("off")
    LEG = P["H"] - P["T_top"]
    R(ax, 0, 0, 80, LEG, WOOD); R(ax, 580, 0, 80, LEG, WOOD); R(ax, -20, LEG, 700, 40, "#efe0c2", hatch="///")
    R(ax, -20, zFA, 700, P["Ff_h"], "#b98d55")
    R(ax, 80, 70, 500, 120, WOOD2, alpha=0.6)
    fl = [B(f"Frontale cassetto {k}") for k in (1, 2, 3)]
    for f_ in fl: R(ax, f_[0], f_[2], f_[3] - f_[0], f_[5] - f_[2], "#5f7a8c")
    ax.text(330, zFA + 40, "FA", ha="center", fontsize=6.5, color="white")
    ax.text(330, 130, "ACi", ha="center", fontsize=6.5)
    ax.text(330, (fl[0][2] + fl[-1][5]) / 2, "3 cassetti", ha="center", fontsize=6.5, color="white")
    dim(ax, 660, cs[5], 660, zFA, 15, f"{zFA - cs[5]:.0f}", vertical=True, fs=6.5)
    ax.text(5, LEG / 2, "G1A", fontsize=6.5, rotation=90); ax.text(585, LEG / 2, "G2A", fontsize=6.5, rotation=90)
    ax.set_xlim(-30, 720); ax.set_ylim(-10, LEG + 60)
    ax.set_title("Vista frontale della campata cassetti", fontsize=8, loc="left")
    pdf.savefig(fig); plt.close(fig)

    # ---------- controlli
    fig = page("Controlli finali")
    checks = ["La scatola è in squadra: diagonali uguali entro 1 mm",
              "Tutti i cassetti escono completamente e rientrano senza sfregare",
              "Fughe tra i frontali uniformi (3 mm) e allineate ai bordi della scatola",
              "I cassetti aperti non toccano la fascia anteriore FA",
              "La cassettiera non si muove spingendola: viti nel ripiano e nelle gambe serrate",
              "Carico per cassetto: fino a 25–30 kg con guide da 45 kg (non riempire di piombo un solo cassetto)"]
    y = 0.86
    for c in checks:
        fig.patches.append(Rectangle((0.045, y - 0.016), 0.012, 0.016, transform=fig.transFigure, fc="white", ec=INK, lw=0.7))
        para(fig, 0.065, y, c, width=110, fs=9); y -= 0.05
    img(fig, "tavolo_completo.png", [0.45, 0.05, 0.53, 0.50], crop=(120, 960, 150, 1400))
    pdf.savefig(fig); plt.close(fig)
print("pagine:", PAGE[0])
