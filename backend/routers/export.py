import io
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from services.image_io import read_image, process_via_an, encode_png
from services.contracts import normalize_steps
from services.pdf_service import images_to_pdf
from services.auto_enhance import enhance

router=APIRouter(prefix='/api/export',tags=['Export'])

@router.post('/image')
async def export_image(file:UploadFile=File(...),format:str=Form('png')):
    # Ảnh gửi là ảnh hiện tại (gốc hoặc đã xử lý), không chạy lại pipeline.
    image=await read_image(file)
    if format not in {'png','jpg'}:
        raise HTTPException(400,'format phải là png hoặc jpg')
    if format=='png':
        body=encode_png(image);media='image/png';ext='png'
    else:
        import cv2
        ok,data=cv2.imencode('.jpg',image,[cv2.IMWRITE_JPEG_QUALITY,95])
        if not ok: raise HTTPException(500,'Không thể mã hóa JPG')
        body=data.tobytes();media='image/jpeg';ext='jpg'
    return Response(content=body, media_type=media,
                    headers={'Content-Disposition':f'attachment; filename="scan_result.{ext}"'})

@router.post('/pdf')
async def export_pdf(files:list[UploadFile]=File(...),mode:str=Form('as_is'),steps:str=Form('[]'),level:str=Form('vua')):
    if not 1 <= len(files) <= 10:
        raise HTTPException(400,'PDF chỉ hỗ trợ 1–10 trang')
    if mode not in {'as_is','manual','auto'}:
        raise HTTPException(400,'mode phải là as_is/manual/auto')
    parsed=normalize_steps(steps) if mode=='manual' else []
    pages=[]
    for file in files:
        img=await read_image(file)
        if mode=='manual': img=process_via_an(img,parsed)
        elif mode=='auto':
            try: img,_=enhance(img,level)
            except ValueError as exc: raise HTTPException(400,str(exc)) from exc
        pages.append(img)
    pdf=images_to_pdf(pages)
    return Response(content=pdf,media_type='application/pdf',
                    headers={'Content-Disposition':'attachment; filename="scan_document.pdf"'})
