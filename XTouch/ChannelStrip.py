#Embedded file name: /Users/versonator/Jenkins/live/output/Live/mac_64_static/Release/python-bundle/MIDI Remote Scripts/MackieControl/ChannelStrip.py
from __future__ import absolute_import, print_function, unicode_literals
from builtins import range
from .MackieControlComponent import *
from itertools import chain
from math import log as _log
import time

class FaderZeroMappingMixin:
    """
    Provides two-way mapping between hardware fader values and Live parameter values
    with an adjustable 0dB breakpoint. Used fot "Faders calibrated to 0dB" setting.
    """

    # Shared constants for all channels
    # FADER_ZERO = 12700       # hardware fader value corresponding to 0 dB
    LIVE_ZERO = 13925        # Live's value corresponding to 0 dB
    MAX_VALUE = 16383        # maximum hardware/Live value
    FEEDBACK_INTERVAL = 0.02  # seconds (50 Hz max update rate)
    FEEDBACK_WAIT = 0.2  # seconds


    # @property
    # def _fader_zero(self):
        # return self.FADER_ZERO

    @property
    def _fader_zero(self):
        """
        Ask the main script what the calibration value is, dynamically.
        """
        calibrate = 0
        if hasattr(self, "main_script") and callable(self.main_script):
            ms = self.main_script()
            if ms and hasattr(ms, "get_faders_zero_calibrate"):
                value = ms.get_faders_zero_calibrate()
                if value is not None:
                    calibrate = value
        return 12700 + calibrate * 20 # step size

    @property
    def _live_zero(self):
        return self.LIVE_ZERO

    @property
    def _max_value(self):
        return self.MAX_VALUE


    def build_fader_map(self, faders_at_zero=True):
        if not faders_at_zero:
            return tuple()
        """Return a 128-point feedback map with breakpoint at zero dB."""
        pairs = []
        ratio_14_to_7_bit = self.MAX_VALUE / 127
        live_zero_7_bit = int(round(self._live_zero / self._max_value * 127))
        fader_zero_7_bit = int(round(self._fader_zero / self._max_value * 127))

        # Zone 1: (0,0) → (fader_zero, live_zero)
        for i in range(live_zero_7_bit + 1):
            i_14_bit = i * ratio_14_to_7_bit
            fader_val = int(round(i_14_bit * self._fader_zero / self._live_zero / ratio_14_to_7_bit))
            pairs.append((fader_val, i))

        # Zone 2: (fader_zero, live_zero) → (127,127)
        for i in range(live_zero_7_bit + 1, 128):
            i_14_bit = i * ratio_14_to_7_bit
            fader_val = int(round(
                (self._fader_zero + (i_14_bit - self._live_zero) * ((self._max_value - self._fader_zero) / (self._max_value - self._live_zero))) / ratio_14_to_7_bit
            ))
            if fader_val > 127:
                fader_val = 127
            pairs.append((fader_val, i))

        return tuple(pairs)

    def fader_to_live(self, fader_val, faders_at_zero=True):
        if not faders_at_zero:
            return fader_val
        """Convert hardware fader → Live value."""
        if fader_val <= self._fader_zero:
            live_val = fader_val * (self._live_zero / self._fader_zero)
        else:
            live_val = self._live_zero + (fader_val - self._fader_zero) * ((self._max_value - self._live_zero) / (self._max_value - self._fader_zero))
        return int(round(live_val))

    def live_to_fader(self, live_val, faders_at_zero=True):
        if not faders_at_zero:
            return live_val
        """Convert hardware live → fader value."""
        if live_val <= self._live_zero:
            fader_val = live_val * (self._fader_zero / self._live_zero)
        else:
            fader_val = self._fader_zero + (live_val - self._live_zero) * ((self._max_value - self._fader_zero) / (self._max_value - self._live_zero))
        return int(round(fader_val))


