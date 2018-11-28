'''
Definition of constants used for sizing and positioning in representation
of gems, gem bar, and now bar
'''
import numpy as np

from kivy.core.window import Window


# gem bar positioning
kTrackLowerLimit = 20                   # x position lower bound of the gem bar
kYOffset = 40
kGemBarYPos = Window.height - kYOffset  # y position where gem bar will be located


# Constants for cursor/now bar
kCursorSize = (40, 40)                  # size of the cursor
kCursorDefaultColor = (1,1,0)           # cursor color
kCursorDecayRate = 10                   # decay of cursor animation
kCursorOscRate = kCursorDecayRate * 2   # speed of animation
kCursorMaxTime = 20                     # 



# Constants for ticks
kBigTickLength = 20                                 # vertical length of downbeat ticks
kSmallTickLength = kBigTickLength // 4              # vertical length of offbeat ticks
kTickWidth = 5                                      # width of ticks
kTickSpacing = Window.width - 2 * kTrackLowerLimit  # horizontal spacing of ticks
kTickDefaultColor = (.5, .5, .5)                    # color for default tick color (grey)
kTickInactiveColor = (.2, .3, .5)                   # color for ticks that will NEVER have gems
kInactiveTicks = (0,1,15,16)                        # index numbers of inactive ticks 


# Functions and constants for Gems
kGemSize = (50, 50)
kGemDefaultColor = (1,1,1,1)#(1,0,1,1)
kGemExitVelocity = 1000
kGemDecayRate = 2#10
kGemGrowthRate = 5


kWinLen = .1 # in seconds


# filepaths
kNowBarPng = '../images/cursor.png'
kGemHitPng = '../images/gem-hit.png'
kGemMissPng = '../images/gem-miss.png'

QUALITIES_FP = ('maj', 'min', 'aug', 'dim')




# Useful lambda functions
PlaceOnBeat = lambda beat : (4*beat-2)/16 * kTickSpacing + kTrackLowerLimit
BpmToPixels = lambda bpm : kTickSpacing * bpm / 240

