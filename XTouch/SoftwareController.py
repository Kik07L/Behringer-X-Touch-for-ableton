#Embedded file name: /Users/versonator/Jenkins/live/output/Live/mac_64_static/Release/python-bundle/MIDI Remote Scripts/MackieControl/SoftwareController.py
from __future__ import absolute_import, print_function, unicode_literals
from .MackieControlComponent import *
import time

class SoftwareController(MackieControlComponent):
    u"""Representing the buttons above the transport, including the basic: """

    def __init__(self, main_script):
        MackieControlComponent.__init__(self, main_script)
        self.__last_can_undo_state = False
        self.__last_can_redo_state = False
        self.__selected_track_group_state = 0
        self.__selected_macro_variation = None
        self.__master_track_selected_state = False
        av = self.application().view
        #self.night_mode_on = False
        self.__assign_mutable_buttons()
        self.__leds_flashing = False
        self.__last_active_cue = None
        self.__pending_delete = {"cue_index": None, "cue_time": None, "expire_time": None}
        av.add_is_view_visible_listener(u'Session', self.__update_session_arranger_button_led)
        av.add_is_view_visible_listener(u'Detail/Clip', self.__update_detail_sub_view_button_led)
        av.add_is_view_visible_listener(u'Detail/DeviceChain', self.__update_detail_sub_view_button_led)
        av.add_is_view_visible_listener(u'Browser', self.__update_browser_button_led)
        av.add_is_view_visible_listener(u'Detail', self.__update_detail_button_led)
        self.song().view.add_draw_mode_listener(self.__update_draw_mode_button_led)
        self.song().add_back_to_arranger_listener(self.__update_back_to_arranger_button_led)
        self.song().add_can_capture_midi_listener(self.__update_capture_midi_button_led) #
        self.song().add_session_automation_record_listener(self.__update_automation_record_button_led)
        self.song().add_re_enable_automation_enabled_listener(self.__update_re_enable_automation_enabled_button_led)
        self.song().add_arrangement_overdub_listener(self.__update_arrangement_overdub_button_led)
        self.song().add_midi_recording_quantization_listener(self._update_function_keys_leds)
        self.song().add_cue_points_listener(self.__on_cues_changed)
        self.song().add_current_song_time_listener(self.__on_playhead_moved)
        self.__update_automation_record_button_led()
        #self.update_outputs_button_led()
