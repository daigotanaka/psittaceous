# The MIT License (MIT)
#
# Copyright (c) 2013 Daigo Tanaka (@daigotanaka)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import os

from time import sleep

import libs


class Listener(object):

    def __init__(self, user="", sample_rate=48000):
        self.sample_rate = sample_rate
        self.user = user
        self.keep_recording = False
        self.recording = None
        self.playing = None

    def system(self, cmd):
        return libs.system(command=cmd, user=self.user)

    def continuous_recording(
            self,
            file="/tmp/noise%d.flac",
            hw="plughw:1,0",
            duration=5,
            nullout=False):
        while self.keep_recording:
            if self.recording is not None:
                raise Exception("Another thread is recording audio.")

            self.recording = 0
            if self.playing is not None:
                self.recording = (self.playing + 1) % 2
            if os.path.exists(file % self.recording):
                os.remove(file % self.recording)
            self.record_flac(
                file=file % self.recording,
                hw=hw,
                duration=duration,
                nullout=nullout)
            self.recording = None

    def get_volume(self, file="/tmp/noise%d.flac", rotation=0):
        if self.playing is not None:
            raise Exception("Another thread is playing audio.")
        self.playing = rotation
        while self.recording == self.playing:
            sleep(0.5)
        file = file % self.playing
        cmd = (
            "/usr/bin/sox " +
            file +
            " -n stats -s 16 2>&1 | /usr/bin/awk '/^Max\\ level/ {print $3}'" +
            " > /tmp/volume.txt")
        self.system(cmd)
        f = open("/tmp/volume.txt")
        output = f.read()
        vol = float(output) if output else -1.0
        self.playing = None
        return vol

    def record_flac(
            self,
            file="/tmp/noise0.flac",
            hw="plughw:1,0",
            duration=5,
            nullout=False):
        if os.path.exists(file):
            raise Exception("File already exists!")

        cmd = "/usr/bin/arecord -D "
        cmd += hw
        cmd += " -q"
        cmd += " -f cd -t wav -d "
        cmd += str(duration)
        cmd += " -r " + str(self.sample_rate)
        cmd += " | /usr/bin/avconv"
        cmd += " -loglevel 0 -i - -ar " + str(self.sample_rate)
        cmd += " " + file

        if nullout:
            cmd += " 1>>/tmp/voice.log 2>>/tmp/voice.log"
        self.system(cmd)

    def record_wav(
            self,
            file="/tmp/noise.wav",
            hw="plughw:1,0",
            duration=5,
            nullout=False):
        if os.path.exists(file):
            raise Exception("File already exists!")

        cmd = "/usr/bin/arecord -D "
        cmd += hw
        cmd += " -q"
        cmd += " -f cd -t wav -d "
        cmd += str(duration)
        cmd += " -r " + str(self.sample_rate) + " " + file
        if nullout:
            cmd += " 1>>/tmp/voice.log 2>>/tmp/voice.log"
        self.system(cmd)

if __name__ == "__main__":
    if os.path.exists("/tmp/noise0.flac"):
        os.remove("/tmp/noise0.flac")

    listener = Listener()
    listener.record_flac()
    print listener.get_volume()
