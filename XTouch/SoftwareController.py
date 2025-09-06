#Embedded file name: /Users/versonator/Jenkins/live/output/Live/mac_64_static/Release/python-bundle/MIDI Remote Scripts/MackieControl/SoftwareController.py
from __future__ import absolute_import, print_function, unicode_literals
from .MackieControlComponent import *

class SoftwareController(MackieControlComponent):
    u"""Representing the buttons above the transport, including the basic: """

    def __init__(self, main_script):
        MackieControlComponent.__init__(self, main_script)
        self.__last_can_undo_state = False
        self.__last_can_redo_state = False
        self.__selected_track_group_state = 0
        self.__master_track_selected_state = False
        av = self.application().view
        #self.night_mode_on = False
        self.__assign_mutable_buttons()
        self.__leds_flashing = False
        av.add_is_view_visible_listener(u'Session', self.__update_session_arranger_button_led)
        av.add_is_view_visible_listener(u'Detail/Clip', self.__update_detail_sub_view_button_led)
        av.add_is_view_visible_listener(u'Browser', self.__update_browser_button_led)
        av.add_is_view_visible_listener(u'Detail', self.__update_detail_button_led)
        self.song().view.add_draw_mode_listener(self.__update_draw_mode_button_led)
        self.song().add_back_to_arranger_listener(self.__update_back_to_arranger_button_led)
        self.song().add_can_capture_midi_listener(self.__update_capture_midi_button_led) #
        self.song().add_session_automation_record_listener(self.__update_automation_record_button_led)
        self.song().add_re_enable_automation_enabled_listener(self.__update_re_enable_automation_enabled_button_led)
        self.song().add_arrangement_overdub_listener(self.__update_arrangement_overdub_button_led)
        self.song().add_midi_recording_quantization_listener(self._update_function_keys_leds)
        self.__update_automation_record_button_led()
        #self.update_outputs_button_led()
