

# 🎧 Trình Chuyển Âm Thanh Thành Văn Bản Bằng Whisper

Một công cụ dòng lệnh mạnh mẽ giúp **tự động chuyển đổi các tệp âm thanh thành văn bản**, hỗ trợ xuất ra định dạng `.txt`, `.docx`, và `.pdf`, sử dụng mô hình **Whisper** của OpenAI.

## ⚙️ Tính Năng Nổi Bật

* ✅ Hỗ trợ quét thư mục và xử lý hàng loạt tệp âm thanh
* 🎙️ Hỗ trợ nhiều định dạng: `.mp3`, `.m4a`, `.wav`, `.flac`, `.ogg`, `.aac`, `.wma`, `.webm`
* 📄 Xuất ra 3 định dạng:

  * Văn bản thuần (`.txt`)
  * Tài liệu Word (`.docx`)
  * Tệp PDF căn lề đẹp (`.pdf`) hỗ trợ font tiếng Việt
* 🧠 Sử dụng mô hình Whisper (phiên bản `large`) từ OpenAI
* 📝 Ghi log kết quả thành công và lỗi rõ ràng
* 🔁 Bỏ qua các tệp đã xử lý để hỗ trợ chạy lại không trùng lặp

## 📁 Cấu Trúc Thư Mục Mẫu

```
your_project/
│
├── transcribe_audio.py
├── ../mp3-test/
│   ├── bai_1.mp3
│   ├── bai_2.wav
│   └── ...
│
└── Kết quả (lưu cùng thư mục với tệp gốc):
    ├── bai_1.txt
    ├── bai_1.docx
    ├── bai_1.pdf
    ├── transcribe_log_success.txt
    ├── transcribe_log_error.txt
    └── transcribe_processed_files.txt
```

## 🛠️ Yêu Cầu

Cài đặt các thư viện cần thiết:

```bash
pip install -r requirements.txt
```

> **Yêu cầu hệ thống**:
>
> * Python ≥ 3.8
> * Đã cài sẵn `ffmpeg` trong hệ thống
> * Có file `arial.ttf` trong máy để hỗ trợ font tiếng Việt khi xuất PDF

## ▶️ Cách Sử Dụng

Chạy lệnh sau để bắt đầu chuyển giọng nói thành văn bản:

```bash
python transcribe_audio.py -i đường_dẫn_thư_mục_chứa_file_âm_thanh
```

Ví dụ:

```bash
python transcribe_audio.py -i ../mp3-test
```

## 📝 Ghi Nhật Ký

* `transcribe_log_success.txt`: Danh sách tệp đã xử lý thành công
* `transcribe_log_error.txt`: Tệp bị lỗi trong quá trình xử lý
* `transcribe_processed_files.txt`: Lưu tên các tệp đã xử lý để tránh trùng lặp

## ✨ Ví Dụ Kết Quả

Tệp `bai_giang_1.mp3` sau khi xử lý sẽ tạo ra:

* `bai_giang_1.txt`: Nội dung văn bản
* `bai_giang_1.docx`: Tài liệu Word có thể chỉnh sửa
* `bai_giang_1.pdf`: Tệp PDF căn chỉnh chuẩn, dễ in ấn

---

## 📘 Giấy Phép

Phát hành theo giấy phép MIT – Sử dụng cho mục đích nghiên cứu và giáo dục.

## 📬 Liên Hệ

Mọi góp ý hoặc câu hỏi xin gửi về:
📧 [nghiencuuthuoc@gmail.com](mailto:nghiencuuthuoc@gmail.com)
