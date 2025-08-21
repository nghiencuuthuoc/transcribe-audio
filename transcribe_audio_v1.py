import os
import sys
import whisper
import time
import argparse
import subprocess
from docx import Document
from datetime import datetime
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

# === CLI ARGUMENTS ===
parser = argparse.ArgumentParser(description="🎵 Transcribe audio files using Whisper")
parser.add_argument('-i', '--input', type=str, default="../mp3-test",
                    help='Input folder containing audio files')
parser.add_argument('--ffmpeg', type=str, default=None,
                    help='Path to ffmpeg executable (e.g., \"..\\apps\\ffmpeg\\bin\\ffmpeg.exe\")')
parser.add_argument('--model', type=str, default="large",
                    help='Whisper model size: tiny/base/small/medium/large or large-v3')
parser.add_argument('--lang', type=str, default="vi",
                    help='Language code for transcription, e.g., \"vi\", \"en\"')
args = parser.parse_args()

# === CONFIGURATION ===
ROOT_FOLDER = os.path.abspath(args.input)
LOG_SUCCESS = os.path.join(ROOT_FOLDER, "transcribe_log_success.txt")
LOG_ERROR = os.path.join(ROOT_FOLDER, "transcribe_log_error.txt")
PROCESSED_LIST = os.path.join(ROOT_FOLDER, "transcribe_processed_files.txt")

SUPPORTED_EXT = [".mp3", ".m4a", ".wav", ".flac", ".ogg", ".aac", ".wma", ".webm"]

print(f"🎵 Supported formats: {', '.join(SUPPORTED_EXT)}")
print(f"📂 Input folder: {ROOT_FOLDER}")
print(f"🗃️ Logs saved in: {ROOT_FOLDER}")

# === Ensure ffmpeg is available ===
def ensure_ffmpeg(ffmpeg_path: str | None) -> str:
    if ffmpeg_path:
        ffmpeg_path = os.path.abspath(ffmpeg_path)
        if not os.path.exists(ffmpeg_path):
            raise RuntimeError(f"ffmpeg not found at: {ffmpeg_path}")
        ffmpeg_dir = os.path.dirname(ffmpeg_path)
        os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
        cmd = ffmpeg_path
    else:
        cmd = "ffmpeg"

    try:
        out = subprocess.run([cmd, "-version"], capture_output=True, text=True)
        if out.returncode != 0:
            raise RuntimeError(out.stderr.strip() or "Unknown ffmpeg error")
        print(f"🎬 ffmpeg OK: {out.stdout.splitlines()[0]}")
    except FileNotFoundError:
        raise RuntimeError(
            "ffmpeg is not available. Install it or pass --ffmpeg <path-to-ffmpeg.exe>"
        )
    return cmd

try:
    _ffmpeg_cmd = ensure_ffmpeg(args.ffmpeg)
except RuntimeError as e:
    print(f"❌ {e}")
    sys.exit(1)

# === Load Whisper model ===
model = whisper.load_model(args.model)

# === Setup PDF font with safe fallback ===
PDF_FONT = "Arial"
try:
    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
except Exception:
    PDF_FONT = "Helvetica"
    print("ℹ️  'arial.ttf' not found. Using built-in 'Helvetica' for PDFs.")

# === Utility Functions ===
def save_txt(text, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def save_docx(text, path):
    doc = Document()
    for para in text.strip().split("\n\n"):
        doc.add_paragraph(para.strip())
    doc.save(path)

def save_pdf(text, path):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='Justify', alignment=4, fontName=PDF_FONT, fontSize=12, leading=18
    ))
    doc = SimpleDocTemplate(
        path, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18
    )
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
all_files = []

for dirpath, _, filenames in os.walk(ROOT_FOLDER):
    for filename in filenames:
        if any(filename.lower().endswith(ext) for ext in SUPPORTED_EXT):
            full_path = os.path.abspath(os.path.join(dirpath, filename))
            if full_path not in processed:
                all_files.append(full_path)

print(f"📁 Total audio files to process: {len(all_files)}")

for full_path in all_files:
    filename = os.path.basename(full_path)
    base_name = os.path.splitext(filename)[0]
    try:
        if not os.path.exists(full_path):
            print(f"⚠️ File not found: {full_path}")
            log_write(LOG_ERROR, f"{datetime.now()} | ERROR | {full_path} | File not found")
            continue

        print(f"\n🔄 [RUNNING] {filename}")
        print(f"⏱️  Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        start_time = time.time()

        result = model.transcribe(full_path, language=args.lang)
        text = result.get("text", "").strip()

        out_dir = os.path.dirname(full_path)
        txt_path = os.path.join(out_dir, base_name + ".txt")
        docx_path = os.path.join(out_dir, base_name + ".docx")
        pdf_path = os.path.join(out_dir, base_name + ".pdf")

        save_txt(text, txt_path)
        save_docx(text, docx_path)
        save_pdf(text, pdf_path)

        duration = time.time() - start_time
        print(f"✅ [DONE] {filename} in {duration:.2f} seconds")
        print(f"🕒 End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        log_write(LOG_SUCCESS, f"{datetime.now()} | SUCCESS | {full_path} | {duration:.2f} sec")
        log_write(PROCESSED_LIST, full_path)
    except Exception as e:
        log_write(LOG_ERROR, f"{datetime.now()} | ERROR | {full_path} | {str(e)}")
        print(f"❌ [ERROR] {filename}: {e}")
