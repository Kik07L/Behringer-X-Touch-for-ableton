#Embedded file name: /Users/versonator/Jenkins/live/output/Live/mac_64_static/Release/python-bundle/MIDI Remote Scripts/MackieControl/MainDisplayController.py
from __future__ import absolute_import, print_function, unicode_literals
from builtins import str
from builtins import range
from .MackieControlComponent import *
import math
import colorsys

class MainDisplayController(MackieControlComponent):
    u""" Controlling all available main displays (the display above the channel strips),
        which will be only one when only using the 'main' Mackie Control, and severals
        when using at least one Mackie Control XT, attached to the main Mackie Control
    
        The Displays can be run in two modes: Channel and Global mode:
        - In channel mode 2*6 characters can be shown for each channel strip
        - In global mode, you can setup the two 54 charchter lines to whatever you want
    
        See 'class ChannelStripController' for descriptions of the stack_index or details
        about the different assignment modes.
    """

    def __init__(self, main_script, display):
        MackieControlComponent.__init__(self, main_script)
        self.__left_extensions = []
        self.__right_extensions = []
        self.__displays = [display]
        self.__own_display = display
        self.__parameters = [ [] for x in range(NUM_CHANNEL_STRIPS) ]
        self.__channel_strip_strings = [ u'' for x in range(NUM_CHANNEL_STRIPS) ]
        self.__channel_strip_mode = True
        self.__show_parameter_names = False
        #self.__chosen_send_color = None
        self.__bank_channel_offset = 0
        self.__meters_enabled = False
        self.__show_return_tracks = False
        self.__last_color_inputs = {}
