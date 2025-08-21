import os
import whisper
from docx import Document
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime

# === CONFIGURATION ===
ROOT_FOLDER = "../mp3-test"
LOG_SUCCESS = "log_success.txt"
LOG_ERROR = "log_error.txt"
PROCESSED_LIST = "processed_files.txt"
SUPPORTED_EXT = [".mp3"]

# === Load Whisper model (change to 'small' or 'large' if needed) ===
# model = whisper.load_model("medium")
model = whisper.load_model("large")  # hoặc "large-v3"

# === Setup PDF font ===
pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))  # Ensure arial.ttf is in the same folder or installed system-wide

def save_txt(text, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def save_docx(text, path):
    doc = Document()
    doc.add_paragraph(text)
    doc.save(path)

def save_pdf(text, path):
    c = canvas.Canvas(path, pagesize=A4)
    c.setFont("Arial", 12)
    width, height = A4
    y = height - 40
    for line in text.splitlines():
        if y < 40:
            c.showPage()
            c.setFont("Arial", 12)
            y = height - 40
        c.drawString(40, y, line)
        y -= 20
    c.save()

def log_write(file, message):
    with open(file, "a", encoding="utf-8") as f:
        f.write(message + "\n")

def load_processed_files():
    if os.path.exists(PROCESSED_LIST):
        with open(PROCESSED_LIST, "r", encoding="utf-8") as f:
            return set(f.read().splitlines())
    return set()

# === Main logic ===
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
            print(f"[RUNNING] {filename}")
            result = model.transcribe(full_path, language="vi")
            text = result["text"].strip()

            # Output paths
            txt_path = os.path.join(dirpath, base_name + ".txt")
            docx_path = os.path.join(dirpath, base_name + ".docx")
            pdf_path = os.path.join(dirpath, base_name + ".pdf")

            save_txt(text, txt_path)
            save_docx(text, docx_path)
            save_pdf(text, pdf_path)

            log_write(LOG_SUCCESS, f"{datetime.now()} | SUCCESS | {full_path}")
            log_write(PROCESSED_LIST, full_path)
        except Exception as e:
            log_write(LOG_ERROR, f"{datetime.now()} | ERROR | {full_path} | {str(e)}")
            print(f"[ERROR] {filename}: {e}")
