#Embedded file name: /Users/versonator/Jenkins/live/output/Live/mac_64_static/Release/python-bundle/MIDI Remote Scripts/MackieControl/Transport.py
from __future__ import absolute_import, print_function, unicode_literals
from __future__ import division
from past.utils import old_div
from .MackieControlComponent import *
import time

class Transport(MackieControlComponent):
    u"""Representing the transport section of the Mackie Control: """

    def __init__(self, main_script):
        MackieControlComponent.__init__(self, main_script)
        self.__forward_button_down = False
        self.____rewind_button_down = False
        self.__zoom_button_down = False
        self.__scrub_button_down = False
        self.__cursor_left_is_down = False
        self.__cursor_right_is_down = False
        self.__cursor_up_is_down = False
        self.__cursor_down_is_down = False
        self.__cursor_repeat_delay = 0
        self.__transport_repeat_delay = 0
        self.____fast_forward_counter = 0
        self.__fast___rewind_counter = 0
        self.__jog_step_count_forward = 0
        self.__jog_step_count_backwards = 0
        self.__last_focussed_clip_play_state = CLIP_STATE_INVALID
        self.__metronome_led_state = False
        self._metronome_flash_ticks = 0
        self._last_beat = None

        self.__assign_mutable_buttons()

        """ Settings menu system """
        self._in_settings_menu = False
        self._menu_items = list(self.main_script()._preferences_spec.items())  # [(key, (default, parser, desc, formatter, short_name)), ...]
        self._menu_index = 0

        self.song().add_record_mode_listener(self.__update_record_button_led)
        self.song().add_is_playing_listener(self.__update_play_button_led)
        self.song().add_loop_listener(self.__update_loop_button_led)
        self.song().add_punch_out_listener(self.__update_punch_out_button_led)
        self.song().add_punch_in_listener(self.__update_punch_in_button_led)
        self.song().add_metronome_listener(self.__update_metronome_button_led)
        self.song().add_can_jump_to_prev_cue_listener(self.__update_prev_cue_button_led)
        self.song().add_can_jump_to_next_cue_listener(self.__update_next_cue_button_led)
        self.application().view.add_is_view_visible_listener(u'Session', self.__on_session_is_visible_changed)
        self.song().view.add_follow_song_listener(self.__update_follow_song_button_led)
        self.refresh_state()

    def destroy(self):
        self.song().remove_record_mode_listener(self.__update_record_button_led)
        self.song().remove_is_playing_listener(self.__update_play_button_led)
        self.song().remove_loop_listener(self.__update_loop_button_led)
        self.song().remove_punch_out_listener(self.__update_punch_out_button_led)
        self.song().remove_punch_in_listener(self.__update_punch_in_button_led)
        self.song().remove_metronome_listener(self.__update_metronome_button_led)
        self.song().remove_can_jump_to_prev_cue_listener(self.__update_prev_cue_button_led)
        self.song().remove_can_jump_to_next_cue_listener(self.__update_next_cue_button_led)
        self.application().view.remove_is_view_visible_listener(u'Session', self.__on_session_is_visible_changed)
        for note in transport_control_switch_ids:
            self.send_button_led(note, BUTTON_STATE_OFF)

        for note in jog_wheel_switch_ids:
            self.send_button_led(note, BUTTON_STATE_OFF)

        for note in marker_control_switch_ids:
            self.send_button_led(note, BUTTON_STATE_OFF)

        MackieControlComponent.destroy(self)

    def instance(self):
        """Return self for public access."""
        return self

    def refresh_state(self):
        self.__assign_mutable_buttons()
        self.__update_play_button_led()
        self.__update_record_button_led()
        self.__update_prev_cue_button_led()
        self.__update_next_cue_button_led()
        self.__update_loop_button_led()
        self.__update_punch_in_button_led()
        self.__update_punch_out_button_led()
        self.__forward_button_down = False
        self.____rewind_button_down = False
        self.__zoom_button_down = False
        self.__scrub_button_down = False
        self.__cursor_left_is_down = False
        self.__cursor_right_is_down = False
        self.__cursor_up_is_down = False
        self.__cursor_down_is_down = False
        self.__cursor_repeat_delay = 0
        self.__transport_repeat_delay = 0
        self.____fast_forward_counter = 0
        self.__fast___rewind_counter = 0
        self.__jog_step_count_forward = 0
        self.__jog_step_count_backwards = 0
        self.__last_focussed_clip_play_state = CLIP_STATE_INVALID
        self.__update_forward_rewind_leds()
        self.__update_zoom_button_led()
        self.__update_scrub_button_led()
        self.__update_metronome_button_led()
        self.__update_follow_song_button_led()

    def session_is_visible(self):
        return self.application().view.is_view_visible(u'Session')
