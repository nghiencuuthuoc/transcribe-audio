import os
import whisper
import time
from docx import Document
from datetime import datetime
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

# === CONFIGURATION ===
ROOT_FOLDER = "../mp3-test"
LOG_SUCCESS = "log/log_success.txt"
LOG_ERROR = "log/log_error.txt"
PROCESSED_LIST = "log/processed_files.txt"
SUPPORTED_EXT = [".mp3"]

# === Ensure log folder exists ===
for path in [LOG_SUCCESS, LOG_ERROR, PROCESSED_LIST]:
    os.makedirs(os.path.dirname(path), exist_ok=True)


# === Load Whisper model ===
model = whisper.load_model("large")  # hoặc "small", "medium", "large-v3"

# === Setup PDF font ===
pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))

def save_txt(text, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def save_docx(text, path):
    doc = Document()
    doc.add_paragraph(text)
    doc.save(path)

def save_pdf(text, path):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=4, fontName='Arial', fontSize=12, leading=18))  # 4 = justify

    doc = SimpleDocTemplate(path, pagesize=A4,
                            rightMargin=30, leftMargin=30,
                            topMargin=30, bottomMargin=18)

    story = []

    for paragraph in text.strip().split("\n\n"):
        story.append(Paragraph(paragraph.strip().replace("\n", " "), styles['Justify']))
        story.append(Spacer(1, 10 * mm))

    doc.build(story)

def log_write(file, message):
    with open(file, "a", encoding="utf-8") as f:
        f.write(message + "\n")

def load_processed_files():
    if os.path.exists(PROCESSED_LIST):
        with open(PROCESSED_LIST, "r", encoding="utf-8") as f:
            return set(f.read().splitlines())
    return set()

# === MAIN LOGIC ===
processed = load_processed_files()

for dirpath, _, filenames in os.walk(ROOT_FOLDER):
    for filename in filenames:
        if not any(filename.lower().endswith(ext) for ext in SUPPORTED_EXT):
            continue

        full_path = os.path.join(dirpath, filename)
        base_name = os.path.splitext(filename)[0]

        if full_path in processed:
            print(f"[SKIP] {filename}")
            continue

        try:
            print(f"\n🔄 [RUNNING] {filename}")
            print(f"⏱️  Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            start_time = time.time()

            result = model.transcribe(full_path, language="vi")
            text = result["text"].strip()

            txt_path = os.path.join(dirpath, base_name + ".txt")
            docx_path = os.path.join(dirpath, base_name + ".docx")
            pdf_path = os.path.join(dirpath, base_name + ".pdf")

            save_txt(text, txt_path)
            save_docx(text, docx_path)
            save_pdf(text, pdf_path)

            end_time = time.time()
            duration = end_time - start_time
            print(f"✅ [DONE] {filename} in {duration:.2f} seconds")
            print(f"🕒 End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

            log_write(LOG_SUCCESS, f"{datetime.now()} | SUCCESS | {full_path} | {duration:.2f} sec")
            log_write(PROCESSED_LIST, full_path)
        except Exception as e:
            log_write(LOG_ERROR, f"{datetime.now()} | ERROR | {full_path} | {str(e)}")
            print(f"❌ [ERROR] {filename}: {e}")
