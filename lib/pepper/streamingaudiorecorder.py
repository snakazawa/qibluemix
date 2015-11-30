# -*- coding: utf-8 -*-



import time
import wave
from naoqi import (ALProxy, ALModule)


class StreamingAudioRecorder(ALModule):
    u"""
    Pepperのマイクに入力されている音声をリアルタイムに取得するためのクラス
    """

    def __init__(self, name):
        ALModule.__init__(self, name)

        self.BIND_PYTHON(self.getName(), "callback")

    def start_record(self, func=None, save_to_file=True):
        self.func = func
        self.save_to_file = save_to_file

        if self.save_to_file:
            self.file = wave.open("temp.wav", "wb")
            self.file.setsampwidth(2)
            self.file.setframerate(16000)
            self.file.setnchannels(1)

        self.pepper_microphone = ALProxy("ALAudioDevice")
        self.pepper_microphone.setClientPreferences(self.getName(), 16000, 3, 1)
        self.pepper_microphone.subscribe(self.getName())

    def stop_record(self):
        self.pepper_microphone.unsubscribe(self.getName())
        time.sleep(1)
        if self.save_to_file:
            self.file.close()

    # overrideのためCamelCase
    def processRemote(self, input_channels, input_samples, time_stamp, input_buff):
        if self.func:
            self.func(input_channels, input_samples, time_stamp, input_buff)
        if self.save_to_file:
            self.file.writeframes(input_buff)
