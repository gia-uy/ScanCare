import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.process import router as process_router
from routers.export import router as export_router

app=FastAPI(title='Scan Document Enhancement - API Diệp',version='2.0.0',
            description='Backend dành cho Streamlit/Frontend; quy tắc auto chỉ là demo cần An kiểm thử.')
origins=[x.strip() for x in os.getenv('FRONTEND_ORIGINS',
          'http://localhost:8501,http://127.0.0.1:8501,http://localhost:3000,http://127.0.0.1:3000').split(',') if x.strip()]
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_methods=['GET','POST'],allow_headers=['*'],
                   expose_headers=['X-Processing-Metadata','Content-Disposition'])

@app.get('/health')
def health():return {'status':'ok','version':'2.0.0'}

app.include_router(process_router)
app.include_router(export_router)
