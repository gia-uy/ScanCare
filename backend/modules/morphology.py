
import cv2
import numpy as np


SHAPES = {
    "rect": cv2.MORPH_RECT,
    "ellipse": cv2.MORPH_ELLIPSE,
    "cross": cv2.MORPH_CROSS,
}

METHODS = {"erosion", "dilation", "opening", "closing"}


def apply_morphology(
    image,
    method,
    kernel_size=3,
    shape="rect",
    threshold=127,
    iterations=1,
):
    """Áp dụng phép hình thái học lên ảnh và trả về ảnh nhị phân."""
    if (
        image is None
        or not isinstance(image, np.ndarray)
        or image.size == 0
    ):
        raise ValueError("Ảnh đầu vào không hợp lệ.")

    if image.dtype != np.uint8 or image.ndim not in (2, 3):
        raise ValueError("Ảnh phải có kiểu uint8 và là ảnh xám hoặc BGR.")

    if method not in METHODS:
        raise ValueError(f"Phương pháp hình thái học không hợp lệ: {method}")

    if (
        not isinstance(kernel_size, int)
        or kernel_size < 1
        or kernel_size % 2 == 0
    ):
        raise ValueError("Kernel phải là số lẻ và lớn hơn hoặc bằng 1.")

    if shape not in SHAPES:
        raise ValueError(f"Hình dạng kernel không hợp lệ: {shape}")

    if not isinstance(threshold, (int, np.integer)) or not 0 <= threshold <= 255:
        raise ValueError("Ngưỡng phải là số nguyên từ 0 đến 255.")

    if not isinstance(iterations, int) or iterations < 1:
        raise ValueError("Số lần lặp phải là số nguyên lớn hơn hoặc bằng 1.")

    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    _, binary = cv2.threshold(
        gray, int(threshold), 255, cv2.THRESH_BINARY_INV
    )

    kernel = cv2.getStructuringElement(
        SHAPES[shape], (kernel_size, kernel_size)
    )

    if method == "erosion":
        result = cv2.erode(binary, kernel, iterations=iterations)
    elif method == "dilation":
        result = cv2.dilate(binary, kernel, iterations=iterations)
    elif method == "opening":
        result = cv2.morphologyEx(
            binary, cv2.MORPH_OPEN, kernel, iterations=iterations
        )
    else:
        result = cv2.morphologyEx(
            binary, cv2.MORPH_CLOSE, kernel, iterations=iterations
        )

    return cv2.bitwise_not(result)


def erosion(image, kernel_size=3, shape="rect", threshold=127, iterations=1):
    return apply_morphology(
        image, "erosion", kernel_size, shape, threshold, iterations
    )


def dilation(image, kernel_size=3, shape="rect", threshold=127, iterations=1):
    return apply_morphology(
        image, "dilation", kernel_size, shape, threshold, iterations
    )


def opening(image, kernel_size=3, shape="rect", threshold=127, iterations=1):
    return apply_morphology(
        image, "opening", kernel_size, shape, threshold, iterations
    )


def closing(image, kernel_size=3, shape="rect", threshold=127, iterations=1):
    return apply_morphology(
        image, "closing", kernel_size, shape, threshold, iterations
    )
