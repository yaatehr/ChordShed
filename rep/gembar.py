from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Line

from kivy.core.window import Window
from kivy.clock import Clock as kivyClock

from .constants import *

'''
Tick ->
 - Small line drawn to show subdivision of bars during the game
 - Simply a line specialized for drawing ticks at a prespecified location
'''
class Tick(InstructionGroup):
    def __init__(self, x, color, big=False):
        super(Tick, self).__init__()
        
        # add new color, grey by default
        self.color = Color(*color)
        self.add( self.color )
        
        # draw and create line
        length = kBigTickLength if big else kSmallTickLength
        y_lo = kGemBarYPos - length
        y_hi = kGemBarYPos + length
        points = (x, y_lo, x, y_hi)
        self.tick = Line(points=points, width=kTickWidth)
        self.add(self.tick)
        
    # keep state for whether or not the line should be visible 
    def disappear(self, active):
        self.color.a = int( not active )





'''
GemBar ->
 - Displays tick marks on the canvas
 - Contains active ticks (meaning gems can be placed on top of them), and inactive ticks (the opposite)
 - When/If necessary (like in menus), can be invisible
'''
class GemBar(InstructionGroup):
    def __init__(self):
        super(GemBar, self).__init__()
        
        # create individual tick marks and hold onto them
        self.ticks = list()
        for i in range(17):
            x = i/16 * kTickSpacing + kTrackLowerLimit
            color = kTickInactiveColor if i in kInactiveTicks else kTickDefaultColor
            big = i%4 == 2           
            tick = Tick(x, color, big=big)
            self.add(tick)
            self.ticks.append(tick)
    
    def disappear(self, active):
        for tick in self.ticks:
            tick.disappear(active)
