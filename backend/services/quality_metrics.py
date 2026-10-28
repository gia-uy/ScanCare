
import time

import cv2
import numpy as np


def calculate_metrics(image):
    """Tính các chỉ số cơ bản trên ảnh xám."""
    if (
        image is None
        or not isinstance(image, np.ndarray)
        or image.size == 0
    ):
        raise ValueError("Ảnh đầu vào không hợp lệ.")

    if image.dtype != np.uint8 or image.ndim not in (2, 3):
        raise ValueError("Ảnh phải có kiểu uint8 và là ảnh xám hoặc BGR.")

    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    return {
        "mean_brightness": float(np.mean(gray)),
        "contrast_std": float(np.std(gray)),
        "laplacian_variance": float(
            cv2.Laplacian(gray, cv2.CV_64F).var()
        ),
    }


def measure_processing_time(process_function, *args, **kwargs):
    """Đo thời gian chạy của một hàm xử lý ảnh."""
    start = time.perf_counter()
    result = process_function(*args, **kwargs)
    elapsed = time.perf_counter() - start

    return result, elapsed