class ChannelStrip(FaderZeroMappingMixin, MackieControlComponent):
    u"""Represets a Channel Strip of the Mackie Control, which consists out of the"""
    
    def __init__(self, main_script, strip_index):
        MackieControlComponent.__init__(self, main_script)
        self.__channel_strip_controller = None
        self.__is_touched = False
        self.__last_feedback_time = 0
        self.__last_fader_val = None
        self.__last_fader_moved_time = 0
        self.__fader_move_pending = False
        self.__faders_at_zero = False
        self.__touch_to_move = False
        self.__strip_index = strip_index
        self.__stack_offset = 0
        self.__bank_and_channel_offset = 0
        self.__assigned_track = None
        self.__v_pot_parameter = None
        self.__v_pot_display_mode = VPOT_DISPLAY_SINGLE_DOT
        self.__fader_parameter = None
        self.__meters_enabled = False
        self.__last_meter_value = -1
        self.__send_meter_mode()
        self.__within_track_added_or_deleted = False
        self.__within_destroy = False
        self.set_bank_and_channel_offset(offset=0, show_return_tracks=False, within_track_added_or_deleted=False)
        self.__last_press_time = 0

    def destroy(self):
        self.__within_destroy = True
        if self.__assigned_track:
            self.__remove_listeners()
        if self.song().view.selected_track_has_listener(self.__update_track_is_selected_led):
            self.song().view.remove_selected_track_listener(self.__update_track_is_selected_led)
        if self.song().view.selected_chain_has_listener(self.__update_track_is_selected_led):
            self.song().view.remove_selected_chain_listener(self.__update_track_is_selected_led)
        self.__assigned_track = None
        self.send_midi((208, 0 + (self.__strip_index << 4)))
        self.__meters_enabled = False
        self.__send_meter_mode()
        self.refresh_state()
        MackieControlComponent.destroy(self)
        self.__within_destroy = False

    def set_channel_strip_controller(self, channel_strip_controller):
        self.__channel_strip_controller = channel_strip_controller

    def strip_index(self):
        return self.__strip_index

    def assigned_track(self):
        return self.__assigned_track

    def is_touched(self):
        return self.__is_touched

    def set_is_touched(self, touched):
        self.__is_touched = touched

    def stack_offset(self):
        return self.__stack_offset

    def set_stack_offset(self, offset):
        u"""This is the offset that one gets by 'stacking' several MackieControl XTs:
           the first is at index 0, the second at 8, etc ...
        """
        self.__stack_offset = offset

    def set_bank_and_channel_offset(self, offset, show_return_tracks, within_track_added_or_deleted):
        final_track_index = self.__strip_index + self.__stack_offset + offset
        self.__within_track_added_or_deleted = within_track_added_or_deleted
        if show_return_tracks:
            tracks = self.song().return_tracks
        else:
            tracks = self.visible_tracks_including_chains()
        if final_track_index < len(tracks):
            new_track = tracks[final_track_index]
        else:
            new_track = None
        if new_track != self.__assigned_track:
            if self.__assigned_track:
                self.__remove_listeners()
            self.__assigned_track = new_track
            if self.__assigned_track:
                self.__add_listeners()
        self.refresh_state()
        self.__within_track_added_or_deleted = False

    def v_pot_parameter(self):
        return self.__v_pot_parameter

    def set_v_pot_parameter(self, parameter, display_mode = VPOT_DISPLAY_SINGLE_DOT):
        self.__v_pot_display_mode = display_mode
        self.__v_pot_parameter = parameter
        if not parameter:
            self.unlight_vpot_leds()

    def fader_parameter(self):
        return self.__fader_parameter

    def set_fader_parameter(self, parameter):
        self.__fader_parameter = parameter
        if not parameter:
            self.reset_fader()

    def enable_meter_mode(self, Enabled, needs_to_send_meter_mode = True):
        self.__meters_enabled = Enabled
        if needs_to_send_meter_mode or Enabled:
            self.__send_meter_mode()

    def reset_fader(self):
        self.send_midi((PB_STATUS + self.__strip_index, 0, 0))

    def unlight_vpot_leds(self):
        self.send_midi((CC_STATUS + 0, 48 + self.__strip_index, 32))

    def show_full_enlighted_poti(self):
        self.send_midi((CC_STATUS + 0, 48 + self.__strip_index, VPOT_DISPLAY_WRAP * 16 + 11))

    def reset_parameter_to_default(self, param):
        param.value = param.default_value

    def handle_channel_strip_switch_ids(self, sw_id, value):
        if sw_id in range(SID_RECORD_ARM_BASE, SID_RECORD_ARM_BASE + NUM_CHANNEL_STRIPS):
            if sw_id - SID_RECORD_ARM_BASE is self.__strip_index:
                if value == BUTTON_PRESSED:
                    if self.shift_is_pressed():
                        exclusive = not self.control_is_pressed()
                        self.__toggle_mon_track(exclusive)
                    else:
                        if self.song().exclusive_arm:
                            exclusive = not self.control_is_pressed()
                        else:
                            exclusive = self.control_is_pressed()
                        self.__toggle_arm_track(exclusive)
        elif sw_id in range(SID_SOLO_BASE, SID_SOLO_BASE + NUM_CHANNEL_STRIPS):
            if sw_id - SID_SOLO_BASE is self.__strip_index:
                if value == BUTTON_PRESSED:
                    if self.shift_is_pressed():
                        self.__channel_strip_controller.add_or_remove_stored_solo(self.__assigned_track)
                    # if self.__channel_strip_controller != None:
                        # self.__channel_strip_controller.reset_solos()
