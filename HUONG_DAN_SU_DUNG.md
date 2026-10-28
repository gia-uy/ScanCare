# Hướng dẫn sử dụng ScanCare

ScanCare giúp làm sạch ảnh tài liệu bằng các bộ lọc và bước xử lý ảnh. Nên
thử từng tùy chọn trên ảnh của bạn, vì ảnh đầu vào và độ mảnh của chữ ảnh
hưởng đến kết quả.

## 1. Mở ứng dụng

Khởi động backend FastAPI và giao diện Streamlit theo hướng dẫn trong
[README](README.md). Mở địa chỉ Streamlit được hiển thị trong terminal.

## 2. Quy trình cơ bản

1. Tải ảnh JPG, JPEG hoặc PNG lên.
2. Chọn tùy chọn xử lý ở khung bên phải.
3. Nhấn **Nâng cao chất lượng tài liệu**.
4. So sánh ảnh gốc và ảnh kết quả. Mục **Thông tin xử lý** cho biết các
   bước backend đã áp dụng.
5. Nếu muốn thử cài đặt khác, thay đổi tùy chọn rồi nhấn **Nâng cao lại
   chất lượng**. Mỗi lần xử lý đều bắt đầu từ ảnh gốc, không xử lý chồng
   lên kết quả cũ.
6. Nhấn **Tải ảnh kết quả về máy** để lưu ảnh PNG.

## 3. Khi nào nên dùng từng chức năng?

### Tự động hiệu chỉnh nền (Smart Enhance)

- **Nên bật** khi nền giấy không đều sáng, bị xám hoặc có vùng sáng tối
  khác nhau.
- **Có thể tắt** khi ảnh đã rõ, nền đồng đều, hoặc cần giữ ảnh màu.
- Đây là quy tắc tự động thử nghiệm, không phải bộ lọc khử nhiễu. Chức năng
  phân tích ảnh để giữ ảnh tương đối sáng/đều hoặc hiệu chỉnh nền khi cần.
  Kết quả của Smart Enhance là ảnh xám.

### Lọc nhiễu: Median hoặc Gaussian

Chỉ chạy khi bật **Bật lọc nhiễu**. Mỗi lần chọn một phương pháp:

- **Median Filter:** nên thử trước với các chấm đen/trắng nhỏ, bụi hoặc
  nhiễu kiểu muối tiêu. Có thể làm mất nét chữ rất mảnh nếu chọn kernel lớn.
- **Gaussian Filter:** làm mượt ảnh; phù hợp để giảm nhiễu hạt nhẹ, nhưng
  có thể làm chữ và biên ảnh mềm/mờ hơn Median.

Mức lọc chọn kernel:

| Mức | Kernel | Gợi ý |
|---|---:|---|
| Nhẹ | 3×3 | Bắt đầu với mức này để giữ chi tiết chữ. |
| Vừa | 5×5 | Thử khi nhiễu rõ hơn; kiểm tra chữ nhỏ sau xử lý. |
| Mạnh | 7×7 | Dành cho nhiễu nhiều; dễ làm mờ hoặc mất nét mảnh. |

Không nhất thiết phải bật lọc nếu ảnh đã sạch. Nếu chưa chắc, hãy so sánh
kết quả ở mức Nhẹ trước khi tăng kernel.

### Tăng độ tương phản

- **Nên bật** khi chữ nhạt, ảnh xám hoặc độ chênh giữa chữ và nền thấp.
- **Nên tắt** khi chữ đã đậm rõ, ảnh có vùng sáng/tối gắt, hoặc muốn giữ
  màu.
- Tùy chọn hiện tại chuyển ảnh sang grayscale trước khi kéo giãn tương
  phản; vì vậy kết quả sẽ không giữ màu.

### Nhị phân hóa (Đen / Trắng)

- **Nên bật** cho tài liệu chủ yếu là chữ đen trên nền giấy sáng, khi muốn
  loại nền xám và làm chữ nổi bật.
- **Nên tắt** nếu ảnh có con dấu màu, ảnh chụp, hình minh họa hoặc cần giữ
  sắc độ/chi tiết nền.
- Ứng dụng dùng ngưỡng cố định `140` (không phải ngưỡng Otsu). Ảnh quá tối
  hoặc quá sáng có thể cần thử thêm các tùy chọn khác.

Khi bật nhị phân hóa, ứng dụng tự chạy thêm:

1. **Opening 3×3:** giúp loại bỏ các đốm nhỏ; có thể làm mảnh hoặc mất nét
   chữ rất nhỏ.
2. **Closing 3×3:** giúp nối các khe hở nhỏ; có thể làm nét chữ dày hơn.

Opening và Closing chỉ chạy sau nhị phân hóa; không có tùy chọn bật riêng
hai phép này trên giao diện.

## 4. Cấu hình nên thử

### Tài liệu sạch, chỉ cần tăng độ rõ

- Tắt lọc nhiễu.
- Tắt Smart Enhance nếu nền đã đều.
- Bật tăng tương phản nếu chữ nhạt.
- Chỉ bật nhị phân hóa nếu muốn đầu ra đen trắng thuần.

### Nhiều chấm bụi hoặc đốm nhiễu nhỏ

- Bật Median Filter, bắt đầu với kernel 3×3.
- Nếu tài liệu chỉ có chữ đen trắng, thử bật nhị phân hóa để áp dụng thêm
  Opening và Closing.
- Nếu chữ mảnh bị mất, giảm mức lọc hoặc tắt nhị phân hóa.

### Nền giấy loang sáng hoặc bị xám

- Bật Smart Enhance để thử hiệu chỉnh nền tự động.
- Có thể bật tăng tương phản nếu chữ vẫn nhạt.
- Kiểm tra ảnh kết quả; Smart Enhance hiện là heuristic thử nghiệm và có
  thể chuyển ảnh màu thành ảnh xám.

### Tài liệu có con dấu đỏ hoặc nội dung màu

- Tắt Smart Enhance để tránh chuyển ảnh sang xám.
- Tắt tăng tương phản và nhị phân hóa vì các bước này chuyển ảnh thành
  grayscale/đen trắng.
- Nếu muốn giữ màu khi giảm nhiễu, chỉ bật Median hoặc Gaussian Filter và
  kiểm tra ảnh kết quả.

## 5. Lưu ý

- Thứ tự xử lý là: **lọc nhiễu (nếu bật) → Smart Enhance (nếu bật) → tăng
  tương phản (nếu bật) → nhị phân hóa (nếu bật) → Opening → Closing**.
- Không phải lúc nào bật tất cả cũng cho ảnh tốt hơn. Hãy thay đổi từng
  lựa chọn và so sánh trước/sau.
- Nên giữ ảnh gốc riêng nếu đây là tài liệu quan trọng.
