import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.units import mm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

# === CONFIG ===
INPUT_FOLDER = "../mp3-test"
FONT_NAME = "Arial"
FONT_PATH = "C:/Windows/Fonts/arial.ttf"  # hoặc DejaVuSans.ttf

pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))

# === STYLE SETUP ===
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name='Justify',
    fontName=FONT_NAME,
    fontSize=12,
    leading=18,
    alignment=4,  # 0=left, 1=center, 2=right, 4=justify
    spaceAfter=10,
))

title_style = ParagraphStyle(
    name='Title',
    fontName=FONT_NAME,
    fontSize=14,
    leading=22,
    alignment=1,  # center
    spaceAfter=20,
)

# === Main processing ===
for dirpath, _, filenames in os.walk(INPUT_FOLDER):
    for filename in filenames:
        if filename.endswith(".txt"):
            txt_path = os.path.join(dirpath, filename)
            base = os.path.splitext(txt_path)[0]
            pdf_path = base + ".pdf"

            # Read text
            with open(txt_path, "r", encoding="utf-8") as f:
                text = f.read().strip().replace("\n", "<br/>")  # giữ xuống dòng

            # Build PDF
            doc = SimpleDocTemplate(
                pdf_path,
                pagesize=A4,
                rightMargin=20*mm,
                leftMargin=20*mm,
                topMargin=20*mm,
                bottomMargin=20*mm
            )

            story = []
            title = f"Transcription: {filename}"
            story.append(Paragraph(title, title_style))
            story.append(Paragraph(text, styles['Justify']))
            doc.build(story)

            print(f"✅ Saved (justify): {pdf_path}")
