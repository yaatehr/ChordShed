'''
Definition of constants used for sizing and positioning in representation
of gems, gem bar, and now bar
'''
import numpy as np

from kivy.core.window import Window
from kivy.clock import Clock as kivyClock

kDt = kivyClock.frametime

# gem bar positioning
kTrackLowerLimit = 20             # x position lower bound of the gem bar
kGemBarYPos = Window.height - 40  # y position where gem bar will be located

# Constants for cursor/now bar
kCursorSize = (40, 40)                  # 
kCursorDefaultColor = (1,1,1)           # 
kCursorDecayRate = 1000                 # 
kCursorOscRate = kCursorDecayRate * 2   # 
kCursorMaxTime = 20                     # 

# Constants for ticks
kBigTickLength = 20                                 # vertical length of downbeat ticks
kSmallTickLength = kBigTickLength // 4              # vertical length of offbeat ticks
kTickWidth = 5                                      # width of ticks
kTickSpacing = Window.width - 2 * kTrackLowerLimit  # horizontal spacing of ticks
kTickDefaultColor = (.5, .5, .5)                    # color for default tick color (grey)
kTickInactiveColor = (.2, .3, .4)                   # color for ticks that will NEVER have gems
kInactiveTicks = (0,1,15,16)                        # index numbers of inactive ticks 


# Functions and constants for Gems
PlaceGemOnBeat = lambda beat : (4*beat-2)/16 * kTickSpacing + kTrackLowerLimit
