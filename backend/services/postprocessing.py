"""Các tùy chọn bổ sung cho ScanCare; tái sử dụng module của An."""
import cv2
import numpy as np
from modules.contrast import contrast_stretching, adaptive_binarization
from modules.morphology import opening, closing


def apply_extra_options(
    image,
    contrast=False,
    binarize=False,
    apply_opening=False,
    apply_closing=False,
):
    """Áp dụng tùy chọn sau Auto/Smart; ảnh uint8 BGR hoặc grayscale."""
    if not contrast and not binarize:
        return image, []

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image.copy()
    if gray.dtype != np.uint8:
        raise ValueError("Yêu cầu ảnh uint8")
    steps = []

    if contrast:
        gray = contrast_stretching(gray)
        steps.append({"method": "contrast_stretching"})

    if binarize:
        block_size = min(35, min(gray.shape))
        if block_size % 2 == 0:
            block_size -= 1
        if block_size < 3:
            raise ValueError("Ảnh phải rộng và cao tối thiểu 3 pixel.")

        gray = adaptive_binarization(gray, block_size=block_size, c=10)
        steps.append({
            "method": "binarization",
            "thresholding": "adaptive_gaussian",
            "block_size": block_size,
            "c": 10,
        })

        if apply_opening:
            gray = opening(gray, kernel_size=3, threshold=127)
            steps.append({
                "method": "opening",
                "kernel_size": 3,
                "threshold": 127,
            })

        if apply_closing:
            gray = closing(gray, kernel_size=3, threshold=127)
            steps.append({
                "method": "closing",
                "kernel_size": 3,
                "threshold": 127,
            })

    return gray, steps
