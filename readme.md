# Whisper Audio Transcriber

> A fast, no-nonsense tool to transcribe audio into **.txt**, **.docx**, and **.pdf** (justified, Vietnamese-ready) using **OpenAI Whisper**. Supports batch folders, resume on crash, and optional CUDA acceleration.

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](#)
[![Whisper](https://img.shields.io/badge/ASR-OpenAI%20Whisper-forestgreen)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#)

---

## ✨ Features

- ✅ **Batch transcription** from a folder (skip files already processed, safe to resume).
- 🎧 **Many formats**: `.mp3`, `.m4a`, `.wav`, `.flac`, `.ogg`, `.aac`, `.wma`, `.webm`.
- 📝 **3 outputs** per file: `.txt`, `.docx`, `.pdf` (PDF justified, hỗ trợ tiếng Việt với font kèm theo).
- ⚙️ **Whisper model** (default `large`) with logs for success/errors.
- 🚀 **CUDA ready**: separate scripts for GPU runs available in repo (e.g., `transcribe_audio_cuda.py`, `transcribe_audio_cuda.bat`).
- 🖼️ **Fonts bundled**: `Arial.ttf`, `DejaVuSans.ttf` for clean PDF rendering.

---

## 📦 Installation

```bash
# 1) Create & activate a virtual environment (recommended)
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 2) Install core dependencies
pip install openai-whisper python-docx reportlab
```

> Note: PDF export requires having an accessible TrueType font. This repo includes `Arial.ttf` and `DejaVuSans.ttf`.

---

## 🚀 Quick Start (CPU)

```bash
python transcribe_audio.py -i path\to\your\audio\folder
# Example
python transcribe_audio.py -i ..\mp3-test
```

**What you get per file** (e.g., `lecture1.mp3`):  
- `lecture1.txt` (plain text)  
- `lecture1.docx` (editable)  
- `lecture1.pdf` (print-ready, justified)  

Log files are written alongside outputs:  
- `transcribe_log_success.txt`  
- `transcribe_log_error.txt`  
- `transcribe_processed_files.txt` (used to skip already-done files)

---

## ⚡ GPU / CUDA (Optional)

If you have an NVIDIA GPU + CUDA, use the GPU script/batch:

```bash
# Python script
python transcribe_audio_cuda.py -i path\to\audio\folder
# or the convenience batch file on Windows
transcribe_audio_cuda.bat
```

---

## 🪟 Simple GUI (Optional)

Prefer a minimal UI? Launch:

```bash
python audio_to_text_gui.py
```

Select your folder and run transcription with a click.

---

## 🗂️ Typical Project Layout

```
your_project/
│
├─ transcribe_audio.py
├─ transcribe_audio_cuda.py
├─ audio_to_text_gui.py
├─ fonts/
│   ├─ Arial.ttf
│   └─ DejaVuSans.ttf
├─ ..\mp3-test/
│   ├─ audio1.mp3
│   ├─ audio2.wav
│   └─ ...
└─ (outputs written next to input files)
   ├─ audio1.txt
   ├─ audio1.docx
   ├─ audio1.pdf
   ├─ transcribe_log_success.txt
   ├─ transcribe_log_error.txt
   └─ transcribe_processed_files.txt
```

---

## 🧠 Model Notes

- Default model: `large` (good accuracy across languages, including Vietnamese).
- You can switch to `medium`/`small` for faster inference but less accuracy.

---

## 🔧 Tips & Troubleshooting

- **Slow on CPU?** Try a smaller Whisper model or use CUDA.
- **PDF tofu/□?** Ensure `Arial.ttf` or `DejaVuSans.ttf` is available.
- **Resuming big batches:** The app writes `transcribe_processed_files.txt`; safe to rerun.
- **Colab run:** A `.url` is included for cloud-based usage.

---

## 📜 License

MIT — for research and educational use.

---

## 💬 Contact

Issues and suggestions are welcome.  
Email: **nghiencuuthuoc@gmail.com**

---

# 🇻🇳 Tóm tắt nhanh (Tiếng Việt)

- Công cụ **chuyển giọng nói → văn bản** từ thư mục audio, xuất **TXT/DOCX/PDF** (PDF canh đều, hỗ trợ tiếng Việt).  
- Chạy CPU hoặc **CUDA**; có **GUI** đơn giản; **tự bỏ qua** file đã xử lý, **tiếp tục** được sau khi gián đoạn.  
- Cài đặt: `pip install openai-whisper python-docx reportlab`.  
- Chạy ví dụ:  
  ```bash
  python transcribe_audio.py -i đường_dẫn_thư_mục_audio
  ```
- Font PDF: dùng `Arial.ttf` hoặc `DejaVuSans.ttf` (đã kèm).
