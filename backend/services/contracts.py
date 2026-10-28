import json
from fastapi import HTTPException
from services.image_io import parse_steps

ALIASES = {
    'median': 'median_filter', 'gaussian': 'gaussian_filter',
    'contrast_stretch': 'contrast_stretching',
    'hist_equalize': 'histogram_equalization',
    'threshold': 'binarization',
}

def normalize_steps(raw: str):
    """Nhận operation+params (API v1.1) hoặc method+tham số (An).
    Trả danh sách dạng An: [{'method': 'median_filter','kernel_size': 3}].
    """
    try:
        data = json.loads(raw)
    except (ValueError, TypeError) as exc:
        raise HTTPException(400, 'steps phải là JSON hợp lệ') from exc
    if not isinstance(data, list) or len(data) > 20:
        raise HTTPException(400, 'steps phải là danh sách không quá 20 bước')
    converted = []
    for index, step in enumerate(data):
        if not isinstance(step, dict):
            raise HTTPException(400, f'Bước {index+1} phải là object')
        operation = step.get('operation', step.get('method'))
        params = step.get('params', None)
        if params is None:
            params = {k: v for k, v in step.items() if k not in {'method','operation'}}
        if not isinstance(params, dict):
            raise HTTPException(400, 'params phải là object')
        name = ALIASES.get(operation, operation)
        if name not in {'median_filter','gaussian_filter','contrast_stretching',
                        'histogram_equalization','binarization',
                        'erosion','dilation','opening','closing'}:
            raise HTTPException(400, f'Thuật toán không hỗ trợ: {operation}')
        allowed = {'median_filter': {'kernel_size'}, 'gaussian_filter': {'kernel_size','sigma'},
                   'contrast_stretching': set(), 'histogram_equalization': set(),
                   'binarization': {'threshold'},
                   **{m: {'kernel_size','shape','threshold','iterations'}
                      for m in ('erosion','dilation','opening','closing')}}[name]
        if set(params) - allowed:
            raise HTTPException(400, f'Tham số không hỗ trợ ở bước {index+1}: {sorted(set(params)-allowed)}')
        kernel = params.get('kernel_size',3)
        if name in {'median_filter','gaussian_filter'}:
            if type(kernel) is not int or kernel not in (3,5,7,9,11):
                raise HTTPException(400,'Kernel lọc nhiễu phải là số lẻ 3–11')
        if name in {'erosion','dilation','opening','closing'}:
            if type(kernel) is not int or not 1 <= kernel <= 15:
                raise HTTPException(400,'Kernel morphology phải trong 1–15')
            if params.get('shape','rect') not in {'rect','ellipse','cross'}:
                raise HTTPException(400,'shape không hợp lệ')
            it = params.get('iterations',1)
            if type(it) is not int or not 1 <= it <= 5:
                raise HTTPException(400,'iterations phải từ 1 đến 5')
        if name in {'binarization','erosion','dilation','opening','closing'}:
            th=params.get('threshold',127)
            if type(th) is not int or not 0 <= th <= 255:
                raise HTTPException(400,'threshold phải từ 0 đến 255')
        if name == 'gaussian_filter':
            sigma=params.get('sigma',0)
            if type(sigma) not in (float,int) or not 0 <= sigma <= 30:
                raise HTTPException(400,'sigma không hợp lệ')
        converted.append({'method': name, **params})
    return converted
