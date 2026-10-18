"""Manuale modulo 3 – Alzatina con mensola -> alzatina_manuale.pdf"""
import json
from manlib import *
from manlib import PAGE, FOOTER

d = json.load(open("parts_kvh.json")); P = d["params"]
parts = {p["name"]: p for p in d["parts"]}
FOOTER[0] = "Modulo 3 – Alzatina con mensola per il tavolo da lavoro – manuale"
H, Tt, RH, TM = P["H"], P["T_top"], P["riser_h"], P["T_riser"]
bw_, bh_ = P["mbat"]
xc = [x + P["Lx"] / 2 for x in d["legs_x"]]
boards = [parts[f"Mensola – tavola {k}"]["box"] for k in (1, 2, 3)]
blen = [round(b[3] - b[0]) for b in boards]
MD = P["riser_d"]
rod_top = H + RH + TM + 12; rod_bot = H - Tt - 60 - 10
ROD = round(rod_top - rod_bot / 1) if False else round(rod_top - (H - Tt - 70))

with PdfPages("alzatina_manuale.pdf") as pdf:
    # ---------- copertina
    fig = plt.figure(figsize=A4); PAGE[0] += 1
    fig.text(0.05, 0.9, "Alzatina con mensola", fontsize=30, weight="bold")
    fig.text(0.05, 0.85, "Modulo 3 del tavolo da lavoro – manuale di costruzione e montaggio", fontsize=14, color=MUTE)
    img(fig, "alz_installazione.png", [0.36, 0.06, 0.62, 0.78], crop=(60, 980, 0, 1500))
    fig.text(0.05, 0.76, "Contenuto", fontsize=11, weight="bold")
    fig.text(0.05, 0.735, "\n".join(["Cosa serve", "Fase 1 · Taglio e foratura", "Fase 2 · Mensola",
                                     "Fase 3 · Montaggio sul tavolo", "Fase 4 · Fissaggio a muro e controlli"]),
             fontsize=9, va="top", linespacing=1.9)
    box_note(fig, 0.05, 0.12, 0.28, 0.38, "In breve",
             f"Mensola lunga 2000, profonda {MD}, a {RH + TM} mm sopra il piano, su 4 montanti KVH 80×120 allineati "
             "alle gambe posteriori.\n\nMensola: 3 tavole lamellari OBI 800×200×14 + un listello 30×40 incollato "
             "sotto il bordo anteriore, che la irrigidisce circa 18 volte.\n\nSi monta sul tavolo base usando le "
             "predisposizioni: foro e dado a tamburo in ogni gamba posteriore.\n\nCosti in alzatina_costi.xlsx.",
             fs=8.3, width=44)
    pdf.savefig(fig); plt.close(fig)

    # ---------- cosa serve
    fig = page("Cosa serve")
    para(fig, 0.04, 0.89, "Materiali", fs=11, weight="bold")
    para(fig, 0.04, 0.86, (
        "• 3 tavole lamellari abete OBI 800×200×14 (art. 2423135)\n"
        "• 1 listello abete 30×40 da 2400\n"
        "• 4 montanti KVH 80×120×250 (tagliati insieme alle travi del tavolo base)\n"
        f"• 2 barre filettate M10 da 1 m → 4 spezzoni da {ROD}\n"
        "• 4 rondelle Ø30 + 4 dadi ciechi M10\n"
        "• Viti 4×50 (listello), colla vinilica D3\n"
        "• 2 angolari a L 100×100 + viti 5×40 + tasselli Ø8"), width=60, fs=8.8)
    para(fig, 0.04, 0.55, "Attrezzi", fs=11, weight="bold")
    para(fig, 0.04, 0.52, (
        "• Sega (troncatrice o circolare), seghetto per metalli\n• Trapano con punta Ø12 normale e punta lunga Ø12 da 300\n"
        "• Punta Ø3 e svasatore, avvitatore, chiave 17\n• Morsetti, squadra, livella, metro"), width=60, fs=8.8)
    box_note(fig, 0.52, 0.48, 0.44, 0.40, "Prima di comprare: verifica le tavole OBI",
             "La scheda del prodotto riporta misure contrastanti (800×200×14 nel titolo, 600×200×18 nella "
             "descrizione). Il progetto è fatto su 800×200×14: misurale in negozio.\n\n"
             f"Se fossero lunghe 600, la tavola centrale ({blen[1]} mm) non si ricava: servono 4 tavole con un "
             "giunto in più a metà della campata centrale, sostenuto solo dal listello. Avvisami e ricalcolo.",
             fs=8.3, width=64)
    box_note(fig, 0.52, 0.10, 0.44, 0.32, "Prerequisiti dal tavolo base",
             "• Nelle 4 gambe posteriori: foro Ø12 in testa e dado a tamburo inserito dal retro, con il foro "
             "filettato in verticale.\n• I 4 montanti M1–M4 tagliati e conservati.\n"
             "• Se il tavolo è già fissato al muro, per avvitare le barre non serve staccarlo: i dadi sono già dentro.",
             fs=8.3, width=64, color="#eef4f8", edge="#8fb1c8")
    pdf.savefig(fig); plt.close(fig)

    # ---------- taglio e foratura
    fig = page("Taglio e foratura", "Fase 1")
    para(fig, 0.04, 0.89, (
        "Taglio\n"
        f"1. Tavole OBI a lunghezza: {blen[0]}, {blen[1]} e {blen[2]} mm (tutte larghe 200). I giunti cadono al centro "
        "dei montanti 2 e 3. Tagli a 90° precisi: le teste si accostano a vista.\n"
        "2. Listello 30×40 a 2000 mm.\n"
        f"3. Barre M10: 4 spezzoni da {ROD} mm, due per barra. Smussa le estremità con la lima.\n\n"
        "Foratura\n"
        "4. Montanti (se non già fatto): foro Ø12 passante in asse, a 60 mm dal filo posteriore; fora 125 mm "
        "da ogni testa con la punta lunga.\n"
        "5. Mensola: i fori Ø12 si fanno in fase 2 a mensola incollata, così i fori sui giunti restano allineati.\n"
        "6. Piano del tavolo: 4 fori Ø12 passanti a 740 dal fronte, x = " + ", ".join(f"{x:.0f}" for x in xc) +
        " da sinistra. Sono in asse con i fori delle gambe: fora dritto con la squadra di guida."), width=64, fs=8.5)
    ax = fig.add_axes([0.04, 0.06, 0.92, 0.36]); ax.set_aspect("equal"); ax.axis("off")
    for k, b in enumerate(boards):
        R(ax, b[0], 0, b[3] - b[0], MD, "#ecd3a8" if k % 2 == 0 else "#e4c99a", lw=0.7)
        ax.text((b[0] + b[3]) / 2, MD / 2 + 25, f"tavola {k+1}\n{blen[k]}", ha="center", fontsize=7)
    R(ax, 0, 0, 2000, bw_, "white", ec=MUTE, ls="--", lw=0.6, alpha=0.6)
    ax.text(1000, bw_ / 2, "listello 30×40 sotto (tratteggio)", ha="center", va="center", fontsize=6.5, color=MUTE)
    ymr = MD - 60
    for x in xc:
        ax.add_patch(Circle((x, ymr), 6, fc=HCOL["M"], ec=INK)); ax.text(x, ymr + 14, f"{x:.0f}", ha="center", fontsize=6.5, color=RED)
    for x in range(75, 2000, 150):
        if all(abs(x - j) > 30 for j in (boards[0][3], boards[1][3])):
            ax.plot(x, bw_ / 2 - 6, marker="x", ms=3, color=INK)
    dim(ax, 2000, 0, 2000, ymr, 30, f"{ymr:.0f}", vertical=True); dim(ax, 2000, ymr, 2000, MD, 30, "60", vertical=True)
    dim(ax, 0, MD, boards[0][3], MD, 25); dim(ax, boards[0][3], MD, boards[1][3], MD, 25); dim(ax, boards[1][3], MD, 2000, MD, 25)
    ax.text(1000, -40, "FRONTE della mensola – vista dall'alto · ✕ = viti 4×50 dal listello (ogni 150, non a meno di 30 mm dai giunti)",
            ha="center", fontsize=7, color=MUTE)
    ax.set_xlim(-30, 2100); ax.set_ylim(-70, MD + 70)
    pdf.savefig(fig); plt.close(fig)

    # ---------- mensola
    fig = page("Mensola", "Fase 2")
    img(fig, "alz_mensola_sotto.png", [0.50, 0.42, 0.49, 0.50], crop=(60, 940, 0, 1500))
    para(fig, 0.04, 0.89, (
        "1. Lavora su un piano dritto (anche il tavolo base). Disponi le 3 tavole a rovescio, testa contro "
        "testa, e controlla con il listello che siano in linea.\n"
        "2. Stendi la colla sul listello e appoggialo a filo del bordo ANTERIORE (che ora è verso di te, a "
        "rovescio), dall'inizio alla fine della mensola.\n"
        "3. Viti 4×50 dal listello nella tavola ogni 150 mm, a 15 mm dal bordo: preforo Ø3 nel listello, "
        "svasatura. La vite entra 10 mm nella tavola da 14: non usare viti più lunghe.\n"
        "4. Ai giunti metti una vite a 30 mm per parte: il listello tiene unite le tavole.\n"
        "5. A colla asciutta, gira la mensola. Fora Ø12 nei 4 punti (a 60 dal filo posteriore): sui giunti il foro "
        "è metà in una tavola e metà nell'altra, va bene così. La rondella e il dado cieco le stringeranno entrambe.\n"
        "6. Leviga (120–180), smussa gli spigoli e tratta con olio."), width=62, fs=8.5)
    ax = fig.add_axes([0.04, 0.05, 0.42, 0.33]); ax.set_aspect("equal"); ax.axis("off")
    R(ax, 0, 0, MD, TM, "#ecd3a8"); R(ax, 0, -bh_, bw_, bh_, "#d4ae7c")
    R(ax, 12.5, -bh_, 5, bh_ + 10, STEEL, lw=0.3)
    R(ax, MD - 66, -30, 12, TM + 30, "white", ec=HCOL["M"], ls="--")
    dim(ax, 0, TM, MD, TM, 14, f"{MD}"); dim(ax, -10, -bh_, -10, TM, -12, f"{bh_ + TM}", vertical=True)
    ax.text(40, -20, "listello 30×40", fontsize=6.5); ax.text(60, 4, "tavola 14", fontsize=6.5)
    ax.text(MD - 60, -40, "Ø12", fontsize=6.5, color=HCOL["M"], ha="center")
    ax.set_xlim(-50, MD + 30); ax.set_ylim(-70, 50)
    ax.set_title("Sezione della mensola (fronte a sinistra)", fontsize=8, loc="left")
    pdf.savefig(fig); plt.close(fig)

    # ---------- montaggio
    fig = page("Montaggio sul tavolo", "Fase 3")
    img(fig, "alz_installazione.png", [0.52, 0.40, 0.47, 0.52], crop=(60, 980, 0, 1500))
    para(fig, 0.04, 0.89, (
        "1. Fora il piano (fase 1, punto 6) e pulisci i trucioli dal foro della gamba.\n"
        "2. Prova ogni posizione: infila una barra nel foro del piano e avvitala di qualche giro nel dado a "
        "tamburo della gamba. Se non prende, il dado è ruotato: vedi il riquadro.\n"
        "3. Appoggia i montanti M1–M4 sul piano, a filo del bordo posteriore e allineati alle gambe.\n"
        "4. Appoggia la mensola sui montanti, a filo dietro e ai lati.\n"
        f"5. Infila le barre da {ROD} dall'alto: attraversano mensola, montante e piano. Avvitale nel dado ruotando "
        "la barra con due dadi bloccati uno contro l'altro in cima, poi toglili.\n"
        "6. Rondella Ø30 e dado cieco sopra la mensola. Stringi con moderazione: la tavola è sottile, basta che il "
        "montante non giri.\n"
        "7. Controlla con la livella che la mensola sia piana; se serve, spessori sotto un montante."), width=62, fs=8.8)
    box_note(fig, 0.78, 0.06, 0.19, 0.30, "Se la barra non entra nel dado",
             "Il foro filettato del dado non è verticale. Stacca il tavolo dal muro, gira il dado dalla fessura sul "
             "retro della gamba con un cacciavite piatto finché la barra prende.", fs=7.8, width=30)
    ax = fig.add_axes([0.50, 0.03, 0.27, 0.36]); ax.set_aspect("equal"); ax.axis("off")
    zt = H + RH
    R(ax, 680, 450, 120, H - Tt - 450, WOOD); R(ax, 520, H - Tt, 280, Tt, "#efe0c2", hatch="///")
    R(ax, 680, H, 120, RH, WOOD); R(ax, 800 - MD, zt, MD, TM, "#ecd3a8"); R(ax, 800 - MD, zt - bh_, bw_, bh_, "#d4ae7c")
    R(ax, 735, H - Tt - 70, 10, ROD, STEEL, lw=0.4)
    R(ax, 725, zt + TM, 30, 3, STEEL); ax.add_patch(Circle((740, zt + TM + 10), 8, fc="#c8cdd2", ec=INK))
    R(ax, 730, H - Tt - 67.5, 70, 15, "white", ec=HCOL["T"], ls="--"); ax.add_patch(Circle((740, H - Tt - 60), 7.5, fc=STEEL, ec=INK))
    ax.plot([800, 800], [430, zt + 60], color="#555", lw=2); ax.text(806, 480, "muro", fontsize=6.5, rotation=90)
    ax.text(805 - MD, zt + 25, f"mensola {TM}", fontsize=6.3); ax.text(612, zt - 30, "listello", fontsize=6.3)
    ax.text(600, H + 120, "montante\n80×120", fontsize=6.3); ax.text(530, H - Tt + 10, "piano 40", fontsize=6.3)
    ax.text(600, 560, "gamba\nposteriore", fontsize=6.3); ax.text(600, H - Tt - 90, "dado D", fontsize=6.3, color=HCOL["T"])
    dim(ax, 680, 450, 800, 450, -20, "120", fs=6.3); dim(ax, 520, H, 520, zt + TM, -12, f"{RH + TM}", vertical=True, fs=6.3)
    ax.set_xlim(480, 840); ax.set_ylim(400, zt + 80)
    ax.set_title(f"Sezione: barra M10 da {ROD} dal dado alla mensola", fontsize=8, loc="left")
    pdf.savefig(fig); plt.close(fig)

    # ---------- muro e controlli
    fig = page("Fissaggio a muro e controlli", "Fase 4")
    para(fig, 0.04, 0.89, (
        "Fissaggio a muro\n"
        "1. 2 angolari a L sulle facce esterne dei montanti M1 (sinistra) e M4 (destra), a metà altezza: "
        "viti 5×40 nel montante, tasselli Ø8 nel muro.\n"
        "2. Non sostituisce il fissaggio a muro del tavolo base: lo completa e impedisce alla mensola di oscillare.\n\n"
        "Carichi consigliati\n"
        "• Fino a 20 kg per campata tra due montanti (monitor, alimentatore da banco, oscilloscopio).\n"
        "• Carichi concentrati pesanti (oltre 10 kg in un punto): mettili vicino a un montante.\n"
        "• Non appoggiarsi né salire sulla mensola."), width=70, fs=8.8)
    checks = ["I 4 dadi ciechi sono serrati e i montanti non ruotano",
              "La mensola è in bolla e a filo del bordo posteriore",
              "I giunti tra le tavole sono chiusi e a livello",
              "Con 10 kg al centro della campata più lunga la mensola non flette in modo visibile",
              "Angolari a muro serrati"]
    para(fig, 0.04, 0.50, "Controlli finali", fs=10.5, weight="bold")
    y = 0.47
    for c in checks:
        fig.patches.append(Rectangle((0.045, y - 0.016), 0.012, 0.016, transform=fig.transFigure, fc="white", ec=INK, lw=0.7))
        para(fig, 0.065, y, c, width=80, fs=8.8); y -= 0.045
    img(fig, "tavolo_completo.png", [0.52, 0.06, 0.46, 0.84], crop=(120, 960, 150, 1400))
    pdf.savefig(fig); plt.close(fig)
print("pagine:", PAGE[0], "barra", ROD)
