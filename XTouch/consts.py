#Embedded file name: /Users/versonator/Jenkins/live/output/Live/mac_64_static/Release/python-bundle/MIDI Remote Scripts/MackieControl/consts.py
from __future__ import absolute_import, print_function, unicode_literals
from builtins import range
from collections import namedtuple
import colorsys

NOTE_OFF_STATUS = 128
NOTE_ON_STATUS = 144
CC_STATUS = 176
PB_STATUS = 224
SYSEX_DEVICE_TYPE = 20
SYSEX_DEVICE_TYPE_XT = 21
NUM_CHANNEL_STRIPS = 8
MASTER_CHANNEL_STRIP_INDEX = 8
BUTTON_STATE_OFF = 0
BUTTON_STATE_ON = 127
BUTTON_STATE_BLINKING = 1
BUTTON_STATES = [0] * 200
BUTTON_PRESSED = 1
BUTTON_RELEASED = 0
NUM_CHARS_PER_DISPLAY_LINE = 54
SELECT_SMPTE_NOTE = 113
SELECT_BEATS_NOTE = 114
SELECT_RUDE_SOLO = 115
FID_PANNING_BASE = 16
JOG_WHEEL_CC_NO = 60
VPOT_DISPLAY_SINGLE_DOT = 0
VPOT_DISPLAY_BOOST_CUT = 1
VPOT_DISPLAY_WRAP = 2
VPOT_DISPLAY_SPREAD = 3
CSM_VOLPAN = 0
CSM_PLUGINS = 1
CSM_IO = 2
CSM_SENDS = 3
CSM_SENDS_SINGLE = 4
CSM_IO_MODE_INPUT_MAIN = 0
CSM_IO_MODE_INPUT_SUB = 1
CSM_IO_MODE_OUTPUT_MAIN = 2
CSM_IO_MODE_OUTPUT_SUB = 3
CSM_IO_MODE_TRACK_COLOR = 4
CSM_IO_FIRST_MODE = CSM_IO_MODE_INPUT_MAIN
CSM_IO_LAST_MODE = CSM_IO_MODE_TRACK_COLOR 
COLORLIST = ["Salmon", "Frank Orange", "Dirty Gold", "Lemonade", "Lime", "Highlighter Green", "Bianchi", "Turquoise", "Sky Blue", "Sapphire 1", "Periwinkle 1", "Orchid", "Magenta", "White", "Fire Hydrant Red", "Tangerine", "Sand", "Sunshine Yellow", "Terminal Green", "Forest", "Tiffany Blue", "Cyan", "Cerulean", "United Nations Blue", "Amethyst", "Iris", "Flamingo", "Aluminum", "Terracotta", "Light Salmon", "Whiskey", "Canary", "Primrose", "Wild Willow", "Dark Sea Green", "Honeydew", "Pale Turquoise", "Periwinkle 2", "Fog", "Dull Lavender", "Whisper", "Silver Chalice", "Dusty Pink", "Barley Corn", "Pale Oyster", "Dark Khaki", "Pistachio", "Dollar Bill", "Neptune", "Nepal", "Polo Blue", "Vista Blue", "Amethyst Smoke", "Lilac", "Turkish Rose", "Steel", "Medium Carmine", "Red Ochre", "Coffee", "Durian Yellow", "Pomelo Green", "Apple", "Aquamarine", "Sea Blue", "Cosmic Cobalt", "Sapphire 2", "Plump Purple", "Purpureus", "Fuchsia Rose", "Eclipse"] 
PCM_DEVICES = 0
PCM_PARAMETERS = 1
PCM_NUMMODES = 2
CLIP_STATE_INVALID = -1
CLIP_STOPPED = 0
CLIP_TRIGGERED = 1
CLIP_PLAYING = 2
scribble_black = (0, 0, 0)
scribble_red = (255, 0, 0)
scribble_green = (0, 255, 0)
scribble_yellow = (255, 255, 0)
scribble_blue = (0, 0, 255)
scribble_magenta = (255, 0, 255)
scribble_cyan = (0, 255, 255)
scribble_white = (255, 255, 255)
g7_seg_led_conv_table = {u' ': 0,
 u'A': 1,
 u'B': 2,
 u'C': 3,
 u'D': 4,
 u'E': 5,
 u'F': 6,
 u'G': 7,
 u'H': 8,
 u'I': 9,
 u'J': 10,
 u'K': 11,
 u'L': 12,
 u'M': 13,
 u'N': 14,
 u'O': 15,
 u'P': 16,
 u'Q': 17,
 u'R': 18,
 u'S': 19,
 u'T': 20,
 u'U': 21,
 u'V': 22,
 u'W': 23,
 u'X': 24,
 u'Y': 25,
 u'Z': 26,
 u'\\': 34,
 u'#': 35,
 u'$': 36,
 u'%': 37,
 u'&': 38,
 u"'": 39,
 u'(': 40,
 u')': 41,
 u'*': 42,
 u'+': 43,
 u',': 44,
 u'0': 48,
 u'1': 49,
 u'2': 50,
 u'3': 51,
 u'4': 52,
 u'5': 53,
 u'6': 54,
 u'7': 55,
 u'8': 56,
 u'9': 57,
 u';': 59,
 u'<': 60}