#                        self.__update_solo_led()
                    else:
                        if self.song().exclusive_solo:
                            exclusive = not self.control_is_pressed()
                        else:
                            exclusive = self.control_is_pressed()
                        self.__toggle_solo_track(exclusive)
        elif sw_id in range(SID_MUTE_BASE, SID_MUTE_BASE + NUM_CHANNEL_STRIPS):
            if sw_id - SID_MUTE_BASE is self.__strip_index:
                if value == BUTTON_PRESSED:
                    self.__toggle_mute_track()
        elif sw_id in range(SID_SELECT_BASE, SID_SELECT_BASE + NUM_CHANNEL_STRIPS):
            if sw_id - SID_SELECT_BASE is self.__strip_index:
                if value == BUTTON_PRESSED: #
                    now = time.time()
                    if (now - self.__last_press_time) <= self.main_script().get_double_tap_threshold():
                        # second press within threshold -> double tap
                        if self.__fader_parameter:
                            self.reset_parameter_to_default(self.__fader_parameter)
                    else:
                        # single tap -> select track
                        self.__select_track()
                    self.__last_press_time = now
        elif sw_id in range(SID_VPOD_PUSH_BASE, SID_VPOD_PUSH_BASE + NUM_CHANNEL_STRIPS):
            if sw_id - SID_VPOD_PUSH_BASE is self.__strip_index:
                if value == BUTTON_PRESSED and self.__channel_strip_controller != None:
                    self.__channel_strip_controller.handle_pressed_v_pot(self.__strip_index, self.__stack_offset)
        elif sw_id in fader_touch_switch_ids:
            if sw_id - SID_FADER_TOUCH_SENSE_BASE is self.__strip_index:
                if value == BUTTON_PRESSED or value == BUTTON_RELEASED:
                    if self.__channel_strip_controller != None:
                        touched = value == BUTTON_PRESSED
                        self.set_is_touched(touched)
                        self.__channel_strip_controller.handle_fader_touch(self.__strip_index, self.__stack_offset, touched)
                if  value == BUTTON_PRESSED and self.main_script().get_touch_fader_to_select():
                    self.__select_track_without_folding()
                elif value == BUTTON_RELEASED and self.__faders_at_zero and not self.main_script().get_flip():
                    self._on_volume_changed()
        # elif sw_id == SID_AUTOMATION_GROUP:
            # if value == BUTTON_PRESSED:
                # self.__toggle_group_mode()

    def handle_vpot_rotation(self, strip_index, cc_value):
        if strip_index is self.__strip_index and self.__channel_strip_controller != None:
            self.__channel_strip_controller.handle_vpot_rotation(self.__strip_index, self.__stack_offset, cc_value)

    def refresh_state(self):
        if not self.__within_track_added_or_deleted:
            self.__update_track_is_selected_led()
        self.__update_solo_led()
        self.__update_mute_led()
        self.__update_arm_led()
        if not self.__within_destroy and self.__assigned_track != None:
            self.__send_meter_mode()
            self.__last_meter_value = -1
        if not self.__assigned_track:
            self.reset_fader()
            self.unlight_vpot_leds()

    def on_update_display_timer(self):
        if self.__fader_move_pending :
            self._on_volume_changed()
        if not self.main_script().is_pro_version or self.__meters_enabled and self.__channel_strip_controller.assignment_mode() == CSM_VOLPAN:
            if self.__assigned_track and isinstance(self.__assigned_track, Live.Track.Track) and self.__assigned_track.has_audio_output:
                if self.__assigned_track.can_be_armed and self.__assigned_track.arm:
                    if self.__assigned_track.has_midi_input:
                        meter_value = self.__assigned_track.input_meter_level
                    elif self.main_script().get_snappy_meters():
                        meter_value = max(self.__assigned_track.input_meter_left,
                                          self.__assigned_track.input_meter_right)
                    else:
                        meter_value = self.__assigned_track.input_meter_level
                elif self.main_script().get_snappy_meters():
                    meter_value = max(self.__assigned_track.output_meter_left,
                                      self.__assigned_track.output_meter_right)
                else:
                    meter_value = self.__assigned_track.output_meter_level
            else:
                meter_value = 0.0
            #meter_byte = int(meter_value * 12.0) + (self.__strip_index << 4)  #old value * 12
            #meter_byte = int(meter_value * 15.2) + (self.__strip_index << 4)
            #meter_byte = int(math.log(meter_value) * 15.2) + (self.__strip_index << 4)
            #meter_byte = 13 + (self.__strip_index << 4)
            #meter_byte = int(_log(0.5,2.7) * 8 + 15) + (self.__strip_index << 4)
            meter_byte = min(int(meter_value * 15.2),14) + (self.__strip_index << 4)
            if self.__last_meter_value != meter_value or meter_value != 0.0:
                self.__last_meter_value = meter_value
                self.send_midi((208, meter_byte))
                #msg = "meter_value" + str(meter_value)
                #self.MackieControlComponent.MainDisplay.send_display_string(msg, 1, 1)

    def build_midi_map(self, midi_map_handle):
        needs_takeover = False
        self.__faders_at_zero = self.main_script().get_faders_zero()
        self.__touch_to_move = self.main_script().get_touch_fader_to_move()

        if self.__fader_parameter:
            
            if self.__faders_at_zero and not self.main_script().get_flip(): # we handle the faders (control + feedback)
                Live.MidiMap.forward_midi_pitchbend(
                    self.script_handle(), midi_map_handle, self.__strip_index
                )
                if not self.__assigned_track.mixer_device.volume.value_has_listener(self._on_volume_changed):
                    self.__assigned_track.mixer_device.volume.add_value_listener(self._on_volume_changed)
                self._on_volume_changed()
            else: # let Live handle the faders both ways
                if hasattr(self.__assigned_track, "mixer_device") and self.__assigned_track.mixer_device.volume.value_has_listener(self._on_volume_changed):
                    self.__assigned_track.mixer_device.volume.remove_value_listener(self._on_volume_changed)
                feedback_rule = Live.MidiMap.PitchBendFeedbackRule()
                feedback_rule.channel = self.__strip_index
                feedback_rule.delay_in_ms = 200.0
                feedback_rule.value_pair_map = tuple()
                # feedback_rule.value_pair_map = self.build_fader_map(self.__faders_at_zero)            
                Live.MidiMap.map_midi_pitchbend_with_feedback_map(midi_map_handle, self.__fader_parameter, self.__strip_index, feedback_rule, not needs_takeover)
                Live.MidiMap.send_feedback_for_parameter(midi_map_handle, self.__fader_parameter)

        else:
            channel = self.__strip_index
            Live.MidiMap.forward_midi_pitchbend(self.script_handle(), midi_map_handle, channel)

        if self.__v_pot_parameter:
            if self.__v_pot_display_mode == VPOT_DISPLAY_SPREAD:
                range_end = 7
            else:
                range_end = 12
            feedback_rule = Live.MidiMap.CCFeedbackRule()
            feedback_rule.channel = 0
            feedback_rule.cc_no = 48 + self.__strip_index
            feedback_rule.cc_value_map = tuple([ self.__v_pot_display_mode * 16 + x for x in range(1, range_end) ])
            feedback_rule.delay_in_ms = -1.0
            Live.MidiMap.map_midi_cc_with_feedback_map(midi_map_handle, self.__v_pot_parameter, 0, FID_PANNING_BASE + self.__strip_index, Live.MidiMap.MapMode.relative_signed_bit, feedback_rule, needs_takeover)
            Live.MidiMap.send_feedback_for_parameter(midi_map_handle, self.__v_pot_parameter)
        else:
            channel = 0
            cc_no = FID_PANNING_BASE + self.__strip_index
            Live.MidiMap.forward_midi_cc(self.script_handle(), midi_map_handle, channel, cc_no)

    def handle_fader_movement(self, value14):
        if (self.__is_touched and self.__touch_to_move and self.__fader_parameter) or not self.__touch_to_move:
            remapped = self.fader_to_live(value14, self.__faders_at_zero)
            if hasattr(self.__assigned_track, 'mixer_device'):
                self.__assigned_track.mixer_device.volume.value = remapped / 16383
        self.__last_fader_moved_time = time.time()

    def _on_volume_changed(self):
        """Live → Hardware feedback (only if not touching)"""
        now = time.time()
        if (now - self.__last_fader_moved_time) < self.FEEDBACK_WAIT:
            self.__fader_move_pending = True
        elif not self.__is_touched and self.__fader_parameter:
            live_val = int(round(self.__fader_parameter.value * self.MAX_VALUE))
            fader_val = self.live_to_fader(live_val, self.__faders_at_zero)

            now = time.time()
            if (now - self.__last_feedback_time) >= self.FEEDBACK_INTERVAL:
                lsb = fader_val & 0x7F
                msb = (fader_val >> 7) & 0x7F
                self.send_midi((PB_STATUS + self.__strip_index, lsb, msb))
                self.__last_feedback_time = now
                self.__last_fader_val = fader_val
                self.__fader_move_pending = False

    def __assigned_track_index(self):
        index = 0
        for t in chain(self.visible_tracks_including_chains(), self.song().return_tracks):
            if t == self.__assigned_track:
                return index
            index += 1

        if self.__assigned_track:
            assert 0

    def __add_listeners(self):
        if not self.song().view.selected_track_has_listener(self.__update_track_is_selected_led):
            self.song().view.add_selected_track_listener(self.__update_track_is_selected_led)
        if not self.song().view.selected_chain_has_listener(self.__update_track_is_selected_led):
            self.song().view.add_selected_chain_listener(self.__update_track_is_selected_led)
        if hasattr(self.__assigned_track, 'can_be_armed') and self.__assigned_track.can_be_armed:
            self.__assigned_track.add_arm_listener(self.__update_arm_led)
            self.__assigned_track.add_current_monitoring_state_listener(self.__update_arm_led)
        self.__assigned_track.add_mute_listener(self.__update_mute_led)
        self.__assigned_track.add_muted_via_solo_listener(self.__update_mute_led)
        self.__assigned_track.add_solo_listener(self.__update_solo_led)

    def __remove_listeners(self):
        if hasattr(self.__assigned_track, 'can_be_armed') and self.__assigned_track.can_be_armed:
            if self.__assigned_track.arm_has_listener(self.__update_arm_led):
                self.__assigned_track.remove_arm_listener(self.__update_arm_led)
            if self.__assigned_track.current_monitoring_state_has_listener(self.__update_arm_led):
                self.__assigned_track.remove_current_monitoring_state_listener(self.__update_arm_led)
        if self.__assigned_track.mute_has_listener(self.__update_mute_led):
             self.__assigned_track.remove_mute_listener(self.__update_mute_led)
        if self.__assigned_track.solo_has_listener(self.__update_solo_led):
             self.__assigned_track.remove_solo_listener(self.__update_solo_led)
        if self.__assigned_track.muted_via_solo_has_listener(self.__update_mute_led):
             self.__assigned_track.remove_muted_via_solo_listener(self.__update_mute_led)

    def __send_meter_mode(self):
        on_mode = 1
        off_mode = 0
        if self.__meters_enabled:
            on_mode = on_mode | 2
        if self.__assigned_track:
            mode = on_mode
        else:
            mode = off_mode
        if self.main_script().is_extension():
            device_type = SYSEX_DEVICE_TYPE_XT
        else:
            device_type = SYSEX_DEVICE_TYPE
        self.send_midi((240,
         0,
         0,
         102,
         device_type,
         32,
         self.__strip_index,
         mode,
         247))

    def __toggle_arm_track(self, exclusive):
        if self.__assigned_track and isinstance(self.__assigned_track, Live.Track.Track) and self.__assigned_track.can_be_armed:
            self.__assigned_track.arm = not self.__assigned_track.arm
            if exclusive:
                for t in self.song().tracks:
                    if t != self.__assigned_track and t.can_be_armed:
                        t.arm = False

    def __toggle_mon_track(self, exclusive):
        if self.__assigned_track and isinstance(self.__assigned_track, Live.Track.Track) and self.__assigned_track.can_be_armed and self.__assigned_track.current_monitoring_state == 1:
            self.__assigned_track.current_monitoring_state = 0
            if exclusive:
                for t in self.song().tracks:
                    if t != self.__assigned_track and t.can_be_armed:
                        t.current_monitoring_state = 1
        else:
            for t in self.song().tracks:
                if t.can_be_armed:
                    t.current_monitoring_state = 1

    def __toggle_mute_track(self):
        if self.__assigned_track:
            self.__assigned_track.mute = not self.__assigned_track.mute

    def __toggle_solo_track(self, exclusive):
        # sel_track = self.song().view.selected_track
        if self.__assigned_track:
            self.__assigned_track.solo = not self.__assigned_track.solo
            if exclusive:
                for t in chain(self.visible_tracks_including_chains(), self.song().return_tracks):
                    if t != self.__assigned_track:
                        t.solo = False
        # self.song().view.selected_track = sel_track

    def __select_track_without_folding(self):
        if self.__assigned_track:
            chainable_device = self.chainable_device(self.__assigned_track)
            all_tracks = tuple(self.visible_tracks_including_chains()) + tuple(self.song().return_tracks)
            if isinstance(all_tracks[self.__assigned_track_index()], Live.Chain.Chain) and self.song().view.selected_chain != all_tracks[self.__assigned_track_index()]:
                self.song().view.selected_chain = all_tracks[self.__assigned_track_index()]
            elif isinstance(all_tracks[self.__assigned_track_index()], Live.Track.Track) and self.song().view.selected_track != all_tracks[self.__assigned_track_index()]:
                self.song().view.selected_track = all_tracks[self.__assigned_track_index()]

    def __select_track(self):
        if self.__assigned_track:
            chainable_device = self.chainable_device(self.__assigned_track)
            all_tracks = tuple(self.visible_tracks_including_chains()) + tuple(self.song().return_tracks)
            if isinstance(all_tracks[self.__assigned_track_index()], Live.Chain.Chain) and self.song().view.selected_chain != all_tracks[self.__assigned_track_index()]:
                self.song().view.selected_chain = all_tracks[self.__assigned_track_index()]
            elif isinstance(all_tracks[self.__assigned_track_index()], Live.Track.Track) and self.song().view.selected_track != all_tracks[self.__assigned_track_index()]:
                self.song().view.selected_track = all_tracks[self.__assigned_track_index()]
            else:
