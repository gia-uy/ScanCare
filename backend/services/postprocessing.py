"""Các tùy chọn bổ sung cho ScanCare; tái sử dụng module của An."""
import cv2
import numpy as np
from modules.contrast import contrast_stretching, binarization
from modules.morphology import opening, closing


def apply_extra_options(image, contrast=False, binarize=False):
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
        gray = binarization(gray, thresh_val=140)
        steps.append({"method": "binarization", "threshold": 140})

        gray = opening(gray, kernel_size=3, threshold=140)
        steps.append({
            "method": "opening",
            "kernel_size": 3,
            "threshold": 140,
        })

        gray = closing(gray, kernel_size=3, threshold=140)
        steps.append({
            "method": "closing",
            "kernel_size": 3,
            "threshold": 140,
        })

    return gray, steps
