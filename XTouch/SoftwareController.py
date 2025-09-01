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
        self.song().add_midi_recording_quantization_listener(self.__update_midi_recording_quantization_buttons_led)
        self.__update_automation_record_button_led()
        self.__quantization_strings = ("quant 0ff", "1'4", "1'8", "1'8T", "1'8 1'8T", "1'16", "1'16T", "1'16 1'16T", "1'32")

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
        self.song().remove_midi_recording_quantization_listener(self.__update_midi_recording_quantization_buttons_led)
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
        current_quantization = SID_SOFTWARE_F1 + self.song().midi_recording_quantization - 1
        if value == BUTTON_PRESSED:
            if self.shift_is_pressed():
                if self.main_script().use_function_buttons == 0:
                    self.main_script().use_function_buttons = 1
                    self.main_script().time_display().show_priority_message("F quantize")
                elif self.main_script().use_function_buttons == 1:
                    self.main_script().time_display().show_priority_message("F disabled")
                    self.main_script().use_function_buttons = 0
                self.main_script().save_preferences()
                self.__update_midi_recording_quantization_buttons_led()
            elif self.main_script().use_function_buttons == 1:
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

    # def handle_touch_master_fader(self, switch_id, value):
        # if value == BUTTON_PRESSED and self.main_script().night_mode_on:
            # self.__flash_leds(1)
        # elif value == BUTTON_RELEASED:
            # self.__flash_leds(0)

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
        if switch_id == SID_ARRAGEMENT_SESSION:    #elif switch_id == SID_AUTOMATION_ON:
            if value == BUTTON_PRESSED:
                self.__toggle_session_arranger_is_visible()
        elif switch_id == SID_SOFTWARE_F13:
            if value == BUTTON_PRESSED:
                self.__toggle_detail_sub_view()
        elif switch_id == SID_SOFTWARE_F10:
            if value == BUTTON_PRESSED:
                self.__toggle_browser_is_visible()
        elif switch_id == SID_SOFTWARE_F12:
            if value == BUTTON_PRESSED:
                self.__toggle_detail_is_visible()
        elif switch_id == SID_FUNC_UNDO:
            if value == BUTTON_PRESSED:
                self.song().undo()
        elif switch_id == SID_FUNC_REDO:
            if value == BUTTON_PRESSED:
                self.song().redo()
        elif switch_id == SID_FUNC_CANCEL:
            if value == BUTTON_PRESSED:
                self.__toggle_back_to_arranger()
        elif switch_id == SID_FUNC_SAVE: #
            if value == BUTTON_PRESSED: #
                self.__capture_midi() #
        elif switch_id == SID_FUNC_GROUP:
            if value == BUTTON_PRESSED:
                self.__toggle_group_mode()
#        elif switch_id == SID_FUNC_MARKER:
#            if value == BUTTON_PRESSED:
#                self.song().set_or_delete_cue()
#        elif switch_id == SID_FUNC_MIXER:
#            if value == BUTTON_PRESSED:
#                self.__toggle_follow_song()
        elif switch_id == SID_AUTOMATION_SNAPSHOT:
            if value == BUTTON_PRESSED:
                self.__toggle_draw_mode()
        elif switch_id == SID_AUTOMATION_RECORD:
            if value == BUTTON_PRESSED:
                self.__toggle_automation_record()
        elif switch_id == SID_AUTOMATION_ON:
            if value == BUTTON_PRESSED:
                self.song().re_enable_automation()
        elif switch_id == SID_SOFTWARE_F9:
            if value == BUTTON_PRESSED:
                self.song().create_midi_track()
        elif switch_id == SID_SOFTWARE_F11:
            if value == BUTTON_PRESSED:
                self.song().create_audio_track()
        elif switch_id == SID_SOFTWARE_F14:
            if value == BUTTON_PRESSED:
                self.song().create_return_track()
        elif switch_id == SID_SOFTWARE_F15:
            if value == BUTTON_PRESSED:
                self.__show_master_channel()
        elif switch_id == SID_FUNC_TRIM:
            if value == BUTTON_PRESSED:
                self.__toggle_arrangement_overdub()

    def refresh_state(self):
        self.main_script().set_shift_is_pressed(False)
        self.main_script().set_option_is_pressed(False)
        self.main_script().set_control_is_pressed(False)
        self.main_script().set_alt_is_pressed(False)
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
        self.__update_outputs_button_led()
        self.__update_night_mode_leds()

    def on_update_display_timer(self):
        self.__update_group_mode_button_led() #have to include here since we can't add a listener for this
        self.__update_outputs_button_led() #have to include here since we can't add a listener for this
        if self.__last_can_undo_state != self.song().can_undo:
            self.__last_can_undo_state = self.song().can_undo
            self.__update_undo_button_led()
        if self.__last_can_redo_state != self.song().can_redo:
            self.__last_can_redo_state = self.song().can_redo
            self.__update_redo_button_led()

    def __show_master_channel(self):
        if self.song().view.selected_track != self.song().master_track:
            self.song().view.selected_track = self.song().master_track
        else:
            self.application().view.show_view(u'Detail/DeviceChain')

    def __toggle_session_arranger_is_visible(self):
        if self.application().view.is_view_visible(u'Session'):
            if self.shift_is_pressed():
                self.application().view.focus_view(u'Session')
            else:
                self.application().view.hide_view(u'Session')
        else:
            assert self.application().view.is_view_visible(u'Arranger')
            if self.shift_is_pressed():
                self.application().view.focus_view(u'Arranger')
            else:
                self.application().view.hide_view(u'Arranger')

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

    def __toggle_detail_is_visible(self):
        if self.application().view.is_view_visible(u'Detail'):
            if self.shift_is_pressed():
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
#                    self.send_button_led(SID_FUNC_GROUP, BUTTON_STATE_BLINKING)
                else:
                    self.song().view.selected_track.fold_state = 1