#            elif self.application().view.is_view_visible(u'Arranger'):
                if hasattr(self.__assigned_track, 'is_foldable') and self.__assigned_track.is_foldable:
                    if self.__assigned_track.fold_state:
                        self.__assigned_track.fold_state = 0
                    else:
                        self.__assigned_track.fold_state = 1
                elif hasattr(self.__assigned_track, 'can_show_chains') and self.__assigned_track.can_show_chains:
                    # if self.song().view.selected_chain:
                        # self.song().view.selected_track = all_tracks[self.__assigned_track_index()]
                    # else:
                    self.__assigned_track.is_showing_chains = not self.__assigned_track.is_showing_chains
                    if hasattr(self.__assigned_track, 'view'):
                        self.__assigned_track.view.is_collapsed = not self.__assigned_track.is_showing_chains
                elif chainable_device:
                    # if self.song().view.selected_chain:
                        # self.song().view.selected_track = all_tracks[self.__assigned_track_index()]
                    # else:
                    chainable_device.is_showing_chains = not chainable_device.is_showing_chains
                    self.__channel_strip_controller.refresh_state()
                else:
                    if hasattr(self.__assigned_track, 'view'):
                        self.__assigned_track.view.is_collapsed = not self.__assigned_track.view.is_collapsed
                    #self.__update_track_is_selected_led()

    def __update_arm_led(self):
        track = self.__assigned_track
        if track and isinstance(track, Live.Track.Track) and track.can_be_armed and track.arm:
            self.send_button_led(SID_RECORD_ARM_BASE + self.__strip_index, BUTTON_STATE_ON)
        else:
            self.send_button_led(SID_RECORD_ARM_BASE + self.__strip_index, BUTTON_STATE_OFF)
        if track and isinstance(track, Live.Track.Track) and track.can_be_armed and track.current_monitoring_state == 0:
            self.send_button_led(SID_RECORD_ARM_BASE + self.__strip_index, BUTTON_STATE_BLINKING)

    def __update_mute_led(self):
        if self.__assigned_track and self.__assigned_track.mute:
            self.send_button_led(SID_MUTE_BASE + self.__strip_index, BUTTON_STATE_ON)
        elif self.__assigned_track and self.main_script().get_show_muted_via_solo() and hasattr(self.__assigned_track, 'muted_via_solo') and self.__assigned_track.muted_via_solo:
            self.send_button_led(SID_MUTE_BASE + self.__strip_index, BUTTON_STATE_BLINKING)
        else:
            self.send_button_led(SID_MUTE_BASE + self.__strip_index, BUTTON_STATE_OFF)

    def __update_solo_led(self):
        if self.__assigned_track and self.__assigned_track.solo:
            self.send_button_led(SID_SOLO_BASE + self.__strip_index, BUTTON_STATE_ON)
        elif self.__channel_strip_controller != None and self.__channel_strip_controller.check_if_stored_solo(self.__assigned_track):
            self.send_button_led(SID_SOLO_BASE + self.__strip_index, BUTTON_STATE_BLINKING)
        else:
            self.send_button_led(SID_SOLO_BASE + self.__strip_index, BUTTON_STATE_OFF)

    def __update_track_is_selected_led(self):