SID_FIRST = 0
SID_RECORD_ARM_BASE = 0
SID_RECORD_ARM_CH1 = 0
SID_RECORD_ARM_CH2 = 1
SID_RECORD_ARM_CH3 = 2
SID_RECORD_ARM_CH4 = 3
SID_RECORD_ARM_CH5 = 4
SID_RECORD_ARM_CH6 = 5
SID_RECORD_ARM_CH7 = 6
SID_RECORD_ARM_CH8 = 7
SID_SOLO_BASE = 8
SID_SOLO_CH1 = 8
SID_SOLO_CH2 = 9
SID_SOLO_CH3 = 10
SID_SOLO_CH4 = 11
SID_SOLO_CH5 = 12
SID_SOLO_CH6 = 13
SID_SOLO_CH7 = 14
SID_SOLO_CH8 = 15
SID_MUTE_BASE = 16
SID_MUTE_CH1 = 16
SID_MUTE_CH2 = 17
SID_MUTE_CH3 = 18
SID_MUTE_CH4 = 19
SID_MUTE_CH5 = 20
SID_MUTE_CH6 = 21
SID_MUTE_CH7 = 22
SID_MUTE_CH8 = 23
SID_SELECT_BASE = 24
SID_SELECT_CH1 = 24
SID_SELECT_CH2 = 25
SID_SELECT_CH3 = 26
SID_SELECT_CH4 = 27
SID_SELECT_CH5 = 28
SID_SELECT_CH6 = 29
SID_SELECT_CH7 = 30
SID_SELECT_CH8 = 31
SID_VPOD_PUSH_BASE = 32
SID_VPOD_PUSH_CH1 = 32
SID_VPOD_PUSH_CH2 = 33
SID_VPOD_PUSH_CH3 = 34
SID_VPOD_PUSH_CH4 = 35
SID_VPOD_PUSH_CH5 = 36
SID_VPOD_PUSH_CH6 = 37
SID_VPOD_PUSH_CH7 = 38
SID_VPOD_PUSH_CH8 = 39
channel_strip_switch_ids = list(range(SID_RECORD_ARM_BASE, SID_VPOD_PUSH_CH8 + 1))

"""
switch_id names reflect button labels on the X-Touch, regardless of function in the script
"""

