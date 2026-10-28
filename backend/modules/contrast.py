
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


def adaptive_binarization(gray_img, block_size=35, c=10):
    """Nhị phân hóa theo vùng cục bộ để xử lý nền sáng không đồng đều."""
    _validate_gray_image(gray_img)

    if (
        not isinstance(block_size, int)
        or block_size < 3
        or block_size % 2 == 0
    ):
        raise ValueError("Block size phải là số lẻ và lớn hơn hoặc bằng 3.")

    if not isinstance(c, (int, float)) or not np.isfinite(c):
        raise ValueError("C phải là một số hữu hạn.")

    height, width = gray_img.shape
    max_block_size = min(height, width)
    if max_block_size % 2 == 0:
        max_block_size -= 1
    if max_block_size < 3:
        raise ValueError("Ảnh phải rộng và cao tối thiểu 3 pixel.")

    effective_block_size = min(block_size, max_block_size)
    return cv2.adaptiveThreshold(
        gray_img,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        effective_block_size,
        c,
    )
