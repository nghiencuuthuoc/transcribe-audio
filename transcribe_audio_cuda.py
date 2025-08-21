import os
import sys
import time
import argparse
import subprocess
from datetime import datetime

import whisper
from docx import Document

# Try to import torch for CUDA checks (optional but recommended)
try:
    import torch
except Exception:
    torch = None

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

# =========================
# CLI ARGUMENTS
# =========================
parser = argparse.ArgumentParser(description="🎵 Transcribe audio files using Whisper (CUDA-ready, smart skip)")
parser.add_argument('-i', '--input', type=str, default="../mp3-test",
                    help='Input folder containing audio files')
parser.add_argument('--ffmpeg', type=str, default=None,
                    help='Path to ffmpeg executable (e.g., "..\\apps\\ffmpeg\\bin\\ffmpeg.exe")')
parser.add_argument('--model', type=str, default="large",
                    help='Whisper model: tiny/base/small/medium/large or large-v3')
parser.add_argument('--lang', type=str, default="vi",
                    help='Language code, e.g., "vi", "en"')
parser.add_argument('--device', type=str, default="auto",
                    choices=["auto", "cuda", "cpu"],
                    help='Device to run on: auto (prefer CUDA), cuda, cpu')
parser.add_argument('--batch_size', type=int, default=16,
                    help='(Hint) Batch size for decoding; whisper adapts internally')
parser.add_argument('--temperature', type=float, default=0.0,
                    help='Decoding temperature (0.0 = greedy)')
parser.add_argument('--verbose', action='store_true',
                    help='Print more details from Whisper')
args = parser.parse_args()

# =========================
# PATHS & CONSTANTS
# =========================
ROOT_FOLDER = os.path.abspath(args.input)
LOG_SUCCESS = os.path.join(ROOT_FOLDER, "transcribe_log_success.txt")
LOG_ERROR = os.path.join(ROOT_FOLDER, "transcribe_log_error.txt")
PROCESSED_LIST = os.path.join(ROOT_FOLDER, "transcribe_processed_files.txt")

SUPPORTED_EXT = [".mp3", ".m4a", ".wav", ".flac", ".ogg", ".aac", ".wma", ".webm"]

print(f"🎵 Supported formats: {', '.join(SUPPORTED_EXT)}")
print(f"📂 Input folder: {ROOT_FOLDER}")
print(f"🗃️ Logs saved in: {ROOT_FOLDER}")

# =========================
# Helpers
# =========================
def ensure_ffmpeg(ffmpeg_path: str | None) -> str:
    """
    Ensure ffmpeg is callable. If a path is provided, prepend its folder to PATH.
    Returns the resolved command to call ("ffmpeg" or the given absolute path).
    Raises RuntimeError if not found/working.
    """
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

def log_write(file, message):
    with open(file, "a", encoding="utf-8") as f:
        f.write(message + "\n")

def load_processed_files():
    if os.path.exists(PROCESSED_LIST):
        with open(PROCESSED_LIST, "r", encoding="utf-8") as f:
            return set(f.read().splitlines())
    return set()

def save_txt(text, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def save_docx(text, path):
    doc = Document()
    # Preserve paragraphs roughly by splitting on double newline
    for para in (text or "").strip().split("\n\n"):
        doc.add_paragraph(para.strip())
    doc.save(path)

def save_pdf(text, path, pdf_font="Helvetica"):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='Justify', alignment=4, fontName=pdf_font, fontSize=12, leading=18
    ))
    doc = SimpleDocTemplate(
        path, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18
    )
    story = []
    for paragraph in (text or "").strip().split("\n\n"):
        story.append(Paragraph(paragraph.strip().replace("\n", " "), styles['Justify']))
        story.append(Spacer(1, 10 * mm))
    doc.build(story)

# =========================
# ffmpeg
# =========================
try:
    _ffmpeg_cmd = ensure_ffmpeg(args.ffmpeg)
except RuntimeError as e:
    print(f"❌ {e}")
    sys.exit(1)

# =========================
# PDF font registration (safe fallback)
# =========================
PDF_FONT = "Arial"
try:
    pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