#
        super().__init__(main_script)
        self.main_script = main_script  # Save reference


    def destroy(self):
        self.enable_meters(False)
        MackieControlComponent.destroy(self)

    def set_controller_extensions(self, left_extensions, right_extensions):
        u""" Called from the main script (after all scripts where initialized), to let us
            know where and how many MackieControlXT are installed.
        """
        self.__left_extensions = left_extensions
        self.__right_extensions = right_extensions
        self.__displays = []
        stack_offset = 0
        for le in left_extensions:
            self.__displays.append(le.main_display())
            le.main_display().set_stack_offset(stack_offset)
            stack_offset += NUM_CHANNEL_STRIPS

        self.__displays.append(self.__own_display)
        self.__own_display.set_stack_offset(stack_offset)
        stack_offset += NUM_CHANNEL_STRIPS
        for re in right_extensions:
            self.__displays.append(re.main_display())
            re.main_display().set_stack_offset(stack_offset)
            stack_offset += NUM_CHANNEL_STRIPS

        self.__parameters = [ [] for x in range(len(self.__displays) * NUM_CHANNEL_STRIPS) ]
        self.__channel_strip_strings = [ u'' for x in range(len(self.__displays) * NUM_CHANNEL_STRIPS) ]
        self.refresh_state()

    def enable_meters(self, enabled):
        if self.__meters_enabled != enabled:
            self.__meters_enabled = enabled
            self.refresh_state()

    def set_show_parameter_names(self, enable):
        self.__show_parameter_names = enable
        #self.__chosen_send_color = None

    # def set_chosen_send_color(self, chosen_send_color):
        # self.__chosen_send_color = chosen_send_color

    def set_channel_offset(self, channel_offset):
        self.__bank_channel_offset = channel_offset

    def parameters(self):
        return self.__parameters

    def set_parameters(self, parameters):
        if parameters:
            self.set_channel_strip_strings(None)
        for d in self.__displays:
            self.__parameters = parameters

    def channel_strip_strings(self):
        return self.__channel_strip_strings

    def set_channel_strip_strings(self, channel_strip_strings):
        if channel_strip_strings:
            self.set_parameters(None)
        self.__channel_strip_strings = channel_strip_strings

    def set_show_return_track_names(self, show_returns):
        self.__show_return_tracks = show_returns

    def refresh_state(self):
        for d in self.__displays:
            d.refresh_state()

    def _get_cached_color(self, display_index, t, raw_color):
        """Return cached match_color() result if raw_color hasn't changed
        and color distance mode is the same."""
        current_mode = self.main_script.get_color_distance_mode()
        current_white_cutoff = self.main_script.get_hue_color_distance_mode_white_cutoff()

        # if mode changed, invalidate cache
        if getattr(self, "_last_color_mode", None) != current_mode:
            self.__last_color_inputs.clear()
            self._last_color_mode = current_mode

        # if white cutoff changed, invalidate cache
        if getattr(self, "_last_white_cutoff", None) != current_white_cutoff:
            self.__last_color_inputs.clear()
            self._last_white_cutoff = current_mode

        key = (display_index, t)
        last = self.__last_color_inputs.get(key)
        if last and last[0] == raw_color:
            return last[1]
        else:
            matched = self.match_color(raw_color)
            self.__last_color_inputs[key] = (raw_color, matched)
            return matched

    def on_update_display_timer(self):
        channel_strip_controller = self.main_script.get_channel_strip_controller()
        assignment_mode = channel_strip_controller.assignment_mode()
        strip_index = 0
        valid_keys = set()   # collect all (display_index, t) used this run

        for display_index, display in enumerate(self.__displays):
            if self.__channel_strip_mode:
                upper_string = u''
                lower_string = u''
                color_list = []
                assignment_mode_colors = (7, 6, 7, 3, 4)  # fallback in case channel colors are unavailable
                track_index_range = range(
                    self.__bank_channel_offset + display.stack_offset(),
                    self.__bank_channel_offset + display.stack_offset() + NUM_CHANNEL_STRIPS
                )

                if self.__show_return_tracks:
                    tracks = self.song().return_tracks
                else:
                    tracks = self.visible_tracks_including_chains()

                for t in track_index_range:
                    raw_color = None
                    key = (display_index, t)
                    valid_keys.add(key)   # mark as used this run

                    if self.__parameters and self.__show_parameter_names:
                        if self.__parameters[strip_index][1]:
                            upper_string += self.__generate_6_char_string(self.__parameters[strip_index][1])
                            if assignment_mode == CSM_SENDS_SINGLE:
                                if isinstance(tracks[t], Live.Track.Track):
                                    raw_color = self.song().return_tracks[channel_strip_controller.chosen_send].color
                                elif isinstance(tracks[t], Live.Chain.Chain):
                                    raw_color = tracks[t].canonical_parent.return_chains[
                                        channel_strip_controller.chosen_send
                                    ].color
                            elif assignment_mode == CSM_SENDS:
                                if (self.song().view.selected_chain and
                                    t < len(self.song().view.selected_chain.canonical_parent.return_chains)):
                                    raw_color = self.song().view.selected_chain.canonical_parent.return_chains[t].color
                                elif t < len(self.song().return_tracks):
                                    raw_color = self.song().return_tracks[t].color
                            else:
                                curr_color = assignment_mode_colors[assignment_mode]
                            if raw_color is not None:
                                curr_color = self._get_cached_color(display_index, t, raw_color)
                        else:
                            upper_string += self.__generate_6_char_string(u'')
                            curr_color = 0

                    elif t < len(tracks):
                        upper_string += self.__generate_6_char_string(tracks[t].name)
                        raw_color = tracks[t].color
                        curr_color = self._get_cached_color(display_index, t, raw_color)
                    else:
                        curr_color = 0
                        upper_string += self.__generate_6_char_string(u'')

                    color_list.append(curr_color)
                    upper_string += u' '

                    if self.__parameters and self.__parameters[strip_index]:
                        if self.__parameters[strip_index][0]:
                            lower_string += self.__generate_6_char_string(str(self.__parameters[strip_index][0]))
                        else:
                            lower_string += self.__generate_6_char_string(u'')
                    elif self.__channel_strip_strings and self.__channel_strip_strings[strip_index]:
                        lower_string += self.__generate_6_char_string(self.__channel_strip_strings[strip_index])
                    else:
                        lower_string += self.__generate_6_char_string(u'')
                    lower_string += u' '
                    strip_index += 1

                display.send_display_string(upper_string, 0, 0)
                if not self.__meters_enabled:
                    display.send_display_string(lower_string, 1, 0)

                color_tuple = tuple(color_list)
                display.send_colors(color_tuple)

            else:
                ascii_message = u'< _1234 guck ma #!?:;_ >'
                if not self.__test:
                    self.__test = 0
                self.__test += 1
                if self.__test > NUM_CHARS_PER_DISPLAY_LINE - len(ascii_message):
                    self.__test = 0
                self.send_display_string(ascii_message, 0, self.__test)

        self.__last_color_inputs = {
            k: v for k, v in self.__last_color_inputs.items() if k in valid_keys
        }

    def __generate_6_char_string(self, display_string):
        if not display_string:
            return u'      '
        if len(display_string.strip()) > 6 and display_string.endswith(u'dB') and display_string.find(u'.') != -1:
            display_string = display_string[:-2]
        if len(display_string) > 6:
            for um in [u' ',
             u'i',
             u'o',
             u'u',
             u'e',
             u'a']:
                while len(display_string) > 6 and display_string.rfind(um, 1) != -1:
                    um_pos = display_string.rfind(um, 1)
                    display_string = display_string[:um_pos] + display_string[um_pos + 1:]

        else:
            display_string = display_string.center(6)
        ret = u''
        for i in range(6):
            ret += display_string[i]

        assert len(ret) == 6
        return ret

    def map_to_xtouch_color(self, rgb):
        r, g, b = [x/255.0 for x in rgb]
        h, s, v = colorsys.rgb_to_hsv(r, g, b)  # h in [0..1], s/v in [0..1]
        h_deg = h * 360

        # thresholds (tweakable)
        if v < 0.2:
            return "black"
#        if s < 0.2:
        if s < self.main_script.get_hue_color_distance_mode_white_cutoff():
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
        if self.main_script.get_color_distance_mode() == 1:  # hue-first mode
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
