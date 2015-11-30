# -*- coding: utf-8 -*-

import time
import wave
from naoqi import ALProxy, ALModule


class StreamingAudioRecorder(ALModule):
    """
    // Unicodeドキュメントはnaoqiライブラリに対応していない...

    Pepperのマイクに入力されている音声をリアルタイムに取得するためのクラス
    """

    DEFAULT_SAVE_PATH = "temp.wav"

    def __init__(self, name, save_path=DEFAULT_SAVE_PATH):
        ALModule.__init__(self, name)
        self.BIND_PYTHON(self.getName(), "callback")
        self.save_path = save_path
        self.func = None

    def start_record(self, func=None):
        self.func = func

        if self.save_path:
            self.file = wave.open(self.save_path, "wb")
            self.file.setsampwidth(2)
            self.file.setframerate(16000)
            self.file.setnchannels(1)

        self.pepper_microphone = ALProxy("ALAudioDevice")
        self.pepper_microphone.setClientPreferences(self.getName(), 16000, 3, 1)
        self.pepper_microphone.subscribe(self.getName())

    def stop_record(self):
        self.pepper_microphone.unsubscribe(self.getName())
        time.sleep(1)
        if self.save_path:
            self.file.close()

    # overrideのためCamelCase
    def processRemote(self, input_channels, input_samples, time_stamp, input_buff):
        if self.func:
            self.func(input_channels, input_samples, time_stamp, input_buff)
        if self.save_path:
            self.file.writeframes(input_buff)
