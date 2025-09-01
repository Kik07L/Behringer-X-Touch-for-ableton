#Embedded file name: /Users/versonator/Jenkins/live/output/Live/mac_64_static/Release/python-bundle/MIDI Remote Scripts/MackieControl/MackieControl.py
from __future__ import absolute_import, print_function, unicode_literals
from builtins import range
from builtins import object
from .consts import *
from .MainDisplay import MainDisplay
from .MainDisplayController import MainDisplayController
from .TimeDisplay import TimeDisplay
from .ChannelStrip import ChannelStrip, MasterChannelStrip
from .ChannelStripController import ChannelStripController
from .SoftwareController import SoftwareController
from .Transport import Transport
from itertools import chain
import Live
import MidiRemoteScript
import os

class MackieControl(object):
    u"""Main class that establishes the Mackie Control <-> Live interaction. It acts
       as a container/manager for all the Mackie Control sub-components like ChannelStrips,
       Displays and so on.
       Futher it is glued to Lives MidiRemoteScript C instance, which will forward some
       notifications to us, and lets us forward some requests that are needed beside the
       general Live API (see 'send_midi' or 'request_rebuild_midi_map').
    """

    def __init__(self, c_instance):

        # -------------------------------------------------------------------
        # Preferences system
        # -------------------------------------------------------------------
        # key -> (default_value, parser, comment, formatter, short_name, choices_or_limits)
        self._preferences_spec = {
            "NIGHT_MODE_ON": (
                False,
                lambda v: v.lower() in ("1", "true", "yes", "on"),
                "Enable Night Mode (true/false)",
                lambda v: "true" if v else "false",
                "might" # m looks like capital n on 7-segment display
            ),
            "COLOR_DISTANCE_MODE": (
                0,
                lambda v: self._parse_color_distance_mode(v),
                "Use alternative color matching method (0 = match by RGB distance, 1 = match primarily by hue)",
                str,
                "color",
                {0: "rgb", 1: "hue"}
            ),
            "HUE_COLOR_DISTANCE_MODE_WHITE_CUTOFF": (
                0.19,
                lambda v: float(v) if v else 0.19,
                "White cutoff for hue-based color matching method (0.00-1.00, higher value = more colors map to white scribble strip)",
                lambda v: f"{v:.2f}",  # fixed to 2 decimals
                "white",
                (0.00, 1.00)  # min/max tuple
            ),
            "USE_FUNCTION_BUTTONS": (
                0,
                lambda v: self._parse_use_function_buttons(v),
                "Use Function buttons (0=disabled, 1=function buttons set MIDI Record Quantization)",
                str,
                "funct",
                {0: "0ff", 1: "quant"}   # raw value → display string
            ),
            "SHOW_CLOCK": (
                0,
                lambda v: self._parse_show_clock(v),
                "Show current time instead of song time/beats (0=off, 1=on with seconds, 2=on without seconds)",
                str,
                "clock",
                {0: "0ff", 1: "0m", 2: "short"}   # raw value → display string
            ),
            "SNAPPY_METERS": (
                True,
                lambda v: v.lower() in ("1", "true", "yes", "on"),
                "Use snappy level meters (true/false)",
                lambda v: "true" if v else "false",
                "snppy"
            ),
            "SHOW_MUTED_VIA_SOLO": (
                False,
                lambda v: v.lower() in ("1", "true", "yes", "on"),
                "Flash Mute LED to indicate tracks muted by active solo (true/false)",
                lambda v: "true" if v else "false",
                "muted"
            ),
            "TOUCH_FADER_TO_SELECT": (
                False,
                lambda v: v.lower() in ("1", "true", "yes", "on"),
                "Select track by touching fader (true/false)",
                lambda v: "true" if v else "false",
                "touch"
            ),
        }
        # copy defaults into attributes (lowercase names)
        for key, spec in self._preferences_spec.items():
            default = spec[0]
            setattr(self, key.lower(), default)

        self._preferences = {k: spec[0] for k, spec in self._preferences_spec.items()}

        self.__c_instance = c_instance
        self.__components = []
        self.__main_display = MainDisplay(self)
        self.__components.append(self.__main_display)
        self.__main_display_controller = MainDisplayController(self, self.__main_display)
        self.__components.append(self.__main_display_controller)
        self.__time_display = TimeDisplay(self)
        self.__components.append(self.__time_display)
        self.__software_controller = SoftwareController(self)
        self.__components.append(self.__software_controller)
        self.__transport = Transport(self)
        self.__components.append(self.__transport)
        self.__channel_strips = [ ChannelStrip(self, i) for i in range(NUM_CHANNEL_STRIPS) ]
        for s in self.__channel_strips:
            self.__components.append(s)
            
        self.__master_strip = MasterChannelStrip(self)
        self.__components.append(self.__master_strip)
        self.__channel_strip_controller = ChannelStripController(self, self.__channel_strips, self.__master_strip, self.__main_display_controller)
        self.__components.append(self.__channel_strip_controller)
        self.__shift_is_pressed = False
        self.__option_is_pressed = False
        self.__control_is_pressed = False
        self.__alt_is_pressed = False
        self.is_pro_version = False
        self._received_firmware_version = False
        self._refresh_state_next_time = 0
        self._ensure_default_preferences_file()
        self._load_preferences()
        self.save_preferences() # in case an options.txt file already exists but new preferences have been added

    def disconnect(self):
        for c in self.__components:
            c.destroy()

    def connect_script_instances(self, instanciated_scripts):
        u"""Called by the Application as soon as all scripts are initialized.
           You can connect yourself to other running scripts here, as we do it
           connect the extension modules (MackieControlXTs).
        """
        try:
