
import cv2
import numpy as np


def median_filter(image, kernel_size=3):
    """
    Lọc nhiễu muối tiêu bằng Median Filter.
    Nhận ảnh NumPy và trả về ảnh sau xử lý.
    """
    if image is None or not isinstance(image, np.ndarray) or image.size == 0:
        raise ValueError("Ảnh đầu vào không hợp lệ.")

    if not isinstance(kernel_size, int) or kernel_size < 3 or kernel_size % 2 == 0:
        raise ValueError("Kernel phải là số lẻ và lớn hơn hoặc bằng 3.")

    return cv2.medianBlur(image, kernel_size)


def gaussian_filter(image, kernel_size=3, sigma=0):
    """
    Làm mượt ảnh và hỗ trợ giảm nhiễu Gaussian.
    Nhận ảnh NumPy và trả về ảnh sau xử lý.
    """
    if image is None or not isinstance(image, np.ndarray) or image.size == 0:
        raise ValueError("Ảnh đầu vào không hợp lệ.")

    if not isinstance(kernel_size, int) or kernel_size < 3 or kernel_size % 2 == 0:
        raise ValueError("Kernel phải là số lẻ và lớn hơn hoặc bằng 3.")

    if not isinstance(sigma, (int, float)) or sigma < 0:
        raise ValueError("Sigma phải là số không âm.")

    return cv2.GaussianBlur(
        image,
        (kernel_size, kernel_size),
        sigmaX=sigma
    )
