import sys
sys.path.append('..')
from common.gfxutil import CEllipse

from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color

from kivy.core.window import Window
from kivy.clock import Clock as kivyClock

from .constants import *


'''
CRectangle ->
 - Similar to CEllipse (in nature, not in implementation)
 - Simple implementation for drawing a Centered Rectangle
'''
'''
class CRectangle(InstructionGroup):
    def __init__(self, pos, size, color=(1,1,1)):
        super(CRectangle, self).__init__()
        
        # set color of rectangle
        self.color = Color(*color)
        self.color.a = .5
        self.add( self.color )
        
        # create rectangle instance
        self.rect = Rectangle(size=size)
        self.add(self.rect)
        
        # set position and size of rectangle
        self.cpos = None
        self.size = size
        self.set_cpos(pos)
            
    def get_cpos(self):
        return self.cpos
        
    def set_cpos(self, cpos):
        self.cpos = cpos
        self.rect.pos = [self.cpos[0] - self.size[0]/2, self.cpos[1] - self.size[1]/2]
        
    def set_color(self, color):
        self.color.rgb = color

'''


'''
NowBar ->
 - Moving cursor that will highlight what gems need to be played
 - Moves across the screen (currently at predetermined rate), will be updated later
 - Once end of path is reached, it will wrap back around to beginning of path
'''
class NowBar(InstructionGroup):
    def __init__(self):
        super(NowBar, self).__init__()
        
        # color the cursor grey
        self.color = kCursorDefaultColor
        self.add( Color(*self.color) ) 
        
        # save position
        self.xpos = kTrackLowerLimit
        self.ypos = kGemBarYPos
        
        # draw the cursor as a centered rectangle
        #self.cursor = CRectangle( (self.xpos, self.ypos), (25, 50), self.color )
        cpos = (self.xpos, self.ypos)
        self.cursor = CEllipse(cpos=cpos, csize=kCursorSize) 
        self.add(self.cursor)
        
        # limits that NowBar will be moving within, correlates with length of gem bar
        self.lim_lo = kTrackLowerLimit
        self.lim_hi = Window.width - self.lim_lo
        
        # initialize position of the NowBar
        self.on_update()
        
    def update_pos(self, new_xpos):
        # update the barline to its new y position
        # y should remain constant
        self.cursor.set_cpos( (new_xpos, self.ypos) )
        if not self.in_bounds():
            self.reset()
        self.xpos = self.cursor.get_cpos()[0]
    
    # move cursor back to beginning of the screen      
    def reset(self):
        self.cursor.set_cpos( (self.lim_lo, self.ypos) )
    
    # find out if the barline is on screen, if so we will draw it
    def in_bounds(self):
        xpos = self.cursor.get_cpos()[0]
        return True if self.lim_lo <= xpos <= self.lim_hi else False
    
    def on_update(self):
        # return whether the bar is active or inactive
        curr_xpos = self.cursor.get_cpos()[0]
        new_xpos = curr_xpos + 2
        self.update_pos(new_xpos)
    
