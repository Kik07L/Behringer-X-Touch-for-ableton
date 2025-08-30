#Embedded file name: /Users/versonator/Jenkins/live/output/Live/mac_64_static/Release/python-bundle/MIDI Remote Scripts/MackieControl/MainDisplay.py
from __future__ import absolute_import, print_function, unicode_literals
from builtins import range
from .MackieControlComponent import *
import math
import colorsys

class MainDisplay(MackieControlComponent):
    u""" Representing one main 2 row display of a Mackie Control or Extension
    """

    def __init__(self, main_script):
        MackieControlComponent.__init__(self, main_script)
        self.__stack_offset = 0
        self.__last_send_messages = [[], []]
        self.__last_send_colors = []

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
        if self.__last_send_colors != colors:
            self.__last_send_colors = colors
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

    def map_to_xtouch_color(self, rgb):
        r, g, b = [x/255.0 for x in rgb]
        h, s, v = colorsys.rgb_to_hsv(r, g, b)  # h in [0..1], s/v in [0..1]
        h_deg = h * 360

        # thresholds (tweakable)
        if v < 0.2:
            return "black"
        if s < 0.2:
            return "white"

        # nearest hue among 6 primaries
        hue_map = {
            "red": 0,
            "yellow": 60,
            "green": 120,
            "cyan": 180,
            "blue": 240,
            "magenta": 300
        }
        nearest = min(hue_map.items(), key=lambda kv: min(abs(h_deg - kv[1]), 360 - abs(h_deg - kv[1])))
        return nearest[0]

    def hsv_distance(self, c1, c2):
        # convert RGB (0-255) to HSV
        r1, g1, b1 = [x/255.0 for x in c1]
        r2, g2, b2 = [x/255.0 for x in c2]
        h1, s1, v1 = colorsys.rgb_to_hsv(r1, g1, b1)
        h2, s2, v2 = colorsys.rgb_to_hsv(r2, g2, b2)

        # hues are 0..1, map to degrees
        h1, h2 = h1 * 360, h2 * 360

        # shortest angular distance
        dh = min(abs(h1 - h2), 360 - abs(h1 - h2))

        # weigh hue most strongly, sat/value lightly
        return (dh / 180.0) ** 2 + (s1 - s2) ** 2 + (v1 - v2) ** 2

    def color_distance(self, color1, color2):
        if self.main_script().get_alternative_color_distance_mode():
            # hue-first perceptual distance
#            return self.hsv_distance(color1, color2)
            # categorical: return 0 if same bin, 1 if different
            return 0 if self.map_to_xtouch_color(color1) == self.map_to_xtouch_color(color2) else 1
        else:
            # fast RGB squared distance
            return ((color1[0] - color2[0]) ** 2) + \
                   ((color1[1] - color2[1]) ** 2) + \
                   ((color1[2] - color2[2]) ** 2)

    # def color_distance(self, color1, color2):
        # if self.main_script().alternative_color_distance_mode(): #activated by SHIFT + DISPLAY/NAME/VALUE; however, only two colors (Vista Blue and Pomelo Green) yield a different result, so not worth the extra compute
            # r_mean = (color1[0] + color2[0]) / 2
            # r_diff = (color1[0] - color2[0])
            # g_diff = (color1[1] - color2[1])
            # b_diff = (color1[2] - color2[2])
            # return math.sqrt(((2 + (r_mean / 256)) * (r_diff ** 2)) + (4 * (g_diff ** 2)) + ((2 + ((255 - r_mean) / 256)) * (b_diff ** 2)))
        # else:
            # return ((color1[0] - color2[0]) ** 2) + ((color1[1] - color2[1]) ** 2) + ((color1[2] - color2[2]) ** 2)

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
        colors_compare_list.append(self.color_distance(trackRGB, scribble_magenta))
        colors_compare_list.append(self.color_distance(trackRGB, scribble_cyan))
        colors_compare_list.append(self.color_distance(trackRGB, scribble_white))
        closest = min(colors_compare_list)
        return colors_compare_list.index(closest)

    def refresh_state(self):
        self.__last_send_messages = [[], []]
        self.__last_send_colors = []

    def on_update_display_timer(self):
        pass
