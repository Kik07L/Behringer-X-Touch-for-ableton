# X-Touch Custom Script for Ableton Live 12

This repository contains a modified version of the MackieControl script, adapted specifically for Behringer X-Touch controllers. Originally developed by Arthur Montvidas and further enhanced by Robrecht & posted on github with the contribution of Kik07L, this version adds support for Ableton Live 12 with numerous improvements, including Extender functionality and colored scribble strips.

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
- **Send/Plug-In Modes:**
  - Scribble strips are lit in a single color for better readability:
    - Yellow: Send mode.
    - Cyan: Plug-in mode.

### Level Meter Enhancements
- **Clipping Indicators:** Channel strip level meters now show clipping when it occurs.
- **Snappy Meters:** Channel strip level meters now react more quickly to changes in audio.

### Button Remapping
#### **Encoder Assign Section**
- `TRACK`: Assign encoders to track properties (cycles through Input Type, Input Channel, Output Type, Output Channel, Track Color)
- `PAN/SURROUND`: Assign encoders to track panning
- `EQ`: Bank left in device control mode
- `SEND`: Assign encoders to track send levels
- `PLUG-IN`: Assign encoders to track devices
- `INST`: Bank right in device control mode

#### **Display Section**
- `DISPLAY`: Switch between Session and Arrangement views.
- `SHIFT + SMPTE/BEATS`: Show current time instead of song time/beats.
- `OPTION + SMPTE/BEATS`: In current time mode, toggle seconds on/off.

#### **Channel Strip**
- `SHIFT + ARM`: Toggle monitoring state (exclusive: **In/Auto**). ARM LED blinks when in **In** mode.
- `SHIFT + CONTROL + ARM`: Toggle monitoring state (non-exclusive).

#### **Transport Section**
- `CLICK`: Toggle metronome. LED blinks when active.
  - `CONTROL + CLICK`: Tap tempo.
- `SCRUB`: Play selected clip in Session view.
- `MARKER`: Jump to the previous marker.
  - `CONTROL + MARKER`: Create or delete a marker at the current position.
- `NUDGE`: Jump to the next marker.
- `CYCLE`: Toggle loop.
- `DROP`: Toggle punch in.
- `REPLACE`: Toggle punch out.
- `SOLO`: Toggle between clip and device views. LED is on in clip view.

#### **Utility Section**
- `SAVE`: Capture MIDI.
- `UNDO`: Undo last action.
- `ENTER`: Redo last action.
- `CANCEL`: Return to Arrangement view. LED lights up when enabled.

#### **Automation Section**
- `READ/OFF`: Re-enable automation.
- `WRITE`: Arm for automation recording.
- `TOUCH`: Toggle Draw mode.
- `LATCH`: Toggle Follow mode.
- `TRIM`: Capture MIDI. LED lights up when active.
- `GROUP`: Expand/collapse selected track (if it is a group). LED behavior:
  - ON: Current track is a group.
  - Blinking: Current track is within a group.

#### **Jog Wheel**
- `SHIFT + Rotation`: Faster movement.
- `ALT + Rotation`: Slower movement.
- `OPTION + Rotation`: Move loop region (faster with SHIFT).
- `OPTION + ALT + Rotation`: Move loop end bracket (faster with SHIFT).
- `CONTROL + Rotation`: Change tempo.
- `ZOOM BUTTON + Rotation`: Zoom in/out in Arrangement view.

#### **Gray Section**
- `GLOBAL VIEW`: Switches between audio/instrument and return tracks
- `MIDI TRACKS`: Create a new MIDI track.
- `INPUTS`: Open/close the browser.
- `AUDIO TRACKS`: Create a new audio track.
- `AUDIO INST`: Open/close the details view.

---

## Installation
1. Unzip the downloaded files.
2. Copy the `XTouch` and `XTouchXT` folders to: "Documents\Ableton\User Library\Remote Scripts"

---

## Compatibility
- Tested with Ableton Live 12.

---

Feel free to contribute or report any issues! 😊
