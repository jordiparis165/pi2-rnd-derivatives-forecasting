from __future__ import annotations

import html
import re
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "Livrables_reunion_14-10-2026"
OUT.mkdir(exist_ok=True)

BLUE = colors.HexColor("#153A5B")
CYAN = colors.HexColor("#1C7897")
LIGHT = colors.HexColor("#EAF2F6")
TEXT = colors.HexColor("#24323D")
MUTED = colors.HexColor("#60717D")

pdfmetrics.registerFont(TTFont("Arial", r"C:\Windows\Fonts\arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", r"C:\Windows\Fonts\arialbd.ttf"))


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("Title", parent=base["Title"], fontName="Arial-Bold", fontSize=20, leading=24, textColor=BLUE, alignment=TA_CENTER, spaceAfter=12),
        "subtitle": ParagraphStyle("Subtitle", parent=base["Normal"], fontName="Arial", fontSize=11, leading=15, textColor=MUTED, alignment=TA_CENTER, spaceAfter=18),
        "h1": ParagraphStyle("H1", parent=base["Heading1"], fontName="Arial-Bold", fontSize=15, leading=19, textColor=BLUE, spaceBefore=12, spaceAfter=7),
        "h2": ParagraphStyle("H2", parent=base["Heading2"], fontName="Arial-Bold", fontSize=12, leading=15, textColor=CYAN, spaceBefore=10, spaceAfter=5),
        "h3": ParagraphStyle("H3", parent=base["Heading3"], fontName="Arial-Bold", fontSize=10.5, leading=14, textColor=TEXT, spaceBefore=8, spaceAfter=4),
        "body": ParagraphStyle("Body", parent=base["BodyText"], fontName="Arial", fontSize=9.4, leading=13.2, textColor=TEXT, alignment=TA_LEFT, spaceAfter=5),
        "bullet": ParagraphStyle("Bullet", parent=base["BodyText"], fontName="Arial", fontSize=9.2, leading=12.8, textColor=TEXT, leftIndent=14, firstLineIndent=-8, spaceAfter=3),
        "quote": ParagraphStyle("Quote", parent=base["BodyText"], fontName="Arial", fontSize=9.5, leading=13.5, textColor=BLUE, leftIndent=14, rightIndent=10, borderColor=CYAN, borderWidth=1.5, borderPadding=8, backColor=LIGHT, spaceBefore=4, spaceAfter=8),
        "small": ParagraphStyle("Small", parent=base["BodyText"], fontName="Arial", fontSize=7.5, leading=10, textColor=MUTED),
    }


ST = styles()


def compact_styles():
    compact = dict(ST)
    compact["title"] = ParagraphStyle("CompactTitle", parent=ST["title"], fontSize=18, leading=21, spaceAfter=7)
    compact["subtitle"] = ParagraphStyle("CompactSubtitle", parent=ST["subtitle"], fontSize=9.5, leading=12, spaceAfter=9)
    compact["h1"] = ParagraphStyle("CompactH1", parent=ST["h1"], fontSize=13, leading=15, spaceBefore=6, spaceAfter=3)
    compact["h2"] = ParagraphStyle("CompactH2", parent=ST["h2"], fontSize=11, leading=13, spaceBefore=5, spaceAfter=2)
    compact["body"] = ParagraphStyle("CompactBody", parent=ST["body"], fontSize=8.4, leading=10.6, spaceAfter=2)
    compact["bullet"] = ParagraphStyle("CompactBullet", parent=ST["bullet"], fontSize=8.3, leading=10.4, spaceAfter=1.5)
    compact["quote"] = ParagraphStyle("CompactQuote", parent=ST["quote"], fontSize=8.5, leading=10.8, borderPadding=6, spaceAfter=4)
    return compact


def markup(text: str) -> str:
    text = html.escape(text.strip())
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" color="#1C7897">\1</a>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`(.+?)`", r'<font name="Courier">\1</font>', text)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    return text


