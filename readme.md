# X-Touch Custom Script for Ableton Live 12

This repository contains a modified version of the MackieControl script, adapted specifically for Behringer X-Touch controllers. Originally developed by Arthur Montvidas and further enhanced by Robrecht & posted on github with the contribution of Kik07L, this version adds support for Ableton Live 12 with numerous improvements, including Extender functionality and colored scribble strips.

# We highly recommend downloading the Release version [here](https://github.com/Kik07L/Behringer-X-Touch-for-ableton/releases). The source code [here](https://github.com/Kik07L/Behringer-X-Touch-for-ableton/archive/refs/heads/main.zip) may include untested or beta features that are potentially unstable.
For a stable experience, please use the latest Release. 😄  

---

link of the Ableton forum page to disscuss and get updated about what's happening : https://forum.ableton.com/viewtopic.php?p=1831258#p1831258

## Features

### Colored Scribble Strips
- **Track Color Matching:** Scribble strip colors follow the track colors set in Ableton Live.
  - Hardware limited to 8 basic colors: black, red, yellow, green, blue, magenta, cyan, and white.
  - Automatically calculates the closest match.
- **Black Color Handling:** Black scribble strips are only used if explicitly selected in Live to prevent unreadable text.
- **Grayscale Handling:** All grayscale colors (except black) default to white scribble strips.
- **Inactive Channels:** Tracks beyond your active channels are marked with black scribble strips to indicate inactivity.
- **Plug-In Mode:**
  - Scribble strips are lit in a single color (Cyan) for better readability.
- **Alternative color matching method (beta):**
  - Attempts to improve color matching by prioritizing hue, to avoid light colors automatically mapping to white.
  - `SHIFT + DISPLAY`: Toggle between default (RGB distance-based) and alternative (hue-based) method. Setting is preserved across sessions.
  - `SHIFT + UP/DOWN`: Tune white cut-off for hue-based matching (higher = more colors map to white scribble strip).

### Level Meter Enhancements
- **Clipping Indicators:** Channel strip level meters now show clipping when it occurs.
- **Snappy Meters:** Channel strip level meters now react more quickly to changes in audio.

### Global Solo
- When one or more tracks are soloed, `SOLO` button in Transport Section toggles their solo state on and off simultaneously.

### Macro Mapper (beta)
- Quick access to 16 multi-mappable macros via the rotary encoders.
- Place the supplied "XTouch/Macro Mapper/X-Touch Macro Mapper" device on the Master track as the first (leftmost) device in the chain.
- Map the Max4Live devices in the rack to any function in the project and rename the 16 macro knobs to suit.
- Press and hold `USER` to bring up mappings on rotary encoders temporarily, or `SHIFT + USER` to lock.
  - Quick access through the `USER` button will work with any device that is first in the chain on the Master channel and has "X-Touch" in its name.

### Single Send Mode (beta)
- Default Sends mode (`SEND`) shows send levels for all return tracks/return chains on the current track/chain.
- New Single Send mode shows send levels for a single return track/return chain across all tracks/chains.
- In default Sends mode, either press `SEND` again or `SHIFT + Press rotary encoder` to select the corresponding return track for Single Send mode.
- Press `EQ` or `INST` to move control to the previous/next return track/return chain send levels.
- Scribble strips will turn black for unavailable sends (if the number of global return tracks differs from the number of return chains in a device with chains visible in the mixer).

### Device Control Lock (beta)
- With the rotary encoders assigned to device parameters (`PLUG-IN` > `Press rotary encoder` to select device), press `SHIFT + PLUG-IN` to lock current assignment.
- Device assignment will no longer be canceled by selecting, soloing, muting or arming other tracks.

### Night Mode (beta)
- Press all four `MODIFY` buttons (`SHIFT`, `OPTION`, `CONTROL` and `ALT`) simultaneously to toggle Night Mode.
- `MODIFY` section LEDs are permanently lit for enhanced visibility.
- Press any `MODIFY` button to temporarily light up all buttons.
- Night Mode setting is remembered across sessions.

### Chains behave as groups (beta)
- Press `SELECT` twice on a track that contains a Rack to expand its chains in the Mixer (same behaviour as with track groups).
- Rack chains react just like normal tracks to faders, `MUTE` and `SOLO` buttons and encoders (in Pan and Sends mode).
- Chain colors appear in scribble strips and can be modified just like track colors (press `TRACK` x5 for color mode).
- Note: if volume or panning for a device chain is macro mapped, the fader/rotary encoder for that chain will have no effect.
- Limitations: chains audio metering and audio routing are currently unavailable in Live's API.