#        return self.application().view.focused_document_view == 'Session'

    def selected_clip_slot(self):
        return self.song().view.highlighted_clip_slot

    def on_update_display_timer(self):
        if self.__transport_repeat_delay > 2:
            if self.alt_is_pressed():
                base_acceleration = 1
            else:
                base_acceleration = self.song().signature_numerator
            if self.song().is_playing:
                base_acceleration *= 4
            if not (self.__forward_button_down and self.____rewind_button_down):
                if self.__forward_button_down:
                    self.____fast_forward_counter += 1
                    self.__fast___rewind_counter -= 4
                    if not self.alt_is_pressed():
                        self.__fast_forward(base_acceleration + max(1, self.____fast_forward_counter / 4))
                    else:
                        self.__fast_forward(base_acceleration)
                if self.____rewind_button_down:
                    self.__fast___rewind_counter += 1
                    self.____fast_forward_counter -= 4
                    if not self.alt_is_pressed():
                        self.__rewind(base_acceleration + max(1, self.__fast___rewind_counter / 4))
                    else:
                        self.__rewind(base_acceleration)
        else:
            self.__transport_repeat_delay += 1
        if self.__cursor_repeat_delay > 2:
            if self.__cursor_left_is_down:
                self.__on_cursor_left_pressed()
            if self.__cursor_right_is_down:
                self.__on_cursor_right_pressed()
            if self.__cursor_up_is_down:
                self.__on_cursor_up_pressed()
            if self.__cursor_down_is_down:
                self.__on_cursor_down_pressed()
        else:
            self.__cursor_repeat_delay += 1
        if self.session_is_visible():
            self.__update_zoom_led_in_session()
#        else:
#            self.__update_scrub_button_led()
        self.__offline_metronome_tick()


    def handle_marker_switch_ids(self, switch_id, value):
        if switch_id == SID_TRANSPORT_MARKER:
            if value == BUTTON_PRESSED:
                if self.control_is_pressed():
                    self.song().set_or_delete_cue()
                else:
                    if self.shift_is_pressed():
                        None
                    else:
                        self.__jump_to_prev_cue()
        elif switch_id == SID_TRANSPORT_NUDGE:
            if value == BUTTON_PRESSED:
                self.__jump_to_next_cue()
        elif switch_id == SID_TRANSPORT_CYCLE:
            if value == BUTTON_PRESSED:
                self.__toggle_loop()
        elif switch_id == SID_TRANSPORT_DROP:
            if value == BUTTON_PRESSED:
                if self.control_is_pressed():
                    self.__set_loopstart_from_cur_position()
                else:
                    self.__toggle_punch_in()
        elif switch_id == SID_TRANSPORT_REPLACE:
            if value == BUTTON_PRESSED:
                if self.control_is_pressed():
                    self.__set_loopend_from_cur_position()
                else:
                    self.__toggle_punch_out()
        # elif switch_id == SID_MARKER_HOME:
            # if value == BUTTON_PRESSED:
                # self.__goto_home()
