# Workbench – tavolo da lavoro modulare

Tavolo da lavoro 2000 × 800 mm, piano a 740 mm, per elettronica, computer e ricarica cartucce.
Il progetto è diviso in **tre moduli indipendenti**, ognuno con il proprio manuale, modello 3D e foglio costi:
si costruisce prima il tavolo base, gli altri si aggiungono quando vuoi.

![Tavolo completo](immagini/tavolo_completo.png)

| Modulo | Cosa comprende | Costo stimato | Cartella |
|---|---|---|---|
| **1 · Tavolo base** | Telaio in travi KVH 80×120, piano lamellare 40, ripiani e rinforzo in OSB/3 18, zona ricarica con piastre intercambiabili, canaline | ~589 € | [moduli/1-tavolo-base](moduli/1-tavolo-base) |
| **2 · Cassettiera** | Cassettiera fissa a 3 cassetti per la campata sinistra + cassetto appeso sotto il piano | ~172 € | [moduli/2-cassettiera](moduli/2-cassettiera) |
| **3 · Alzatina** | 4 montanti + mensola 2000×200 in tavole OBI 800×200×14 con listello di rinforzo | ~62 € | [moduli/3-alzatina](moduli/3-alzatina) |

I costi comprendono prezzi verificati (travi, lamellare, OSB, tavole OBI) e stime da sostituire, evidenziate in giallo nei fogli.

## Come si collegano i moduli

- Il **tavolo base** prepara tutto: nelle 4 gambe posteriori c'è un foro Ø12 in testa e un dado a tamburo M10, e i 4 montanti dell'alzatina vengono tagliati dalle stesse travi del telaio (le 4 barre KVH bastano).
- La **cassettiera** non richiede lavorazioni sul telaio: si appoggia al ripiano OSB della campata sinistra e si avvita alle gambe; le guide del cassetto appeso si avvitano sulle traverse.
- L'**alzatina** si monta forando il piano in 4 punti e avvitando le barre M10 nei dadi già presenti nelle gambe.

## Contenuto di ogni modulo

- `*_manuale.pdf` – manuale passo passo: materiali, taglio, foratura, montaggio, sezioni quotate, controlli
- `*_costi.xlsx` – distinta e costi con formule
- `*.step` – modello 3D del modulo (FreeCAD, Fusion 360, SolidWorks)
- `immagini/` – viste di montaggio

Il tavolo base ha in più le tavole quotate (`tavolo_base_tavole.pdf`).
Il modello completo con tutti i moduli è in `modello/tavolo_completo.step`.

## Scelte di materiale

- **Travi KVH 80×120**: il prezzo al metro più basso tra quelle trovate, legno essiccato e stabile (confronto nel foglio costi del modulo 1).
- **OSB/3 18 per ripiani e rinforzo**: circa 10 €/m², un solo pannello basta per tutto. Il lamellare 40 costerebbe 2,5 volte tanto; le tavole OBI 800×200×14 sarebbero ancora più care e più sottili.
- **Tavole OBI 800×200×14 per la mensola**: tre tavole e un listello costano meno di un pannello intero; il listello sotto il bordo anteriore la rende circa 18 volte più rigida.

## Rigenerare i file

Gli script in `modello/` sono parametrici (Python + CadQuery). Da quella cartella:

```bash
pip install cadquery openpyxl matplotlib vtk
python tavolo_kvh.py          # modello completo, parts_kvh.json
python fori.py                # tutti i fori + controllo collisioni
python step_moduli.py         # un STEP per modulo
python costi.py               # confronto travi (confronto.json)
python costi_moduli.py        # i tre fogli costi
python manuale_render.py      # viste del tavolo base
python render_moduli.py       # viste di cassettiera e alzatina
python tavole_kvh.py          # tavole quotate del tavolo base
python manuale.py             # manuale del tavolo base
python manuale_cassettiera.py
python manuale_alzatina.py
```

I parametri (dimensioni, sezioni, campate, spessori) sono nel dizionario `P` di `tavolo_kvh.py`.
Gli script si aspettano le immagini nella stessa cartella in cui vengono eseguiti.

## Archivio

Versioni precedenti, non più in sviluppo:

- `archivio/quadrotti-8x8/` – prima versione in quadrotti di abete 8×8
- `archivio/listelli-25x50/` – versione in listelli 25×50 laminati
