import configparser
import os
from flask import Flask, request, Response, render_template
from PIL import Image
from io import BytesIO
from ocrdiffer.ocrdiffer import OCRDiffer

config = configparser.ConfigParser()
config.read(os.path.dirname(os.path.realpath(__file__)) + '/config.ini')
app = Flask(__name__)


def after_request(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


app.after_request(after_request)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/ocrdiff/', methods=['POST'])
def ocrdiff():
    engine = request.form['engine']
    if engine == 'baidu':
        differ = OCRDiffer(engine='baidu', token=config['baidu']['token'], accurate=request.args.get('accurate', False))
    elif engine == 'ali':
        differ = OCRDiffer(engine='ali', appcode=config['ali']['appcode'])
    else:
        differ = OCRDiffer(engine='sogou', pid=config['sogou']['pid'], key=config['sogou']['key'])
    img1 = request.files['img1']
    img2 = request.files['img2']
    img1 = Image.open(img1)
    img2 = Image.open(img2)
    out = differ.work(img1, img2)
    byte = BytesIO()
    out.save(byte, format='png')
    return Response(byte.getvalue(), headers={'Content-Disposition': 'attachment;filename=out.png'})


if __name__ == '__main__':
    app.run(debug=True)
