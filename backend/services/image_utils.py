
import io

import cv2
import numpy as np
from PIL import Image, UnidentifiedImageError


ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}


def load_image(uploaded_file):
    """Đọc ảnh tải lên và chuyển thành ảnh BGR của OpenCV."""
    if uploaded_file is None:
        raise ValueError("Vui lòng chọn ảnh.")

    filename = getattr(uploaded_file, "name", "")
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Chỉ hỗ trợ ảnh JPG, JPEG hoặc PNG.")

    try:
        image_bytes = uploaded_file.getvalue()

        with Image.open(io.BytesIO(image_bytes)) as pil_image:
            pil_image.verify()

        with Image.open(io.BytesIO(image_bytes)) as pil_image:
            rgb_image = np.array(pil_image.convert("RGB"))

    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ValueError("Không thể đọc ảnh. Vui lòng chọn tệp ảnh hợp lệ.") from exc

    if rgb_image.size == 0:
        raise ValueError("Ảnh đầu vào rỗng.")

    return cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)


def image_to_rgb(image):
    """Chuyển ảnh BGR hoặc ảnh xám sang RGB để hiển thị trên Streamlit."""
    if image is None or not isinstance(image, np.ndarray) or image.size == 0:
        raise ValueError("Ảnh đầu vào không hợp lệ.")

    if image.ndim == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

    if image.ndim == 3 and image.shape[2] == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    raise ValueError("Định dạng ảnh không được hỗ trợ.")


def encode_image(image, image_format="PNG"):
    """Mã hóa ảnh thành bytes để ứng dụng có thể tải xuống."""
    if image is None or not isinstance(image, np.ndarray) or image.size == 0:
        raise ValueError("Ảnh đầu vào không hợp lệ.")

    image_format = image_format.upper()
    if image_format not in {"PNG", "JPEG", "JPG"}:
        raise ValueError("Chỉ hỗ trợ xuất ảnh PNG hoặc JPG.")

    if image.ndim == 2:
        output_image = Image.fromarray(image)
    elif image.ndim == 3 and image.shape[2] == 3:
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        output_image = Image.fromarray(rgb_image)
    else:
        raise ValueError("Định dạng ảnh không được hỗ trợ.")

    if image_format == "JPG":
        image_format = "JPEG"

    buffer = io.BytesIO()
    output_image.save(buffer, format=image_format)
    return buffer.getvalue()