#        elif switch_id == SID_TRANSPORT_SOLO:
#            if value == BUTTON_PRESSED:
#                self.__goto_end()

    def handle_transport_switch_ids(self, switch_id, value):
        if switch_id == SID_TRANSPORT_REWIND:
            if value == BUTTON_PRESSED:
                self.__rewind()
                self.____rewind_button_down = True
            elif value == BUTTON_RELEASED:
                self.____rewind_button_down = False
                self.__fast___rewind_counter = 0
            self.__update_forward_rewind_leds()
        elif switch_id == SID_TRANSPORT_FAST_FORWARD:
            if value == BUTTON_PRESSED:
                self.__fast_forward()
                self.__forward_button_down = True
            elif value == BUTTON_RELEASED:
                self.__forward_button_down = False
                self.____fast_forward_counter = 0
            self.__update_forward_rewind_leds()
        elif switch_id == SID_TRANSPORT_STOP:
            if value == BUTTON_PRESSED:
                self.__stop_song()
        elif switch_id == SID_TRANSPORT_PLAY:
            if value == BUTTON_PRESSED:
                self.__start_song()
        elif switch_id == SID_TRANSPORT_RECORD:
            if value == BUTTON_PRESSED:
                self.__toggle_record()

        elif switch_id == SID_TRANSPORT_CLICK:
            if value == BUTTON_PRESSED:
                if self.control_is_pressed():
                    self.__on_tap_tempo(    )
                else:
                    self.__toggle_metronome()

        elif switch_id == SID_AUTOMATION_LATCH:
                if value == BUTTON_PRESSED:
                    self.__toggle_follow()


    def handle_jog_wheel_rotation(self, value):
        backwards = value >= 64

        if not self._in_settings_menu:
            if self.control_is_pressed():
                if self.alt_is_pressed():
                    step = 0.1
                else:
                    step = 1.0
                if backwards:
                    amount = -(value - 64)
                else:
                    amount = value
                tempo = max(20, min(999, self.song().tempo + amount * step))
                self.song().tempo = tempo
            elif self.session_is_visible():
                num_steps_per_session_scroll = 4
                if backwards:
                    self.__jog_step_count_backwards += 1
                    if self.__jog_step_count_backwards >= num_steps_per_session_scroll:
                        self.__jog_step_count_backwards = 0
                        step = -1
                    else:
                        step = 0
                else:
                    self.__jog_step_count_forward += 1
                    if self.__jog_step_count_forward >= num_steps_per_session_scroll:
                        self.__jog_step_count_forward = 0
                        step = 1
                    else:
                        step = 0
                if step:
                    new_index = list(self.song().scenes).index(self.song().view.selected_scene) + step
                    new_index = min(len(self.song().scenes) - 1, max(0, new_index))
                    self.song().view.selected_scene = self.song().scenes[new_index]
            else:
                if self.__zoom_button_down:
    #            if self.shift_is_pressed():
                    nav = Live.Application.Application.View.NavDirection
                    if backwards:
                        self.application().view.zoom_view(nav.left, u'', self.alt_is_pressed())
                    else:
                        self.application().view.zoom_view(nav.right, u'', self.alt_is_pressed())
                else:

                    if backwards:
                        step = max(1.0, (value - 64) / 2.0)
                    else:
                        step = max(1.0, value / 2.0)
                    if self.song().is_playing or self.shift_is_pressed():
                        step *= 4.0

                    if self.option_is_pressed():
                        if self.alt_is_pressed():
                            if backwards:
                                self.song().loop_length -= step
                            else:
                                self.song().loop_length += step
                        else:
                            if backwards:
                                self.song().loop_start -= step
                            else:
                                self.song().loop_start += step
                    else:
                        if self.alt_is_pressed():
                            step /= 4.0
                        if self.__scrub_button_down:
                            if backwards:
                                self.song().scrub_by(-step)
                            else:
                                self.song().scrub_by(step)
                        elif backwards:
                            self.song().jump_by(-step)
                        else:
                            self.song().jump_by(step)
        else:
            self._toggle_current_preference(not backwards)
            self._show_current_menu_item()

