
import time

import cv2
import numpy as np

from .filtering import median_filter, gaussian_filter
from .contrast import contrast_stretching, histogram_equalization


def auto_enhance(image, level="Trung bình"):
    """
    Cải thiện ảnh tài liệu theo các quy tắc cơ bản.

    Returns:
        result: Ảnh sau xử lý.
        steps: Danh sách các bước đã áp dụng.
        elapsed: Thời gian xử lý (giây).
        analysis: Các chỉ số ảnh dùng để tham khảo.
    """
    if (
        image is None
        or not isinstance(image, np.ndarray)
        or image.size == 0
    ):
        raise ValueError("Ảnh đầu vào không hợp lệ.")

    levels = {
        "Nhẹ": 3,
        "Trung bình": 5,
        "Mạnh": 7,
    }
    if level not in levels:
        raise ValueError("Mức xử lý phải là Nhẹ, Trung bình hoặc Mạnh.")

    start = time.perf_counter()
    result = image.copy()

    gray = (
        cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
        if result.ndim == 3
        else result.copy()
    )

    # Chỉ số tham khảo; không phải bộ nhận diện nhiễu đã được xác thực.
    contrast = float(np.std(gray))
    laplacian_variance = float(cv2.Laplacian(gray, cv2.CV_64F).var())

    steps = []

    # Chỉ áp dụng Gaussian khi ảnh có độ biến thiên cường độ cao.
    # Đây là quy tắc thử nghiệm, cần đánh giá bằng ảnh mẫu.
    if laplacian_variance > 150:
        kernel_size = levels[level]
        result = gaussian_filter(result, kernel_size=kernel_size)
        steps.append({
            "method": "gaussian_filter",
            "kernel_size": kernel_size,
            "sigma": 0,
        })

    gray_result = (
        cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
        if result.ndim == 3
        else result
    )

    # Tăng tương phản khi độ lệch chuẩn của ảnh xám tương đối thấp.
    if float(np.std(gray_result)) < 50:
        result = contrast_stretching(gray_result)
        steps.append({"method": "contrast_stretching"})

    elapsed = time.perf_counter() - start

    analysis = {
        "contrast_std": contrast,
        "laplacian_variance": laplacian_variance,
        "note": (
            "Các chỉ số chỉ mang tính tham khảo; cần kiểm thử trên "
            "ảnh tài liệu thực tế trước khi kết luận về nhiễu."
        ),
    }

    return result, steps, elapsed, analysis