#                    self.send_button_led(SID_FUNC_GROUP, BUTTON_STATE_ON)
            elif self.song().view.selected_track.is_grouped:
                self.song().view.selected_track.group_track.fold_state = 1
#            else:
#                self.send_button_led(SID_FUNC_GROUP, BUTTON_STATE_OFF)
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
            self.send_button_led(SID_FUNC_TRIM, BUTTON_STATE_ON)
        else:
            self.send_button_led(SID_FUNC_TRIM, BUTTON_STATE_OFF)

    def __update_session_arranger_button_led(self):
        if self.application().view.is_view_visible(u'Session'):
            #self.send_button_led(SID_AUTOMATION_ON, BUTTON_STATE_ON)
            self.send_button_led(SID_ARRAGEMENT_SESSION, BUTTON_STATE_ON)
        else:
            #self.send_button_led(SID_AUTOMATION_ON, BUTTON_STATE_OFF)
            self.send_button_led(SID_ARRAGEMENT_SESSION, BUTTON_STATE_OFF)

    def __update_detail_sub_view_button_led(self):
        if self.application().view.is_view_visible(u'Detail/Clip'):
            self.send_button_led(SID_SOFTWARE_F13, BUTTON_STATE_ON)
        else:
            self.send_button_led(SID_SOFTWARE_F13, BUTTON_STATE_OFF)

    def __update_browser_button_led(self):
        if self.application().view.is_view_visible(u'Browser'):
            self.send_button_led(SID_SOFTWARE_F10, BUTTON_STATE_ON)
        else:
            self.send_button_led(SID_SOFTWARE_F10, BUTTON_STATE_OFF)

    def __update_detail_button_led(self):
        if self.application().view.is_view_visible(u'Detail'):
            self.send_button_led(SID_SOFTWARE_F12, BUTTON_STATE_ON)
        else:
            self.send_button_led(SID_SOFTWARE_F12, BUTTON_STATE_OFF)

    def __update_undo_button_led(self):
        if self.song().can_undo:
            self.send_button_led(SID_FUNC_UNDO, BUTTON_STATE_ON)
        else:
            self.send_button_led(SID_FUNC_UNDO, BUTTON_STATE_OFF)

    def __update_redo_button_led(self):
        if self.song().can_redo:
            self.send_button_led(SID_FUNC_REDO, BUTTON_STATE_ON)
        else:
            self.send_button_led(SID_FUNC_REDO, BUTTON_STATE_OFF)

    def __update_outputs_button_led(self):
        if self.song().view.selected_track == self.song().master_track:
            self.new_master_track_selected_state = True
        else:
            self.new_master_track_selected_state = False

        if self.__master_track_selected_state != self.new_master_track_selected_state:
            self.__master_track_selected_state = self.new_master_track_selected_state
            if self.__master_track_selected_state == True:
                self.send_button_led(SID_SOFTWARE_F15, BUTTON_STATE_ON)
#                self.send_button_led(SID_SOFTWARE_F15, BUTTON_STATE_ON)
            else:
                self.send_button_led(SID_SOFTWARE_F15, BUTTON_STATE_OFF)
#                self.send_button_led(SID_SOFTWARE_F15, BUTTON_STATE_OFF)

    def __update_back_to_arranger_button_led(self):
        if self.song().back_to_arranger:
            self.send_button_led(SID_FUNC_CANCEL, BUTTON_STATE_ON)
        else:
            self.send_button_led(SID_FUNC_CANCEL, BUTTON_STATE_OFF)

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
                self.send_button_led(SID_FUNC_GROUP, BUTTON_STATE_ON)
            elif self.__selected_track_group_state == 1:
                self.send_button_led(SID_FUNC_GROUP, BUTTON_STATE_BLINKING)
            else:
                self.send_button_led(SID_FUNC_GROUP, BUTTON_STATE_OFF)

    def __update_midi_recording_quantization_buttons_led(self):
        if self.main_script().use_function_buttons == 1:
            current_quantization = SID_SOFTWARE_F1 + self.song().midi_recording_quantization - 1
            for key in function_key_control_switch_ids:
                if key == current_quantization:
                    self.send_button_led(key, BUTTON_STATE_ON)
                else:
                    self.send_button_led(key, BUTTON_STATE_OFF)
        else:
            for key in function_key_control_switch_ids:
                self.send_button_led(key, BUTTON_STATE_OFF)

    def __update_capture_midi_button_led(self): #
        if self.song().can_capture_midi:
            self.send_button_led(SID_FUNC_SAVE, BUTTON_STATE_ON)
        else:
            self.send_button_led(SID_FUNC_SAVE, BUTTON_STATE_OFF)

    def __update_draw_mode_button_led(self):
        if self.song().view.draw_mode:
            self.send_button_led(SID_AUTOMATION_SNAPSHOT, BUTTON_STATE_ON)
        else:
            self.send_button_led(SID_AUTOMATION_SNAPSHOT, BUTTON_STATE_OFF)

    def __update_automation_record_button_led(self):
        if self.song().session_automation_record:
            self.send_button_led(SID_AUTOMATION_RECORD, BUTTON_STATE_ON)
        else:
            self.send_button_led(SID_AUTOMATION_RECORD, BUTTON_STATE_OFF)

    def __update_re_enable_automation_enabled_button_led(self):
        if self.song().re_enable_automation_enabled:
            self.send_button_led(SID_AUTOMATION_ON, BUTTON_STATE_BLINKING)
        else:
            self.send_button_led(SID_AUTOMATION_ON, BUTTON_STATE_OFF)
