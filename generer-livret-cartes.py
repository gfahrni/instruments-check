#!/usr/bin/env python3
"""Genere le livret Word A4 du catalogue des cartes de Edwin et Ambre (photos seules).

Source : cartes.json + images locales cartes/ (aucun telechargement).
Une section par enfant, cartes triees par numero croissant, 4 par rangee.
Usage : python3 generer-livret-cartes.py
"""
import json
import os
from concurrent.futures import ThreadPoolExecutor

from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
JSON = os.path.join(HERE, "cartes.json")
WORK = "/var/folders/4x/l5bh9wgd63ndbfxxh9vbvyt40000gn/T/opencode/cartes-livret"
OUT = os.path.join(HERE, "catalogue-cartes-edwin-ambre.docx")

PAGE = (21.0, 29.7)  # A4
M_TB, M_LR = 1.0, 1.0
N_COLS = 4
CELL, IMG = 4.75, 4.5
FRAME_W, FRAME_H = 400, 560  # cadre ratio carte (~2,5x3,5), photo entiere sur fond blanc
BORDER_SZ = "8"

# une couleur de cadre/fond par enfant
COLORS = {
    "edwin": ("C62828", "FFEBEE"),  # rouge Mario
    "ambre": ("AD1457", "FCE4EC"),  # rose princesse
}
FALLBACK = ("808080", "FFFFFF")

os.makedirs(WORK, exist_ok=True)


def set_cell_border(cell, color, bg):
    """Cadre fin colore + fond pastel + marges interieures (w:sz en 1/8 de point)."""
    tcPr = cell._tc.get_or_add_tcPr()
    borders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right"):
        el = OxmlElement("w:" + edge)
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), BORDER_SZ)
        el.set(qn("w:color"), color)
        borders.append(el)
    tcPr.append(borders)
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), bg)
    tcPr.append(shd)
    mar = OxmlElement("w:tcMar")
    for edge, w in (("top", "60"), ("left", "60"), ("bottom", "60"), ("right", "60")):
        el = OxmlElement("w:" + edge)
        el.set(qn("w:w"), w)
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    tcPr.append(mar)


def keep_row_together(row):
    """Interdit de couper une rangee entre 2 pages."""
    row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))


def num_key(card):
    """Trie par numero : 1, 2, ... 252 puis les Limited Edition (LE1, LE2, ...)."""
    n = card["num"]
    if n.isdigit():
        return (0, int(n))
    digits = "".join(ch for ch in n if ch.isdigit())
    return (1, int(digits or 0))


def prep(card):
    """Recadre l'image dans un cadre uniforme (letterbox blanc) -> grille reguliere."""
    cid = card["id"]
    dest = os.path.join(WORK, cid.replace("/", "_") + ".jpg")
    if os.path.exists(dest):
        return cid, True
    try:
        im = Image.open(os.path.join(HERE, card["img"])).convert("RGB")
        im.thumbnail((FRAME_W, FRAME_H), Image.LANCZOS)
        canvas = Image.new("RGB", (FRAME_W, FRAME_H), (255, 255, 255))
        canvas.paste(im, ((FRAME_W - im.width) // 2, (FRAME_H - im.height) // 2))
        canvas.save(dest, "JPEG", quality=82)
        return cid, True
    except Exception as e:
        print("   !!", cid, e, flush=True)
        return cid, False


print("1/3 lecture des donnees...", flush=True)
data = json.load(open(JSON, encoding="utf-8"))
total = sum(len(k["cartes"]) for k in data.values())
print("   enfants:", len(data), "• cartes:", total, flush=True)

print("2/3 preparation des %d photos..." % total, flush=True)
ok = {}
with ThreadPoolExecutor(max_workers=12) as ex:
    for cid, good in ex.map(prep, [c for k in data.values() for c in k["cartes"]]):
        ok[cid] = good
print("   images OK:", sum(ok.values()), "/", total, flush=True)

print("3/3 construction du docx...", flush=True)
doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(PAGE[0]), Cm(PAGE[1])
sec.top_margin = sec.bottom_margin = Cm(M_TB)
sec.left_margin = sec.right_margin = Cm(M_LR)

doc.add_heading("Catalogue des cartes", level=1)
doc.add_paragraph(
    "Edwin & Ambre • %d cartes • photos seules • 4 cartes par rangee" % total)

for kid_id, kid in data.items():
    color, bg = COLORS.get(kid_id, FALLBACK)
    cards = sorted(kid["cartes"], key=num_key)
    h = doc.add_heading(
        "%s (%s) — %d cartes" % (kid["nom"], kid["instrument"], len(cards)), level=2)
    h.paragraph_format.keep_with_next = True
    for run in h.runs:
        run.font.color.rgb = RGBColor.from_string(color)

    table = doc.add_table(rows=0, cols=N_COLS)
    table.autofit = False
    for i in range(0, len(cards), N_COLS):
        row = table.add_row()
        keep_row_together(row)
        for j in range(N_COLS):
            cell = row.cells[j]
            cell.width = Cm(CELL)
            cell.vertical_alignment = 0  # haut
            if i + j >= len(cards):
                continue
            card = cards[i + j]
            set_cell_border(cell, color, bg)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            if ok.get(card["id"]):
                run = p.add_run()
                run.add_picture(os.path.join(WORK, card["id"] + ".jpg"), width=Cm(IMG))

doc.save(OUT)
print("OK:", OUT, "%.1f Mo" % (os.path.getsize(OUT) / 1e6), flush=True)
