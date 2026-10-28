import json
import os
import cv2
import numpy as np
from fastapi import HTTPException, UploadFile

MAX_BYTES = int(os.getenv("MAX_IMAGE_BYTES", str(10 * 1024 * 1024)))
MAX_PIXELS = int(os.getenv("MAX_IMAGE_PIXELS", "20000000"))
SUPPORTED_TYPES = {"image/jpeg", "image/png", "image/jpg", "application/octet-stream"}
OPERATIONS = {"median", "gaussian", "contrast_stretch", "hist_equalize", "threshold", "erosion", "dilation", "opening", "closing"}
MORPH = {"erosion", "dilation", "opening", "closing"}

async def read_image(file: UploadFile) -> np.ndarray:
    if file.content_type not in SUPPORTED_TYPES:
        raise HTTPException(status_code=415, detail="Chỉ hỗ trợ ảnh JPG/PNG.")
    raw = await file.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="Ảnh vượt giới hạn 10 MB (mặc định).")
    if not raw:
        raise HTTPException(status_code=400, detail="File ảnh trống.")
    if not (raw.startswith(b'\x89PNG\r\n\x1a\n') or raw.startswith(b'\xff\xd8\xff')):
        raise HTTPException(status_code=415, detail="Nội dung file không phải PNG/JPEG.")
    # Read dimensions from headers before decompression (defense against oversized images).
    if raw.startswith(b'\x89PNG') and len(raw) >= 24:
        w, h = int.from_bytes(raw[16:20], 'big'), int.from_bytes(raw[20:24], 'big')
        if w * h > MAX_PIXELS:
            raise HTTPException(status_code=413, detail="Ảnh có quá nhiều pixel.")
    image = cv2.imdecode(np.frombuffer(raw, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None or image.size == 0:
        raise HTTPException(status_code=400, detail="Không đọc được dữ liệu ảnh.")
    if image.shape[0] * image.shape[1] > MAX_PIXELS:
        raise HTTPException(status_code=413, detail="Ảnh có quá nhiều pixel.")
    return image

def parse_steps(value: str) -> list[dict]:
    try:
        steps = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        raise HTTPException(status_code=400, detail="steps phải là chuỗi JSON hợp lệ.")
    if not isinstance(steps, list) or len(steps) > 20:
        raise HTTPException(status_code=400, detail="steps phải là mảng tối đa 20 bước.")
    for i, step in enumerate(steps):
        if not isinstance(step, dict) or step.get("operation") not in OPERATIONS:
            raise HTTPException(status_code=400, detail=f"Bước {i+1}: operation không hợp lệ.")
        params = step.get("params", {})
        if not isinstance(params, dict):
            raise HTTPException(status_code=400, detail=f"Bước {i+1}: params phải là object.")
        op = step["operation"]
        if op in MORPH | {"median", "gaussian"}:
            k = params.get("kernel_size", 3)
            if isinstance(k, bool) or not isinstance(k, int) or k < 1 or k > 31 or k % 2 == 0 or (op in {"median", "gaussian"} and k < 3):
                raise HTTPException(status_code=400, detail=f"Bước {i+1}: kernel_size phải lẻ, trong khoảng {3 if op in {'median','gaussian'} else 1}–31.")
        if op in MORPH:
            if params.get("shape", "rect") not in {"rect", "ellipse", "cross"}:
                raise HTTPException(status_code=400, detail=f"Bước {i+1}: shape phải là rect/ellipse/cross.")
            it = params.get("iterations", 1)
            if isinstance(it, bool) or not isinstance(it, int) or not (1 <= it <= 10):
                raise HTTPException(status_code=400, detail=f"Bước {i+1}: iterations phải là số nguyên từ 1 đến 10.")
        if op == "threshold":
            v = params.get("threshold", 127)
            if isinstance(v, bool) or not isinstance(v, int) or not 0 <= v <= 255:
                raise HTTPException(status_code=400, detail=f"Bước {i+1}: threshold phải từ 0 đến 255.")
            if not isinstance(params.get("invert", False), bool):
                raise HTTPException(status_code=400, detail=f"Bước {i+1}: invert phải là boolean.")
        if op == "gaussian":
            sigma = params.get("sigma", 0)
            if isinstance(sigma, bool) or not isinstance(sigma, (int, float)) or not 0 <= sigma <= 100:
                raise HTTPException(status_code=400, detail=f"Bước {i+1}: sigma không hợp lệ.")
    return steps

def process_via_an(image: np.ndarray, steps: list[dict]) -> np.ndarray:
    from processing.pipeline import process_image
    try:
        result = process_image(image, steps)
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e)) from e
    except (ValueError, TypeError, cv2.error) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    if not isinstance(result, np.ndarray) or result.dtype != np.uint8 or result.ndim not in (2, 3):
        raise HTTPException(status_code=500, detail="Module xử lý ảnh trả về dữ liệu không hợp lệ.")
    if result.ndim == 3 and result.shape[2] not in (3, 4):
        raise HTTPException(status_code=500, detail="Số kênh ảnh trả về không được hỗ trợ.")
    if result.size == 0:
        raise HTTPException(status_code=500, detail="Ảnh kết quả rỗng.")
    return result

def encode_png(image: np.ndarray) -> bytes:
    ok, data = cv2.imencode('.png', image)
    if not ok:
        raise HTTPException(status_code=500, detail="Không thể mã hóa PNG.")
    return data.tobytes()