#        self.__quantization_strings = ("quant:  0ff", "1'4", "1'8", "1'8T", "1'8 1'8T", "1'16", "1'16T", "1'16 1'16T", "1'32")
        self.__quantization_strings = ("quant: 0ff", "quant: 4", "quant: 8", "quant: 8T", "quant: 8 8T", "quant:16", "quant:16T", "quant:1616T", "quant:32")
        self.__save_current_view(False)
        #self.__toggle_user_button_mapping()
        
    def destroy(self):
        av = self.application().view
        av.remove_is_view_visible_listener(u'Session', self.__update_session_arranger_button_led)
        av.remove_is_view_visible_listener(u'Detail/Clip', self.__update_detail_sub_view_button_led)
        av.remove_is_view_visible_listener(u'Browser', self.__update_browser_button_led)
        av.remove_is_view_visible_listener(u'Detail', self.__update_detail_button_led)
        self.song().view.remove_draw_mode_listener(self.__update_draw_mode_button_led)
        self.song().remove_back_to_arranger_listener(self.__update_back_to_arranger_button_led)
        self.song().remove_can_capture_midi_listener(self.__update_capture_midi_button_led)
        self.song().remove_arrangement_overdub_listener(self.__update_arrangement_overdub_button_led)
        self.song().remove_midi_recording_quantization_listener(self._update_function_keys_leds)
        for note in software_controls_switch_ids:
            self.send_button_led(note, BUTTON_STATE_OFF)

        for note in function_key_control_switch_ids:
            self.send_button_led(note, BUTTON_STATE_OFF)
    
        for note in modify_key_control_switch_ids:
            self.send_button_led(note, BUTTON_STATE_OFF)

        MackieControlComponent.destroy(self)

    def instance(self):
        """Return self for public access."""
        return self

    def handle_function_key_switch_ids(self, switch_id, value):
        if value == BUTTON_PRESSED:
            if self.shift_is_pressed():
                spec = self.main_script()._preferences_spec["USE_FUNCTION_BUTTONS"]
                default, parser, comment, formatter, short_name, choices_or_limits = spec
                selector = (switch_id - SID_SOFTWARE_F1)
                # Only allow values defined in choices_or_limits
                if selector in choices_or_limits:
                    self.main_script().use_function_buttons = selector
                    self.main_script().save_preferences()
                    label = choices_or_limits[selector]
                    self.main_script().time_display().show_priority_message(
                        f"{short_name[:5]}.{label}", 2000
                    )
                self._update_function_keys_leds(False)
            elif (self.option_is_pressed() or self.main_script().use_function_buttons == 2) and self.song().view.selected_track and hasattr(self.song().view.selected_track, 'input_routing_type'):
                selector = (switch_id - SID_SOFTWARE_F1)
                self.set_input_type(self.song().view.selected_track, selector, self.song().view.selected_track.has_midi_input)
                self._update_function_keys_leds(False)
            elif (self.control_is_pressed() or self.alt_is_pressed() or self.main_script().use_function_buttons == 3) and self.song().view.selected_track and hasattr(self.song().view.selected_track, 'input_routing_channel'):
                selector = (switch_id - SID_SOFTWARE_F1) + (8 if self.alt_is_pressed() else 0)
                self.set_input_channel(self.song().view.selected_track, selector, self.song().view.selected_track.has_midi_input)
                self._update_function_keys_leds(False)
            elif self.main_script().use_function_buttons == 1: # quantization mode
                current_quantization = SID_SOFTWARE_F1 + self.song().midi_recording_quantization - 1
                if switch_id == current_quantization:
                    self.song().midi_recording_quantization = 0
                else:
                    self.song().midi_recording_quantization = switch_id - SID_SOFTWARE_F1 + 1
                self.main_script().time_display().show_priority_message(self.__quantization_strings[self.song().midi_recording_quantization], 1000)

    def handle_modify_key_switch_ids(self, switch_id, value):
        if switch_id == SID_MOD_SHIFT:
            self.main_script().set_shift_is_pressed(value == BUTTON_PRESSED)
        elif switch_id == SID_MOD_OPTION:
            self.main_script().set_option_is_pressed(value == BUTTON_PRESSED)
        elif switch_id == SID_MOD_CTRL:
            self.main_script().set_control_is_pressed(value == BUTTON_PRESSED)
        elif switch_id == SID_MOD_ALT:
            self.main_script().set_alt_is_pressed(value == BUTTON_PRESSED)
        if self.main_script().night_mode_on and value == BUTTON_PRESSED:
            self.__flash_leds(1)
        elif value == BUTTON_RELEASED:
            self.__flash_leds(0)
        if self.shift_is_pressed() and self.option_is_pressed() and self.control_is_pressed() and self.alt_is_pressed():
            self.__toggle_night_mode()

    def __toggle_night_mode(self):
        self.main_script().night_mode_on = not self.main_script().night_mode_on
        self.main_script().time_display().show_priority_message("night mode", 1000)
        if not self.main_script().night_mode_on:
            self.main_script().time_display().show_message("0ff", 2000)
        else:
            self.main_script().time_display().show_message("0m", 2000)
        self.main_script().save_preferences()
        self.__update_night_mode_leds()

    def __update_night_mode_leds(self):
        led_state = BUTTON_STATE_OFF
        if self.main_script().night_mode_on == True:
            led_state = BUTTON_STATE_ON
        for note in range(SID_MOD_SHIFT, SID_MOD_ALT + 1):
            self.send_button_led(note, led_state)

    def handle_touch_master_fader(self, switch_id, value):
        if value == BUTTON_PRESSED and self.main_script().touch_fader_to_select:
            self._show_master_channel(show_detail=False)

    def __flash_leds(self, onOff):
        leds_to_flash = list(transport_control_switch_ids + function_key_control_switch_ids + marker_control_switch_ids + software_controls_switch_ids + channel_strip_control_switch_ids + tuple(jog_wheel_switch_ids))
        leds_to_flash.sort()
        if onOff == 1 and self.__leds_flashing == False:
            for b in leds_to_flash:
                if BUTTON_STATES[b] == BUTTON_STATE_OFF:
                    self.send_midi((NOTE_ON_STATUS, b, BUTTON_STATE_BLINKING))
            self.__leds_flashing = True
        elif onOff == 0 and self.__leds_flashing == True:
            for b in leds_to_flash:
                self.send_midi((NOTE_ON_STATUS, b, BUTTON_STATES[b]))
            self.__leds_flashing = False

    def handle_software_controls_switch_ids(self, switch_id, value):

        # if switch_id == SID_GLOBAL_VIEW:
            # if value == BUTTON_PRESSED:
                # if self.control_is_pressed():
                    # self.__save_current_view()
                # elif self.shift_is_pressed():
                    # self.__recall_saved_view()
                # else:
                    # self.__toggle_session_arranger_is_visible()

        if switch_id == SID_SOFTWARE_MIDI_TRACKS:
            if value == BUTTON_PRESSED:
                if self.control_is_pressed():
                    self.__save_current_view()
                elif self.shift_is_pressed():
                    self.__recall_saved_view()
                else:
                    self.__toggle_session_arranger_is_visible()
        elif switch_id == SID_SOFTWARE_INPUTS:
            if value == BUTTON_PRESSED:
                self.__toggle_detail_sub_view()
        elif switch_id == SID_SOFTWARE_AUDIO_TRACKS:
            if value == BUTTON_PRESSED:
                self.__toggle_detail_is_visible()
        elif switch_id == SID_SOFTWARE_AUDIO_INST:
            if value == BUTTON_PRESSED:
                self.__toggle_browser_is_visible()
        elif switch_id == SID_SOFTWARE_AUX:
            if value == BUTTON_PRESSED:
                self.song().create_midi_track()
        elif switch_id == SID_SOFTWARE_BUSES:
            if value == BUTTON_PRESSED:
                self.song().create_audio_track()
        elif switch_id == SID_SOFTWARE_OUTPUTS:
            if value == BUTTON_PRESSED:
                self.song().create_return_track()
            # if value == BUTTON_PRESSED:
                # self._show_master_channel()

        elif switch_id == SID_AUTOMATION_READ_OFF:
            if value == BUTTON_PRESSED:
                self.song().re_enable_automation()
        elif switch_id == SID_AUTOMATION_WRITE:
            if value == BUTTON_PRESSED:
                self.__toggle_automation_record()
        elif switch_id == self.__overdub_button:
            if value == BUTTON_PRESSED:
                self.__toggle_arrangement_overdub()
        elif switch_id == SID_AUTOMATION_GROUP:
            if value == BUTTON_PRESSED:
                self.__toggle_group_mode()
        elif switch_id == SID_AUTOMATION_TOUCH:
            if value == BUTTON_PRESSED:
                self.__toggle_draw_mode()

        elif switch_id == SID_FUNC_SAVE: #
            if value == BUTTON_PRESSED: #
                self.__capture_midi() #
        elif switch_id == self.__back_to_arrangement_button:
            if value == BUTTON_PRESSED:
                self.__toggle_back_to_arranger()
        elif switch_id == SID_FUNC_UNDO:
            if value == BUTTON_PRESSED:
                self.song().undo()
        elif switch_id == SID_FUNC_ENTER:
            if value == BUTTON_PRESSED:
                self.song().redo()


    def refresh_state(self):
        self.main_script().set_shift_is_pressed(False)
        self.main_script().set_option_is_pressed(False)
        self.main_script().set_control_is_pressed(False)
        self.main_script().set_alt_is_pressed(False)
        self.__assign_mutable_buttons()
        self.__update_session_arranger_button_led()
        self.__update_detail_sub_view_button_led()
        self.__update_browser_button_led()
        self.__update_detail_button_led()
        self.__update_undo_button_led()
        self.__update_redo_button_led()
        self.__update_draw_mode_button_led()
        self.__update_back_to_arranger_button_led()
        self.__update_capture_midi_button_led() #
        self.__update_group_mode_button_led()
        #self.update_outputs_button_led()
        self.__update_night_mode_leds()
        self._update_function_keys_leds(False)
        self.__update_arrangement_overdub_button_led()
        #self.__toggle_user_button_mapping()

    def on_update_display_timer(self):
        self.__update_group_mode_button_led() #have to include here since we can't add a listener for this
        if self.__last_can_undo_state != self.song().can_undo:
            self.__last_can_undo_state = self.song().can_undo
            self.__update_undo_button_led()
        if self.__last_can_redo_state != self.song().can_redo:
            self.__last_can_redo_state = self.song().can_redo
            self.__update_redo_button_led()

    def _show_master_channel(self, show_detail=True):
        if self.song().view.selected_track != self.song().master_track:
            self.song().view.selected_track = self.song().master_track
        elif show_detail:
            self.song().master_track.view.is_collapsed = not self.song().master_track.view.is_collapsed
            #self.__toggle_detail_is_visible(focus=False)

    def __save_current_view(self, verbose=True):
        self.__saved_view_session_arranger = self.application().view.focused_document_view
        self.__saved_view_browser = self.application().view.is_view_visible(u'Browser')
        self.__saved_view_detail_clip = self.application().view.is_view_visible(u'Detail/Clip')
        self.__saved_view_detail_device_chain = self.application().view.is_view_visible(u'Detail/DeviceChain')
        self.__saved_view_detail = self.application().view.is_view_visible(u'Detail')
        if verbose:
            self.main_script().time_display().show_priority_message("Wieu sawed")

    def __recall_saved_view(self, verbose=True):
        self.application().view.focus_view(self.__saved_view_session_arranger)
        if self.__saved_view_browser:
            self.application().view.show_view(u'Browser')
        else:
            self.application().view.hide_view(u'Browser')
        if self.__saved_view_detail_clip:
            self.application().view.show_view(u'Detail/Clip')
        else:
            self.application().view.hide_view(u'Detail/Clip')
        if self.__saved_view_detail_device_chain:
            self.application().view.show_view(u'Detail/DeviceChain')
        else:
            self.application().view.hide_view(u'Detail/DeviceChain')
        if self.__saved_view_detail:
            self.application().view.show_view(u'Detail')
        else:
            self.application().view.hide_view(u'Detail')
        if verbose:
            self.main_script().time_display().show_priority_message("Wieu recal")

    def __assign_mutable_buttons(self):
        if self.main_script().get_overlay_layout():
            self.__overdub_button = SID_TRANSPORT_SOLO
            self.__back_to_arrangement_button = SID_AUTOMATION_TRIM
        else:
            self.__overdub_button = SID_AUTOMATION_TRIM
            self.__back_to_arrangement_button = SID_FUNC_CANCEL

    def __toggle_session_arranger_is_visible(self):
        if self.application().view.is_view_visible(u'Session', True):
            self.application().view.hide_view(u'Session')
        else:
            assert self.application().view.is_view_visible(u'Arranger', True)
            self.application().view.hide_view(u'Arranger')
        self.__update_session_arranger_button_led()

    def __toggle_detail_sub_view(self):
        if self.application().view.is_view_visible(u'Detail/Clip'):
            if self.shift_is_pressed():
                self.application().view.focus_view(u'Detail/Clip')
            else:
                self.application().view.show_view(u'Detail/DeviceChain')
        elif self.shift_is_pressed():
            self.application().view.focus_view(u'Detail/DeviceChain')
        else:
            self.application().view.show_view(u'Detail/Clip')

    def __toggle_browser_is_visible(self):
        if self.application().view.is_view_visible(u'Browser'):
            if self.shift_is_pressed():
                self.application().view.focus_view(u'Browser')
            else:
                self.application().view.hide_view(u'Browser')
        else:
            self.application().view.show_view(u'Browser')

    def __toggle_detail_is_visible(self, focus=True):
        if self.application().view.is_view_visible(u'Detail'):
            if self.shift_is_pressed() and focus:
                self.application().view.focus_view(u'Detail')
            else:
                self.application().view.hide_view(u'Detail')
        else:
            self.application().view.show_view(u'Detail')

    def __toggle_arrangement_overdub(self):
        self.song().arrangement_overdub = not self.song().arrangement_overdub

    def __toggle_back_to_arranger(self):
        self.song().back_to_arranger = not self.song().back_to_arranger

    def __capture_midi(self): #
        self.song().capture_midi()

    def __toggle_draw_mode(self):
        self.song().view.draw_mode = not self.song().view.draw_mode

    def __toggle_group_mode(self):
            if self.song().view.selected_track.is_foldable:
                if self.song().view.selected_track.fold_state:
                    self.song().view.selected_track.fold_state = 0
