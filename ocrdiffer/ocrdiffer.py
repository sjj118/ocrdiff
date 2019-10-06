from .ocr import *
from .match import match_box
from .diff import diff_words
from .draw import highlight
from .split import split_word
from io import BytesIO
from PIL import Image
import base64


class OCRDiffer(object):
    def __init__(self, engine='baidu', *args, **kwargs):
        if engine == 'baidu':
            self.__engine = BaiduOCREngine(*args, **kwargs)
        elif engine == 'sogou':
            self.__engine = SogouOCREngine(*args, **kwargs)
        elif engine == 'ali':
            self.__engine = AliOCREngine(*args, **kwargs)
        else:
            raise OCREngineUnknownError()

    def work(self, img1, img2):
        img2.resize(img1.size)
        ocr1 = self.__engine.ocr(img1)
        ocr2 = self.__engine.ocr(img2)
        ocr1 = split_word(ocr1)
        ocr2 = split_word(ocr2)
        mat, unmat1, unmat2 = match_box(ocr1, ocr2)
        diff1, diff2 = diff_words(mat)
        out = highlight(img1, img2, ocr1, ocr2, diff1 + unmat1, diff2 + unmat2)
        return out

    def work_http(self, img1, img2):
        dec1 = base64.b64decode(img1)
        dec2 = base64.b64decode(img2)
        img1 = Image.open(BytesIO(dec1))
        img2 = Image.open(BytesIO(dec2))
        return self.work(img1, img2)
