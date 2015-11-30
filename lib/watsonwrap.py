# -*- coding: utf-8 -*-

u"""
Watson Bluemixのラッパー
"""

import time
import websocket
import json
import wave
import requests
import re
from functools import partial
from websocket._abnf import ABNF


class WatsonWrap:
    u"""
    Watson Bluemixのラッパークラス
    """
    VERSION = "v1"

    def __init__(self, username, password, url):
        self.auth = (username, password)  # basic
        self.version = self.VERSION
        m = re.match(r'(.+?)://(.+?)/(.+?)/api', url)
        if m is None:
            raise Exception('不正なURLが渡されました')
        self.domain = m.group(2)
        self.service = m.group(3)

    def get_token(self):
        url = self._get_url(service="authorization", action="token") + "?url=" + self._get_url_short()
        return requests.get(url, auth=self.auth)

    def recognize(self, audio_path, header_opts={}, query_opts={}, param_opts={}):
        url = self._get_url(action="recognize")
        headers = dict({"Content_Type": "multipart/form-data"}, **header_opts)
        query = dict({"model": "ja-JP_BroadbandModel"}, **query_opts)

        type = self._get_wave_type_str(audio_path)

        params = dict({"part_content_type": type, "data_parts_count": 1, "continuous": False,
                       "inactivity_timeout": -1}, **param_opts)
        audio = open(audio_path, "rb")
        files = {"params": json.dumps(params), "file": audio}
        return requests.post(url, params=query, files=files, auth=self.auth, headers=headers)

    def recognize_stream(self, token, start_params={}):
        # 注意: query parameterの最初はwatson-tokenでないといけない
        url = self._get_url(scheme="wss", action="recognize") \
              + "?watson-token={token}&model={model}".format(token=token, model="ja-JP_BroadbandModel")
        stream = STTStreaming(url, start_params=start_params)
        return stream

    def tag_recognize(self, image_path):
        url = self._get_url(action="tag/recognize")
        headers = {"Content_Type": "multipart/form-data"}
        files = {"img_File": open(image_path, "rb")}
        return requests.post(url, files=files, headers=headers, auth=self.auth)

    def get_tag_labels(self):
        url = self._get_url(action="tag/labels")
        return requests.get(url, auth=self.auth)

    def _get_url_short(self, scheme="https", service=None):
        if service is None:
            service = self.service
        return "{scheme}://{domain}/{service}/api".format(scheme=scheme, domain=self.domain, service=service)

    def _get_url(self, scheme="https", service=None, action=None):
        if service is None:
            service = self.service
        return "{scheme}://{domain}/{service}/api/{version}/{action}" \
            .format(scheme=scheme, domain=self.domain, service=service, version=self.version, action=action)

    def _get_wave_type_str(self, path):
        wave = self._get_wave_info(path)
        return ";".join(["audio/wav", "rate=" + str(wave["rate"]), "channels=" + str(wave["channels"])])

    def _get_wave_info(self, path):
        f = wave.open(path, "rb")
        info = {"channels": f.getnchannels(), "rate": f.getframerate()}
        f.close()
        return info


class STTStreaming:
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
