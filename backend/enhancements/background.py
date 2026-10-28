
import cv2
import numpy as np


def correct_background(image, kernel_size=51, scale=255):
    """
    Hiệu chỉnh nền tài liệu bằng Gaussian Background Correction.

    image: ảnh grayscale uint8
    kernel_size: kích thước Gaussian kernel (số lẻ)
    scale: hệ số chuẩn hóa mức sáng

    Trả về: ảnh grayscale đã hiệu chỉnh nền.
    """

    if image is None or image.ndim != 2:
        raise ValueError("Đầu vào phải là ảnh grayscale.")

    if image.dtype != np.uint8:
        raise ValueError("Ảnh phải có kiểu uint8.")

    if kernel_size < 3 or kernel_size % 2 == 0:
        raise ValueError("kernel_size phải là số lẻ >= 3.")

    background = cv2.GaussianBlur(
        image,
        (kernel_size, kernel_size),
        0
    )

    corrected = cv2.divide(
        image,
        background,
        scale=scale
    )

    return corrected