#            from MackieControlXT.MackieControlXT import MackieControlXT
            from XTouchXT.MackieControlXT import MackieControlXT
        except:
            print(u'failed to load the MackieControl XT script (might not be installed)')

        found_self = False
        right_extensions = []
        left_extensions = []
        for s in instanciated_scripts:
            if s is self:
                found_self = True
            elif isinstance(s, MackieControlXT):
                s.set_mackie_control_main(self)
                if found_self:
                    right_extensions.append(s)
                else:
                    left_extensions.append(s)

        assert found_self
        self.__main_display_controller.set_controller_extensions(left_extensions, right_extensions)
        self.__channel_strip_controller.set_controller_extensions(left_extensions, right_extensions)

    def request_firmware_version(self):
        if not self._received_firmware_version:
            self.send_midi((240,
             0,
             0,
             102,
             SYSEX_DEVICE_TYPE,
             19,
             0,
             247))

    def application(self):
        u"""returns a reference to the application that we are running in"""
        return Live.Application.get_application()

    def song(self):
        u"""returns a reference to the Live Song that we do interact with"""
        return self.__c_instance.song()

    def handle(self):
        u"""returns a handle to the c_interface that is needed when forwarding MIDI events
           via the MIDI map
        """
        return self.__c_instance.handle()

    def time_display(self):
        return self.__time_display.instance()

    def transport(self):
        return self.__transport.instance()

    def refresh_state(self):
        for c in self.__components:
            c.refresh_state()

        self.request_firmware_version()
        self._refresh_state_next_time = 30

    def is_extension(self):
        return False

    def request_rebuild_midi_map(self):
        u""" To be called from any components, as soon as their internal state changed in a
        way, that we do need to remap the mappings that are processed directly by the
        Live engine.
        Dont assume that the request will immediately result in a call to
        your build_midi_map function. For performance reasons this is only
        called once per GUI frame."""
        self.__c_instance.request_rebuild_midi_map()

    def build_midi_map(self, midi_map_handle):
        u"""New MIDI mappings can only be set when the scripts 'build_midi_map' function
        is invoked by our C instance sibling. Its either invoked when we have requested it
        (see 'request_rebuild_midi_map' above) or when due to a change in Lives internal state,
        a rebuild is needed."""
        for s in self.__channel_strips:
            s.build_midi_map(midi_map_handle)

        self.__master_strip.build_midi_map(midi_map_handle)
        for i in range(SID_FIRST, SID_LAST + 1):
            Live.MidiMap.forward_midi_note(self.handle(), midi_map_handle, 0, i)
            # if self.use_function_keys_for_quantization_mode or i not in function_key_control_switch_ids:
                # Live.MidiMap.forward_midi_note(self.handle(), midi_map_handle, 0, i)

        Live.MidiMap.forward_midi_cc(self.handle(), midi_map_handle, 0, JOG_WHEEL_CC_NO)

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
        u"""Use this function to send MIDI events through Live to the _real_ MIDI devices
        that this script is assigned to."""
        self.__c_instance.send_midi(midi_event_bytes)

    def send_button_led(self, buttonID, buttonState):
        self.send_midi((NOTE_ON_STATUS, buttonID, buttonState))
        BUTTON_STATES[buttonID] = buttonState

    def receive_midi(self, midi_bytes):
        if midi_bytes[0] & 240 == NOTE_ON_STATUS or midi_bytes[0] & 240 == NOTE_OFF_STATUS:
            note = midi_bytes[1]
            value = BUTTON_PRESSED if midi_bytes[2] > 0 else BUTTON_RELEASED
            if note in range(SID_FIRST, SID_LAST + 1):
                if note in display_switch_ids:
                    self.__handle_display_switch_ids(note, value)
                if note in channel_strip_switch_ids + fader_touch_switch_ids:
                    for s in self.__channel_strips:
                        s.handle_channel_strip_switch_ids(note, value)

                if note in channel_strip_control_switch_ids:
                    self.__channel_strip_controller.handle_assignment_switch_ids(note, value)
                if note in modify_key_control_switch_ids:
                    self.__software_controller.handle_modify_key_switch_ids(note, value)
                # if note == SID_FADER_TOUCH_SENSE_MASTER:
                    # self.__software_controller.handle_touch_master_fader(note, value)
                if note in function_key_control_switch_ids:
                    self.__software_controller.handle_function_key_switch_ids(note, value)
                if note in software_controls_switch_ids:
                    self.__software_controller.handle_software_controls_switch_ids(note, value)
                if note in transport_control_switch_ids:
                    self.__transport.handle_transport_switch_ids(note, value)
                if note in marker_control_switch_ids:
                    self.__transport.handle_marker_switch_ids(note, value)
                if note in jog_wheel_switch_ids:
                    self.__transport.handle_jog_wheel_switch_ids(note, value)
        elif midi_bytes[0] & 240 == CC_STATUS:
            cc_no = midi_bytes[1]
            cc_value = midi_bytes[2]
            if cc_no == JOG_WHEEL_CC_NO:
                self.__transport.handle_jog_wheel_rotation(cc_value)
            elif cc_no in range(FID_PANNING_BASE, FID_PANNING_BASE + NUM_CHANNEL_STRIPS):
                for s in self.__channel_strips:
                    s.handle_vpot_rotation(cc_no - FID_PANNING_BASE, cc_value)

        elif midi_bytes[0] == 240 and len(midi_bytes) == 12 and midi_bytes[5] == 20:
            version_bytes = midi_bytes[6:-2]
            major_version = version_bytes[1]
            self.is_pro_version = major_version > 50
            self._received_firmware_version = True

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

    def shift_is_pressed(self):
        return self.__shift_is_pressed

    def set_shift_is_pressed(self, pressed):
        self.__shift_is_pressed = pressed

    def option_is_pressed(self):
        return self.__option_is_pressed

    def set_option_is_pressed(self, pressed):
        self.__option_is_pressed = pressed

    def control_is_pressed(self):
        return self.__control_is_pressed

    def set_control_is_pressed(self, pressed):
        self.__control_is_pressed = pressed

    def alt_is_pressed(self):
        return self.__alt_is_pressed

    def set_alt_is_pressed(self, pressed):
        self.__alt_is_pressed = pressed

    def get_alternative_color_distance_mode(self):
        result = False
        if self.color_distance_mode == 1:
            result = True
        return result

    def toggle_alternative_color_distance_mode(self):
        # look up spec
        spec = self._preferences_spec["COLOR_DISTANCE_MODE"]
        default, parser, description, typ, group, mapping = spec

        # cycle between available keys
        keys = sorted(mapping.keys())
        try:
            idx = keys.index(self.color_distance_mode)
        except ValueError:
            idx = 0
        next_val = keys[(idx + 1) % len(keys)]

        # update and save
        self.color_distance_mode = next_val
        label = mapping.get(next_val, str(next_val))
        self.__time_display.show_priority_message(f"Color:  {label}", 2000)
        self.save_preferences()

    def __handle_display_switch_ids(self, switch_id, value):
        if switch_id == SID_DISPLAY_NAME_VALUE:
            if value == BUTTON_PRESSED:
                self.__channel_strip_controller.toggle_meter_mode()
        elif switch_id == SID_DISPLAY_SMPTE_BEATS:
            if value == BUTTON_PRESSED:
                if self.shift_is_pressed():
                    self.__time_display.toggle_show_clock()
                else:
                    self.__time_display.toggle_mode()

    def get_channel_strip_controller(self):
        return self.__channel_strip_controller

    def get_snappy_meters(self):
        return self.snappy_meters

    def get_alternative_color_distance_mode_white_cutoff(self):
        return self.hue_color_distance_mode_white_cutoff

    def increment_alternative_color_distance_mode_white_cutoff(self, increment):
        self.hue_color_distance_mode_white_cutoff = min(
            max(self.hue_color_distance_mode_white_cutoff + increment, 0.0), 1.0
        )

    def get_show_muted_via_solo(self):
        result = False
        if hasattr(self, 'show_muted_via_solo'):
            result = self.show_muted_via_solo
        return result

    def get_touch_fader_to_select(self):
        result = False
        if hasattr(self, 'touch_fader_to_select'):
            result = self.touch_fader_to_select
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

    def _load_preferences(self):
        """Load preferences from options.txt and apply them."""
        prefs_path = os.path.join(os.path.dirname(__file__), "options.txt")
        if not os.path.exists(prefs_path):
            return

        with open(prefs_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                # Chop off inline comments
                if "#" in line:
                    line = line.split("#", 1)[0].strip()

                if "=" not in line:
                    continue
                key, value = [p.strip() for p in line.split("=", 1)]
                self._apply_preference(key, value)


    def _apply_preference(self, key, value):
        """Apply a single preference from string using the parser in the spec."""
        spec = self._preferences_spec.get(key)
        if not spec:
            return  # unknown key, ignore
        default, parser, comment, formatter, short_name, *rest = spec
        choices_or_limits = rest[0] if rest else None
        try:
            parsed_value = parser(value)
            # If choices_or_limits is a tuple of (min, max), clamp
            if isinstance(choices_or_limits, tuple) and len(choices_or_limits) == 2:
                min_val, max_val = choices_or_limits
                parsed_value = max(min_val, min(parsed_value, max_val))
            setattr(self, key.lower(), parsed_value)
        except Exception:
            setattr(self, key.lower(), default)


    def _apply_preference(self, key, value):
        """Apply a single preference from string using the parser in the spec."""
        spec = self._preferences_spec.get(key)
        if not spec:
            return  # unknown key, ignore
        default, parser, comment, formatter, short_name, *rest = spec
        try:
            parsed_value = parser(value)
            setattr(self, key.lower(), parsed_value)
        except Exception:
            setattr(self, key.lower(), default)


    def _ensure_default_preferences_file(self):
        """Create options.txt with default values and comments if it doesn't exist."""
        prefs_path = os.path.join(os.path.dirname(__file__), "options.txt")
        if os.path.exists(prefs_path):
            return  # don't overwrite user's file

        lines = [
            "# User preferences for Behringer X-Touch"
        ]
        for key, spec in self._preferences_spec.items():
            default, parser, comment, formatter, short_name, *rest = spec

            val_str = formatter(default)
            comment_str = f" {comment}" if comment else ""
            lines.append("")
            lines.append(f"#{comment_str}")
            lines.append(f"# Default = {val_str}")
            lines.append(f"{key} = {val_str}")

        with open(prefs_path, "w") as f:
            f.write("\n".join(lines) + "\n")


    def save_preferences(self):
        """Write current preference values back into options.txt"""
        prefs_path = os.path.join(os.path.dirname(__file__), "options.txt")

        lines = [
            "# User preferences for Behringer X-Touch",
        ]
        for key, spec in self._preferences_spec.items():
            default, parser, comment, formatter, short_name, *rest = spec

            # Get the current value, falling back to the default if not set
            current_value = getattr(self, key.lower(), default)

            # Format the value using the provided formatter
            val_str = formatter(current_value)

            # Include comment if present
            comment_str = f" {comment}" if comment else ""

            lines.append("")
            lines.append(f"#{comment_str}")
            lines.append(f"# Default = {formatter(default)}")
            lines.append(f"{key} = {val_str}")

        # Write to options.txt
        with open(prefs_path, "w") as f:
            f.write("\n".join(lines) + "\n")

    def _parse_show_clock(self, v):
        v = v.strip().lower()
        if v in ("0", "off", "false", "no"):
            return 0
        if v in ("1", "on", "full"):
            return 1
        if v in ("2", "short", "no-seconds", "nos"):
            return 2
        return 0

    def _parse_use_function_buttons(self, v):
        v = v.strip().lower()
        if v in ("0", "off", "false", "no"):
            return 0
        if v in ("1", "on", "quantization", "quantization mode"):
            return 1
        return 0
        
    def _parse_color_distance_mode(self, v):
        v = v.strip().lower()
        if v in ("0", "off", "rgb", "false", "no"):
            return 0
        if v in ("1", "on", "hue", "true"):
            return 1
        return 0