#        if isinstance(self.__assigned_track, Live.Chain.Chain) and self.song().view.selected_chain == self.__assigned_track:
        if self.song().view.selected_chain and self.song().view.selected_chain == self.__assigned_track:
            self.send_button_led(SID_SELECT_BASE + self.__strip_index, BUTTON_STATE_ON)
#        elif self.__assigned_track.is_part_of_selection:
        elif self.song().view.selected_track == self.__assigned_track:
            if (self.__assigned_track.is_foldable and self.__assigned_track.fold_state == 0) or (self.__assigned_track.can_show_chains and self.__assigned_track.is_showing_chains):
                self.send_button_led(SID_SELECT_BASE + self.__strip_index, BUTTON_STATE_BLINKING)
            else:
                self.send_button_led(SID_SELECT_BASE + self.__strip_index, BUTTON_STATE_ON)
            # if self.__assigned_track.is_foldable:
                # if self.__assigned_track.fold_state:
                    # self.send_button_led(SID_AUTOMATION_GROUP, BUTTON_STATE_ON)
                # else:
                    # self.send_button_led(SID_AUTOMATION_GROUP, BUTTON_STATE_BLINKING)
            # elif self.__assigned_track.is_grouped:
                # self.send_button_led(SID_AUTOMATION_GROUP, BUTTON_STATE_BLINKING)
            # else:
                # self.send_button_led(SID_AUTOMATION_GROUP, BUTTON_STATE_OFF)
        elif self.song().view.selected_track.group_track and self.song().view.selected_track.group_track == self.__assigned_track:
            self.send_button_led(SID_SELECT_BASE + self.__strip_index, BUTTON_STATE_BLINKING)
        else:
            self.send_button_led(SID_SELECT_BASE + self.__strip_index, BUTTON_STATE_OFF)