SID_ASSIGNMENT_TRACK = 40
SID_ASSIGNMENT_SEND = 41
SID_ASSIGNMENT_PAN = 42
SID_ASSIGNMENT_PLUG_IN = 43
SID_ASSIGNMENT_EQ = 44
SID_ASSIGNMENT_INST = 45
SID_FADERBANK_PREV_BANK = 46
SID_FADERBANK_NEXT_BANK = 47
SID_FADERBANK_PREV_CH = 48
SID_FADERBANK_NEXT_CH = 49
SID_FADERBANK_FLIP = 50
SID_GLOBAL_VIEW = 51
SID_FADERBANK_NAME_VALUE = 52
SID_DISPLAY_SMPTE_BEATS = 53
SID_SOFTWARE_F1 = 54
SID_SOFTWARE_F2 = 55
SID_SOFTWARE_F3 = 56
SID_SOFTWARE_F4 = 57
SID_SOFTWARE_F5 = 58
SID_SOFTWARE_F6 = 59
SID_SOFTWARE_F7 = 60
SID_SOFTWARE_F8 = 61
SID_SOFTWARE_MIDI_TRACKS = 62
SID_SOFTWARE_INPUTS = 63
SID_SOFTWARE_AUDIO_TRACKS = 64
SID_SOFTWARE_AUDIO_INST = 65
SID_SOFTWARE_AUX = 66
SID_SOFTWARE_BUSES = 67
SID_SOFTWARE_OUTPUTS = 68
SID_SOFTWARE_USER = 69
SID_MOD_SHIFT = 70
SID_MOD_OPTION = 71
SID_MOD_CTRL = 72
SID_MOD_ALT = 73
SID_AUTOMATION_READ_OFF = 74
SID_AUTOMATION_WRITE = 75
SID_AUTOMATION_TRIM = 76
SID_AUTOMATION_TOUCH = 77
SID_AUTOMATION_LATCH = 78
SID_AUTOMATION_GROUP = 79
SID_FUNC_SAVE = 80
SID_FUNC_UNDO = 81
SID_FUNC_CANCEL = 82 
SID_FUNC_ENTER = 83
SID_TRANSPORT_MARKER = 84
SID_TRANSPORT_NUDGE = 85
SID_TRANSPORT_CYCLE = 86
SID_TRANSPORT_DROP = 87
SID_TRANSPORT_REPLACE = 88
SID_TRANSPORT_CLICK = 89
SID_TRANSPORT_SOLO = 90
SID_TRANSPORT_REWIND = 91
SID_TRANSPORT_FAST_FORWARD = 92
SID_TRANSPORT_STOP = 93
SID_TRANSPORT_PLAY = 94
SID_TRANSPORT_RECORD = 95
 
SID_JOG_CURSOR_UP = 96
SID_JOG_CURSOR_DOWN = 97
SID_JOG_CURSOR_LEFT = 98
SID_JOG_CURSOR_RIGHT = 99
SID_JOG_ZOOM = 100
SID_JOG_SCRUB = 101
jog_wheel_switch_ids = list(range(SID_JOG_CURSOR_UP, SID_JOG_SCRUB + 1))

SID_USER_FOOT_SWITCHA = 102
SID_USER_FOOT_SWITCHB = 103
SID_FADER_TOUCH_SENSE_BASE = 104
SID_FADER_TOUCH_SENSE_CH1 = 104
SID_FADER_TOUCH_SENSE_CH2 = 105
SID_FADER_TOUCH_SENSE_CH3 = 106
SID_FADER_TOUCH_SENSE_CH4 = 107
SID_FADER_TOUCH_SENSE_CH5 = 108
SID_FADER_TOUCH_SENSE_CH6 = 109
SID_FADER_TOUCH_SENSE_CH7 = 110
SID_FADER_TOUCH_SENSE_CH8 = 111
SID_FADER_TOUCH_SENSE_MASTER = 112
fader_touch_switch_ids = list(range(SID_FADER_TOUCH_SENSE_CH1, SID_FADER_TOUCH_SENSE_CH8 + 1))
SID_LAST = 112

"""
switch_id group definitions moved to end (where all switch_ids have already been defined) and turned into explicit lists (instead of ranges)
to facilitate dispatching button functions to different parts of the script
"""

# handled in ChannelStripController
channel_strip_assignment_switch_ids = (SID_ASSIGNMENT_TRACK,
 SID_ASSIGNMENT_SEND,
 SID_ASSIGNMENT_PAN,
 SID_ASSIGNMENT_PLUG_IN,
 SID_ASSIGNMENT_EQ,
 SID_ASSIGNMENT_INST)

display_switch_ids = (SID_FADERBANK_NAME_VALUE, SID_DISPLAY_SMPTE_BEATS)