def header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setFillColor(BLUE)
    canvas.rect(0, h - 0.55 * cm, w, 0.55 * cm, fill=1, stroke=0)
    canvas.setFont("Arial", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(2 * cm, 1.15 * cm, "Projet PI² n°176 — ESILV")
    canvas.drawRightString(w - 2 * cm, 1.15 * cm, f"Page {doc.page}")
    canvas.restoreState()


def make_doc(path: Path):
    doc = BaseDocTemplate(str(path), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm, bottomMargin=1.7 * cm, title=path.stem)
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    doc.addPageTemplates(PageTemplate(id="main", frames=frame, onPage=header_footer))
    return doc


def parse_markdown(path: Path, title: str, subtitle: str, compact: bool = False):
    current = compact_styles() if compact else ST
    lines = path.read_text(encoding="utf-8").splitlines()
    story = [Paragraph(markup(title), current["title"]), Paragraph(markup(subtitle), current["subtitle"])]
    in_quote = False
    in_math = False
    table_rows = []

    def flush_table():
        nonlocal table_rows
        if not table_rows:
            return
        usable = [r for r in table_rows if not all(set(c.strip()) <= {"-", ":"} for c in r)]
        if usable:
            data = [[Paragraph(markup(c), current["small"] if i else current["body"]) for c in row] for i, row in enumerate(usable)]
            widths = [doc_width / len(data[0])] * len(data[0])
            tbl = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
            tbl.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), BLUE),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Arial-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#B9C8D1")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.extend([tbl, Spacer(1, 6)])
        table_rows = []

    for raw in lines:
        line = raw.rstrip()
        if line.strip() == "\\[":
            in_math = True
            continue
        if line.strip() == "\\]":
            in_math = False
            continue
        if in_math:
            if "q_t(K,T)" in line:
                story.append(Paragraph("q(K,T) = exp[r(T−t)] × ∂²C(K,T) / ∂K²", current["quote"]))
            else:
                story.append(Paragraph(markup(line), current["quote"]))
            continue
        if line.startswith("|") and line.endswith("|"):
            table_rows.append([c.strip() for c in line.strip("|").split("|")])
            continue
        flush_table()
        if not line.strip():
            in_quote = False
            continue
        if line.startswith("# "):
            continue
        if line.startswith("## "):
            story.append(Paragraph(markup(line[3:]), current["h1"]))
        elif line.startswith("### "):
            story.append(Paragraph(markup(line[4:]), current["h2"]))
        elif line.startswith("#### "):
            story.append(Paragraph(markup(line[5:]), current["h3"]))
        elif line.startswith("> "):
            story.append(Paragraph(markup(line[2:]), current["quote"]))
            in_quote = True
        elif re.match(r"^\d+\.\s", line):
            number, content = line.split(". ", 1)
            story.append(Paragraph(f"<b>{number}.</b> {markup(content)}", current["bullet"]))
        elif line.startswith("- "):
            story.append(Paragraph(f"• {markup(line[2:])}", current["bullet"]))
        else:
            style = current["quote"] if in_quote else current["body"]
            story.append(Paragraph(markup(line), style))
    flush_table()
    return story


doc_width = A4[0] - 4 * cm


def build_markdown_pdf(src: str, out: str, title: str, subtitle: str, compact: bool = False):
    target = OUT / out
    doc = make_doc(target)
    doc.build(parse_markdown(ROOT / src, title, subtitle, compact=compact))
    return target


def build_cover(path: Path):
    doc = make_doc(path)
    story = [
        Spacer(1, 3.1 * cm),
        Paragraph("Projet PI² n°176", ST["title"]),
        Paragraph("Dynamic of RND and Forecasting the Price of Derivatives", ParagraphStyle("cover", parent=ST["h1"], alignment=TA_CENTER, fontSize=17, leading=22)),
        Spacer(1, 1.1 * cm),
        Paragraph("Dossier de préparation — Réunion de lancement", ParagraphStyle("cover2", parent=ST["body"], alignment=TA_CENTER, fontSize=13, leading=18, textColor=CYAN)),
        Spacer(1, 0.7 * cm),
        Paragraph("14 octobre 2026", ST["subtitle"]),
        Spacer(1, 2.0 * cm),
        Paragraph("Rayan Ait Arkoub · Matthieu Balliste · Ilan Chahdi<br/>Nathan Denoux · Jordi Paris", ParagraphStyle("authors", parent=ST["body"], alignment=TA_CENTER, fontSize=11, leading=17)),
        Spacer(1, 2.2 * cm),
        Paragraph("Contenu : brief opérationnel, préparation détaillée et bibliographie structurée.", ParagraphStyle("desc", parent=ST["body"], alignment=TA_CENTER, textColor=MUTED)),
    ]
    doc.build(story)


brief = build_markdown_pdf("Brief_reunion_16h.md", "01_Brief_reunion_16h.pdf", "Projet PI² n°176", "Brief opérationnel — réunion du 14 octobre 2026 à 16 h", compact=True)
prep = build_markdown_pdf("Preparation_reunion_14-10-2026.md", "02_Preparation_complete_reunion.pdf", "Projet PI² n°176", "Préparation complète de la réunion de lancement")
biblio = build_markdown_pdf("Bibliographie_commentee.md", "03_Bibliographie_structuree.pdf", "Projet PI² n°176", "Bibliographie structurée et commentée")
minutes = build_markdown_pdf("Compte_rendu_kickoff_14-10-2026.md", "04_Compte_rendu_kickoff.pdf", "Projet PI² n°176", "Compte rendu de la réunion de lancement du 14 octobre 2026")
action = build_markdown_pdf("Plan_action_16-20_octobre_2026.md", "05_Plan_action_avant_suivi.pdf", "Projet PI² n°176", "Plan d'action du 16 au 20 octobre 2026")

cover = OUT / "_cover.pdf"
build_cover(cover)
writer = PdfWriter()
for pdf in (cover, brief, prep, biblio, minutes, action):
    for page in PdfReader(str(pdf)).pages:
        writer.add_page(page)
combined = OUT / "Dossier_complet_reunion_14-10-2026.pdf"
with combined.open("wb") as stream:
    writer.write(stream)
cover.unlink()

for source in ("brief_reunion_14-10-2026.tex", "bibliographie_projet_176.tex", "references.bib"):
    (OUT / source).write_bytes((ROOT / source).read_bytes())

print("PDF generated:")
for path in sorted(OUT.iterdir()):
    print(f"- {path.name} ({path.stat().st_size} bytes)")