### Feedback messages (beta)
- Short messages on Time Display provide feedback on various actions.

### Persistent settings (beta)
- Global settings (Night Mode, show clock...) are now preserved across sessions.
- Settings can be edited through built-in global settings menu and are saved in options.txt.

### Global settings menu (beta)
- `SHIFT + ZOOM`: Open settings menu.
- `UP`, `DOWN`: Browse settings.
- `LEFT`, `RIGHT`: Change setting.
- `JOG WHEEL`: Change setting.
- `SCRUB`: Reset setting to default.
- `ZOOM`: Save and exit.

### Function Section modes (beta)
- Available modes: MIDI Record Quantization, current track Input Type, current track Input Channel.
- See Button Mappings for more details.

### Metronome button blinks in time (beta)
- Metronome button (`CLICK`) blinks in time while song is playing (on by default, can be disabled through settings menu)

### Other optional features
- Select track by touching fader (off by default, can be enabled through settings menu).
- Indicate track muted via solo by flashing `MUTE` button LED (off by default, can be enabled through settings menu).
- When faders are flipped, master fader controls Cue volume (off by default, can be enabled through settings menu).

## Button Mappings
### **Encoder Assign Section**
- `TRACK`: Assign encoders to track properties (cycles through Input Type, Input Channel, Output Type, Output Channel, Track Color).
- `PAN/SURROUND`: Assign encoders to track panning.
- `EQ`: Bank left in device control or Single Send mode.
- `SEND`: Assign encoders to track send levels.
  - `SEND`: press again for Single Send mode.
  - Alternatively, `SHIFT + Press rotary encoder`: Single Send mode for selected return track.
- `PLUG-IN`: Assign encoders to track devices.
  - `Press rotary encoder` to select device.
  - `SHIFT + PLUG-IN`: lock current device assigment.
- `INST`: Bank right in device control or Single Send mode.

### **Display Section**
- `DISPLAY`: Switch between audio/instrument and return tracks.
- `SHIFT + SMPTE/BEATS`: Show clock instead of song time/beats. Press again to show clock without seconds.

### **Channel Strip**
- `REC`: Arm track for recording.
  - If "Exclusive" is enabled for arming in Live settings, all other tracks will be de-armed.
  - `CONTROL + REC`: Inverts the exclusive/non-exclusive setting for arming.
- `SHIFT + REC`: Toggle monitoring state (exclusive: **In/Auto**). REC LED blinks when in **In** mode.
  - `SHIFT + CONTROL + REC`: Toggle monitoring state (non-exclusive).
- `SOLO`: Solo track.
  - If "Exclusive" is enabled for soloing in Live settings, all other tracks will be unsoloed.
  - `CONTROL + SOLO`: Inverts the exclusive/non-exclusive setting for soloing.
  - `SHIFT + SOLO`: Adds/removes track to/from previously soloed tracks (track `SOLO` LEDs blinking, see `SOLO` button in Transport Section).
- `MUTE`: Mute track.
- `SELECT`: Select track. Press again to fold/unfold.
  - Parent track of a selected grouped track or chain will blink to indicate where group/chain starts.

### **Gray Section**
- `FLIP`: Swap faders and rotary encoders.
- `GLOBAL VIEW`: Select the Master Track.
  - Enable Flip Reverse in the global settings menu to swap `FLIP` and `GLOBAL VIEW`, so `FLIP` selects the Master Track (consistent with channel strip `SELECT` buttons) and `GLOBAL VIEW` swaps faders and encoders.
- `MIDI TRACKS`: Switch between Session and Arrangement views.
  - `CONTROL + MIDI TRACKS`: Store current view (Session/Arrangement, browser, clip/devices).
  - `SHIFT + MIDI TRACKS`: Recall stored view (Session/Arrangement, browser, clip/devices).
- `INPUTS`: Toggle between clip and device views. LED is on in clip view.
- `AUDIO TRACKS`: Open/close the details view.
- `AUDIO INST`: Open/close the browser.
- `AUX`: Create a new MIDI track.
- `BUSES`: Create a new audio track.
- `OUTPUTS`: Create a new return track.
- `USER`: Press and hold to show Macro Mapper.
  - `SHIFT + USER`: Lock Macro Mapper.