class MasterChannelStrip(FaderZeroMappingMixin, MackieControlComponent):

    def __init__(self, main_script, software_controller=None):
        MackieControlComponent.__init__(self, main_script)
        self.__strip_index = MASTER_CHANNEL_STRIP_INDEX
        self.__assigned_track = self.song().master_track
        self.__channel_strip_controller = None
        self.__software_controller = software_controller
        self.__is_touched = False
        self.__volume = None
        self.__last_feedback_time = 0
        self.__last_fader_val = None
        self.__last_fader_moved_time = 0
        self.__fader_move_pending = False
        self.__faders_at_zero = False
        self.__touch_to_move = False

    def destroy(self):
        self.reset_fader()
        MackieControlComponent.destroy(self)

    def set_channel_strip_controller(self, channel_strip_controller):
        self.__channel_strip_controller = channel_strip_controller

    def handle_channel_strip_switch_ids(self, sw_id, value):
        pass

    def refresh_state(self):
        pass

    def on_update_display_timer(self):
        if self.__fader_move_pending:
            self._on_volume_changed()

    def enable_meter_mode(self, Enabled):
        pass

    def reset_fader(self):
        self.send_midi((PB_STATUS + self.__strip_index, 0, 0))

    def handle_touch_master_fader(self, switch_id, value):
        if self.__assigned_track:
            if value == BUTTON_PRESSED or value == BUTTON_RELEASED:
                touched = value == BUTTON_PRESSED
                self.set_is_touched(touched)
                # self.__channel_strip_controller.handle_fader_touch(self.__strip_index, 0, touched)
            if value == BUTTON_PRESSED and self.main_script().touch_fader_to_select:
                self.__software_controller._select_master_channel(collapse=False)
            elif value == BUTTON_RELEASED and self.__faders_at_zero:
                self._on_volume_changed()

    def is_touched(self):
        return self.__is_touched

    def set_is_touched(self, touched):
        self.__is_touched = touched

    def build_midi_map(self, midi_map_handle):
        if self.__assigned_track:
            needs_takeover = False
            
            self.__faders_at_zero = self.main_script().get_faders_zero()
            self.__touch_to_move = self.main_script().get_touch_fader_to_move()
            
            if self.__faders_at_zero: # we handle the faders (control + feedback)
                Live.MidiMap.forward_midi_pitchbend(
                    self.script_handle(), midi_map_handle, self.__strip_index
                )
                if self.__volume != self.master_fader_destination():
                    if self.__volume and self.__volume.value_has_listener(self._on_volume_changed):
                        self.__volume.remove_value_listener(self._on_volume_changed)
                self.__volume = self.master_fader_destination()
                if not self.__volume.value_has_listener(self._on_volume_changed):
                    self.__volume.add_value_listener(self._on_volume_changed)
                self._on_volume_changed()
            else: # let Live handle the faders both ways
                self.__volume = self.master_fader_destination()
                if self.__volume and self.__volume.value_has_listener(self._on_volume_changed):
                    self.__volume.remove_value_listener(self._on_volume_changed)
                feedback_rule = Live.MidiMap.PitchBendFeedbackRule()
                feedback_rule.channel = self.__strip_index
                feedback_rule.delay_in_ms = 200.0
                feedback_rule.value_pair_map = tuple()
                # feedback_rule.value_pair_map = self.build_fader_map(self.__faders_at_zero)
                Live.MidiMap.map_midi_pitchbend_with_feedback_map(midi_map_handle, self.__volume, self.__strip_index, feedback_rule, not needs_takeover)
                Live.MidiMap.send_feedback_for_parameter(midi_map_handle, self.__volume)

    def handle_fader_movement(self, value14):
        if (self.__is_touched and self.__touch_to_move) or not self.__touch_to_move:
            remapped = self.fader_to_live(value14, self.__faders_at_zero)
            # Scale remapped → 0.0–1.0 parameter range
            self.__volume = self.master_fader_destination()
            self.__volume.value = remapped / 16383
        self.__last_fader_moved_time = time.time()

    def _on_volume_changed(self):
        """Live → Hardware feedback (only if not touching)"""
        now = time.time()
        if (now - self.__last_fader_moved_time) < self.FEEDBACK_WAIT:
            self.__fader_move_pending = True
        elif not self.__is_touched and self.__volume:
            live_val = int(round(self.__volume.value * self.MAX_VALUE))
            fader_val = self.live_to_fader(live_val, self.__faders_at_zero)

            if (now - self.__last_feedback_time) >= self.FEEDBACK_INTERVAL:
                lsb = fader_val & 0x7F
                msb = (fader_val >> 7) & 0x7F
                self.send_midi((PB_STATUS + self.__strip_index, lsb, msb))
                self.__last_feedback_time = now
                self.__last_fader_val = fader_val
                self.__fader_move_pending = False

    def master_fader_destination(self):
        volume = None
        if self.main_script().get_flip() and self.main_script().master_fader_controls_cue_volume_on_flip:
            volume = self.__assigned_track.mixer_device.cue_volume
        else:
            volume = self.__assigned_track.mixer_device.volume
        return volume

    def reset_parameter_to_default(self, param):
        param.value = param.default_value