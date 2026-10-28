
import cv2
import numpy as np

from modules.filtering import median_filter, gaussian_filter
from modules.contrast import (
    contrast_stretching,
    histogram_equalization,
    binarization,
)
from modules.morphology import apply_morphology


def process_image(image, steps):
    """Xử lý ảnh theo danh sách các bước được cung cấp."""
    if (
        image is None
        or not isinstance(image, np.ndarray)
        or image.size == 0
    ):
        raise ValueError("Ảnh đầu vào không hợp lệ.")

    result = image.copy()

    for step in steps:
        method = step.get("method")

        if method in {
            "contrast_stretching",
            "histogram_equalization",
            "binarization",
        }:
            gray = (
                cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
                if result.ndim == 3
                else result
            )

            if method == "contrast_stretching":
                result = contrast_stretching(gray)
            elif method == "histogram_equalization":
                result = histogram_equalization(gray)
            else:
                result = binarization(
                    gray, step.get("threshold", 127)
                )

        elif method == "median_filter":
            result = median_filter(
                result, step.get("kernel_size", 3)
            )

        elif method == "gaussian_filter":
            result = gaussian_filter(
                result,
                step.get("kernel_size", 3),
                step.get("sigma", 0),
            )

        elif method in {
            "erosion", "dilation", "opening", "closing"
        }:
            result = apply_morphology(
                result,
                method=method,
                kernel_size=step.get("kernel_size", 3),
                shape=step.get("shape", "rect"),
                threshold=step.get("threshold", 127),
                iterations=step.get("iterations", 1),
            )

        else:
            raise ValueError(
                f"Thuật toán không hợp lệ: {method}"
            )

    return result