### **Function Section**
- `SHIFT + F1-F8`: Select Function Section mode.
  - `F1`: Disabled (allow `F1-F8` to be MIDI mapped).  
  - `F2`: MIDI Record Quantization (`F1-F8`, press twice for no quantization).
  - `F3`: Current track Input Type (`F1-F8`, press twice for All Ins on MIDI track).
  - `F4`: Current track Input Channel (`F1-F8`, `ALT + F1-F8` for Channels 9-16, press twice for All Channels on MIDI track).
- `OPTION + F1-F8`: Quick select current track Input Type.
- `CONTROL/ALT + F1-F8`: Quick select current track Input Channel (`CONTROL` for Channels 1-8, `ALT` for Channels 9-16).

### **Master Channel Strip**
- `FLIP`: Swap faders and rotary encoders.
  - If enabled in the global settings menu, `Master Fader` controls Cue/Preview volume in flipped state.
- `SHIFT + FLIP`: Select the Master Track. Press again to show Master device chain.

### **Automation Section**
- `READ/OFF`: Re-enable automation.
- `WRITE`: Arm for automation recording.
- `TOUCH`: Toggle Draw mode.
- `LATCH`: Toggle Follow mode.
- `TRIM`: Toggle MIDI arrangement overdub.
- `GROUP`: Expand/collapse selected track (if it is a group or contains chains). LED behavior:
  - ON: Current track is a group or contains chains.
  - Blinking: Current track is within a group or is a chain within a track.

### **Utility Section**
- `SAVE`: Capture MIDI. LED lights up when active.
- `UNDO`: Undo last action.
- `ENTER`: Redo last action.
- `CANCEL`: Return to Arrangement view. LED lights up when enabled.

### **Transport Section**
- `CLICK`: Toggle metronome. LED blinks when active.
  - `CONTROL + CLICK`: Tap tempo.
- `SCRUB`: Play selected clip in Session view.
- `MARKER`: Jump to the previous marker.
  - `CONTROL + MARKER`: Create or delete a marker at the current position.
- `NUDGE`: Jump to the next marker.
- `CYCLE`: Toggle loop.
- `DROP`: Toggle punch in.
  - `CONTROL + DROP`: Set loop start at current song time.
- `REPLACE`: Toggle punch out.
  - `CONTROL + REPLACE`: Set loop end at current song time.
- `SOLO`: Lights up when one or more tracks are soloed. Press to toggle all solo states on and off at once (Global Solo function). LED behavior:
  - ON: Tracks soloed, press to unsolo all at once.
  - Blinking: Previously soloed tracks stored, press to restore.
  - OFF: No tracks soloed, press to solo current track.
  - `CONTROL + SOLO`: Toggle solo states in time with song (delayed according to global launch quantization as set in Live).
  - `SHIFT + SOLO`: Reset.

### **Jog Wheel and Navigation Buttons**
- `Rotation`, `UP`, `DOWN`, `LEFT`, `RIGHT`: Move playhead/clip slot selection.
- `SHIFT + Rotation`: Faster movement.
- `ALT + Rotation`: Slower movement.
- `ALT + LEFT`, `ALT + RIGHT`: Select time region.
- `OPTION + Rotation`: Move loop region (faster with `SHIFT`).
- `OPTION + ALT + Rotation`: Move loop end bracket (faster with `SHIFT`).
- `CONTROL + Rotation`: Change tempo.
- `ZOOM BUTTON`: Activate zoom (in Arrangement view).
  - `Rotation`, `LEFT` or `RIGHT`: Zoom in/out.
  - `UP`, `DOWN`: Adjust current track height.
  - `ALT + UP`, `ALT + DOWN`: Adjust all tracks height.
- `ZOOM BUTTON`: Fire selected clip (in Session view).
  - `OPTION + ZOOM BUTTON`: Stop selected clip (in Session view).
  - `ALT + ZOOM BUTTON`: Toggle stop button for selected clip slot (in Session view).
- `SCRUB`: Fire selected scene (in Session view).
  - `OPTION + SCRUB`: Stop all clips (in Session view).

---

## Installation
1. Unzip the downloaded files.
2. Copy the `XTouch` and `XTouchXT` folders to the Remote Scripts folder in your User Library.

- **Windows:** Documents\Ableton\User Library\Remote Scripts
- **Mac:** Music/Ableton/User Library/Remote Scripts

For more info, see the [Ableton Live help page](https://help.ableton.com/hc/en-us/articles/209072009-Installing-third-party-remote-scripts?pk_vid=00fb25b3f17d28b5174887569027d6e6).

---

## Compatibility
- Tested with Ableton Live 12.

---

Feel free to contribute or report any issues! 😊
