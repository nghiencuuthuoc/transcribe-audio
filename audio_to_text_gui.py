import os
import whisper
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.filedialog import askdirectory
from docx import Document
from fpdf import FPDF
from datetime import datetime
import urllib.request
from PIL import Image, ImageTk

# === CONFIG ===
ROOT_FOLDER = "../mp3-test"
LOG_SUCCESS = "log_success.txt"
LOG_ERROR = "log_error.txt"
PROCESSED_LIST = "processed_files.txt"
SUPPORTED_EXT = [".mp3", ".wav", ".m4a", ".flac", ".aac", ".ogg"]
ASSET_FOLDER = "../asset"
LOGO_URL = "https://raw.githubusercontent.com/nghiencuuthuoc/PharmApp/refs/heads/master/images/nct_logo_3000x3000_20250606.png"
LOGO_FILE = os.path.join(ASSET_FOLDER, "nct_logo.png")

# === Ensure asset folder ===
os.makedirs(ASSET_FOLDER, exist_ok=True)

# === Try downloading logo ===
def download_logo():
    try:
        urllib.request.urlretrieve(LOGO_URL, LOGO_FILE)
        return True
    except:
        return False

has_logo = download_logo()

# === Whisper model ===
model = whisper.load_model("medium")

# === Utilities ===
def save_txt(text, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def save_docx(text, path):
    doc = Document()
    doc.add_paragraph(text)
    doc.save(path)

def save_pdf(text, path):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("Arial", "", fname="arial.ttf", uni=True)  # You need Arial.ttf
    pdf.set_font("Arial", size=12)
    for line in text.splitlines():
        pdf.multi_cell(0, 10, line)
    pdf.output(path)

def log_write(file, message):
    with open(file, "a", encoding="utf-8") as f:
        f.write(message + "\n")

def load_processed():
    if os.path.exists(PROCESSED_LIST):
        with open(PROCESSED_LIST, "r", encoding="utf-8") as f:
            return set(f.read().splitlines())
    return set()

def transcribe_folder(folder, progress_label):
    processed = load_processed()
    count = 0
    for dirpath, _, filenames in os.walk(folder):
        for file in filenames:
            if not any(file.lower().endswith(ext) for ext in SUPPORTED_EXT):
                continue
            full_path = os.path.join(dirpath, file)
            base_name = os.path.splitext(file)[0]
            if full_path in processed:
                continue
            try:
                progress_label["text"] = f"Processing: {file}"
                result = model.transcribe(full_path, language="vi")
                text = result["text"].strip()

                txt_path = os.path.join(dirpath, base_name + ".txt")
                docx_path = os.path.join(dirpath, base_name + ".docx")
                pdf_path = os.path.join(dirpath, base_name + ".pdf")

                save_txt(text, txt_path)
                save_docx(text, docx_path)
                save_pdf(text, pdf_path)

                log_write(LOG_SUCCESS, f"{datetime.now()} | SUCCESS | {full_path}")
                log_write(PROCESSED_LIST, full_path)
                count += 1
            except Exception as e:
                log_write(LOG_ERROR, f"{datetime.now()} | ERROR | {full_path} | {str(e)}")
    progress_label["text"] = f"✅ Done. {count} files processed."

# === GUI ===
def start_gui():
    def browse_folder():
        folder = askdirectory()
        if folder:
            folder_var.set(folder)

    def start_processing():
        folder = folder_var.get()
        if not os.path.isdir(folder):
            messagebox.showerror("Error", "Please select a valid folder.")
            return
        threading.Thread(target=transcribe_folder, args=(folder, progress_label), daemon=True).start()

    root = tk.Tk()
    root.title("🧠 PharmApp - Audio to Text")
    root.geometry("680x550")
    root.configure(bg="white")

    # Logo
    if has_logo and os.path.exists(LOGO_FILE):
        img = Image.open(LOGO_FILE)
        img = img.resize((120, 120))
        logo_img = ImageTk.PhotoImage(img)
        logo_label = tk.Label(root, image=logo_img, bg="white")
        logo_label.pack(pady=10)

    title = tk.Label(root, text="🎤 Convert Audio to Text (Tiếng Việt)", font=("Arial", 16, "bold"), bg="white")
    title.pack(pady=10)

    frame = ttk.Frame(root)
    frame.pack(pady=10)

    folder_var = tk.StringVar(value=ROOT_FOLDER)
    folder_entry = ttk.Entry(frame, textvariable=folder_var, width=50)
    folder_entry.pack(side=tk.LEFT, padx=5)

    browse_btn = ttk.Button(frame, text="Browse", command=browse_folder)
    browse_btn.pack(side=tk.LEFT)

    start_btn = ttk.Button(root, text="▶️ Start Transcription", command=start_processing)
    start_btn.pack(pady=15)

    progress_label = tk.Label(root, text="", bg="white", fg="green", font=("Arial", 11))
    progress_label.pack()

    # Footer
    footer = tk.Label(root, text=(
        "| Copyright 2025 |  Nghiên Cứu Thuốc | 🧠 PharmApp |\n"
        "| Discover | Design | Optimize | Create | Deliver |\n"
        "www.nghiencuuthuoc.com | Zalo: +84888999311 | www.pharmapp.vn"
    ), bg="white", font=("Arial", 9), justify="center")
    footer.pack(side=tk.BOTTOM, pady=20)

    root.mainloop()

if __name__ == "__main__":
    start_gui()
