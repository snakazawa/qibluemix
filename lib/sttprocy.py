# -*- coding: utf-8 -*-

"""
Pepperのマイクから拾った音声をテキストに変換するプロキシ。
変換にはBluemix Speech To Textを用い、WebSocketで音声データを流し続ける。
変換結果はPepperのメモリに格納される。

# Memories
## WordRecognition
[[word:utf-8, confidence:float]*]

変換結果のリストを格納する。

## Status
"running"|"stop"|"error"

プロキシの状態を示す。
"running"を指定すると変換を開始する。
"stop"を指定すると変換を停止する。

## Error
Error|None

エラー情報
"""

import json
from naoqi import (ALProxy, ALModule)


class STTProxy(ALModule):
    STATUS_EVENT = "Status"
    WORD_EVENT = "WordRecognition"
    ERROR_EVENT = "Error"

    def __init__(self, name, event_root_path, streaming_recorder, watson_recognize_stream, confidence=0.4):
        ALModule.__init__(self, name)
        self.BIND_PYTHON(self.getName(), "_on_received_status")
        self.memory = ALProxy("ALMemory")
        self.name = name
        self.confidence = confidence  # 許容値(0~1.0)
        self.event_root_path = event_root_path
        self.streaming_recorder = streaming_recorder
        self.watson_recognize_stream = watson_recognize_stream
        self.status = "stop"
        # recorder, stream それぞれのstatusも管理したほうが良さそう

    def subscribe_events(self):
        self.memory.subscribeToEvent(self.event_root_path + self.STATUS_EVENT, self.getName(), "_on_received_status")
        self.memory.raiseEvent(self.event_root_path + self.STATUS_EVENT, "stop")
        self.memory.raiseEvent(self.event_root_path + self.WORD_EVENT, [])
        self.memory.raiseEvent(self.event_root_path + self.ERROR_EVENT, None)

    def start(self):
        print "[STTProxy] start speech to text"
        self.status = "running"
        self.memory.raiseEvent(self.event_root_path + self.STATUS_EVENT, "running")
        self.watson_recognize_stream.run(
            on_open=self._on_stream_open,
            on_close=self._on_stream_close,
            on_error=self._on_stream_error,
            on_message=self._on_stream_message)

    def stop(self):
        print "[STTProxy] stop speech to text"
        self.status = "stop"
        self.streaming_recorder.stop_record()
        self.watson_recognize_stream.stop()
        self.memory.raiseEvent(self.event_root_path + self.STATUS_EVENT, "stop")

    def _on_stream_open(self, stream):
        print "[Watson] on stream open"
        self.streaming_recorder.start_record(self._record_process)

    def _on_stream_close(self, stream):
        print "[Watson] on stream close"
        if self.status != "stop":
            self.stop()

    def _on_stream_error(self, stream, error):
        print "[Watson] on stream error {0}".format(error)
        self.status = "error"
        self.memory.raiseEvent(self.event_root_path + self.STATUS_EVENT, "error")
        self.memory.raiseEvent(self.event_root_path + self.ERROR_EVENT, str(error))

    def _on_stream_message(self, stream, message):
        if self.status != "running":
            return
        d = json.loads(message)
        if len(d["results"]) == 0:
            return
        if not d["results"][0]["final"]:
            return
        words = [[x["transcript"].encode('utf-8'), x["confidence"]] for x in d["results"][0]["alternatives"]
                 if float(x["confidence"]) >= self.confidence]
        if len(words) > 0:
            print "on stream message: "
            for word in words:
                print str(word[0]) + ", " + str(word[1])
            self.memory.raiseEvent(self.event_root_path + self.WORD_EVENT, words)

    def _record_process(self, inputChannels, inputSamples, timeStamp, inputBuff):
        self.watson_recognize_stream.send(inputBuff, is_binary=True)

    def _on_received_status(self, key, value, message):
        print "[Memory] received: {0} {1} {2}".format(key, value, message)
        if value == "running" and self.status != "running":
            self.start()
        elif value == "stop" and self.status != "stop":
            self.stop()
