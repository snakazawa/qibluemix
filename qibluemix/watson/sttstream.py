# -*- coding: utf-8 -*-

import time
import json
import websocket
from functools import partial
from websocket._abnf import ABNF


class STTStream:
    u"""
    WebSocket を利用して Bluemix Speech To Text を扱うためのクラス
    """
    DEFAULT_START_PARAMS = {
        'action': 'start',
        'content-type': 'audio/l16; rate=16000; channels=1',
        'interim_results': True,
        'continuous': True,
        'timestamps': True
    }

    DEFAULT_STOP_PARAMS = {'action': 'stop'}

    def __init__(self, url, start_params={}):
        self.url = url
        self.state = "none"
        self.start_params = dict(self.DEFAULT_START_PARAMS, **start_params)
        self.ws = None

    def run(self, on_message=None, on_error=None, on_close=None, on_open=None, keep_running=True):
        # on_closeは内部でinspectしているが、partial instanceはinspectできないためlambdaで記述している
        self.ws = websocket.WebSocketApp(self.url,  # header={'Transfer-encoding': 'chunked'},
                                         on_message=partial(self._on_message, on_message),
                                         on_error=partial(self._on_error, on_error),
                                         on_close=lambda ws: self._on_close(on_close, ws),
                                         on_open=partial(self._on_open, on_open),
                                         keep_running=keep_running)
        self.ws.run_forever()

    def stop(self):
        self.ws.send(json.dumps(self.DEFAULT_STOP_PARAMS))
        time.sleep(3)
        self.ws.close()

    def send(self, data, is_binary=False):
        self.ws.send(data, ABNF.OPCODE_BINARY if is_binary else ABNF.OPCODE_TEXT)

    def can_send(self):
        return self.state == "open"

    def _on_message(self, user_func, ws, message):
        if user_func:
            user_func(self, message)

    def _on_error(self, user_func, ws, error):
        if self.state == "none":
            self.state = "error"
        if user_func:
            user_func(self, error)

    def _on_close(self, user_func, ws):
        self.state = "close"
        if user_func:
            user_func(self)

    def _on_open(self, user_func, ws):
        self.state = "open"
        ws.send(json.dumps(self.start_params))
        if user_func:
            user_func(self)
