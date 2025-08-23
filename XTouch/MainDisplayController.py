#Embedded file name: /Users/versonator/Jenkins/live/output/Live/mac_64_static/Release/python-bundle/MIDI Remote Scripts/MackieControl/MainDisplayController.py
from __future__ import absolute_import, print_function, unicode_literals
from builtins import str
from builtins import range
from .MackieControlComponent import *

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
        for display in self.__displays:
            if self.__channel_strip_mode:
                upper_string = u''
                lower_string = u''
                color_list = []
                assignment_mode_colors = (7, 6, 7, 3, 4)
                track_index_range = range(self.__bank_channel_offset + display.stack_offset(), self.__bank_channel_offset + display.stack_offset() + NUM_CHANNEL_STRIPS)
                if self.__show_return_tracks:
                    tracks = self.song().return_tracks
                else:
                    tracks = self.visible_tracks_including_chains()
                for t in track_index_range:
                    if self.__parameters and self.__show_parameter_names:
                        if self.__parameters[strip_index][1]:
                            upper_string += self.__generate_6_char_string(self.__parameters[strip_index][1])
                            if assignment_mode == CSM_SENDS_SINGLE:
                                if isinstance(tracks[t], Live.Track.Track):
                                    curr_color = display.match_color(self.song().return_tracks[channel_strip_controller.chosen_send].color)
                                elif isinstance(tracks[t], Live.Chain.Chain):
                                    curr_color = display.match_color(tracks[t].canonical_parent.return_chains[channel_strip_controller.chosen_send].color)
                            elif assignment_mode == CSM_SENDS:
                                if self.song().view.selected_chain:
                                    curr_color = display.match_color(self.song().view.selected_chain.canonical_parent.return_chains[t].color)
                                else:
                                    curr_color = display.match_color(self.song().return_tracks[t].color)
                            else:
                                curr_color = assignment_mode_colors[assignment_mode]
                            # if self.__chosen_send_color:
                                # curr_color = display.match_color(self.__chosen_send_color) #if in Single Send mode, show the color of the currently edited return track
                            # else:
                                # curr_color = assignment_mode_colors[assignment_mode]
                        else:
                            upper_string += self.__generate_6_char_string(u'')
                            curr_color = 0
                    elif t < len(tracks):
                        upper_string += self.__generate_6_char_string(tracks[t].name)
                        curr_color = display.match_color(tracks[t].color)
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

#                if (assignment_mode == CSM_PLUGINS):
#                    color_tuple = (3, 3, 3, 3, 3, 3, 3, 3)
#                elif (assignment_mode == CSM_SENDS):
#                    color_tuple = (6, 6, 6, 6, 6, 6, 6, 6)
#                else:
#                    color_tuple = tuple(color_list)
                color_tuple = tuple(color_list)
                display.send_colors(color_tuple)


            else:
                ascii_message = u'< _1234 guck ma #!?:;_ >'
                if not self.__test:
                    self.__test = 0
                self.__test = self.__test + 1
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
