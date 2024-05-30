from flask import Flask, request, jsonify, render_template
# from openai import OpenAI
import os
import random
import requests
from dotenv import load_dotenv
from dashscope import Generation
import base64
import json
import hashlib
import time
import websocket
import _thread as thread
import ssl
from xf_util import Ws_Param
# os.environ['http_proxy']="http://127.0.0.1:7890"
# os.environ['https_proxy']="http://127.0.0.1:7890"
load_dotenv()
os.environ['DASHSCOPE_API_KEY'] = os.getenv("DASHSCOPE_API_KEY")
app = Flask(__name__)

# Load your OpenAI API key from environment variable
# openai.api_key = os.getenv("OPENAI_API_KEY")
IFLYTEK_APPID = os.getenv("IFLYTEK_APPID")
IFLYTEK_API_KEY = os.getenv("IFLYTEK_API_KEY")
IFLYTEK_API_SECRET = os.getenv("IFLYTEK_API_SECRET")
def get_iflytek_tts(text):
    wsParam = Ws_Param(APPID=IFLYTEK_APPID, APISecret=IFLYTEK_API_SECRET,
                           APIKey=IFLYTEK_API_KEY,
                           Text=text)
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()

    def on_message(ws, message):
        try:
            message = json.loads(message)
            code = message["code"]
            sid = message["sid"]
            audio = message["data"]["audio"]
            audio = base64.b64decode(audio)
            status = message["data"]["status"]
            print(message)
            # if status == 2:
            #     print("ws is closed")
            #     ws.close()
            # if code != 0:
            #     errMsg = message["message"]
            #     print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
            # else:
            with open('./static/demo.mp3', 'wb') as f:
                f.write(audio)

        except Exception as e:
            print("receive msg,but parse exception:", e)

    def on_error(ws, error):
        print("### error:", error)

    def on_open(ws):
        def run(*args):
            d = {"common": wsParam.CommonArgs,
                 "business": wsParam.BusinessArgs,
                 "data": wsParam.Data,
                 }
            d = json.dumps(d)
            print("------>开始发送文本数据")
            ws.send(d)
            # if os.path.exists('./demo.pcm'):
            #     os.remove('./demo.pcm')

        thread.start_new_thread(run, ())

    def on_close(ws):
        print("### closed ###")
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question')
    messages = [{'role': 'system', 'content': 'You are a helpful assistant.'},
                {'role': 'user', 'content': question}]
    response = Generation.call(model="qwen-turbo",
                               messages=messages,
                               # 设置随机数种子seed，如果没有设置，则随机数种子默认为1234
                               seed=random.randint(1, 10000),
                               # 将输出设置为"message"格式
                               result_format='message')
    answer = response.output.choices[0]['message']['content']
    get_iflytek_tts(answer)

    # Save audio to a file
    audio_file_path = '/static/demo.mp3'
    # with open(audio_file_path, 'wb') as audio_file:
    #     audio_file.write(audio_content)
    answer=list(answer)
    print(answer)
    return jsonify({"answer":answer,'audio_file':audio_file_path})

if __name__ == '__main__':
    app.run(debug=True)
