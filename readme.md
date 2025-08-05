

# 🎧 Whisper Audio Transcriber

A powerful command-line tool to **automatically transcribe audio files** into `.txt`, `.docx`, and `.pdf` formats using OpenAI's Whisper model.

## 🚀 Features

* ✅ Supports batch transcription from folders
* 🎙️ Supports many audio formats: `.mp3`, `.m4a`, `.wav`, `.flac`, `.ogg`, `.aac`, `.wma`, `.webm`
* 📄 Outputs in three formats:

  * Plain text (`.txt`)
  * Word document (`.docx`)
  * Justified PDF (`.pdf`) with Vietnamese font support
* 🧠 Powered by [OpenAI Whisper](https://github.com/openai/whisper) (`large` model by default)
* 📝 Automatically logs success and error cases
* 🔁 Skip already processed files to allow resuming transcription

## 📁 Folder Structure

```
your_project/
│
├── transcribe_audio.py
├── ../mp3-test/
│   ├── audio1.mp3
│   ├── audio2.wav
│   └── ...
│
└── Output (same as input folder):
    ├── audio1.txt
    ├── audio1.docx
    ├── audio1.pdf
    ├── transcribe_log_success.txt
    ├── transcribe_log_error.txt
    └── transcribe_processed_files.txt
```

## 🛠️ Requirements

Install dependencies:

```bash
pip install openai-whisper python-docx reportlab
```

**Note**: You must have a `Arial.ttf` font file in your environment for PDF export.

## ▶️ Usage

```bash
python transcribe_audio.py -i path/to/audio/folder
```

Example:

```bash
python transcribe_audio.py -i ../mp3-test
```

## 📒 Logs

* ✅ `transcribe_log_success.txt`: Success logs with duration
* ❌ `transcribe_log_error.txt`: Errors encountered during transcription
* 📂 `transcribe_processed_files.txt`: List of already processed files

## ✨ Demo Output Example

For a file `lecture1.mp3`, this script will generate:

* `lecture1.txt`: Plain transcript
* `lecture1.docx`: Editable Word document
* `lecture1.pdf`: Printable PDF with clean layout

---

## 🧠 License

MIT License. Developed for educational and research use.

## 📬 Contact

For questions or suggestions, reach out at [📧 nghiencuuthuoc@gmail.com](mailto:nghiencuuthuoc@gmail.com)
