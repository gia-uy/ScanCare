# ScanCare backend

Backend dùng FastAPI để cung cấp API xử lý ảnh cho frontend Streamlit.
Hướng dẫn khởi động cả frontend và backend nằm trong
[README của ứng dụng](../README.md).

Các endpoint chính:

- `GET /health`: kiểm tra trạng thái API.
- `POST /api/enhance-with-options`: xử lý ảnh theo các tùy chọn trên giao diện.
- `POST /api/analyze`: phân tích ảnh.
- `POST /api/process`: chạy pipeline xử lý ảnh.
- `POST /api/export/image` và `POST /api/export/pdf`: xuất kết quả.

Tài liệu tương tác của API có tại `http://127.0.0.1:8000/docs` khi backend
đang chạy.
