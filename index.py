# -*- coding: utf-8 -*-

"""
see lib/speechtotextproxy.py
"""

from naoqi import (ALBroker)
from lib.streamingrecorder import StreamingRecorder
from lib.speechtotextproxy import SpeechToTextProxy
from lib.watsonwrap import WatsonWrap

PEPPER_IP = "192.168.___.___"
PEPPER_PORT = 9559
EVENT_ROOT_NAME = "Bluemix/SpeechToTextProxy/"  # 本アプリが使用するPepperのメモリのルートパス
USERNAME = "********"  # credentials.username (Bluemix Speech To Text)
PASSWORD = "********"  # credentials.password (Bluemix Speech To Text)
URL = "https://stream.watsonplatform.net/speech-to-text/api"
CONFIDENCE = 0.2  # 変換における信頼性の許容値(0.0~1.0) 許容値未満の変換結果は無視される

StreamingRecorderModule = None
SpeechToTextProxyModule = None

broker = None


def main():
    global StreamingRecorderModule
    global SpeechToTextProxyModule
    global broker

    watson = WatsonWrap(USERNAME, PASSWORD, URL)

    print "init watson"
    token = get_token(watson)
    stream = watson.recognize_stream(token)

    print "init remote pepper"
    broker = ALBroker("myBroker", "0.0.0.0", 0, PEPPER_IP, PEPPER_PORT)

    print "init StreamingRecorderModule"
    recorder = StreamingRecorderModule = StreamingRecorder("StreamingRecorderModule")

    print "init SpeechToTextProxyMoudle"
    proxy = SpeechToTextProxyModule = SpeechToTextProxy("SpeechToTextProxyModule", EVENT_ROOT_NAME, recorder, stream,
                                                        confidence=CONFIDENCE)
    proxy.subscribe_events()

    print "ready..."

    # forever
    while True:
        pass


def get_token(watson):
    r = watson.get_token()
    if r.status_code != 200:
        print r.url
        print r.status_code
        print r.text.encode('utf-8')
        exit(1)

    return r.text


if __name__ == "__main__":
    main()