#        self.__quantization_strings = ("quant:  0ff", "1'4", "1'8", "1'8T", "1'8 1'8T", "1'16", "1'16T", "1'16 1'16T", "1'32")
        self.__quantization_strings = ("quant: 0ff", "quant: 4", "quant: 8", "quant: 8T", "quant: 8 8T", "quant:16", "quant:16T", "quant:1616T", "quant:32")
        self.__save_current_view(False)
        #self.__toggle_user_button_mapping()
        self._update_function_keys_leds(False)
        
    def destroy(self):
        av = self.application().view
        av.remove_is_view_visible_listener(u'Session', self.__update_session_arranger_button_led)
        av.remove_is_view_visible_listener(u'Detail/Clip', self.__update_detail_sub_view_button_led)
        av.remove_is_view_visible_listener(u'Detail/DeviceChain', self.__update_detail_sub_view_button_led)
        av.remove_is_view_visible_listener(u'Browser', self.__update_browser_button_led)
        av.remove_is_view_visible_listener(u'Detail', self.__update_detail_button_led)
        self.song().view.remove_draw_mode_listener(self.__update_draw_mode_button_led)
        self.song().remove_back_to_arranger_listener(self.__update_back_to_arranger_button_led)
        self.song().remove_can_capture_midi_listener(self.__update_capture_midi_button_led)
        self.song().remove_arrangement_overdub_listener(self.__update_arrangement_overdub_button_led)
        self.song().remove_midi_recording_quantization_listener(self._update_function_keys_leds)
        self.song().remove_cue_points_listener(self.__on_cues_changed)
        self.song().remove_current_song_time_listener(self.__on_playhead_moved)
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

    def set_channel_strip_controller(self, csc):
        self.__channel_strip_controller = csc

    def set_main_display_controller(self, csc):
        self.__main_display_controller = csc


    def handle_function_key_switch_ids(self, switch_id, value):
        if value == BUTTON_PRESSED:
            if self.shift_is_pressed(): # select function keys mode
                spec = self.main_script()._preferences_spec["USE_FUNCTION_BUTTONS"]
                default, parser, comment, formatter, short_name, choices_or_limits = spec
                selector = (switch_id - SID_SOFTWARE_F1)
                # Only allow values defined in choices_or_limits
                if selector in choices_or_limits:
                    self.main_script().use_function_buttons = selector
                    self.main_script().save_preferences()
                    label = choices_or_limits[selector]
                    self.main_script().time_display().show_priority_message(
                        f"{short_name[:5]}.{label:>5}", 2000
                    )
                self._update_function_keys_leds(False)
                return

            if self.main_script().use_function_buttons == 1 and not self.option_is_pressed() and not  self.control_is_pressed() and not self.alt_is_pressed(): # quantization mode, lets unused modifiers through for quick (modeless) input selection
                current_quantization = SID_SOFTWARE_F1 + self.song().midi_recording_quantization - 1
                if switch_id == current_quantization:
                    self.song().midi_recording_quantization = 0
                else:
                    self.song().midi_recording_quantization = switch_id - SID_SOFTWARE_F1 + 1
                self.main_script().time_display().show_priority_message(self.__quantization_strings[self.song().midi_recording_quantization], 1000)
                return

            if self.main_script().use_function_buttons == 6 and not self.option_is_pressed() and not self.control_is_pressed():  # locator mode
                selector = switch_id - SID_SOFTWARE_F1 + (8 if self.alt_is_pressed() else 0)
                cue_points = sorted(self.song().cue_points, key=lambda cp: cp.time)
                delete_expire_time = 4000

                if selector < len(cue_points):
                    cp = cue_points[selector]
                    current_time = self.song().current_song_time
                    cuename = cp.name
                    if cuename.isdigit():
                        cuename = f"Ltr{int(cuename):>2}".rjust(5)
                    shortname = self.generate_x_char_string(cuename, 5)

                    # Only allow delete if playhead is near the cue and song is stopped
                    if abs(current_time - cp.time) < 1e-3 and not self.song().is_playing:
                        # First press → show confirmation
                        if self.__pending_delete["cue_index"] != selector:
                            self.__pending_delete = {"cue_index": selector, "cue_time": current_time, "expire_time": time.time() + (delete_expire_time / 1000.0)}
                            self.main_script().time_display().show_priority_message(f"dlte .{shortname:>5}", delete_expire_time)
                            return

                        # Second press → delete cue
                        if self.__pending_delete["cue_index"] == selector:
                            self.song().set_or_delete_cue()
                            self.main_script().time_display().show_priority_message(f"dltd .{shortname:>5}", 1000)
                            self.__pending_delete = {"cue_index": None, "cue_time": None, "expire_time": None}
                            return

                    else:
                        # Not deleting → jump to cue
                        cp.jump()

                elif not self.song().is_cue_point_selected():
                    self.song().set_or_delete_cue()

                self._update_function_keys_leds()
                return

            # elif self.main_script().use_function_buttons == 6 and not self.option_is_pressed() and not self.control_is_pressed():  # locator mode, lets unused modifiers through for quick (modeless) input selection
                # selector = switch_id - SID_SOFTWARE_F1 + (8 if self.alt_is_pressed() else 0)
                # cue_points = sorted(self.song().cue_points, key=lambda cp: cp.time)
                # if selector < len(cue_points):
                    # if self.song().current_song_time == cue_points[selector].time:
                        # self.song().set_or_delete_cue()
                        # self.main_script().time_display().show_priority_message(f"Lctr:deletd", 1000)
                    # else:
                        # cp = cue_points[selector]
                        # cp.jump()
                # elif not self.song().is_cue_point_selected():
                    # self.song().set_or_delete_cue()
                # self._update_function_keys_leds()
                # return

            if self.main_script().use_function_buttons == 7 and not  self.control_is_pressed() and not self.alt_is_pressed(): # macro mapper variations mode, lets unused modifiers through for quick (modeless) input selection
                if self.__channel_strip_controller._macro_mapper == None:
                    self.main_script().time_display().show_priority_message("no mapper", 1000)
                    return
                else:
                    number_of_variations = self.__channel_strip_controller._macro_mapper.variation_count
                    selector = (switch_id - SID_SOFTWARE_F1)
                    if selector < number_of_variations:
                        self.__channel_strip_controller._macro_mapper.selected_variation_index = selector
                        if self.option_is_pressed():
                            self.__channel_strip_controller._macro_mapper.delete_selected_variation()
                            self.__selected_macro_variation = None
                            self.main_script().time_display().show_priority_message(f"delet.varF{selector + 1}", 2000)
                        else:
                            self.__channel_strip_controller._macro_mapper.recall_selected_variation()
                            self.__selected_macro_variation = selector
                            self.main_script().time_display().show_priority_message(f"recal.varF{selector + 1}", 2000)
                    elif not self.option_is_pressed(): # press unlit button to store new variation; OPTION = delete variation, would be strange if it would create a new one
                        self.__channel_strip_controller._macro_mapper.store_variation()
                        number_of_variations = self.__channel_strip_controller._macro_mapper.variation_count
                        self.main_script().time_display().show_priority_message(f"store.varF{number_of_variations}", 2000)
                        self.__selected_macro_variation = number_of_variations - 1
                    self._update_function_keys_leds()
                    return
                    
            if (self.option_is_pressed() or self.main_script().use_function_buttons == 2) and self.song().view.selected_track and hasattr(self.song().view.selected_track, 'input_routing_type'):