##                if self.option_is_pressed():
##                    if self.alt_is_pressed():
##                        if backwards:
##                            self.song().loop_length -= 1
##                        else:
##                            self.song().loop_length += 1
##                    else:
##                        if backwards:
##                            self.song().loop_start -= 1
##                        else:
##                            self.song().loop_start += 1
##                else:
##                    if backwards:
##                        step = max(1.0, (value - 64) / 2.0)
##                    else:
##                        step = max(1.0, value / 2.0)
##                    if self.song().is_playing or self.shift_is_pressed():
##                        step *= 4.0
##                    if self.alt_is_pressed():
##                        step /= 4.0
##                    if self.__scrub_button_down:
##                        if backwards:
##                            self.song().scrub_by(-step)
##                        else:
##                            self.song().scrub_by(step)
##                    elif backwards:
##                        self.song().jump_by(-step)
##                    else:
##                        self.song().jump_by(step)

    def handle_jog_wheel_switch_ids(self, switch_id, value):
        if not self._in_settings_menu:
            if switch_id == SID_JOG_CURSOR_UP:
                """ code for direct white cut-off control for hue color matching method, redundant now thanks to settings menu
                if self.shift_is_pressed() and value == BUTTON_PRESSED and self.main_script().get_color_distance_mode() == True:
                    self.main_script().increment_hue_color_distance_mode_white_cutoff(+0.01)
                    self.main_script().time_display().show_priority_message("white. " + f'{self.main_script().get_hue_color_distance_mode_white_cutoff():.2f}', 1000)
                    self.main_script().save_preferences()
                elif value == BUTTON_PRESSED:
                """
                if value == BUTTON_PRESSED:
                    self.__cursor_up_is_down = True
                    self.__cursor_repeat_delay = 0
                    self.__on_cursor_up_pressed()
                elif value == BUTTON_RELEASED:
                    self.__cursor_up_is_down = False
            elif switch_id == SID_JOG_CURSOR_DOWN:
                """ code for direct white cut-off control for hue color matching method, redundant now thanks to settings menu
                if self.shift_is_pressed() and value == BUTTON_PRESSED and self.main_script().get_color_distance_mode() == True:
                    self.main_script().increment_hue_color_distance_mode_white_cutoff(-0.01)
                    self.main_script().time_display().show_priority_message("white. " + f'{self.main_script().get_hue_color_distance_mode_white_cutoff():.2f}', 1000)
                    self.main_script().save_preferences()
                elif value == BUTTON_PRESSED:
                """
                if value == BUTTON_PRESSED:
                    self.__cursor_down_is_down = True
                    self.__cursor_repeat_delay = 0
                    self.__on_cursor_down_pressed()
                elif value == BUTTON_RELEASED:
                    self.__cursor_down_is_down = False
            elif switch_id == SID_JOG_CURSOR_LEFT:
                if value == BUTTON_PRESSED:
                    self.__cursor_left_is_down = True
                    self.__cursor_repeat_delay = 0
                    self.__on_cursor_left_pressed()
                elif value == BUTTON_RELEASED:
                    self.__cursor_left_is_down = False
            elif switch_id == SID_JOG_CURSOR_RIGHT:
                if value == BUTTON_PRESSED:
                    self.__cursor_right_is_down = True
                    self.__cursor_repeat_delay = 0
                    self.__on_cursor_right_pressed()
                elif value == BUTTON_RELEASED:
                    self.__cursor_right_is_down = False
            elif switch_id == SID_JOG_ZOOM:
                if value == BUTTON_PRESSED:
                    if self.shift_is_pressed() and not self._in_settings_menu:
                        # Enter settings menu
                        self._in_settings_menu = True
                        #self._menu_index = 0 # edited this out to have position in menu preserved after exiting and re-entering
                        self._show_current_menu_item()
                    elif self.session_is_visible():
                        if self.selected_clip_slot():
                            if self.alt_is_pressed():
                                self.selected_clip_slot().has_stop_button = not self.selected_clip_slot().has_stop_button
                            elif self.option_is_pressed():
                                self.selected_clip_slot().stop()
                            else:
                                self.selected_clip_slot().fire()
                    else:
                        self.__zoom_button_down = not self.__zoom_button_down
                        self.__update_zoom_button_led()
            elif switch_id == self.__scrub_button:
                if value == BUTTON_PRESSED:
                    if self.session_is_visible():
                        if self.option_is_pressed():
                            self.song().stop_all_clips()
                        else:
                            self.song().view.selected_scene.fire_as_selected()
                    else:
                        self.__scrub_button_down = not self.__scrub_button_down
    #                    self.song().back_to_arranger = 0
                        self.__update_scrub_button_led()

        elif value == BUTTON_PRESSED:
            if switch_id == SID_JOG_CURSOR_UP:
                self._previous_menu_item()
                # self._menu_index = (self._menu_index - 1) % len(self._menu_items)
            elif switch_id == SID_JOG_CURSOR_DOWN:
                self._next_menu_item()
                # self._menu_index = (self._menu_index + 1) % len(self._menu_items)
            elif switch_id in (SID_JOG_CURSOR_LEFT, SID_JOG_CURSOR_RIGHT):
                self._toggle_current_preference(switch_id == SID_JOG_CURSOR_RIGHT)
            elif switch_id == SID_JOG_ZOOM:
                self.save_preferences_and_exit()
                self.main_script().time_display().show_priority_message("SAWED", 1000)
                return True
            elif switch_id == self.__scrub_button:
                self._reset_current_preference_to_default()
            self._show_current_menu_item()
            return True






    def __on_cursor_up_pressed(self):
        nav = Live.Application.Application.View.NavDirection
        if self.__zoom_button_down:
            self.application().view.zoom_view(nav.up, u'', self.alt_is_pressed())
        else:
            self.application().view.scroll_view(nav.up, u'', self.alt_is_pressed())

    def __on_cursor_down_pressed(self):
        nav = Live.Application.Application.View.NavDirection
        if self.__zoom_button_down:
            self.application().view.zoom_view(nav.down, u'', self.alt_is_pressed())
        else:
            self.application().view.scroll_view(nav.down, u'', self.alt_is_pressed())

    def __on_cursor_left_pressed(self):
        nav = Live.Application.Application.View.NavDirection
        if self.__zoom_button_down:
            self.application().view.zoom_view(nav.left, u'', self.alt_is_pressed())
        else:
            self.application().view.scroll_view(nav.left, u'', self.alt_is_pressed())

    def __on_cursor_right_pressed(self):
        nav = Live.Application.Application.View.NavDirection
        if self.__zoom_button_down:
            self.application().view.zoom_view(nav.right, u'', self.alt_is_pressed())
        else:
            self.application().view.scroll_view(nav.right, u'', self.alt_is_pressed())

    def __toggle_record(self):
        self.song().record_mode = not self.song().record_mode

    def __toggle_metronome(self):
        self.song().metronome = not self.song().metronome

    def __on_tap_tempo(self):
        self.song().tap_tempo()

    def __rewind(self, acceleration = 1):
        beats = acceleration
        self.song().jump_by(-beats)

    def __fast_forward(self, acceleration = 1):
        beats = acceleration
        self.song().jump_by(beats)

    def __stop_song(self):
        self.song().stop_playing()

    def __start_song(self):
        if self.shift_is_pressed():
            if not self.song().is_playing:
                self.song().continue_playing()
            else:
                self.song().stop_playing()
        elif self.control_is_pressed():
            self.song().play_selection()
        else:
            self.song().start_playing()

    def __toggle_follow(self):
        self.song().view.follow_song = not self.song().view.follow_song

    def __toggle_loop(self):
        self.song().loop = not self.song().loop

    def __toggle_punch_in(self):
        self.song().punch_in = not self.song().punch_in

    def __toggle_punch_out(self):
        self.song().punch_out = not self.song().punch_out

    def __jump_to_prev_cue(self):
        self.song().jump_to_prev_cue()

    def __jump_to_next_cue(self):
        self.song().jump_to_next_cue()

    def __set_loopstart_from_cur_position(self):
        if self.song().current_song_time < self.song().loop_start + self.song().loop_length:
            old_loop_start = self.song().loop_start
            self.song().loop_start = self.song().current_song_time
            self.song().loop_length += old_loop_start - self.song().loop_start

    def __set_loopend_from_cur_position(self):
        if self.song().current_song_time > self.song().loop_start:
            self.song().loop_length = self.song().current_song_time - self.song().loop_start

    def __goto_home(self):
        self.song().current_song_time = 0

    def __goto_end(self):
        self.song().current_song_time = self.song().last_event_time

    def __on_session_is_visible_changed(self):
        if not self.session_is_visible():
            self.__update_zoom_button_led()

    def __update_zoom_led_in_session(self):
        if self.session_is_visible():
            clip_slot = self.selected_clip_slot()
            if clip_slot and clip_slot.clip:
                if clip_slot.clip.is_triggered:
                    state = CLIP_TRIGGERED
                elif clip_slot.clip.is_playing:
                    state = CLIP_PLAYING
                else:
                    state = CLIP_STOPPED
            else:
                state = CLIP_STOPPED
            if state != self.__last_focussed_clip_play_state:
                self.__last_focussed_clip_play_state = state
                if state == CLIP_PLAYING:
                    self.send_button_led(SID_JOG_ZOOM, BUTTON_STATE_ON)
                elif state == CLIP_TRIGGERED:
                    self.send_button_led(SID_JOG_ZOOM, BUTTON_STATE_BLINKING)
                else:
                    self.send_button_led(SID_JOG_ZOOM, BUTTON_STATE_OFF)

    def __update_forward_rewind_leds(self):
        if self.__forward_button_down:
            self.send_button_led(SID_TRANSPORT_FAST_FORWARD, BUTTON_STATE_ON)
            self.__transport_repeat_delay = 0
        else:
            self.send_button_led(SID_TRANSPORT_FAST_FORWARD, BUTTON_STATE_OFF)
        if self.____rewind_button_down:
            self.send_button_led(SID_TRANSPORT_REWIND, BUTTON_STATE_ON)
            self.__transport_repeat_delay = 0
        else:
            self.send_button_led(SID_TRANSPORT_REWIND, BUTTON_STATE_OFF)

    def __update_zoom_button_led(self):
        if self.__zoom_button_down:
            self.send_button_led(SID_JOG_ZOOM, BUTTON_STATE_ON)
        else:
            self.send_button_led(SID_JOG_ZOOM, BUTTON_STATE_OFF)

    def __update_scrub_button_led(self):
