# -*- coding: utf-8 -*-

u"""
see readme.md
"""

import time
from naoqi import (ALBroker)
from lib import pepper, STTProxy, WatsonWrap, get_logger

# ==== parameters ====
PEPPER_IP = "192.168.___.___"
PEPPER_PORT = 9559
EVENT_ROOT_NAME = "Bluemix/STTProxy/"  # 本アプリが使用するPepperのメモリのルートパス
USERNAME = "********"  # credentials.username (Bluemix Speech To Text)
PASSWORD = "********"  # credentials.password (Bluemix Speech To Text)
URL = "https://stream.watsonplatform.net/speech-to-text/api"
CONFIDENCE = 0.2  # 変換における信頼性の許容値(0.0~1.0) 許容値未満の変換結果は無視される
# ==== /parameters ====

StreamingRecorderModule = None
SpeechToTextProxyModule = None
broker = None
logger = get_logger()


def main():
    global StreamingRecorderModule
    global SpeechToTextProxyModule
    global broker

    logger.info("init watson")
    watson = WatsonWrap(USERNAME, PASSWORD, URL)
    token = get_token(watson)
    stream = watson.recognize_stream(token)

    logger.info("init remote pepper")
    broker = ALBroker("myBroker", "0.0.0.0", 0, PEPPER_IP, PEPPER_PORT)

    logger.info("init StreamingRecorderModule")
    recorder = StreamingRecorderModule = pepper.StreamingAudioRecorder("StreamingRecorderModule")

    logger.info("init SpeechToTextProxyModule")
    proxy = SpeechToTextProxyModule = STTProxy("SpeechToTextProxyModule", EVENT_ROOT_NAME, recorder, stream,
                                               confidence=CONFIDENCE)
    proxy.init_events()

    logger.info("ready...")

    # forever
    while True:
        time.sleep(1)


def get_token(watson):
    r = watson.get_token()
    if r.status_code != 200:
        logger.info(r.url)
        logger.info(r.status_code)
        logger.info(r.text.encode('utf-8'))
        exit(1)

    return r.text


if __name__ == "__main__":
    main()
