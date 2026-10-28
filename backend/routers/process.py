import json
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response, JSONResponse
from services.image_io import read_image, process_via_an, encode_png
from services.contracts import normalize_steps
from services.auto_enhance import enhance,analyze
from enhancements.smart_enhance import smart_enhance
from services.postprocessing import apply_extra_options
from services.filter_service import apply_selected_filter

router=APIRouter(prefix='/api',tags=['Process'])

@router.post('/analyze')
async def analyze_upload(file:UploadFile=File(...)):
    image=await read_image(file)
    return {'analysis':analyze(image),'width':int(image.shape[1]),'height':int(image.shape[0])}

@router.post('/auto-enhance')
async def auto_enhance(file:UploadFile=File(...),level:str=Form('vua')):
    image=await read_image(file)
    try:
        out,metadata=enhance(image,level)
    except ValueError as exc:
        raise HTTPException(400,str(exc)) from exc
    # metadata trong header để Streamlit/Frontend đọc; ảnh là PNG thuần.
    return Response(content=encode_png(out),media_type='image/png',
                    headers={'X-Processing-Metadata':json.dumps(metadata,ensure_ascii=True),
                             'Access-Control-Expose-Headers':'X-Processing-Metadata'})

@router.post('/process')
async def process(file:UploadFile=File(...), steps:str=Form('[]')):
    parsed=normalize_steps(steps)
    image=await read_image(file)
    result=process_via_an(image,parsed)
    return Response(content=encode_png(result),media_type='image/png')


@router.post('/smart-enhance')
async def smart_enhance_upload(file: UploadFile = File(...)):
    # Đọc ảnh bằng hàm có sẵn của backend
    image = await read_image(file)

    try:
        # Gọi thuật toán riêng của bạn
        result, metadata = smart_enhance(image)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        ) from exc

    # Trả ảnh PNG và metadata giống auto-enhance
    return Response(
        content=encode_png(result),
        media_type='image/png',
        headers={
            'X-Processing-Metadata': json.dumps(
                metadata,
                ensure_ascii=True
            ),
            'Access-Control-Expose-Headers':
                'X-Processing-Metadata'
        }
    )


@router.post('/enhance-with-options')
async def enhance_with_options(
    file: UploadFile = File(...),
    mode: str = Form('smart'),
    level: str = Form('vua'),
    apply_filter: bool = Form(False),
    filter_method: str = Form('median'),
    filter_level: str = Form('nhe'),
    contrast: bool = Form(False),
    binarize: bool = Form(False),
):
    image = await read_image(file)

    try:
        # 1. Người dùng có thể bật/tắt bộ lọc
        filtered, filter_steps = apply_selected_filter(
            image,
            apply_filter=apply_filter,
            filter_method=filter_method,
            filter_level=filter_level
        )

        # 2. Smart Enhance hoặc Auto Enhance
        if mode == 'smart':
            output, metadata = smart_enhance(filtered)

        elif mode == 'an':
            output, metadata = enhance(filtered, level)

        elif mode == 'none':
            output = filtered
            metadata = {
                'steps': [{'method': 'keep_filtered_image'}],
                'policy': 'smart_enhance_disabled',
            }

        else:
            raise ValueError('mode phải là smart, an hoặc none')

        # 3. Tăng tương phản và nhị phân hóa
        output, extra_steps = apply_extra_options(
            output,
            contrast,
            binarize
        )

        # 4. Metadata
        metadata = dict(metadata)

        metadata['steps'] = [
            *filter_steps,
            *metadata.get('steps', []),
            *extra_steps
        ]

        metadata['filter_options'] = {
            'enabled': apply_filter,
            'method': filter_method if apply_filter else None,
            'level': filter_level if apply_filter else None
        }

        metadata['extra_options'] = {
            'contrast': contrast,
            'binarize': binarize
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        ) from exc

    return Response(
        content=encode_png(output),
        media_type='image/png',
        headers={
            'X-Processing-Metadata': json.dumps(
                metadata,
                ensure_ascii=True
            ),
            'Access-Control-Expose-Headers':
                'X-Processing-Metadata'
        }
    )