#        if self.session_is_visible():
#            if self.__scrub_button_down:
#                self.send_button_led(self.__scrub_button, BUTTON_STATE_ON)
#            else:
#                self.send_button_led(self.__scrub_button, BUTTON_STATE_OFF)
#        else:
#            if self.song().back_to_arranger:
#                self.send_button_led(self.__scrub_button, BUTTON_STATE_ON)
#            else:
#                self.send_button_led(self.__scrub_button, BUTTON_STATE_OFF)
        if self.__scrub_button_down:
            self.send_button_led(self.__scrub_button, BUTTON_STATE_ON)
        else:
            self.send_button_led(self.__scrub_button, BUTTON_STATE_OFF)


    def __update_play_button_led(self):
        if self.song().is_playing:
            self.send_button_led(SID_TRANSPORT_PLAY, BUTTON_STATE_ON)
            self.send_button_led(SID_TRANSPORT_STOP, BUTTON_STATE_OFF)
        else:
            self.send_button_led(SID_TRANSPORT_PLAY, BUTTON_STATE_OFF)
            self.send_button_led(SID_TRANSPORT_STOP, BUTTON_STATE_ON)

    def __update_record_button_led(self):
        if self.song().record_mode:
            self.send_button_led(SID_TRANSPORT_RECORD, BUTTON_STATE_ON)
        else:
            self.send_button_led(SID_TRANSPORT_RECORD, BUTTON_STATE_OFF)

    def __update_follow_song_button_led(self):
        if self.song().view.follow_song:
            self.send_button_led(SID_AUTOMATION_LATCH, BUTTON_STATE_ON)
        else:
            self.send_button_led(SID_AUTOMATION_LATCH, BUTTON_STATE_OFF)

    def __update_prev_cue_button_led(self):
        if self.song().can_jump_to_prev_cue:
            self.send_button_led(SID_TRANSPORT_MARKER, BUTTON_STATE_ON)
        else:
            self.send_button_led(SID_TRANSPORT_MARKER, BUTTON_STATE_OFF)

    def __update_next_cue_button_led(self):
        if self.song().can_jump_to_next_cue:
            self.send_button_led(SID_TRANSPORT_NUDGE, BUTTON_STATE_ON)
        else:
            self.send_button_led(SID_TRANSPORT_NUDGE, BUTTON_STATE_OFF)

    def __update_loop_button_led(self):
        if self.song().loop:
            self.send_button_led(SID_TRANSPORT_CYCLE, BUTTON_STATE_ON)
        else:
            self.send_button_led(SID_TRANSPORT_CYCLE, BUTTON_STATE_OFF)

    def __update_punch_in_button_led(self):
        if self.song().punch_in:
            self.send_button_led(SID_TRANSPORT_DROP, BUTTON_STATE_ON)
        else:
            self.send_button_led(SID_TRANSPORT_DROP, BUTTON_STATE_OFF)

    def __update_punch_out_button_led(self):
        if self.song().punch_out:
            self.send_button_led(SID_TRANSPORT_REPLACE, BUTTON_STATE_ON)
        else:
            self.send_button_led(SID_TRANSPORT_REPLACE, BUTTON_STATE_OFF)

    def __assign_mutable_buttons(self):
        if self.main_script().get_debug_parameter_1():
            self.__scrub_button = SID_TRANSPORT_SOLO
        else:
            self.__scrub_button = SID_JOG_SCRUB

    # --- Main update for LED state ---
    def __update_metronome_button_led(self):
        if not self.song().metronome:
            # Clear LED and stop listeners
            self.send_button_led(SID_TRANSPORT_CLICK, BUTTON_STATE_OFF)
            self._last_beat = None
            self._metronome_flash_ticks = 0
            self._offline_last_toggle = None
            self.__remove_metronome_beat_listener()
            return

        if not self.main_script().get_metronome_blinks_in_time():
            # Use X-Touch built-in blink
            self.send_button_led(SID_TRANSPORT_CLICK, BUTTON_STATE_BLINKING)
            self._last_beat = None
            self._metronome_flash_ticks = 0
            self._offline_last_toggle = None
            self.__remove_metronome_beat_listener()
            return

        # Drive LED ourselves
        self.__add_metronome_beat_listener()

        if self.song().is_playing:
            self.__on_song_time_changed()
        else:
            # Initialize offline blink state
            if not hasattr(self, "_offline_led_state"):
                self._offline_led_state = False
            if not hasattr(self, "_offline_last_toggle"):
                self._offline_last_toggle = time.time()

    # --- Listener management ---
    def __add_metronome_beat_listener(self):
        if not self.song().current_song_time_has_listener(self.__on_song_time_changed):
            self.song().add_current_song_time_listener(self.__on_song_time_changed)

    def __remove_metronome_beat_listener(self):
        if self.song().current_song_time_has_listener(self.__on_song_time_changed):
            self.song().remove_current_song_time_listener(self.__on_song_time_changed)

    # --- Playing mode: beat-synced flashing ---
    def __on_song_time_changed(self):
        if not self.song().metronome or not self.song().is_playing:
            return

        pos = self.song().get_current_beats_song_time()
        beats = pos.beats        # 1-based beat in bar
        ticks = pos.ticks

        # Detect new beat
        if beats != getattr(self, "_last_beat", None):
            self._last_beat = beats
            ppq = 120  # adjust for flash duration
            flash_length = ppq // 2 if beats == 1 else ppq // 16
            self.send_button_led(SID_TRANSPORT_CLICK, BUTTON_STATE_ON)
            self._metronome_flash_ticks = ticks + flash_length

        # Turn off LED after flash interval
        if getattr(self, "_metronome_flash_ticks", 0) and ticks >= self._metronome_flash_ticks:
            self.send_button_led(SID_TRANSPORT_CLICK, BUTTON_STATE_OFF)
            self._metronome_flash_ticks = 0

    # --- Offline blinking when song stopped ---
    def __offline_metronome_tick(self):
        if not self.song().metronome or self.song().is_playing or not self.main_script().get_metronome_blinks_in_time():
            return

        now = time.time()
        # initialize if first call
        last_toggle = getattr(self, "_offline_last_toggle", None)
        if last_toggle is None:
            self._offline_last_toggle = now
            last_toggle = now

        beat_interval = 60.0 / self.song().tempo  # seconds per beat

        if now - last_toggle >= beat_interval:
            self._offline_last_toggle = now
            self._offline_led_state = not getattr(self, "_offline_led_state", False)
            self.send_button_led(
                SID_TRANSPORT_CLICK,
                BUTTON_STATE_ON if self._offline_led_state else BUTTON_STATE_OFF
            )

    """ Settings menu system """    

    def _next_menu_item(self):
        self._rebuild_menu_items()
        if not self._menu_items:
            return
        self._menu_index = (self._menu_index + 1) % len(self._menu_items)
        self._show_current_menu_item()

    def _previous_menu_item(self):
        self._rebuild_menu_items()
        if not self._menu_items:
            return
        self._menu_index = (self._menu_index - 1) % len(self._menu_items)
        self._show_current_menu_item()

    def _show_current_menu_item(self):
        self._rebuild_menu_items()
        if not self._menu_items:
            return  # nothing to show

        if self._menu_index >= len(self._menu_items):
            self._menu_index = 0

        key, spec = self._menu_items[self._menu_index]
        default, parser, desc, formatter, short_name, *rest = spec
        value = getattr(self.main_script(), key.lower())

        label = None
        if rest:
            choices_or_limits = rest[0]
            if isinstance(choices_or_limits, dict):
                label = choices_or_limits.get(value, str(value))

        display_val = label if label else formatter(value)
        msg = f"{short_name[:5]}.{display_val:>5}"
        self.main_script().time_display().show_permanent_message(msg)


    def _reset_current_preference_to_default(self):
        self._rebuild_menu_items()
        if not self._menu_items:
            return

        if self._menu_index >= len(self._menu_items):
            self._menu_index = 0

        key, spec = self._menu_items[self._menu_index]
        default, parser, desc, formatter, short_name, *rest = spec

        setattr(self.main_script(), key.lower(), default)
        self.main_script().refresh_state()
        self._rebuild_menu_items()


    def _toggle_current_preference(self, forward=True):
        self._rebuild_menu_items()
        if not self._menu_items:
            return

        if self._menu_index >= len(self._menu_items):
            self._menu_index = 0

        key, spec = self._menu_items[self._menu_index]
        default, parser, desc, formatter, short_name, *rest = spec
        value = getattr(self.main_script(), key.lower())

        # Unpack optional fields safely
        choices_or_limits = rest[0] if len(rest) >= 1 else None
        visibility_func    = rest[1] if len(rest) >= 2 else None
        step_size          = rest[2] if len(rest) >= 3 else 0.01

        # Skip invisible items
        if visibility_func and not visibility_func(self.main_script()):
            return

        # Toggle/update value
        if isinstance(choices_or_limits, dict):
            keys = list(choices_or_limits.keys())
            idx = keys.index(value) if value in keys else 0
            idx = (idx + (1 if forward else -1)) % len(keys)
            new_value = keys[idx]

        elif isinstance(default, bool):
            new_value = not value

        elif isinstance(default, int):
            new_value = value + (1 if forward else -1)

        elif isinstance(default, float):
            new_value = round(value + (step_size if forward else -step_size), 3)

        else:
            new_value = value

        # Apply numeric limits
        if isinstance(choices_or_limits, tuple) and len(choices_or_limits) == 2:
            min_val, max_val = choices_or_limits
            if isinstance(new_value, (int, float)):
                new_value = max(min_val, min(new_value, max_val))

        # Store and refresh
        setattr(self.main_script(), key.lower(), new_value)
        self.main_script().save_preferences()
        self.main_script().refresh_state()
        self._rebuild_menu_items()

    def save_preferences_and_exit(self):
        self.main_script().save_preferences()
        self._in_settings_menu = False  # exit menu
        return True

    def _rebuild_menu_items(self):
        """Rebuilds the list of menu items depending on active preferences."""
        self._menu_items = []
        for key, spec in self.main_script()._preferences_spec.items():
            *base, last = spec
            visible_if = last if callable(last) else None
            if visible_if and not visible_if(self.main_script()):
                continue
            self._menu_items.append((key, spec))

        if self._menu_index >= len(self._menu_items):
            self._menu_index = 0
