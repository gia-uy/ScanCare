import io, json, sys
from pathlib import Path
import cv2
import numpy as np
from fastapi.testclient import TestClient
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from main import app
client=TestClient(app)

def img_bytes():
    arr=np.full((160,220,3),225,dtype=np.uint8)
    cv2.putText(arr,'SCAN TEST',(18,85),cv2.FONT_HERSHEY_SIMPLEX,.7,(0,0,0),2)
    ok,enc=cv2.imencode('.png',arr); assert ok
    return enc.tobytes()

def upload(path,data=None):
    return {'file':(path,data if data is not None else img_bytes(),'image/png')}

def test_health():assert client.get('/health').status_code==200
def test_analyze():
    r=client.post('/api/analyze',files=upload('test.png'))
    assert r.status_code==200 and 'analysis' in r.json()
def test_auto():
    r=client.post('/api/auto-enhance',files=upload('test.png'),data={'level':'vua'})
    assert r.status_code==200 and r.content.startswith(b'\x89PNG')
    meta=json.loads(r.headers['X-Processing-Metadata'])
    assert 'steps' in meta and 'processing_ms' in meta
def test_auto_invalid_level():
    r=client.post('/api/auto-enhance',files=upload('test.png'),data={'level':'unknown'})
    assert r.status_code==400
def test_manual_old_contract():
    steps=[{'operation':'median','params':{'kernel_size':3}},
           {'operation':'closing','params':{'kernel_size':1}}]
    r=client.post('/api/process',files=upload('test.png'),data={'steps':json.dumps(steps)})
    assert r.status_code==200,r.text
def test_manual_an_contract():
    steps=[{'method':'gaussian_filter','kernel_size':3,'sigma':0}]
    r=client.post('/api/process',files=upload('test.png'),data={'steps':json.dumps(steps)})
    assert r.status_code==200,r.text
def test_manual_invalid_kernel():
    steps=[{'method':'median_filter','kernel_size':2}]
    r=client.post('/api/process',files=upload('test.png'),data={'steps':json.dumps(steps)})
    assert r.status_code==400
def test_enhance_options_applies_morphology_after_binarization():
    r=client.post(
        '/api/enhance-with-options',
        files=upload('test.png'),
        data={'mode':'smart','binarize':'true'},
    )
    assert r.status_code==200,r.text
    meta=json.loads(r.headers['X-Processing-Metadata'])
    methods=[step['method'] for step in meta['steps']]
    assert methods[-3:]==['binarization','opening','closing']
def test_enhance_options_skips_morphology_without_binarization():
    r=client.post(
        '/api/enhance-with-options',
        files=upload('test.png'),
        data={'mode':'smart','binarize':'false'},
    )
    assert r.status_code==200,r.text
    meta=json.loads(r.headers['X-Processing-Metadata'])
    methods=[step['method'] for step in meta['steps']]
    assert 'opening' not in methods
    assert 'closing' not in methods
def test_enhance_options_without_smart_enhance():
    r=client.post(
        '/api/enhance-with-options',
        files=upload('test.png'),
        data={
            'mode':'none',
            'apply_filter':'true',
            'filter_method':'median',
            'filter_level':'nhe',
            'contrast':'true',
            'binarize':'true',
        },
    )
    assert r.status_code==200,r.text
    meta=json.loads(r.headers['X-Processing-Metadata'])
    methods=[step['method'] for step in meta['steps']]
    assert methods[:2]==['median_filter','keep_filtered_image']
    assert methods[-3:]==['binarization','opening','closing']
    assert meta['policy']=='smart_enhance_disabled'
def test_pdf_as_is():
    data=img_bytes()
    r=client.post('/api/export/pdf',files=[('files',('1.png',data,'image/png')),('files',('2.png',data,'image/png'))])
    assert r.status_code==200 and r.content.startswith(b'%PDF')
def test_export_jpg():
    r=client.post('/api/export/image',files=upload('test.png'),data={'format':'jpg'})
    assert r.status_code==200 and r.content.startswith(b'\xff\xd8')
def test_invalid_file():
    r=client.post('/api/analyze',files={'file':('bad.png',b'not-image','image/png')})
    assert r.status_code in (400,415)
