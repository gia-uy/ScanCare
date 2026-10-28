from io import BytesIO
from PIL import Image
import cv2
import numpy as np

def images_to_pdf(images: list[np.ndarray]) -> bytes:
    pages = []
    for arr in images:
        if arr.ndim == 2:
            pil = Image.fromarray(arr, mode="L").convert("RGB")
        elif arr.shape[2] == 4:
            pil = Image.fromarray(cv2.cvtColor(arr, cv2.COLOR_BGRA2RGB))
        else:
            pil = Image.fromarray(cv2.cvtColor(arr, cv2.COLOR_BGR2RGB))
        pages.append(pil)
    output = BytesIO()
    pages[0].save(output, format="PDF", save_all=True, append_images=pages[1:], resolution=150.0)
    return output.getvalue()