# handled in ChannelStripController
channel_strip_control_switch_ids = (SID_FADERBANK_PREV_BANK,
 SID_FADERBANK_NEXT_BANK,
 SID_FADERBANK_PREV_CH,
 SID_FADERBANK_NEXT_CH,
 SID_FADERBANK_FLIP,
 SID_GLOBAL_VIEW,
 SID_FADERBANK_NAME_VALUE,
 SID_TRANSPORT_SOLO,
 SID_SOFTWARE_USER,
 SID_FUNC_CANCEL) # SID_FUNC_CANCEL also in here to allow layout switch by __assign_mutable_buttons()

# handled in SoftwareController
function_key_control_switch_ids = (SID_SOFTWARE_F1,
 SID_SOFTWARE_F2,
 SID_SOFTWARE_F3,
 SID_SOFTWARE_F4,
 SID_SOFTWARE_F5,
 SID_SOFTWARE_F6,
 SID_SOFTWARE_F7,
 SID_SOFTWARE_F8)

# handled in SoftwareController
modify_key_control_switch_ids = (SID_MOD_SHIFT,
 SID_MOD_OPTION,
 SID_MOD_CTRL,
 SID_MOD_ALT)

# handled in SoftwareController
software_controls_switch_ids = (SID_AUTOMATION_READ_OFF,
 SID_AUTOMATION_WRITE,
 SID_AUTOMATION_TOUCH,
 SID_FUNC_UNDO,
 SID_FUNC_ENTER,
 SID_AUTOMATION_TRIM,
 SID_FUNC_SAVE,
 SID_FUNC_CANCEL,
 SID_AUTOMATION_GROUP,
 SID_SOFTWARE_MIDI_TRACKS,
 SID_SOFTWARE_INPUTS,
 SID_SOFTWARE_AUDIO_TRACKS,
 SID_SOFTWARE_AUDIO_INST,
 SID_SOFTWARE_AUX,
 SID_SOFTWARE_BUSES,
 SID_SOFTWARE_OUTPUTS,
 SID_TRANSPORT_SOLO, # SID_TRANSPORT_SOLO also in here to allow layout switch by __assign_mutable_buttons()
 SID_JOG_SCRUB) # SID_JOG_SCRUB also in here to allow layout switch by __assign_mutable_buttons()

# handled in Transport
transport_control_switch_ids = (SID_TRANSPORT_CLICK,
 SID_TRANSPORT_REWIND,
 SID_TRANSPORT_FAST_FORWARD,
 SID_TRANSPORT_STOP,
 SID_TRANSPORT_PLAY,
 SID_TRANSPORT_RECORD,
 SID_AUTOMATION_LATCH)

# handled in Transport
marker_control_switch_ids = (SID_TRANSPORT_MARKER,
 SID_TRANSPORT_NUDGE,
 SID_TRANSPORT_CYCLE,
 SID_TRANSPORT_DROP,
 SID_TRANSPORT_REPLACE)

# handled in Transport
jog_wheel_switch_ids = (SID_JOG_CURSOR_UP,
 SID_JOG_CURSOR_DOWN,
 SID_JOG_CURSOR_LEFT,
 SID_JOG_CURSOR_RIGHT,
 SID_JOG_ZOOM,
 SID_JOG_SCRUB,
 SID_TRANSPORT_SOLO) # SID_TRANSPORT_SOLO also in here to allow layout switch by __assign_mutable_buttons()

"""
color definitions for the reworked color matching system
"""

# Define our structure
XTouchColor = namedtuple("XTouchColor", "name rgb hsv mix")

def rgb_to_hsv_tuple(rgb):
    """Convert (r,g,b) 0–255 to HSV (h,s,v) with floats 0–1."""
    r, g, b = [c / 255.0 for c in rgb]
    return colorsys.rgb_to_hsv(r, g, b)

# === Extended X-Touch Palette (46 entries) ===
# Basics first, then 2-way mixes, then 3-way mixes.
# In normal operation, only basics are used.