except Exception:
    PDF_FONT = "Helvetica"
    print("ℹ️  'arial.ttf' not found. Using built-in 'Helvetica' for PDFs.")

# =========================
# Device selection (CUDA)
# =========================
def pick_device():
    # User-forced choice
    if args.device == "cpu":
        return "cpu", False
    if args.device == "cuda":
        if torch is None or not torch.cuda.is_available():
            print("⚠️ Requested CUDA but PyTorch CUDA is not available; falling back to CPU.")
            return "cpu", False
        return "cuda", True

    # AUTO: prefer CUDA if available
    if torch is not None and torch.cuda.is_available():
        return "cuda", True
    return "cpu", False

device, has_cuda = pick_device()

if has_cuda:
    try:
        gpu_name = torch.cuda.get_device_name(0)
        print(f"🟢 Using CUDA: {gpu_name}")
    except Exception:
        print("🟢 Using CUDA")
else:
    print("🟡 Running on CPU")

# FP16 is only for CUDA
use_fp16 = bool(has_cuda)

# =========================
# Load Whisper model on chosen device
# =========================
print(f"🧠 Loading Whisper model '{args.model}' on device: {device} (fp16={use_fp16}) ...")
# openai/whisper supports the 'device' parameter
model = whisper.load_model(args.model, device=device)

# =========================
# Collect audio files
# =========================
all_files = []
for dirpath, _, filenames in os.walk(ROOT_FOLDER):
    for filename in filenames:
        if any(filename.lower().endswith(ext) for ext in SUPPORTED_EXT):
            full_path = os.path.abspath(os.path.join(dirpath, filename))
            all_files.append(full_path)

print(f"📁 Total audio files found: {len(all_files)}")

# =========================
# Transcribe loop (smart skip)
# =========================
processed = load_processed_files()

for full_path in all_files:
    filename = os.path.basename(full_path)
    base_name = os.path.splitext(filename)[0]
    out_dir = os.path.dirname(full_path)

    # Output paths
    txt_path = os.path.join(out_dir, base_name + ".txt")
    docx_path = os.path.join(out_dir, base_name + ".docx")
    pdf_path = os.path.join(out_dir, base_name + ".pdf")

    # Skip conditions:
    # 1) Already recorded in processed list
    # 2) OR all outputs already exist (txt, docx, pdf)
    already_converted = os.path.exists(txt_path) and os.path.exists(docx_path) and os.path.exists(pdf_path)
    if full_path in processed or already_converted:
        print(f"⏩ Skip {filename} (already processed or outputs exist)")
        continue

    try:
        if not os.path.exists(full_path):
            print(f"⚠️ File not found: {full_path}")
            log_write(LOG_ERROR, f"{datetime.now()} | ERROR | {full_path} | File not found")
            continue

        print(f"\n🔄 [RUNNING] {filename}")
        print(f"⏱️  Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        start_time = time.time()

        # Whisper decode params
        transcribe_kwargs = {
            "language": args.lang,
            "fp16": use_fp16,                # GPU => True, CPU => False (avoid FP16 warning)
            "temperature": args.temperature, # 0.0 => greedy
            "verbose": args.verbose
        }

        result = model.transcribe(full_path, **transcribe_kwargs)
        text = (result.get("text") or "").strip()

        # Save outputs (will overwrite partial/old outputs if any)
        save_txt(text, txt_path)
        save_docx(text, docx_path)
        save_pdf(text, pdf_path, pdf_font=PDF_FONT)

        duration = time.time() - start_time
        print(f"✅ [DONE] {filename} in {duration:.2f} seconds")
        print(f"🕒 End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        log_write(LOG_SUCCESS, f"{datetime.now()} | SUCCESS | {full_path} | {duration:.2f} sec")
        # Mark as processed
        log_write(PROCESSED_LIST, full_path)

    except Exception as e:
        log_write(LOG_ERROR, f"{datetime.now()} | ERROR | {full_path} | {str(e)}")
        print(f"❌ [ERROR] {filename}: {e}")
