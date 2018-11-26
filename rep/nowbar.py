import sys
sys.path.append('..')
from common.gfxutil import CEllipse

from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color

from kivy.core.window import Window

from math import cos, exp

from .constants import *


'''
NowBar ->
 - Moving cursor that will highlight what gems need to be played
 - Moves across the screen (currently at predetermined rate), will be updated later
 - Once end of path is reached, it will wrap back around to beginning of path
'''
class NowBar(InstructionGroup):
    def __init__(self, bpm):
        super(NowBar, self).__init__()
        
        # color the cursor grey
        self.color = Color(*kCursorDefaultColor)
        self.add( self.color ) 
        
        # save position and size
        self.xpos = PlaceOnBeat(.75) #kTrackLowerLimit
        self.xstart = self.xpos
        self.ypos = kGemBarYPos
        self.csize = kCursorSize
        
        # draw the cursor as a circle
        cpos = (self.xpos, self.ypos)
        self.cursor = CEllipse(cpos=cpos, csize=self.csize)
        self.add(self.cursor)
        
        # limits that NowBar will be moving within, correlates with length of gem bar
        self.lim_lo = kTrackLowerLimit
        self.lim_hi = Window.width - self.lim_lo
        
        # save time for animation, by starting large, the cursor will maintain its size
        self.t = kCursorMaxTime
        
        # save speed of the cursor
        self.v = BpmToPixels(bpm)
        
        # initialize position of the NowBar
        self.active = True
        
        # hold callback that will be used to indicate reaching the end of the line
        self.end_cb = None
        
    
    def install_cb(self, cb):
        self.end_cb = cb 
        
    def change_bpm(self, bpm):
        self.v = BpmToPixels(bpm)   
    
    def update_pos(self, dt):
        # update the barline to its new y position
        # y should remain constant
        curr_xpos = self.cursor.get_cpos()[0]
        new_xpos = curr_xpos + self.v * dt
        self.cursor.set_cpos( (new_xpos, self.ypos) )
        if not self.in_bounds():
            if self.end_cb:
                self.end_cb()
            self.reset()
        self.xpos = self.cursor.get_cpos()[0]
        
    # move cursor back to beginning of the screen      
    def reset(self):
        self.cursor.set_cpos( (self.lim_lo, self.ypos) )
        
    def restart(self):
        self.cursor.set_cpos( (self.xstart, self.ypos) )
        self.activate(True)
        
    # animate
    def animate(self, dt):
        new_size = kCursorSize[0] * exp(-kCursorDecayRate*self.t) * cos(kCursorOscRate*self.t) + kCursorSize[0] 
        self.csize = (new_size, new_size)
        self.cursor.csize = self.csize
        self.t = kCursorMaxTime if (self.t + dt >= kCursorMaxTime) else self.t + dt 
    
    # reset time for animating key presses, can call this function when input is recorded   
    def time_reset(self):
        self.t = 0
    
    # find out if the barline is on screen, if so we will draw it
    def in_bounds(self):
        xpos = self.cursor.get_cpos()[0]
        return True if self.lim_lo <= xpos <= self.lim_hi else False
    
    def activate(self, active):
        self.active = active
    
    # update position and update animation
    def on_update(self, dt):
        # return whether the bar is active or inactive
        self.update_pos(dt)
        self.animate(dt)
        return self.active
        
        





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

    
