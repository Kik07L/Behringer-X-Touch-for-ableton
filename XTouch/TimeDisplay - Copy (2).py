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
        self.main_script().show_clock = 0
        self.__smpt_format = Live.Song.TimeFormat.smpte_25
        self.__last_send_time = []
        
        # message override system
        self.__message_queue = []  # list of (msg, expire_time)
        self.__current_message = None
        self.__message_expire = 0

        self.show_beats()

    def destroy(self):
        self.clear_display()
        MackieControlComponent.destroy(self)

    def instance(self):
        """Return self for public access."""
        return self

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
        self.main_script().show_clock = 0
        if self.__show_beat_time:
            self.show_smpte(self.__smpt_format)
        else:
            self.show_beats()

    def toggle_show_clock(self):
        if self.main_script().show_clock == 0:
            self.main_script().show_clock = 1 #show time with seconds
            self.send_button_led(SELECT_BEATS_NOTE, BUTTON_STATE_ON)
            self.send_button_led(SELECT_SMPTE_NOTE, BUTTON_STATE_ON)
        elif self.main_script().show_clock == 1:
            self.main_script().show_clock = 2 #show time without seconds
            self.send_button_led(SELECT_BEATS_NOTE, BUTTON_STATE_ON)
            self.send_button_led(SELECT_SMPTE_NOTE, BUTTON_STATE_ON)
        elif self.main_script().show_clock == 2:
            self.main_script().show_clock = 0
            if self.__show_beat_time:
                self.show_beats()
            else:
                self.show_smpte(self.__smpt_format)
        self.main_script().save_preferences()

    def clear_display(self):
        time_string = [ u' ' for i in range(10) ]
        self.__send_time_string(time_string, points_positions=())
        self.send_button_led(SELECT_BEATS_NOTE, BUTTON_STATE_OFF)
        self.send_button_led(SELECT_SMPTE_NOTE, BUTTON_STATE_OFF)

    def refresh_state(self):
        self.show_beats()
        self.__last_send_time = []

    # ----------------------------
    # Message handling additions
    # ----------------------------

    def show_message(self, msg, duration=2000):
        """Queue a message to display for <duration> ms."""
        if not msg:
            return
        msg = str(msg).ljust(10)[:10]
        expire_time = time.time() + (duration / 1000.0)
        self.__message_queue.append((msg, expire_time))

    def show_priority_message(self, msg, duration=2000):
        """Show a message immediately, interrupting current/queued ones."""
        if not msg:
            return
        msg = str(msg).ljust(10)[:10]
        expire_time = time.time() + (duration / 1000.0)
        # Clear queue and override current
        self.__message_queue = []
        self.__current_message = msg
        self.__message_expire = expire_time
        time_string, points = self.__prepare_display_string(msg)
        self.__send_time_string(time_string, points_positions=points)

    def __update_message_state(self):
        now = time.time()
        if self.__current_message and now < self.__message_expire:
            return True
        else:
            if self.__current_message:
                # just expired
                self.__last_send_time = []  # force refresh next update
            self.__current_message = None

        if self.__message_queue:
            msg, exp = self.__message_queue.pop(0)
            self.__current_message = msg
            self.__message_expire = exp
            time_string, points = self.__prepare_display_string(msg)
            self.__send_time_string(time_string, points_positions=points)
            return True
        return False

    def __prepare_display_string(self, s):
        reverse_s = s[::-1]
        points = []
        for i in range(len(s)):
            if reverse_s[i] in (u'.', u':'):
                points.append(i - len(points))
        clean_s = [c for c in s if c not in (u'.', u':')]
        return clean_s, tuple(points)


    # ----------------------------

    def on_update_display_timer(self):
        u"""Called by a timer which gets called every 100 ms."""

        if self.__update_message_state():
            return

        if self.main_script().show_clock:
            t = time.localtime()
            if self.main_script().show_clock == 1:
                time_string = time.strftime("%H:%M:%S   ", t).rjust(12, " ")
            elif self.main_script().show_clock == 2:
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
