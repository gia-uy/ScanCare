"""Adapter HTTP cho auto_enhance thực tế của An; KHÔNG định nghĩa lại thuật toán."""
import cv2
import numpy as np
from modules.auto_enhance import auto_enhance

LEVELS = {'nhe':'Nhẹ','vua':'Trung bình','manh':'Mạnh',
          'Nhẹ':'Nhẹ','Vừa':'Trung bình','Trung bình':'Trung bình','Mạnh':'Mạnh'}

def analyze(image):
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY) if image.ndim==3 else image
    return {'contrast_std':float(np.std(gray)),
            'laplacian_variance':float(cv2.Laplacian(gray,cv2.CV_64F).var()),
            'note':'Chỉ số tham khảo; không khẳng định loại nhiễu.'}

def enhance(image,level='vua'):
    if level not in LEVELS:
        raise ValueError('Mức lọc phải là nhe, vua, manh hoặc Nhẹ, Vừa/Trung bình, Mạnh')
    output,steps,elapsed,analysis = auto_enhance(image,level=LEVELS[level])
    return output, {'level':level,'level_label':LEVELS[level],
                    'steps':steps,'analysis':analysis,
                    'processing_ms':round(elapsed*1000,2),
                    'policy':'an_rule_based_preliminary'}