#                    self.send_button_led(SID_AUTOMATION_GROUP, BUTTON_STATE_BLINKING)
                else:
                    self.song().view.selected_track.fold_state = 1
#                    self.send_button_led(SID_AUTOMATION_GROUP, BUTTON_STATE_ON)
            elif self.song().view.selected_track.is_grouped:
                self.song().view.selected_track.group_track.fold_state = 1
#            else:
#                self.send_button_led(SID_AUTOMATION_GROUP, BUTTON_STATE_OFF)
            elif isinstance(self.song().view.selected_track, Live.Chain.Chain):
                self.song().view.selected_track.canonical_parent.is_showing_chains = False
            elif self.song().view.selected_track.can_show_chains:
                self.song().view.selected_track.is_showing_chains = not self.song().view.selected_track.is_showing_chains

    def __toggle_follow_song(self):
        self.song().view.follow_song = not self.song().view.follow_song

    def __toggle_automation_record(self):
        self.song().session_automation_record = not self.song().session_automation_record

    def __update_arrangement_overdub_button_led(self):
        if self.song().arrangement_overdub:
            self.send_button_led(self.__overdub_button, BUTTON_STATE_ON)
        else:
            self.send_button_led(self.__overdub_button, BUTTON_STATE_OFF)

    # def __update_grey_section_leds(self):
        # for i in range(62, 69):
            # self.send_button_led(i, BUTTON_STATE_OFF)
        # self.__update_detail_button_led()
        # self.__update_detail_sub_view_button_led()
        # self.__update_browser_button_led()
        # self.update_outputs_button_led()

    def __update_session_arranger_button_led(self):
        if self.application().view.is_view_visible(u'Session'):
            self.send_button_led(SID_SOFTWARE_MIDI_TRACKS, BUTTON_STATE_ON)
        else:
            self.send_button_led(SID_SOFTWARE_MIDI_TRACKS, BUTTON_STATE_OFF)

    def __update_detail_sub_view_button_led(self):
        if self.application().view.is_view_visible(u'Detail/Clip'):
            self.send_button_led(SID_SOFTWARE_INPUTS, BUTTON_STATE_ON)
        else:
            self.send_button_led(SID_SOFTWARE_INPUTS, BUTTON_STATE_OFF)

    def __update_browser_button_led(self):
        if self.application().view.is_view_visible(u'Browser'):
            self.send_button_led(SID_SOFTWARE_AUDIO_INST, BUTTON_STATE_ON)
        else:
            self.send_button_led(SID_SOFTWARE_AUDIO_INST, BUTTON_STATE_OFF)

    def __update_detail_button_led(self):
        if self.application().view.is_view_visible(u'Detail'):
            self.send_button_led(SID_SOFTWARE_AUDIO_TRACKS, BUTTON_STATE_ON)
        else:
            self.send_button_led(SID_SOFTWARE_AUDIO_TRACKS, BUTTON_STATE_OFF)

    def __update_undo_button_led(self):
        if self.song().can_undo:
            self.send_button_led(SID_FUNC_UNDO, BUTTON_STATE_ON)
        else:
            self.send_button_led(SID_FUNC_UNDO, BUTTON_STATE_OFF)

    def __update_redo_button_led(self):
        if self.song().can_redo:
            self.send_button_led(SID_FUNC_ENTER, BUTTON_STATE_ON)
        else:
            self.send_button_led(SID_FUNC_ENTER, BUTTON_STATE_OFF)

    """
    def update_outputs_button_led(self):
        if self.song().view.selected_track == self.song().master_track:
            self.new_master_track_selected_state = True
        else:
            self.new_master_track_selected_state = False

        if self.__master_track_selected_state != self.new_master_track_selected_state:
            self.__master_track_selected_state = self.new_master_track_selected_state
            if self.__master_track_selected_state == True:
                self.send_button_led(SID_SOFTWARE_OUTPUTS, BUTTON_STATE_ON)
#                self.send_button_led(SID_SOFTWARE_OUTPUTS, BUTTON_STATE_ON)
            else:
                self.send_button_led(SID_SOFTWARE_OUTPUTS, BUTTON_STATE_OFF)
#                self.send_button_led(SID_SOFTWARE_OUTPUTS, BUTTON_STATE_OFF)"""

    def __update_back_to_arranger_button_led(self):
        if self.song().back_to_arranger:
            self.send_button_led(self.__back_to_arrangement_button, BUTTON_STATE_ON)
        else:
            self.send_button_led(self.__back_to_arrangement_button, BUTTON_STATE_OFF)

    def __update_group_mode_button_led(self):
        if isinstance(self.song().view.selected_chain, Live.Chain.Chain):
            self.new_selected_track_group_state = 1
        elif self.song().view.selected_track.can_show_chains:
            self.new_selected_track_group_state = 2
        elif self.song().view.selected_track.is_grouped or self.song().view.selected_track.is_foldable:
            if self.song().view.selected_track.is_foldable:
                if self.song().view.selected_track.fold_state == 1: #currently not using this distinction (LED on in both cases)
                    self.new_selected_track_group_state = 2
                else:
                    self.new_selected_track_group_state = 2
            else:
                self.new_selected_track_group_state = 1
        else:
            self.new_selected_track_group_state = 0
        
        if self.__selected_track_group_state != self.new_selected_track_group_state:
            self.__selected_track_group_state = self.new_selected_track_group_state
            if self.__selected_track_group_state == 2:
                self.send_button_led(SID_AUTOMATION_GROUP, BUTTON_STATE_ON)
            elif self.__selected_track_group_state == 1:
                self.send_button_led(SID_AUTOMATION_GROUP, BUTTON_STATE_BLINKING)
            else:
                self.send_button_led(SID_AUTOMATION_GROUP, BUTTON_STATE_OFF)

    def _update_function_keys_leds(self, verbose=True):
        if self.main_script().use_function_buttons == 1:
            current_quantization = SID_SOFTWARE_F1 + self.song().midi_recording_quantization - 1
            for key in function_key_control_switch_ids:
                if key == current_quantization:
                    self.send_button_led(key, BUTTON_STATE_ON)
                else:
                    self.send_button_led(key, BUTTON_STATE_OFF)
            if verbose:
                self.main_script().time_display().show_priority_message(self.__quantization_strings[self.song().midi_recording_quantization], 1000)
        elif self.main_script().use_function_buttons == 2:
            led_index = SID_SOFTWARE_F1 + self.get_input_type_index(self.song().view.selected_track)
            if self.song().view.selected_track.has_midi_input:
                led_index -= 1
            for key in function_key_control_switch_ids:
                if key == led_index or led_index < SID_SOFTWARE_F1: # or led_index < SID_SOFTWARE_F1 to light all LEDs for all ins
                    self.send_button_led(key, BUTTON_STATE_ON)
                else:
                    self.send_button_led(key, BUTTON_STATE_OFF)
            if verbose:
                self.main_script().time_display().show_priority_message(self.song().view.selected_track.input_routing_type.display_name, 1000)
        elif self.main_script().use_function_buttons == 3:
            led_index = SID_SOFTWARE_F1 + self.get_input_channel_index(self.song().view.selected_track)
            if self.song().view.selected_track.has_midi_input:
                led_index -= 1
            for key in function_key_control_switch_ids:
                if key == led_index or led_index < SID_SOFTWARE_F1: # or led_index < SID_SOFTWARE_F1 to light all LEDs for all channels
                    self.send_button_led(key, BUTTON_STATE_ON)
                elif key == led_index - 8:
                    self.send_button_led(key, BUTTON_STATE_BLINKING)
                else:
                    self.send_button_led(key, BUTTON_STATE_OFF)
            if verbose:
                self.main_script().time_display().show_priority_message(self.song().view.selected_track.input_routing_channel.display_name, 1000)
        else:
            for key in function_key_control_switch_ids:
                self.send_button_led(key, BUTTON_STATE_OFF)

    def get_input_type_index(self, track):
        selected = track.input_routing_type
        available = track.available_input_routing_types

        if not available or track.is_foldable:  # group tracks are foldable
            return 1000

        for i, t in enumerate(available):
            if t.display_name == selected.display_name:
                return i
        return 1000 # no input selected or available

    def get_input_channel_index(self, track):
        print(dir(track.input_routing_channel))
        selected = track.input_routing_channel
        available = track.available_input_routing_channels

        if not available or track.is_foldable:  # group tracks are foldable
            return 1000

        for i, chan in enumerate(available):
            if chan.display_name == selected.display_name:
                return i
        return 1000 # no input selected or available

    def __update_capture_midi_button_led(self): #
        if self.song().can_capture_midi:
            self.send_button_led(SID_FUNC_SAVE, BUTTON_STATE_ON)
        else:
            self.send_button_led(SID_FUNC_SAVE, BUTTON_STATE_OFF)

    def __update_draw_mode_button_led(self):
        if self.song().view.draw_mode:
            self.send_button_led(SID_AUTOMATION_TOUCH, BUTTON_STATE_ON)
        else:
            self.send_button_led(SID_AUTOMATION_TOUCH, BUTTON_STATE_OFF)

    def __update_automation_record_button_led(self):
        if self.song().session_automation_record:
            self.send_button_led(SID_AUTOMATION_WRITE, BUTTON_STATE_ON)
        else:
            self.send_button_led(SID_AUTOMATION_WRITE, BUTTON_STATE_OFF)

    def __update_re_enable_automation_enabled_button_led(self):
        if self.song().re_enable_automation_enabled:
            self.send_button_led(SID_AUTOMATION_READ_OFF, BUTTON_STATE_BLINKING)
        else:
            self.send_button_led(SID_AUTOMATION_READ_OFF, BUTTON_STATE_OFF)

    def set_input_channel(self, track, button_index, midi=False):
        """
        Set the track's input_routing_channel to the button_index-th available channel.
        button_index: int 0–7
        """
        available = track.available_input_routing_channels
        if button_index + 1 < len(available):
            if midi:
                if track.input_routing_channel == available[button_index + 1]:
                    track.input_routing_channel = available[0]
                else:
                    track.input_routing_channel = available[button_index + 1]
            else:
                target = available[button_index]
                track.input_routing_channel = target
            chan = track.input_routing_channel
            if chan is not None:
                name = chan.display_name.replace(" ","")[:10]
            self.main_script().time_display().show_priority_message(name, 1000)
        

    def set_input_type(self, track, button_index, midi=False):
        """
        Set the track's input_routing_channel to the button_index-th available channel.
        button_index: int 0–7
        """
        available = track.available_input_routing_types
        if button_index + 1 < len(available):
            if midi:
                if track.input_routing_type == available[button_index + 1]:
                    track.input_routing_type = available[0]
                else:
                    track.input_routing_type = available[button_index + 1]
            else:
                target = available[button_index]
                track.input_routing_type = target
            typ = track.input_routing_type
            if typ is not None:
                name = typ.display_name.replace(" ","")[:10]
            self.main_script().time_display().show_priority_message(name, 1000)

    def __toggle_user_button_mapping(self): # toggles an alternative Gray Section layout where view buttons and new track buttons are grouped
        return
        global SID_SOFTWARE_MIDI_TRACKS, SID_SOFTWARE_INPUTS, SID_SOFTWARE_AUDIO_TRACKS, SID_SOFTWARE_AUDIO_INST, SID_SOFTWARE_AUX, SID_SOFTWARE_BUSES, SID_SOFTWARE_OUTPUTS
        if not self.main_script().get_overlay_layout():
            SID_SOFTWARE_MIDI_TRACKS, SID_SOFTWARE_INPUTS, SID_SOFTWARE_AUDIO_TRACKS, SID_SOFTWARE_AUDIO_INST, SID_SOFTWARE_AUX, SID_SOFTWARE_BUSES, SID_SOFTWARE_OUTPUTS = range(62, 69)
        else:
            SID_SOFTWARE_MIDI_TRACKS, SID_SOFTWARE_INPUTS, SID_SOFTWARE_AUDIO_TRACKS, SID_SOFTWARE_AUDIO_INST, SID_SOFTWARE_AUX, SID_SOFTWARE_BUSES, SID_SOFTWARE_OUTPUTS = 66, 62, 67, 63, 64, 68, 65 # New MIDI, Audio and Return Track buttons to the right
#            SID_SOFTWARE_MIDI_TRACKS, SID_SOFTWARE_INPUTS, SID_SOFTWARE_AUDIO_TRACKS, SID_SOFTWARE_AUDIO_INST, SID_SOFTWARE_AUX, SID_SOFTWARE_BUSES = 62, 65, 63, 66, 67, 64, 68 # New MIDI, Audio and Return Track buttons to the left
        self.__update_grey_section_leds()

