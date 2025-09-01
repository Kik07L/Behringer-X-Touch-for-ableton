# X-Touch Custom Script for Ableton Live 12

This repository contains a modified version of the MackieControl script, adapted specifically for Behringer X-Touch controllers. Originally developed by Arthur Montvidas and further enhanced by Robrecht & posted on github with the contribution of Kik07L, this version adds support for Ableton Live 12 with numerous improvements, including Extender functionality and colored scribble strips.

# We highly recommend downloading the Release version [here](https://github.com/Kik07L/Behringer-X-Touch-for-ableton/releases). The source code here may include untested or beta features that are potentially unstable.
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
- Some global settings (Night Mode, show clock...) are now preserved across sessions.
- Settings are saved in options.txt.

### Optional features
- Select track by touching fader (off by default, can be enabled by editing options.txt).
- Indicate track muted via solo by flashing `MUTE` button LED (off by default, can be enabled by editing options.txt).

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

### **Transport Section**
- `CLICK`: Toggle metronome. LED blinks when active.
  - `CONTROL + CLICK`: Tap tempo.
- `SCRUB`: Play selected clip in Session view.
- `MARKER`: Jump to the previous marker.
  - `CONTROL + MARKER`: Create or delete a marker at the current position.
- `NUDGE`: Jump to the next marker.
- `CYCLE`: Toggle loop.
- `DROP`: Toggle punch in.
- `REPLACE`: Toggle punch out.
- `SOLO`: Lights up when one or more tracks are soloed. Press to toggle all solo states on and off at once (Global Solo function). LED behavior:
  - ON: Tracks soloed, press to unsolo all at once.
  - Blinking: Previously soloed tracks stored, press to restore.
  - OFF: No tracks soloed, press to solo current track.
  - `CONTROL + SOLO`: Toggle solo states in time with song (delayed according to global launch quantization as set in Live).
  - `SHIFT + SOLO`: Reset.

### **Utility Section**
- `SAVE`: Capture MIDI. LED lights up when active.
- `UNDO`: Undo last action.
- `ENTER`: Redo last action.
- `CANCEL`: Return to Arrangement view. LED lights up when enabled.

### **Automation Section**
- `READ/OFF`: Re-enable automation.
- `WRITE`: Arm for automation recording.
- `TOUCH`: Toggle Draw mode.
- `LATCH`: Toggle Follow mode.
- `TRIM`: Toggle MIDI arrangement overdub.
- `GROUP`: Expand/collapse selected track (if it is a group or contains chains). LED behavior:
  - ON: Current track is a group or contains chains.
  - Blinking: Current track is within a group or is a chain within a track.

### **Jog Wheel**
- `SHIFT + Rotation`: Faster movement.
- `ALT + Rotation`: Slower movement.
- `OPTION + Rotation`: Move loop region (faster with `SHIFT`).
- `OPTION + ALT + Rotation`: Move loop end bracket (faster with `SHIFT`).
- `CONTROL + Rotation`: Change tempo.
- `ZOOM BUTTON + Rotation`: Zoom in/out in Arrangement view.

### **Function Section**
- `SHIFT + F1-F8`: Enable/disable Record Quantization selection. Leave disabled to allow Function buttons to be MIDI mapped. Setting is remembered across sessions.
- `F1-F8`: Select Record Quantization. Press lit button again for no quantization.

### **Gray Section**
- `GLOBAL VIEW`: Switch between Session and Arrangement views.
- `MIDI TRACKS`: Create a new MIDI track.
- `INPUTS`: Open/close the browser.
- `AUDIO TRACKS`: Create a new audio track.
- `AUDIO INST`: Open/close the details view.
- `AUX`: Toggle between clip and device views. LED is on in clip view.
- `BUSES`: Create a new return track.
- `OUTPUTS`: Select the Master Track. Press again to show Master device chain.
- `USER`: Press and hold to show Macro Mapper.
  - `SHIFT + USER`: Lock Macro Mapper.
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
