# ScanCare

ScanCare gồm giao diện Streamlit ở `frontend` và API xử lý ảnh FastAPI ở
`backend`. Frontend gửi ảnh và các tùy chọn xử lý tới backend qua
`http://127.0.0.1:8000/api`.

Xem [Hướng dẫn sử dụng](HUONG_DAN_SU_DUNG.md) để biết khi nào nên dùng
Median, Gaussian, tăng tương phản, nhị phân hóa, Opening và Closing.

## Chạy ứng dụng trên Windows

Mở hai terminal tại thư mục `app`.

Terminal 1 — chạy API:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Terminal 2 — chạy giao diện:

```powershell
cd frontend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Mở địa chỉ Streamlit hiển thị trong terminal (mặc định
`http://localhost:8501`). Có thể kiểm tra backend tại
`http://127.0.0.1:8000/health` và xem tài liệu API tại
`http://127.0.0.1:8000/docs`.

Frontend mặc định gọi API ở `http://127.0.0.1:8000/api`. Nếu backend chạy
ở địa chỉ khác, đặt biến môi trường `API_URL` trước khi khởi động frontend,
ví dụ:

```powershell
$env:API_URL = "http://127.0.0.1:8000/api"
```

## Quy trình xử lý

Khi bật nhị phân hóa trên giao diện, backend thực hiện nhị phân hóa với
ngưỡng 140, sau đó chạy Opening rồi Closing, mỗi phép dùng kernel 3×3.
Khi tắt nhị phân hóa, hai phép hình thái học cũng được bỏ qua. Các bước đã
chạy được trả về trong metadata `X-Processing-Metadata`.

## Kiểm thử backend

```powershell
cd backend
python -m pytest tests/test_spec.py -q
```
