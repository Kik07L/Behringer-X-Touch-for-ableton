#Embedded file name: /Users/versonator/Jenkins/live/output/Live/mac_64_static/Release/python-bundle/MIDI Remote Scripts/MackieControl/MainDisplay.py
from __future__ import absolute_import, print_function, unicode_literals
from builtins import range
from .MackieControlComponent import *

class MainDisplay(MackieControlComponent):
    u""" Representing one main 2 row display of a Mackie Control or Extension
    """

    def __init__(self, main_script):
        MackieControlComponent.__init__(self, main_script)
        self.__stack_offset = 0
        self.__last_send_messages = [[], []]

    def destroy(self):
        NUM_CHARS_PER_DISPLAY_LINE = 56
        upper_message = u'Ableton Live '.center(NUM_CHARS_PER_DISPLAY_LINE)
        self.send_display_string(upper_message, 0, 0)
        lower_message = u' Offline'.center(NUM_CHARS_PER_DISPLAY_LINE)
        self.send_display_string(lower_message, 1, 0)
        self.send_colors((0, 0, 0, 6, 6, 0, 0, 0))
        MackieControlComponent.destroy(self)

    def stack_offset(self):
        return self.__stack_offset

    def set_stack_offset(self, offset):
        u"""This is the offset that one gets by 'stacking' several MackieControl XTs:
           the first is at index 0, the second at 8, etc ...
        """
        self.__stack_offset = offset

    def send_display_string(self, display_string, display_row, cursor_offset):
        if display_row == 0:
            offset = cursor_offset
        elif display_row == 1:
            offset = NUM_CHARS_PER_DISPLAY_LINE + 2 + cursor_offset
        else:
            assert 0
        message_string = [ ord(c) for c in display_string ]
        for i in range(len(message_string)):
            if message_string[i] >= 128:
                message_string[i] = 0

        if self.__last_send_messages[display_row] != message_string:
            self.__last_send_messages[display_row] = message_string
            if self.main_script().is_extension():
                device_type = SYSEX_DEVICE_TYPE_XT
            else:
                device_type = SYSEX_DEVICE_TYPE
            display_sysex = (240,
             0,
             0,
             102,
             device_type,
             18,
             offset) + tuple(message_string) + (247,)
            self.send_midi(display_sysex)

    def send_colors(self, colors):
        if self.main_script().is_extension():
            device_type = SYSEX_DEVICE_TYPE_XT
        else:
            device_type = SYSEX_DEVICE_TYPE
        colors_sysex = (240,
         0,
         0,
         102,
         device_type,
         114) + colors + (247,)
        self.send_midi(colors_sysex)

    def color_distance(self, color1, color2):
        return ((color1[0] - color2[0]) ** 2) + ((color1[1] - color2[1]) ** 2) + ((color1[2] - color2[2]) ** 2)

    def match_color(self, trackRGBint):
        track_R = (trackRGBint >> 16) & 255
        track_G = (trackRGBint >> 8) & 255
        track_B = trackRGBint & 255
        if (track_R <= 60 and track_G <= 60 and track_B <= 60): #Ableton Live's black swatch or darker
            return 0
        elif (track_R == track_G and track_G == track_B): #grayscale defaults to white
            return 7
        trackRGB = (track_R, track_G, track_B)
#        colors_compare_list = []
        colors_compare_list = [195075] #exclude black by setting first value to highest possible
#        colors_compare_list.append(self.color_distance(trackRGB, scribble_black)) #exclude black from comparison (only true black should get a black scribble script)
        colors_compare_list.append(self.color_distance(trackRGB, scribble_red))
        colors_compare_list.append(self.color_distance(trackRGB, scribble_green))
        colors_compare_list.append(self.color_distance(trackRGB, scribble_yellow))
        colors_compare_list.append(self.color_distance(trackRGB, scribble_blue))
        colors_compare_list.append(self.color_distance(trackRGB, scribble_fuchsia))
        colors_compare_list.append(self.color_distance(trackRGB, scribble_teal))
        colors_compare_list.append(self.color_distance(trackRGB, scribble_white))
        closest = min(colors_compare_list)
        return colors_compare_list.index(closest)

    def refresh_state(self):
        self.__last_send_messages = [[], []]

    def on_update_display_timer(self):
        pass
