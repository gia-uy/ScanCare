
import cv2
import numpy as np

from modules.filtering import median_filter
from enhancements.background import correct_background


def analyze_document(image):
    """
    Phân tích độ sáng và sự không đồng đều giữa
    các vùng trong 80% trung tâm ảnh.
    """
    gray = (
        cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if image.ndim == 3
        else image
    )

    h, w = gray.shape

    # Lấy vùng trung tâm 80%
    new_h = max(1, int(h * 0.8))
    new_w = max(1, int(w * 0.8))

    y = (h - new_h) // 2
    x = (w - new_w) // 2

    region = gray[y:y + new_h, x:x + new_w]

    brightness = float(np.mean(region))

    # Chia thành lưới 4x4
    regional_values = []

    for row in np.array_split(region, 4, axis=0):
        for cell in np.array_split(row, 4, axis=1):
            regional_values.append(
                float(np.percentile(cell, 80))
            )

    illumination_range = (
        max(regional_values) - min(regional_values)
    )

    return {
        "brightness_80": round(brightness, 2),
        "illumination_80": round(illumination_range, 2),
    }


def choose_method(analysis):
    """
    Quy tắc thử nghiệm từ bộ 5 ảnh scan.

    A: Chỉ dùng Median.
    B: Median + Background Correction.
    """
    brightness = analysis["brightness_80"]
    illumination = analysis["illumination_80"]

    if brightness >= 190 and illumination <= 35:
        return "A"

    return "B"


def smart_enhance(image):
    """
    Tự động chọn phương án xử lý ảnh scan.

    Trả về:
        processed: ảnh kết quả
        metadata: thông tin phân tích và xử lý
    """
    if image is None or image.dtype != np.uint8:
        raise ValueError("Ảnh đầu vào phải là uint8.")

    if image.ndim == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    elif image.ndim == 2:
        gray = image.copy()
    else:
        raise ValueError("Ảnh phải là grayscale hoặc BGR.")

    analysis = analyze_document(gray)
    decision = choose_method(analysis)

    # Dùng thuật toán Median của An

    if decision == "A":
        # Ảnh đã tương đối sáng và đều:
        # không lọc để bảo toàn nét chữ.
        processed = gray.copy()

        steps = [
            {"method": "keep_original"}
        ]

    else:
        # Chỉ hiệu chỉnh nền, không mặc định Median.
        processed = correct_background(
            gray,
            kernel_size=51,
            scale=255
        )

        steps = [
            {
                "method": "background_correction",
                "kernel_size": 51,
                "scale": 255
            }
        ]

    metadata = {
        "decision": decision,
        "analysis": analysis,
        "steps": steps,
        "policy": "diep_smart_enhance_experimental"
    }

    return processed, metadata
