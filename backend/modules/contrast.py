
import cv2
import numpy as np


def _validate_gray_image(gray_img):
    """Kiểm tra ảnh đầu vào có phải ảnh xám uint8 hợp lệ không."""
    if (
        gray_img is None
        or not isinstance(gray_img, np.ndarray)
        or gray_img.size == 0
    ):
        raise ValueError("Ảnh đầu vào không hợp lệ.")

    if gray_img.ndim != 2 or gray_img.dtype != np.uint8:
        raise ValueError("Đầu vào phải là ảnh xám uint8.")


def contrast_stretching(gray_img):
    """Kéo giãn độ tương phản của ảnh xám."""
    _validate_gray_image(gray_img)

    r_min = float(np.min(gray_img))
    r_max = float(np.max(gray_img))

    if r_max == r_min:
        return gray_img.copy()

    stretched = (gray_img.astype(np.float32) - r_min) * (
        255.0 / (r_max - r_min)
    )

    return np.clip(stretched, 0, 255).astype(np.uint8)


def histogram_equalization(gray_img):
    """Cân bằng histogram của ảnh xám."""
    _validate_gray_image(gray_img)
    return cv2.equalizeHist(gray_img)


def binarization(gray_img, thresh_val=127):
    """Nhị phân hóa ảnh xám theo ngưỡng cho trước."""
    _validate_gray_image(gray_img)

    if (
        not isinstance(thresh_val, (int, np.integer))
        or not 0 <= thresh_val <= 255
    ):
        raise ValueError("Ngưỡng phải là số nguyên từ 0 đến 255.")

    _, binary_img = cv2.threshold(
        gray_img, int(thresh_val), 255, cv2.THRESH_BINARY
    )

    return binary_img