#            if self.main_script().use_function_buttons == 2 and self.song().view.selected_track != self.song().master_track and hasattr(self.song().view.selected_track, 'input_routing_type'):
#                selector = (switch_id - SID_SOFTWARE_F1)
                selector = (switch_id - SID_SOFTWARE_F1) + (8 if self.alt_is_pressed() else 0)
                self.set_input_type(self.song().view.selected_track, selector, self.song().view.selected_track.has_midi_input)
                self._update_function_keys_leds(False)
                return

            if (self.control_is_pressed() or self.alt_is_pressed() or self.main_script().use_function_buttons == 3) and self.song().view.selected_track and hasattr(self.song().view.selected_track, 'input_routing_channel'):
#            if self.main_script().use_function_buttons == 3 and self.song().view.selected_track != self.song().master_track and hasattr(self.song().view.selected_track, 'input_routing_channel'):
                selector = (switch_id - SID_SOFTWARE_F1) + (8 if self.alt_is_pressed() else 0)
                self.set_input_channel(self.song().view.selected_track, selector, self.song().view.selected_track.has_midi_input)
                self._update_function_keys_leds(False)
                return

    def __cancel_delete_locator(self, check_time=False):
        if self.__pending_delete["cue_index"] is not None:
            if not check_time:
                self.__pending_delete = {"cue_index": None, "cue_time": None, "expire_time": None}
                self.main_script().time_display().show_priority_message("", 0)
            elif time.time() > self.__pending_delete["expire_time"]:
                self.__pending_delete = {"cue_index": None, "cue_time": None, "expire_time": None}
        return

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

    def __flash_leds(self, onOff):
        leds_to_flash = list(channel_strip_assignment_switch_ids + transport_control_switch_ids + function_key_control_switch_ids + marker_control_switch_ids + software_controls_switch_ids + channel_strip_control_switch_ids + tuple(jog_wheel_switch_ids))
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
                self.send_button_led(switch_id, BUTTON_STATE_ON)
            elif value == BUTTON_RELEASED:
                self.send_button_led(switch_id, BUTTON_STATE_OFF)                
        elif switch_id == SID_SOFTWARE_BUSES:
            if value == BUTTON_PRESSED:
                self.song().create_audio_track()
                self.send_button_led(switch_id, BUTTON_STATE_ON)
            elif value == BUTTON_RELEASED:
                self.send_button_led(switch_id, BUTTON_STATE_OFF)                
        elif switch_id == SID_SOFTWARE_OUTPUTS:
            if value == BUTTON_PRESSED:
                self.song().create_return_track()
                self.send_button_led(switch_id, BUTTON_STATE_ON)
            elif value == BUTTON_RELEASED:
                self.send_button_led(switch_id, BUTTON_STATE_OFF)

        elif switch_id == SID_AUTOMATION_READ_OFF:
            if value == BUTTON_PRESSED:
                if self.option_is_pressed():
                    self.__do_party_trick() # leaving this in for now, but shortcut has been replaced by SHIFT + DISPLAY NAME/VALUE
                else:
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
                # Live.Licensing.PythonLicensingBridge.save_current_set()
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
        self.__cancel_delete_locator(True)
        if self.__last_can_undo_state != self.song().can_undo:
            self.__last_can_undo_state = self.song().can_undo
            self.__update_undo_button_led()
        if self.__last_can_redo_state != self.song().can_redo:
            self.__last_can_redo_state = self.song().can_redo
            self.__update_redo_button_led()

    def _select_master_channel(self, collapse=True):
        if self.song().view.selected_track != self.song().master_track:
            self.song().view.selected_track = self.song().master_track
        elif collapse:
            self.song().master_track.view.is_collapsed = not self.song().master_track.view.is_collapsed
            #self.__toggle_detail_is_visible(focus=False)

    def __do_party_trick(self):
        # self.main_script().time_display().show_priority_message("COLOR. MIX")
        self.__main_display_controller._party_trick()

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
        if not self.__saved_view_detail:
            # self.application().view.show_view(u'Detail')
        # else:
            self.application().view.hide_view(u'Detail')
        if verbose:
            self.main_script().time_display().show_priority_message("Wieu recal")

    def __assign_mutable_buttons(self):
        if self.main_script().get_overlay_layout() or self.main_script().get_debug_parameter_1():
            self.__overdub_button = SID_JOG_SCRUB if self.main_script().get_debug_parameter_1() else SID_TRANSPORT_SOLO
            self.__back_to_arrangement_button = SID_AUTOMATION_TRIM
        else:
            self.__overdub_button = SID_AUTOMATION_TRIM
            self.__back_to_arrangement_button = SID_FUNC_CANCEL

    def __toggle_session_arranger_is_visible(self):
        if self.application().view.is_view_visible(u'Session'):
            self.application().view.hide_view(u'Session')
        else:
            assert self.application().view.is_view_visible(u'Arranger')
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
        if self.application().view.is_view_visible(u'Arranger'):
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

    def __on_cues_changed(self):
        if self.main_script().use_function_buttons == 6:
            self.__cancel_delete_locator()
            self._update_function_keys_leds(False)

    def __on_playhead_moved(self):
        if self.main_script().use_function_buttons == 6:
            self.__cancel_delete_locator()
            self._update_function_keys_leds()

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

        elif self.main_script().use_function_buttons == 2 and self.song().view.selected_track != self.song().master_track:
            led_index = SID_SOFTWARE_F1 + self.get_input_type_index(self.song().view.selected_track)
            if self.song().view.selected_track.has_midi_input:
                led_index -= 1
            for key in function_key_control_switch_ids:
                if key == led_index or led_index < SID_SOFTWARE_F1: # or led_index < SID_SOFTWARE_F1 to light all LEDs for all ins
                    self.send_button_led(key, BUTTON_STATE_ON)
                elif key == led_index - 8:
                    self.send_button_led(key, BUTTON_STATE_BLINKING)
                else:
                    self.send_button_led(key, BUTTON_STATE_OFF)
            if verbose:
                self.main_script().time_display().show_priority_message(self.song().view.selected_track.input_routing_type.display_name, 1000)

        elif self.main_script().use_function_buttons == 3 and self.song().view.selected_track != self.song().master_track:
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

        elif self.main_script().use_function_buttons == 6:  # Cue Mode
            cue_points = sorted(self.song().cue_points, key=lambda cp: cp.time)
            playhead = self.song().current_song_time
            active_cue = None

            total_cues = min(len(cue_points), 16)  # only map 16 cues max

            # Find which cue slot is active (0–15), or None if outside range
            active_slot = None
            for i in range(total_cues):
                start = cue_points[i].time
                end = cue_points[i + 1].time if i + 1 < len(cue_points) else float('inf')
                if start <= playhead < end:
                    active_cue = cue_points[i]
                    active_slot = i
                    break

            # LED feedback
            for i, key in enumerate(function_key_control_switch_ids):  # 8 buttons
                led_state = BUTTON_STATE_OFF

                if active_slot is not None:
                    # --- Normal case: playhead inside mapped cue range ---
                    if active_slot < 8:  # slot 0–7 active
                        if active_slot == i:
                            led_state = BUTTON_STATE_BLINKING
                        elif i < total_cues:
                            led_state = BUTTON_STATE_ON
                    else:  # slot 8–15 active
                        if active_slot == i + 8:
                            led_state = BUTTON_STATE_ON
                        elif i + 8 < total_cues:
                            led_state = BUTTON_STATE_BLINKING
                else:
                    # --- Fallbacks ---
                    if playhead < (cue_points[0].time if cue_points else 0):
                        # Before first cue -> light up only as many buttons as cue slots exist
                        if i < min(total_cues, 8):
                            led_state = BUTTON_STATE_ON
                        elif i + 8 < total_cues:
                            led_state = BUTTON_STATE_ON
                        else:
                            led_state = BUTTON_STATE_OFF
                    elif total_cues > 0 and playhead >= cue_points[total_cues - 1].time:
                        # Beyond last mapped cue -> all BLINK
                        led_state = BUTTON_STATE_BLINKING

                self.send_button_led(key, led_state)

            # active_cue is still set for display etc.


            # --- Section detection (all cues, not just first 16) ---
            for i, cp in enumerate(cue_points):
                start = cp.time
                end = cue_points[i + 1].time if i + 1 < len(cue_points) else float('inf')
                if start <= playhead < end:
                    active_cue = cp
                    break

            # --- Display update ---
            if verbose and active_cue is not None and active_cue != self.__last_active_cue and (self.__last_active_cue in cue_points or self.__last_active_cue is None):
                cuename = None
                name = active_cue.name.strip()
                if name.isdigit():
                    cuename = f"Locator {int(name):>2}".rjust(10)
                else:
                    cuename = name
                shortname = self.generate_x_char_string(cuename, 10) or "Locator"
                self.main_script().time_display().show_priority_message(f"{shortname:>10}", 1000)
            self.__last_active_cue = active_cue


        elif self.main_script().use_function_buttons == 7 and self.__channel_strip_controller._macro_mapper != None: # macro mapper variations mode
            number_of_variations = self.__channel_strip_controller._macro_mapper.variation_count
            for key in function_key_control_switch_ids:
                if self.__selected_macro_variation != None and key == self.__selected_macro_variation + SID_SOFTWARE_F1: # unreliable
                    self.send_button_led(key, BUTTON_STATE_BLINKING)
                elif key < SID_SOFTWARE_F1 + number_of_variations:
                    self.send_button_led(key, BUTTON_STATE_ON)
                else:
                    self.send_button_led(key, BUTTON_STATE_OFF)

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
        if midi and button_index + 1 < len(available):
            if track.input_routing_channel == available[button_index + 1]:
                track.input_routing_channel = available[0]
            else:
                track.input_routing_channel = available[button_index + 1]
        elif button_index + 1 <= len(available):
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
        if midi and button_index + 1 < len(available):
            if track.input_routing_type == available[button_index + 1]:
                track.input_routing_type = available[0]
            else:
                track.input_routing_type = available[button_index + 1]
        elif button_index + 1 <= len(available):
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

