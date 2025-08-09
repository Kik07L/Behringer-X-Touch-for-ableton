#Embedded file name: /Users/versonator/Jenkins/live/output/Live/mac_64_static/Release/python-bundle/MIDI Remote Scripts/MackieControl/TimeDisplay.py
from __future__ import absolute_import, print_function, unicode_literals
from builtins import str
from builtins import range
from .MackieControlComponent import *
import time

class TimeDisplay(MackieControlComponent):
    u"""Represents the Mackie Controls Time-Display, plus the two LED's that show the"""

    def __init__(self, main_script):
        MackieControlComponent.__init__(self, main_script)
        self.__main_script = main_script
        self.__show_beat_time = False
        self.__show_current_time = 0
        self.__show_seconds = True
        self.__smpt_format = Live.Song.TimeFormat.smpte_25
        self.__last_send_time = []
        self.show_beats()

    def destroy(self):
        self.clear_display()
        MackieControlComponent.destroy(self)

    def show_beats(self):
        self.__show_beat_time = True
        self.send_button_led(SELECT_BEATS_NOTE, BUTTON_STATE_ON)
        self.send_button_led(SELECT_SMPTE_NOTE, BUTTON_STATE_OFF)

    def show_smpte(self, smpte_mode):
        self.__show_beat_time = False
        self.__smpt_format = smpte_mode
        self.send_button_led(SELECT_BEATS_NOTE, BUTTON_STATE_OFF)
        self.send_button_led(SELECT_SMPTE_NOTE, BUTTON_STATE_ON)

    def toggle_mode(self):
        self.__show_current_time = 0
        if self.__show_beat_time:
            self.show_smpte(self.__smpt_format)
        else:
            self.show_beats()

    def toggle_show_current_time(self):
        if self.__show_current_time == 0:
            self.__show_current_time = 1 #show time with seconds
            self.send_button_led(SELECT_BEATS_NOTE, BUTTON_STATE_ON)
            self.send_button_led(SELECT_SMPTE_NOTE, BUTTON_STATE_ON)
        elif self.__show_current_time == 1:
            self.__show_current_time = 2 #show time without seconds
            self.send_button_led(SELECT_BEATS_NOTE, BUTTON_STATE_ON)
            self.send_button_led(SELECT_SMPTE_NOTE, BUTTON_STATE_ON)
        elif self.__show_current_time == 2:
            self.__show_current_time = 0
            if self.__show_beat_time:
                self.show_beats()
            else:
                self.show_smpte(self.__smpt_format)

    # def toggle_show_seconds(self):
        # if self.__show_seconds:
            # self.__show_seconds = False
        # else:
            # self.__show_seconds = True

    def clear_display(self):
        time_string = [ u' ' for i in range(10) ]
        self.__send_time_string(time_string, points_positions=())
        self.send_button_led(SELECT_BEATS_NOTE, BUTTON_STATE_OFF)
        self.send_button_led(SELECT_SMPTE_NOTE, BUTTON_STATE_OFF)

    def refresh_state(self):
        self.show_beats()
        self.__last_send_time = []

    def on_update_display_timer(self):
        u"""Called by a timer which gets called every 100 ms. We will simply check if the"""

        if self.__show_current_time:
            t = time.localtime()
            if self.__show_current_time == 1:
                time_string = time.strftime("%H:%M:%S   ", t).rjust(12, " ")
            elif self.__show_current_time == 2:
                time_string = time.strftime("%H:%M     ", t).rjust(11, " ")
        elif self.__show_beat_time:
            time_string = str(self.song().get_current_beats_song_time())
        else:
            time_string = str(self.song().get_current_smpte_song_time(self.__smpt_format))

        reverse_time_string = time_string[::-1]
        points = []
        for i in range(len(time_string)):
            if reverse_time_string[i] in (u'.', u':'):
                points.append(i - len(points))

        time_string = [ c for c in time_string if c not in (u'.', u':') ]
        if self.__last_send_time != time_string:
            self.__last_send_time = time_string
            self.__send_time_string(time_string, points_positions=tuple(points))

    def __send_time_string(self, time_string, points_positions):
        assert len(time_string) >= 10
        for c in range(0, 10):
            char = time_string[9 - c].upper()
            char_code = g7_seg_led_conv_table[char]
            if c in points_positions:
                char_code += 64
            self.send_midi((176, 64 + c, char_code))