PALETTE_EXTENDED = [
    # --- Basics (indices 0–7) ---
    XTouchColor("black",   (0,0,0),       rgb_to_hsv_tuple((0,0,0)),       (0,)),
    XTouchColor("red",     (255,0,0),     rgb_to_hsv_tuple((255,0,0)),     (1,)),
    XTouchColor("green",   (0,255,0),     rgb_to_hsv_tuple((0,255,0)),     (2,)),
    XTouchColor("yellow",  (255,255,0),   rgb_to_hsv_tuple((255,255,0)),   (3,)),
    XTouchColor("blue",    (0,0,255),     rgb_to_hsv_tuple((0,0,255)),     (4,)),
    XTouchColor("magenta", (255,0,255),   rgb_to_hsv_tuple((255,0,255)),   (5,)),
    XTouchColor("cyan",    (0,255,255),   rgb_to_hsv_tuple((0,255,255)),   (6,)),
    XTouchColor("white",   (255,255,255), rgb_to_hsv_tuple((255,255,255)), (7,)),

    # --- 2-way mixes (indices 8–26) ---
    XTouchColor("dark red",         (127,0,0),     rgb_to_hsv_tuple((127,0,0)),     (0,1)),
    XTouchColor("dark green",       (0,127,0),     rgb_to_hsv_tuple((0,127,0)),     (0,2)),
    XTouchColor("dark blue",        (0,0,127),     rgb_to_hsv_tuple((0,0,127)),     (0,4)),
    XTouchColor("teal",             (0,127,127),   rgb_to_hsv_tuple((0,127,127)),   (2,4)),  # optimal
    XTouchColor("olive",            (127,127,0),   rgb_to_hsv_tuple((127,127,0)),   (1,2)),  # optimal
    XTouchColor("purple",           (127,0,127),   rgb_to_hsv_tuple((127,0,127)),   (1,4)),  # optimal
    XTouchColor("sky blue",         (0,127,255),   rgb_to_hsv_tuple((0,127,255)),   (4,6)),
    XTouchColor("spring green",     (0,255,127),   rgb_to_hsv_tuple((0,255,127)),   (2,6)),
    XTouchColor("chartreuse",       (127,255,0),   rgb_to_hsv_tuple((127,255,0)),   (2,3)),
    XTouchColor("violet",           (127,0,255),   rgb_to_hsv_tuple((127,0,255)),   (4,5)),
    XTouchColor("pink",             (255,0,127),   rgb_to_hsv_tuple((255,0,127)),   (1,5)),
    XTouchColor("orange",           (255,127,0),   rgb_to_hsv_tuple((255,127,0)),   (1,3)),
    XTouchColor("light red",        (255,127,127), rgb_to_hsv_tuple((255,127,127)), (3,5)),  # optimal
    XTouchColor("pale green",       (127,255,127), rgb_to_hsv_tuple((127,255,127)), (3,6)),  # optimal
    XTouchColor("pale blue",        (127,127,255), rgb_to_hsv_tuple((127,127,255)), (5,6)),  # optimal
    XTouchColor("light cyan",       (127,255,255), rgb_to_hsv_tuple((127,255,255)), (6,7)),
    XTouchColor("light magenta",    (255,127,255), rgb_to_hsv_tuple((255,127,255)), (5,7)),
    XTouchColor("light yellow",     (255,255,127), rgb_to_hsv_tuple((255,255,127)), (3,7)),
    XTouchColor("neutral gray",     (127,127,127), rgb_to_hsv_tuple((127,127,127)), (2,5)),  # optimal

    # --- 3-way mixes ---
    XTouchColor("mix_0_0_4",        (0,0,85),      rgb_to_hsv_tuple((0,0,85)),      (0,0,4)),
    XTouchColor("mix_0_4_4",        (0,0,170),     rgb_to_hsv_tuple((0,0,170)),     (0,4,4)),
    XTouchColor("mix_0_0_2",        (0,85,0),      rgb_to_hsv_tuple((0,85,0)),      (0,0,2)),
    XTouchColor("mix_0_2_4",        (0,85,85),     rgb_to_hsv_tuple((0,85,85)),     (0,2,4)),
    XTouchColor("teal blue",        (0,85,170),    rgb_to_hsv_tuple((0,85,170)),    (0,4,6)),
    XTouchColor("mix_4_4_6",        (0,85,255),    rgb_to_hsv_tuple((0,85,255)),    (4,4,6)),
    XTouchColor("mix_0_2_2",        (0,170,0),     rgb_to_hsv_tuple((0,170,0)),     (0,2,2)),
    XTouchColor("sea green",        (0,170,85),    rgb_to_hsv_tuple((0,170,85)),    (0,2,6)),
    XTouchColor("mix_2_4_6",        (0,170,170),   rgb_to_hsv_tuple((0,170,170)),   (2,4,6)),
    XTouchColor("mix_4_6_6",        (0,170,255),   rgb_to_hsv_tuple((0,170,255)),   (4,6,6)),
    XTouchColor("mix_2_2_6",        (0,255,85),    rgb_to_hsv_tuple((0,255,85)),    (2,2,6)),
    XTouchColor("mix_2_6_6",        (0,255,170),   rgb_to_hsv_tuple((0,255,170)),   (2,6,6)),
    XTouchColor("mix_0_0_1",        (85,0,0),      rgb_to_hsv_tuple((85,0,0)),      (0,0,1)),
    XTouchColor("mix_0_1_4",        (85,0,85),     rgb_to_hsv_tuple((85,0,85)),     (0,1,4)),
    XTouchColor("indigo",           (85,0,170),    rgb_to_hsv_tuple((85,0,170)),    (0,4,5)),
    XTouchColor("mix_4_4_5",        (85,0,255),    rgb_to_hsv_tuple((85,0,255)),    (4,4,5)),
    XTouchColor("mix_0_1_2",        (85,85,0),     rgb_to_hsv_tuple((85,85,0)),     (0,1,2)),
    XTouchColor("dark gray",        (85,85,85),    rgb_to_hsv_tuple((85,85,85)),    (0,1,6)),
    XTouchColor("aqua blue",        (85,85,170),   rgb_to_hsv_tuple((85,85,170)),   (0,4,7)),
    XTouchColor("mix_4_5_6",        (85,85,255),   rgb_to_hsv_tuple((85,85,255)),   (4,5,6)),
    XTouchColor("olive green",      (85,170,0),    rgb_to_hsv_tuple((85,170,0)),    (0,2,3)),
    XTouchColor("forest",           (85,170,85),   rgb_to_hsv_tuple((85,170,85)),   (0,2,7)),
    XTouchColor("mix_0_6_7",        (85,170,170),  rgb_to_hsv_tuple((85,170,170)),  (0,6,7)),
    XTouchColor("azure",            (85,170,255),  rgb_to_hsv_tuple((85,170,255)),  (4,6,7)),
    XTouchColor("mix_2_2_3",        (85,255,0),    rgb_to_hsv_tuple((85,255,0)),    (2,2,3)),
    XTouchColor("spring green",     (85,255,85),   rgb_to_hsv_tuple((85,255,85)),   (2,3,6)),
    XTouchColor("sky cyan",         (85,255,170),  rgb_to_hsv_tuple((85,255,170)),  (2,6,7)),
    XTouchColor("mix_6_6_7",        (85,255,255),  rgb_to_hsv_tuple((85,255,255)),  (6,6,7)),
    XTouchColor("mix_0_1_1",        (170,0,0),     rgb_to_hsv_tuple((170,0,0)),     (0,1,1)),
    XTouchColor("crimson",          (170,0,85),    rgb_to_hsv_tuple((170,0,85)),    (0,1,5)),
    XTouchColor("mix_1_4_5",        (170,0,170),   rgb_to_hsv_tuple((170,0,170)),   (1,4,5)),
    XTouchColor("mix_4_5_5",        (170,0,255),   rgb_to_hsv_tuple((170,0,255)),   (4,5,5)),
    XTouchColor("brown",            (170,85,0),    rgb_to_hsv_tuple((170,85,0)),    (0,1,3)),
    XTouchColor("rose",             (170,85,85),   rgb_to_hsv_tuple((170,85,85)),   (0,1,7)),
    XTouchColor("violet",           (170,85,170),  rgb_to_hsv_tuple((170,85,170)),  (0,5,7)),
    XTouchColor("lavender",         (170,85,255),  rgb_to_hsv_tuple((170,85,255)),  (4,5,7)),
    XTouchColor("mix_1_2_3",        (170,170,0),   rgb_to_hsv_tuple((170,170,0)),   (1,2,3)),
    XTouchColor("light olive",      (170,170,85),  rgb_to_hsv_tuple((170,170,85)),  (0,3,7)),
    XTouchColor("silver gray",      (170,170,170), rgb_to_hsv_tuple((170,170,170)), (1,6,7)),
    XTouchColor("pastel blue",      (170,170,255), rgb_to_hsv_tuple((170,170,255)), (5,6,7)),
    XTouchColor("mix_2_3_3",        (170,255,0),   rgb_to_hsv_tuple((170,255,0)),   (2,3,3)),
    XTouchColor("mix_2_3_7",        (170,255,85),  rgb_to_hsv_tuple((170,255,85)),  (2,3,7)),
    XTouchColor("mix_3_6_7",        (170,255,170), rgb_to_hsv_tuple((170,255,170)), (3,6,7)),
    XTouchColor("pastel cyan",      (170,255,255), rgb_to_hsv_tuple((170,255,255)), (6,7,7)),
    XTouchColor("mix_1_1_5",        (255,0,85),    rgb_to_hsv_tuple((255,0,85)),    (1,1,5)),
    XTouchColor("mix_1_5_5",        (255,0,170),   rgb_to_hsv_tuple((255,0,170)),   (1,5,5)),
    XTouchColor("mix_1_1_3",        (255,85,0),    rgb_to_hsv_tuple((255,85,0)),    (1,1,3)),
    XTouchColor("mix_1_3_5",        (255,85,85),   rgb_to_hsv_tuple((255,85,85)),   (1,3,5)),
    XTouchColor("pink",             (255,85,170),  rgb_to_hsv_tuple((255,85,170)),  (1,5,7)),
    XTouchColor("mix_5_5_7",        (255,85,255),  rgb_to_hsv_tuple((255,85,255)),  (5,5,7)),
    XTouchColor("orange-yellow",    (255,170,0),   rgb_to_hsv_tuple((255,170,0)),   (1,3,3)),
    XTouchColor("peach",            (255,170,85),  rgb_to_hsv_tuple((255,170,85)),  (1,3,7)),
    XTouchColor("mix_3_5_7",        (255,170,170), rgb_to_hsv_tuple((255,170,170)), (3,5,7)),
    XTouchColor("pastel magenta",   (255,170,255), rgb_to_hsv_tuple((255,170,255)), (5,7,7)),
    XTouchColor("mix_3_3_7",        (255,255,85),  rgb_to_hsv_tuple((255,255,85)),  (3,3,7)),
    XTouchColor("pastel yellow",    (255,255,170), rgb_to_hsv_tuple((255,255,170)), (3,7,7)),
]

# Convenience slices
PALETTE_8 = PALETTE_EXTENDED[:8] # X-Touch basics only
PALETTE_6 = PALETTE_EXTENDED[1:7] # X-Touch basics without black and white
PALETTE_27 = PALETTE_EXTENDED[:27] # X-Touch basics and 2-way mixes only

# Hex overrides for Live palette colors that should map to basics
OVERRIDE_MAP = {
    # "FF3636": (1,),  # map to pure red
    # "FF39D4": (5,),  # map to pure magenta
}

RGB_BLACK   = (0,   0,   0)
RGB_WHITE   = (255, 255, 255)
RGB_RED     = (255, 0,   0)
RGB_GREEN   = (0,   255, 0)
RGB_BLUE    = (0,   0,   255)
RGB_YELLOW  = (255, 255, 0)
RGB_MAGENTA = (255, 0,   255)
RGB_CYAN    = (0,   255, 255)
