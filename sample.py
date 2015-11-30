# -*- coding: utf-8 -*-

u"""
see readme.md
"""

import time
from naoqi import ALBroker
from lib import STTProxy, get_logger
from lib.pepper import SpeechRecognitionMemory, StreamingAudioRecorder
from lib.watson import Watson

# ==== parameters ====
PEPPER_IP = "192.168.10.101"
PEPPER_PORT = 9559
EVENT_ROOT_NAME = "Bluemix/STTProxy/"  # 本アプリが使用するPepperのメモリのルートパス
USERNAME = "171e6d24-fe75-4531-b0c2-596e5eb8cdf5"  # credentials.username (Bluemix Speech To Text)
PASSWORD = "eiGyFVAn6qSH"  # credentials.password (Bluemix Speech To Text)
URL = "https://stream.watsonplatform.net/speech-to-text/api"
CONFIDENCE = 0.2  # 変換における信頼性の許容値(0.0~1.0) 許容値未満の変換結果は無視される
# ==== /parameters ====

StreamingAudioRecorderModule = None
SpeechRecognitionMemoryModule = None
broker = None
logger = get_logger()


def main():
    global SpeechRecognitionMemoryModule
    global StreamingAudioRecorderModule
    global broker

    logger.info("init watson")
    watson = Watson(USERNAME, PASSWORD, URL)
    token = get_token(watson)
    stream = watson.recognize_stream(token)

    logger.info("init remote pepper")
    broker = ALBroker("myBroker", "0.0.0.0", 0, PEPPER_IP, PEPPER_PORT)

    logger.info("init StreamingAudioRecorder")
    recorder = StreamingAudioRecorderModule = StreamingAudioRecorder("StreamingAudioRecorderModule")

    logger.info("init SpeechRecognitionMemory")
    memory = SpeechRecognitionMemoryModule = SpeechRecognitionMemory("SpeechRecognitionMemoryModule", EVENT_ROOT_NAME)

    logger.info("init SpeechToTextProxy")
    proxy = STTProxy(recorder, stream, memory)
    proxy.init()

    logger.info("ready...")

    manual(proxy, duration=10, after_wait=3)

    # forever
    # while True:
    #     time.sleep(1)


def manual(proxy, duration=10, after_wait=3):
    logger.info("start")
    proxy.start()

    time.sleep(duration)

    logger.info("stop")
    proxy.stop()

    time.sleep(after_wait)
    logger.info("end")


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
