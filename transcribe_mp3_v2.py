#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
transcribe_mp3_v2.py

Improvements vs v1:
- Auto-create log folder/files if missing
- Skip files already processed (processed_files.txt)
- Skip if all outputs (.txt/.docx/.pdf) already exist
- Robust logging with timestamps
- Fallback PDF font if Arial not available
- CLI args: --root, --model, --lang, --ext, --device
- Normalized absolute paths for reliability
"""

import os
import sys
import time
import argparse
from datetime import datetime
import shutil

# 3rd-party
try:
    import whisper
except Exception as e:
    print("❌ Missing dependency: whisper (pip install -U openai-whisper) —", e)
    sys.exit(1)

try:
    from docx import Document
except Exception as e:
    print("❌ Missing dependency: python-docx (pip install python-docx) —", e)
    sys.exit(1)

try:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
except Exception as e:
    print("❌ Missing dependency: reportlab (pip install reportlab) —", e)
    sys.exit(1)


# =========================
# Helpers
# =========================
def ensure_parent_dir(path: str) -> None:
    """Ensure parent directory exists for a file path."""
    parent = os.path.dirname(os.path.abspath(path))
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)


def safe_log_append(file_path: str, message: str) -> None:
    """Append a message to log file, creating parent dir if needed."""
    ensure_parent_dir(file_path)
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(message + "\n")


def load_processed_set(processed_list_file: str) -> set:
    """Load processed file paths (as absolute paths) into a set."""
    if os.path.exists(processed_list_file):
        with open(processed_list_file, "r", encoding="utf-8") as f:
            lines = [ln.strip() for ln in f.read().splitlines() if ln.strip()]
        return set(lines)
    return set()


def register_pdf_font() -> str:
    """
    Try to register Arial; if not found, fall back to Helvetica (built-in).
    Returns the font name to use.
    """
    try:
        # common locations for Arial on Windows; or local working dir
        candidates = [
            "arial.ttf",
            r"C:\Windows\Fonts\arial.ttf",
            r"/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",
            r"/usr/share/fonts/truetype/msttcorefonts/arial.ttf",
        ]
        for c in candidates:
            if os.path.exists(c):
                pdfmetrics.registerFont(TTFont("Arial", c))
                return "Arial"
        # try register anyway in current dir (in case user drops file alongside script)
        if os.path.exists("arial.ttf"):
            pdfmetrics.registerFont(TTFont("Arial", "arial.ttf"))
            return "Arial"
    except Exception:
        pass
    # Fallback
    return "Helvetica"


def save_txt(text: str, path: str) -> None:
    ensure_parent_dir(path)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def save_docx(text: str, path: str) -> None:
    ensure_parent_dir(path)
    doc = Document()
    doc.add_paragraph(text)
    doc.save(path)


def save_pdf(text: str, path: str, font_name: str = "Helvetica") -> None:
    ensure_parent_dir(path)
    styles = getSampleStyleSheet()
    # alignment=4 means justify in reportlab
    styles.add(ParagraphStyle(name='Justify', alignment=4,
                              fontName=font_name, fontSize=12, leading=18))

    doc = SimpleDocTemplate(
        path, pagesize=A4,
        rightMargin=30, leftMargin=30,
        topMargin=30, bottomMargin=18
    )

    story = []
    for paragraph in text.strip().split("\n\n"):
        story.append(Paragraph(paragraph.strip().replace("\n", " "), styles['Justify']))
        story.append(Spacer(1, 10 * mm))

    doc.build(story)


def human_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def ensure_ffmpeg(ffmpeg_path: str | None):
    # Nếu sẵn trong PATH thì thôi
    if shutil.which("ffmpeg"):
        return
    # Nếu truyền --ffmpeg và file tồn tại: thêm vào PATH tạm thời cho tiến trình này
    if ffmpeg_path and os.path.isfile(ffmpeg_path):
        os.environ["PATH"] = os.pathsep.join([os.path.dirname(ffmpeg_path), os.environ.get("PATH", "")])
    # Kiểm tra lại
    if not shutil.which("ffmpeg"):
        raise RuntimeError(
            "FFmpeg not found. Install FFmpeg or pass --ffmpeg <path-to-ffmpeg.exe> "
            "E.g. --ffmpeg .\\apps\\ffmpeg\\bin\\ffmpeg.exe"
        )

# =========================
# Core
# =========================
def transcribe_folder(
    root_folder: str,
    model_name: str,
    language: str,
    exts: list,
    device: str,
    log_success: str,
    log_error: str,
    processed_list: str,
) -> None:
    # Normalize
    root_folder = os.path.abspath(root_folder)
    log_success_abs = os.path.abspath(log_success)
    log_error_abs = os.path.abspath(log_error)
    processed_list_abs = os.path.abspath(processed_list)

    # Ensure log folder exists
    for path in [log_success_abs, log_error_abs, processed_list_abs]:
        ensure_parent_dir(path)

    # Load processed set
    processed = load_processed_set(processed_list_abs)

    # Load Whisper model
    print(f"🎙️  Loading Whisper model: {model_name} (device={device})")
    model = whisper.load_model(model_name, device=device)

    # Register PDF font
    font_name = register_pdf_font()
    if font_name == "Helvetica":
        print("ℹ️  Arial not found. Using built-in 'Helvetica' for PDF.")
    else:
        print("✅ Registered PDF font:", font_name)

    # Walk files
    total = 0
    skipped_processed = 0
    skipped_existing = 0
    succeeded = 0
    failed = 0

    print(f"📁 Root: {root_folder}")
    for dirpath, _, filenames in os.walk(root_folder):
        for filename in filenames:
            if not any(filename.lower().endswith(ext.lower()) for ext in exts):
                continue

            total += 1
            full_path = os.path.abspath(os.path.join(dirpath, filename))
            base_name, _ = os.path.splitext(filename)

            # Skip if already processed before
            if full_path in processed:
                print(f"[SKIP • processed] {filename}")
                skipped_processed += 1
                continue

            # Expected outputs
            txt_path = os.path.join(dirpath, base_name + ".txt")
            docx_path = os.path.join(dirpath, base_name + ".docx")
            pdf_path = os.path.join(dirpath, base_name + ".pdf")

            # Skip if outputs already exist
            if all(os.path.exists(p) for p in [txt_path, docx_path, pdf_path]):
                print(f"[SKIP • existing outputs] {filename}")
                # Mark as processed to avoid rework next time
                safe_log_append(processed_list_abs, full_path)
                processed.add(full_path)
                skipped_existing += 1
                continue

            # Transcribe
            try:
                print(f"\n🔄 [RUNNING] {filename}")
                print(f"⏱️  Start time: {human_time()}")
                start = time.time()

                # language hint (e.g., "vi") can speed up or improve quality for target language
                result = model.transcribe(full_path, language=language)
                text = (result.get("text") or "").strip()

                # Save outputs
                save_txt(text, txt_path)
                save_docx(text, docx_path)
                save_pdf(text, pdf_path, font_name=font_name)

                duration = time.time() - start
                print(f"✅ [DONE] {filename} in {duration:.2f} seconds")
                print(f"🕒 End time: {human_time()}\n")

                # Logs
                safe_log_append(log_success_abs, f"{datetime.now()} | SUCCESS | {full_path} | {duration:.2f} sec")
                safe_log_append(processed_list_abs, full_path)
                processed.add(full_path)
                succeeded += 1
            except Exception as e:
                err = f"{datetime.now()} | ERROR | {full_path} | {str(e)}"
                safe_log_append(log_error_abs, err)
                print(f"❌ [ERROR] {filename}: {e}")
                failed += 1

    print("\n===== SUMMARY =====")
    print(f"Total audio files found: {total}")
    print(f"Skipped (processed):     {skipped_processed}")
    print(f"Skipped (existing out):  {skipped_existing}")
    print(f"Succeeded:               {succeeded}")
    print(f"Failed:                  {failed}")
    print("====================")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Batch transcribe audio files in a folder to TXT/DOCX/PDF.")
    parser.add_argument("--root", type=str, default="../mp3-test",
                        help="Root folder to scan for audio files (default: ../mp3-test)")
    parser.add_argument("--model", type=str, default="large",
                        help="Whisper model name (tiny|base|small|medium|large|large-v3...) (default: large)")
    parser.add_argument("--lang", type=str, default="vi",
                        help="Language hint (e.g., vi, en) (default: vi)")
    parser.add_argument("--ext", type=str, default=".mp3",
                        help="Comma-separated list of extensions (e.g., .mp3,.m4a,.wav) (default: .mp3)")
    parser.add_argument("--device", type=str, default="cpu",
                        help="Device for inference (cpu or cuda) (default: cpu)")
    parser.add_argument("--log_success", type=str, default="log/log_success.txt",
                        help="Path to success log file (default: log/log_success.txt)")
    parser.add_argument("--log_error", type=str, default="log/log_error.txt",
                        help="Path to error log file (default: log/log_error.txt)")
    parser.add_argument("--processed_list", type=str, default="log/processed_files.txt",
                        help="Path to processed list file (default: log/processed_files.txt)")
    parser.add_argument("--ffmpeg", type=str, default="", help="Path to ffmpeg.exe (optional)")

    return parser.parse_args()


def main():
    args = parse_args()
    exts = [e.strip() for e in args.ext.split(",") if e.strip()]
    ensure_ffmpeg(args.ffmpeg or None)
    transcribe_folder(
        root_folder=args.root,
        model_name=args.model,
        language=args.lang,
        exts=exts,
        device=args.device,
        log_success=args.log_success,
        log_error=args.log_error,
        processed_list=args.processed_list,
    )


if __name__ == "__main__":
    main()
