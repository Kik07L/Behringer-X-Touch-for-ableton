#Embedded file name: /Users/versonator/Jenkins/live/output/Live/mac_64_static/Release/python-bundle/MIDI Remote Scripts/MackieControl/MainDisplayController.py
from __future__ import absolute_import, print_function, unicode_literals
from builtins import str
from builtins import range
from .MackieControlComponent import *
import math
import colorsys
import time

class ColorAlternator(object):
    def __init__(self):
        self._frame_index = 0
        self._last_update_time = 0
        self._last_mix_tuple = None

    def next_frame(self, mix_tuple):
        """
        mix_tuple: tuple of 8 mixes (each a tuple of 1,2,3 indices).
        Returns a single 8-tuple of indices for this frame.
        """
        # reset frame index if input has changed
        # if mix_tuple != self._last_mix_tuple:
            # self._frame_index = 0
            # self._last_mix_tuple = mix_tuple

        frame = []
        now = time.time()
        # if (now - self._last_update_time) > 0.001:
        for mix in mix_tuple:
            if not mix:
                frame.append(7)  # fallback: white
            else:
                frame.append(mix[self._frame_index % len(mix)])
        self._frame_index += 1
        self._last_update_time = now
        return tuple(frame)
        # else:
            # return None

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
        self.__bank_channel_offset = 0
        self.__meters_enabled = False
        self.__show_return_tracks = False
        self._alternator = ColorAlternator()
        self._last_display_time = None
        self._display_intervals = []
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

    def on_update_display_timer(self):
        channel_strip_controller = self.main_script.get_channel_strip_controller()
        assignment_mode = channel_strip_controller.assignment_mode()
        strip_index = 0

        if self.main_script.debug_show_display_update_interval:
            now = time.time()
            if self._last_display_time is not None:
                interval = now - self._last_display_time
                self._display_intervals.append(interval)

                # keep only the last 100 samples
                if len(self._display_intervals) > 100:
                    self._display_intervals.pop(0)

                # debug message (ms)
                avg = sum(self._display_intervals) / len(self._display_intervals)
                self.main_script.time_display().show_priority_message(
                    f"{interval*1000:>5.1f} {avg*1000:>5.1f}"
                )
            self._last_display_time = now

        for display_index, display in enumerate(self.__displays):
            if self.__channel_strip_mode:
                upper_string = u''
                lower_string = u''
                color_list = []
                assignment_mode_colors = (RGB_WHITE, RGB_CYAN, RGB_WHITE, RGB_YELLOW, RGB_BLUE)  # fallback in case channel colors are unavailable
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
                                curr_color = self.int_to_rgb(raw_color)
                        else:
                            upper_string += self.__generate_6_char_string(u'')
                            curr_color = None

                    elif t < len(tracks):
                        upper_string += self.__generate_6_char_string(tracks[t].name)
                        # upper_string += self.color_int_to_hex(tracks[t].color)
                        raw_color = tracks[t].color
                        curr_color = self.int_to_rgb(raw_color)
                    else:
                        curr_color = None
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
                display._last_color_tuple = color_tuple
                matched_tuple = self._match_colors(color_tuple)
                display.send_colors(matched_tuple)

            else:
                ascii_message = u'< _1234 guck ma #!?:;_ >'
                if not self.__test:
                    self.__test = 0
                self.__test += 1
                if self.__test > NUM_CHARS_PER_DISPLAY_LINE - len(ascii_message):
                    self.__test = 0
                self.send_display_string(ascii_message, 0, self.__test)

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

    def int_to_rgb(self, color_int):
        """Convert Ableton Live's 0xRRGGBB color int to (r,g,b)."""
        r = (color_int >> 16) & 0xFF
        g = (color_int >> 8) & 0xFF
        b = color_int & 0xFF
        return (r, g, b)

    def color_int_to_hex(self, color_int):
        """Convert Ableton Live's track.color int (0x00RRGGBB) to 'RRGGBB' hex."""
        return f"{color_int:06X}"

    def _match_colors(self, rgb_tuple, with_mixes=False):
        """
        Map a tuple of 8 (r,g,b) colors to X-Touch indices.
        Normal mode: flat 8-tuple of ints.
        Inspection mode (with_mixes=True): 8-tuple of mixes (tuples of 1–3 ints).
        """
        results = []
        mode = self.main_script.get_color_distance_mode()
        black_strips = self.main_script.color_off_mode_hide_inactive_channel_strips

        # Palette & metric by mode
        if with_mixes:
            # palette = PALETTE_27
            palette = PALETTE_EXTENDED
            metric = "hue"
            black_cutoff = 0.3
            white_cutoff = 0
            inactive_color = 0
        elif mode == 0:  # RGB
            palette = PALETTE_8
            metric = "rgb"
            black_cutoff = 0.3
            white_cutoff = 0
            inactive_color = 0
        elif mode == 1:  # Hue
            palette = PALETTE_6
            metric = "hue"
            black_cutoff = 0.3
            white_cutoff = self.main_script.get_hue_color_distance_mode_white_cutoff()
            inactive_color = 0
        elif mode == 2:  # Off
            black_cutoff = 0
            white_cutoff = 1
            inactive_color = 0 if black_strips else 7
        else:
            palette = PALETTE_8
            metric = "rgb"
            black_cutoff = 0.3
            white_cutoff = 0
            inactive_color = 0

        for idx, rgb in enumerate(rgb_tuple):
            if rgb == None:
                matched = (inactive_color,) if with_mixes else inactive_color
                results.append(matched)
                continue
            cached = self._get_cached_color(rgb, mode, white_cutoff, with_mixes)
            if cached is not None:
                results.append(cached)
                continue

            # Convert to hex for quick override check
            hexval = f"{(rgb[0]<<16 | rgb[1]<<8 | rgb[2]):06X}"
            if with_mixes and hexval in OVERRIDE_MAP:
                results.append(OVERRIDE_MAP[hexval])
                continue

            # Convert to HSV
            r, g, b = [c/255.0 for c in rgb]
            h, s, v = colorsys.rgb_to_hsv(r, g, b)

            # Black / White cutoffs
            if v < black_cutoff:
                matched = (0,) if with_mixes else 0
            elif s <= white_cutoff:
                matched = (7,) if with_mixes else 7
            else:
                # """ Saturation boost turned off for now (helped against colors being fairly light, but also reduced number of different colors)
                # Saturation boost in party trick mode
                if with_mixes:
                    bias = self.main_script.color_mix_mode_saturation_boost / 100.0
                    # v = max(v, bias) # straight bottom cap
                    # s = max(s, bias) # straight bottom cap
                    v = v + (1.0 - v) * bias  # bias value upwards for party trick color mix mode
                    s = s + (1.0 - s) * bias  # bias saturation upwards for party trick color mix mode

                    # back-convert to RGB so downstream still sees (r,g,b) ints
                    rgb = tuple(int(x*255) for x in colorsys.hsv_to_rgb(h, s, v))
                    # """

                matched = self._map_palette(rgb, palette, with_mixes, metric)

            # Store in cache
            self._set_cached_color(rgb, mode, white_cutoff, with_mixes, matched)
            results.append(matched)

        return tuple(results)

    def _map_palette(self, rgb, palette, with_mixes, metric="rgb"):
        best_entry = min(palette, key=lambda entry: self._distance(rgb, entry, metric))
        return best_entry.mix if with_mixes else best_entry.mix[0]

    def _distance(self, rgb, entry, metric="rgb"):
        if metric == "rgb":
            er, eg, eb = entry.rgb
            base_dist = ((rgb[0] - er) ** 2 +
                         (rgb[1] - eg) ** 2 +
                         (rgb[2] - eb) ** 2)
        elif metric == "hue":
            r, g, b = [c/255.0 for c in rgb]
            h1, s1, v1 = colorsys.rgb_to_hsv(r, g, b)
            h2, s2, v2 = entry.hsv
            h1, h2 = h1 * 360, h2 * 360
            dh = min(abs(h1 - h2), 360 - abs(h1 - h2))
            base_dist = (dh / 180.0) ** 2 + (s1 - s2) ** 2 + (v1 - v2) ** 2
        else:
            return 0
        """
        # ---- bias against mixes ----
        if len(entry.mix) > 2:
            penalty = 1.15  # +15% distance if it's a 3-way mix
        elif len(entry.mix) > 1:
            penalty = 1.10  # +10% distance if it's a 2-way mix
        else:
            penalty = 1.00
        base_dist *= penalty
        """
        return base_dist
        
    def _get_cached_color(self, raw_rgb, mode, white_cutoff, with_mixes):
        """
        Return cached result if input hasn't changed.
        Cache key includes mode, white cutoff, and with_mixes flag.
        """
        key = (raw_rgb, mode, white_cutoff, with_mixes)
        last = getattr(self, "_last_color_inputs", None)
        if last is None:
            self._last_color_inputs = {}
            return None

        return self._last_color_inputs.get(key)


    def _set_cached_color(self, raw_rgb, mode, white_cutoff, with_mixes, matched):
        """
        Store match result in cache.
        """
        if not hasattr(self, "_last_color_inputs"):
            self._last_color_inputs = {}

        key = (raw_rgb, mode, white_cutoff, with_mixes)
        self._last_color_inputs[key] = matched

    def _party_trick(self):
        color_tuple = tuple(
            rgb for display in self.__displays
            for rgb in display._last_color_tuple
        )
        matched_tuple = self._match_colors(color_tuple, with_mixes=True)
        interval = self.main_script.color_mix_mode_interval / 1000 # delay time to respect MIDI hardware limitations (default: 0.02)
        times = int(2000 // self.main_script.color_mix_mode_interval) # make sure the effect lasts 2 seconds, regardless of the interval
                
        for i in range(times):
            frame = self._alternator.next_frame(matched_tuple)
            for display_index, display in enumerate(self.__displays):
                now = time.time()
                start = display_index * 8
                end = display_index * 8 + 8
                display.send_colors(frame[start:end])
            time.sleep(interval)
