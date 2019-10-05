import requests
from io import BytesIO
import base64
import hashlib
import time
import json
from .errors import *


class OCREngine(object):
    def ocr(self, img):
        pass


class OCRBox(object):
    def __init__(self, x, y, w, h):
        self.__x = x
        self.__y = y
        self.__w = w
        self.__h = h

    @property
    def left(self):
        return self.__x

    @property
    def right(self):
        return self.__x + self.__w

    @property
    def top(self):
        return self.__y

    @property
    def bottom(self):
        return self.__y + self.__h

    @property
    def width(self):
        return self.__w

    @property
    def height(self):
        return self.__h

    def __repr__(self):
        return 'OCRBox(%d,%d,%d,%d)' % (self.__x, self.__y, self.__w, self.__h)


class OCRWord(OCRBox):
    def __init__(self, location, word, chars):
        self.__word = word
        self.__chars = chars
        super().__init__(location.left, location.top, location.width, location.height)

    @property
    def word(self):
        return self.__word

    @property
    def chars(self):
        return self.__chars

    def __len__(self):
        return len(self.word)

    def __getitem__(self, key):
        boxes = self.chars[key]
        left = min([it.left for it in boxes])
        right = max([it.right for it in boxes])
        top = min([it.top for it in boxes])
        bottom = max([it.bottom for it in boxes])
        return OCRWord(OCRBox(left, top, right - left, bottom - top), self.word[key], boxes)

    def __repr__(self):
        return 'OCRWord(%s,%s,%s)' % (super().__repr__(), self.__word.__repr__(), self.chars.__repr__())


class BaiduOCREngine(OCREngine):
    def __init__(self, token, accurate=False):
        self.__token = token
        self.__url = 'https://aip.baidubce.com/rest/2.0/ocr/v1/' + ('accurate' if accurate else 'general')
        self.__headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        self.__params = {'access_token': token}
        self.__body = {'recognize_granularity': 'small'}

    @staticmethod
    def __loc2box(loc):
        return OCRBox(loc['left'], loc['top'], loc['width'], loc['height'])

    def ocr(self, img):
        byte = BytesIO()
        img.save(byte, format='png')
        encoded = base64.b64encode(byte.getvalue()).decode()
        self.__body['image'] = encoded
        response = requests.post(url=self.__url, params=self.__params, headers=self.__headers, data=self.__body).json()
        if 'code' in response:
            raise BaiduOCRError(code=response['code'], message=response['message'])
        results = response['words_result']
        words = [
            OCRWord(
                self.__loc2box(word['location']),
                ''.join([c['char'] for c in word['chars']]),
                [self.__loc2box(c['location']) for c in word['chars']]
            ) for word in results
        ]
        return words


class SogouOCREngine(OCREngine):
    def __init__(self, pid, key):
        self.__pid = pid
        self.__key = key
        self.__service = 'basicOpenOcr'
        self.__url = 'http://deepi.sogou.com/api/sogouService'
        self.__headers = {'content-type': "application/x-www-form-urlencoded", 'accept': "application/json"}
        self.__params = {'pid': pid, 'key': key, 'service': self.__service}
        self.__body = {}

    @staticmethod
    def __frame2box(frame):
        x0, y0 = map(int, frame[0].split(','))
        x1, y1 = map(int, frame[1].split(','))
        x2, y2 = map(int, frame[2].split(','))
        x3, y3 = map(int, frame[3].split(','))
        left = min(x0, x1, x2, x3)
        right = max(x0, x1, x2, x3)
        top = min(y0, y1, y2, y3)
        bottom = max(y0, y1, y2, y3)
        return OCRBox(left, top, right - left, bottom - top)

    @staticmethod
    def __split(box, n):
        det = box.width / n
        return [OCRBox(round(box.left + det * c), box.top, round(det), box.height) for c in range(n)]

    def ocr(self, img):
        byte = BytesIO()
        img.save(byte, format='png')
        encoded = base64.b64encode(byte.getvalue()).decode()
        self.__body['image'] = encoded
        salt = str(time.time_ns())
        sign = self.__md5(self.__pid + self.__service + salt + encoded[:1024] + self.__key)
        self.__params['salt'] = salt
        self.__params['sign'] = sign
        response = requests.post(url=self.__url, params=self.__params, headers=self.__headers, data=self.__body).json()
        if 'code' in response:
            raise SogouOCRError(code=response['code'], message=response['message'])
        if 'err_code' in response:
            raise SogouOCRError(code=response['err_code'], message=response['err_msg'])
        results = response['result']
        words = [
            OCRWord(
                self.__frame2box(word['frame']),
                word['content'].strip(),
                self.__split(self.__frame2box(word['frame']), len(word['content'].strip()))
            ) for word in results
        ]
        return words

    @staticmethod
    def __md5(s):
        return hashlib.md5(s.encode('utf8')).hexdigest()


class AliOCREngine(OCREngine):
    def __init__(self, appcode):
        self.__appcode = appcode
        self.__url = 'https://ocrapi-advanced.taobao.com/ocrservice/advanced'
        self.__headers = {'content-type': 'application/json', 'Authorization': 'APPCODE ' + appcode}
        self.__body = {'charInfo': True}

    @staticmethod
    def __pos2box(pos):
        left = pos[0]['x']
        top = pos[0]['y']
        right = pos[2]['x']
        bottom = pos[2]['y']
        return OCRBox(left, top, right - left, bottom - top)

    @staticmethod
    def __char2box(char):
        return OCRBox(char['x'], char['y'], char['w'], char['h'])

    def ocr(self, img):
        byte = BytesIO()
        img.save(byte, format='png')
        encoded = base64.b64encode(byte.getvalue()).decode()
        self.__body['img'] = encoded
        response = requests.post(url=self.__url, headers=self.__headers, data=json.dumps(self.__body)).json()
        if 'error_code' in response:
            raise AliOCRError(code=response['error_code'], message=response['error_msg'])
        results = response['prism_wordsInfo']
        words = [
            OCRWord(
                self.__pos2box(word['pos']),
                ''.join([c['word'] for c in word['charInfo']]),
                [self.__char2box(c) for c in word['charInfo']]
            ) for word in results
        ]
        return words
