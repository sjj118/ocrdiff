import os
import argparse
import configparser
from PIL import Image
from ocrdiffer.ocrdiffer import OCRDiffer
from ocrdiffer.errors import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('img1')
    parser.add_argument('img2')
    parser.add_argument('-e', '--engine', action='store', help='select ocr engine: baidu/ali/sogou(default)')
    parser.add_argument('-a', '--accurate', action='store_true', help='enable accurate mode')
    args = parser.parse_args()
    config = configparser.ConfigParser()
    config.read(os.path.dirname(os.path.realpath(__file__)) + '/config.ini')
    if args.engine == 'baidu':
        differ = OCRDiffer(engine='baidu', token=config['baidu']['token'], accurate=args.accurate)
    elif args.engine == 'ali':
        differ = OCRDiffer(engine='ali', appcode=config['ali']['appcode'])
    else:
        differ = OCRDiffer(engine='sogou', pid=config['sogou']['pid'], key=config['sogou']['key'])
    img1 = Image.open(args.img1)
    img2 = Image.open(args.img2)
    try:
        out = differ.work(img1, img2)
    except BaiduOCRError as e:
        print('百度OCR错误[%d]: %s' % (e.code, e.message))
    except SogouOCRError as e:
        print('搜狗OCR错误[%d]: %s' % (e.code, e.message))
    except AliOCRError as e:
        print('阿里OCR错误[%d]: %s' % (e.code, e.message))
    else:
        out.show()
