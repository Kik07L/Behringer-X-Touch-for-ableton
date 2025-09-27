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
        # self.main_script().show_clock = 0
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

    def __prepare_display_string(self, s, align_left=True):
        """Return (clean_chars_list, points_positions_tuple) ready for __send_time_string.
        - Converts to str
        - Extracts decimal points/colons as LED points
        - Pads/trims to exactly 10 character *cells* (post-clean)
        - Keeps messages left-aligned by default (pad right) while preserving point positions
        """
        s = str(s)
        # Determine LED points from the raw string (before stripping)
        reverse_s = s[::-1]
        points = []
        for i in range(len(s)):
            if reverse_s[i] in (u'.', u':'):
                points.append(i - len(points))

        # Remove characters that map to LED points
        clean = [c for c in s if c not in (u'.', u':')]

        # Normalize to exactly 10 display cells
        if len(clean) < 10:
            pad = 10 - len(clean)
            if align_left:
                # Left-aligned text => pad on the RIGHT.
                clean = clean + [u' '] * pad
                # Dots are indexed from the rightmost cell (c=0).
                # Adding cells on the RIGHT shifts all existing digits left,
                # so each dot's position increases by 'pad'.
                points = [p + pad for p in points]
            else:
                # Right-aligned text => pad on the LEFT.
                clean = [u' '] * pad + clean
                # No shift needed because rightmost anchor stays fixed.
        elif len(clean) > 10:
            # Keep the rightmost 10 cells (consistent with c=0 being rightmost).
            clean = clean[-10:]
            # Drop any points that would fall outside 0..9 after trimming.
            points = [p for p in points if 0 <= p <= 9]

        return clean, tuple(points)

    def show_message(self, msg, duration=2000, align_left=True):
        """Queue a message to display for <duration> ms."""
        if msg is None:
            return
        time_string, points = self.__prepare_display_string(msg, align_left=align_left)
        expire_time = time.time() + (duration / 1000.0)
        self.__message_queue.append((time_string, points, expire_time))

    def show_priority_message(self, msg, duration=2000, align_left=True):
        """Show a message immediately, interrupting current/queued ones."""
        if msg is None:
            return
        time_string, points = self.__prepare_display_string(msg, align_left=align_left)
        expire_time = time.time() + (duration / 1000.0)
        # Clear queue and override current
        self.__message_queue = []
        self.main_script().transport().save_preferences_and_exit()
        self.__current_message = (time_string, points)
        self.__message_expire = expire_time
        self.__send_time_string(time_string, points_positions=points)

    def show_permanent_message(self, msg, align_left=True):
        """Show a message immediately, interrupting current/queued ones."""
        if msg is None:
            return
        time_string, points = self.__prepare_display_string(msg, align_left=align_left)
        # Clear queue and override current
        self.__message_queue = []
        self.__current_message = (time_string, points)
        self.__message_expire = time.time() + 9999
        self.__send_time_string(time_string, points_positions=points)

    def __update_message_state(self):
        now = time.time()
        if self.__current_message and now < self.__message_expire:
            return True
        else:
            if self.__current_message:
                # just expired, force refresh
                self.__last_send_time = []
            self.__current_message = None
        if self.__message_queue:
            msg_chars, msg_points, exp = self.__message_queue.pop(0)
            self.__current_message = (msg_chars, msg_points)
            self.__message_expire = exp
            self.__send_time_string(msg_chars, points_positions=msg_points)
            return True
        return False

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
        # Normalize to exactly 10 characters and clamp point positions
        if len(time_string) < 10:
            pad = 10 - len(time_string)
            # Pad LEFT to preserve rightmost anchoring used by the hardware
            time_string = [u' '] * pad + time_string
        elif len(time_string) > 10:
            time_string = time_string[-10:]

        # Ensure points are within 0..9
        if points_positions:
            points_positions = tuple(p for p in points_positions if 0 <= p <= 9)

        assert len(time_string) == 10
        for c in range(0, 10):
            char = time_string[9 - c].upper()
            char_code = g7_seg_led_conv_table.get(char, g7_seg_led_conv_table[' '])
            if c in points_positions:
                char_code += 64
            self.send_midi((176, 64 + c, char_code))
