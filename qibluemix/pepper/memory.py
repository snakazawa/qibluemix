# -*- coding: utf-8 -*-

from naoqi import ALProxy, ALModule
from qibluemix import get_logger

logger = get_logger()


class SpeechRecognitionMemory(ALModule):
    """
    // Unicodeドキュメントはnaoqiライブラリに対応していない...

    声の検出用Memory

    # Memories
    ## WordRecognized
    [[word:utf-8, confidence:float]*]

    変換結果のリストを格納する。

    ## Status
    "running"|"stop"|"error"

    プロキシの状態を示す。
    "running"を指定すると変換を開始する。
    "stop"を指定すると変換を停止する。

    ## Error
    Error|None

    エラー情報を格納する。
    """

    STATUS_EVENT = "Status"
    WORD_EVENT = "WordRecognized"
    ERROR_EVENT = "Error"

    def __init__(self, name, event_root_path):
        ALModule.__init__(self, name)
        self.memory = ALProxy("ALMemory")
        self.name = name
        self.event_root_path = event_root_path
        self.status = "stop"
        self.status_handler = None
        self.subscribed_on_received_status = False

    def init_events(self, status_handler=None):
        self.memory.raiseEvent(self.event_root_path + self.STATUS_EVENT, "stop")
        self.memory.raiseEvent(self.event_root_path + self.WORD_EVENT, [])
        self.memory.raiseEvent(self.event_root_path + self.ERROR_EVENT, None)
        self.status_handler = status_handler
        if not self.subscribed_on_received_status:
            key = self.event_root_path + self.STATUS_EVENT
            logger.debug("[Memory] subscribe {0} {1}".format(key, self.getName()))
            self.subscribed_on_received_status = True
            self.memory.subscribeToEvent(key, self.getName(), "on_received_status")

    def raise_event(self, name, value):
        self.memory.raiseEvent(self.event_root_path + name, value)

    def start(self):
        self.status = "running"
        self.raise_event(self.STATUS_EVENT, "running")

    def stop(self):
        self.status = "stop"
        self.raise_event(self.STATUS_EVENT, "stop")

    def error(self, value):
        self.status = "error"
        self.raise_event(self.STATUS_EVENT, "error")
        self.raise_event(self.ERROR_EVENT, value)

    def recognize(self, value):
        self.raise_event(self.WORD_EVENT, value)

    def on_received_status(self, key, value, message):
        logger.debug("[Memory] received: {0} {1} {2}".format(key, value, message))
        if self.status_handler:
            self.status_handler(key, value, message)
