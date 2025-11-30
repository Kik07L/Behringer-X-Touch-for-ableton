#Embedded file name: /Users/versonator/Jenkins/live/output/Live/mac_64_static/Release/python-bundle/MIDI Remote Scripts/MackieControlXT/MackieControlXT.py
from __future__ import absolute_import, print_function, unicode_literals
from builtins import range
from builtins import object
from XTouch.consts import *
from XTouch.MainDisplay import MainDisplay
from XTouch.ChannelStrip import ChannelStrip
from itertools import chain
import Live

class MackieControlXT(object):
    u"""Extension for a Mackie Control.
       Only works hand in hand with a 'main' Mackie Control as master
    """

    def __init__(self, c_instance):
        self.__c_instance = c_instance
        self.__components = []
        self.__main_display = MainDisplay(self)
        self.__components.append(self.__main_display)
        self.__channel_strips = [ ChannelStrip(self, i) for i in range(NUM_CHANNEL_STRIPS) ]
        for s in self.__channel_strips:
            self.__components.append(s)

        self._mackie_control_main = None
        self.is_pro_version = False
        self._received_firmware_version = False
        self._refresh_state_next_time = 0

    def disconnect(self):
        for c in self.__components:
            c.destroy()

    def connect_script_instances(self, instanciated_scripts):
        pass

    def request_firmware_version(self):
        if not self._received_firmware_version:
            self.send_midi((240,
             0,
             0,
             102,
             SYSEX_DEVICE_TYPE_XT,
             19,
             0,
             247))

    def is_extension(self):
        return True

    def time_display(self):
        return self.__time_display.instance()

    def mackie_control_main(self, mackie_control_main):
        return self._mackie_control_main

    def set_mackie_control_main(self, mackie_control_main):
        self._mackie_control_main = mackie_control_main

    def channel_strips(self):
        return self.__channel_strips

    def main_display(self):
        return self.__main_display

    def shift_is_pressed(self):
        is_pressed = False
        if self._mackie_control_main != None:
            is_pressed = self._mackie_control_main.shift_is_pressed()
        return is_pressed

    def option_is_pressed(self):
        is_pressed = False
        if self._mackie_control_main != None:
            is_pressed = self._mackie_control_main.option_is_pressed()
        return is_pressed

    def control_is_pressed(self):
        is_pressed = False
        if self._mackie_control_main != None:
            is_pressed = self._mackie_control_main.control_is_pressed()
        return is_pressed

    def alt_is_pressed(self):
        is_pressed = False
        if self._mackie_control_main != None:
            is_pressed = self._mackie_control_main.alt_is_pressed()
        return is_pressed

    def get_snappy_meters(self):
        result = False
        if self._mackie_control_main != None:
            result = self._mackie_control_main.get_snappy_meters()
        return result

    def get_color_distance_mode(self):
        return self._mackie_control_main.get_color_distance_mode()

    def get_show_muted_via_solo(self):
        result = False
        if hasattr(self, '_mackie_control_main') and self._mackie_control_main != None:
            result = self._mackie_control_main.get_show_muted_via_solo()
        return result

    def get_touch_fader_to_select(self):
        result = False
        if hasattr(self, '_mackie_control_main') and self._mackie_control_main != None:
            result = self._mackie_control_main.get_touch_fader_to_select()
        return result

    def get_faders_zero(self):
        result = False
        if hasattr(self, '_mackie_control_main') and self._mackie_control_main != None:
            result = self._mackie_control_main.get_faders_zero()
        return result

    def get_faders_zero_calibrate(self):
        result = None
        if hasattr(self, '_mackie_control_main') and self._mackie_control_main != None:
            result = self._mackie_control_main.get_faders_zero_calibrate()
        return result

    def get_touch_fader_to_move(self):
        result = False
        if hasattr(self, '_mackie_control_main') and self._mackie_control_main != None:
            result = self._mackie_control_main.get_touch_fader_to_move()
        return result

    def get_flip(self):
        result = False
        if hasattr(self, '_mackie_control_main') and self._mackie_control_main != None:
            result = self._mackie_control_main.get_flip()
        return result

    def get_double_tap_threshold(self):
        result = 0.2
        if hasattr(self, '_mackie_control_main') and self._mackie_control_main != None:
            result = self._mackie_control_main.get_double_tap_threshold()
        return result        

    def application(self):
        return Live.Application.get_application()

    def song(self):
        return self.__c_instance.song()

    def handle(self):
        return self.__c_instance.handle()

    def refresh_state(self):
        for c in self.__components:
            c.refresh_state()

        self.request_firmware_version()
        self._refresh_state_next_time = 30

    def request_rebuild_midi_map(self):
        self.__c_instance.request_rebuild_midi_map()

    def build_midi_map(self, midi_map_handle):
        for s in self.__channel_strips:
            s.build_midi_map(midi_map_handle)

        for i in channel_strip_switch_ids + fader_touch_switch_ids:
            Live.MidiMap.forward_midi_note(self.handle(), midi_map_handle, 0, i)

    def update_display(self):
        if self._refresh_state_next_time > 0:
            self._refresh_state_next_time -= 1
            if self._refresh_state_next_time == 0:
                for c in self.__components:
                    c.refresh_state()

                self.request_firmware_version()
        for c in self.__components:
            c.on_update_display_timer()

    def send_midi(self, midi_event_bytes):
        self.__c_instance.send_midi(midi_event_bytes)

    def send_button_led(self, buttonID, buttonState):
        if buttonState != BUTTON_STATE_HEARTBEAT:
            self.send_midi((NOTE_ON_STATUS, buttonID, buttonState))
        BUTTON_STATES[buttonID] = buttonState

    def receive_midi(self, midi_bytes):
        if midi_bytes[0] & 240 == NOTE_ON_STATUS or midi_bytes[0] & 240 == NOTE_OFF_STATUS:
            note = midi_bytes[1]
            value = BUTTON_PRESSED if midi_bytes[2] > 0 else BUTTON_RELEASED
            if note in range(SID_FIRST, SID_LAST + 1):
                if note in channel_strip_switch_ids + fader_touch_switch_ids:
                    for s in self.__channel_strips:
                        s.handle_channel_strip_switch_ids(note, value)

        elif midi_bytes[0] & 240 == CC_STATUS:
            cc_no = midi_bytes[1]
            cc_value = midi_bytes[2]
            if cc_no in range(FID_PANNING_BASE, FID_PANNING_BASE + NUM_CHANNEL_STRIPS):
                for s in self.__channel_strips:
                    s.handle_vpot_rotation(cc_no - FID_PANNING_BASE, cc_value)

        elif midi_bytes[0] == 240 and len(midi_bytes) == 12 and midi_bytes[5] == 20:
            version_bytes = midi_bytes[6:-2]
            major_version = version_bytes[1]
            self.is_pro_version = major_version > 50
            self._received_firmware_version = True

        elif self.get_faders_zero() and midi_bytes[0] & 0xF0 == 0xE0:  # pitchbend
            channel = midi_bytes[0] & 0x0F
            lsb = midi_bytes[1]
            msb = midi_bytes[2]
            value14 = (msb << 7) | lsb

            # route to the correct channel strip
            if channel < len(self.__channel_strips):
                self.__channel_strips[channel].handle_fader_movement(value14)

    def can_lock_to_devices(self):
        return False

    def suggest_input_port(self):
        return u''

    def suggest_output_port(self):
        return u''

    def suggest_map_mode(self, cc_no, channel):
        result = Live.MidiMap.MapMode.absolute
        if cc_no in range(FID_PANNING_BASE, FID_PANNING_BASE + NUM_CHANNEL_STRIPS):
            result = Live.MidiMap.MapMode.relative_signed_bit
        return result

    def visible_tracks_including_chains(self):
        """
        Returns a flattened list of all visible tracks, including any chains
        that are currently unfolded for a given track.
        """

        # If Arrangement view is main view: simply return visible tracks (we won't bother with chains)
        # if self.application().view.focused_document_view == "Arranger":
            # return self.song().visible_tracks

        # This list will hold the final, flattened result.
        tracks_and_chains_list = []

        # Iterate through the top-level visible tracks.
        for track in self.song().visible_tracks:
            # First, add the main track itself.
            tracks_and_chains_list.append(track)

            # Check if the track can and is currently showing its chains.
            if track.can_show_chains and track.is_showing_chains:
                # If so, extend our list with the track's chains.
                for device in track.devices:
                    if hasattr(device, 'can_show_chains') and device.can_show_chains and device.is_showing_chains:
                        for single_chain in chain(device.chains, device.return_chains):
                            tracks_and_chains_list.append(single_chain)
                            for chain_device in single_chain.devices:
                                if isinstance(chain_device, Live.RackDevice.RackDevice) and chain_device.can_show_chains and chain_device.is_showing_chains:
                                    tracks_and_chains_list.extend(list(chain_device.chains))
                                    tracks_and_chains_list.extend(list(chain_device.return_chains))
                        # This is the correct device (e.g., a Drum Rack).
                        # Extend our list with its chains.
                        # tracks_and_chains_list.extend(list(device.chains))
                        # tracks_and_chains_list.extend(list(device.return_chains))
                        # Once found, we can break the inner loop
                        # as only one device's chains can be shown at a time.
                        break
        
        return tracks_and_chains_list
        
    def tracks_including_chains(self):
        """
        Returns a flattened list of all tracks, including any chains
        that can be unfolded for a given track.
        """
        # This list will hold the final, flattened result.
        tracks_and_chains_list = []

        # Iterate through the top-level tracks.
        for track in self.song().tracks:
            # First, add the main track itself.
            tracks_and_chains_list.append(track)

            # Check if the track can show its chains.
            if track.can_show_chains:
                # If so, extend our list with the track's chains.
                for device in track.devices:
                    if hasattr(device, 'can_show_chains') and device.can_show_chains:
                        for single_chain in chain(device.chains, device.return_chains):
                            tracks_and_chains_list.append(single_chain)
                            for chain_device in single_chain.devices:
                                if isinstance(chain_device, Live.RackDevice.RackDevice) and chain_device.can_show_chains:
                                    tracks_and_chains_list.extend(list(chain_device.chains))
                                    tracks_and_chains_list.extend(list(chain_device.return_chains))
                        # This is the correct device (e.g., a Drum Rack).
                        # Extend our list with its chains.
                        # tracks_and_chains_list.extend(list(device.chains))
                        # tracks_and_chains_list.extend(list(device.return_chains))
                        # Once found, we can break the inner loop
                        # as only one device's chains can be shown at a time.
                        break
        
        return tracks_and_chains_list

    def chainable_device(self, track):
        for chain_device in track.devices:
            if isinstance(chain_device, Live.RackDevice.RackDevice) and chain_device.can_show_chains:
                return chain_device
        return None
