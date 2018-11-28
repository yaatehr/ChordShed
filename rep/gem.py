import sys
sys.path.append('..')
from common.gfxutil import CEllipse

from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color

from kivy.clock import Clock as kivyClock
from kivy.core.image import Image

from math import exp

from .constants import *



'''
Gem
'''
class Gem(InstructionGroup):
    def __init__(self, chord, beat):
        super(Gem, self).__init__()
        
        # color the gem
        self.color = Color(*kGemDefaultColor)
        self.add(self.color)
        
        # save chord and beat
        self.chord = chord
        self.beat = beat
        
        # give position and size of gem
        self.xpos = PlaceOnBeat(beat)
        self.ypos = kGemBarYPos
        self.csize = (0,0)
        
        # draw gem as a 4 segment circle
        cpos = (self.xpos, self.ypos)
        self.gem = CEllipse(cpos=cpos, csize=self.csize, texture=Image(kGemPng).texture)
        self.add(self.gem)
        
        # state for when to animate
        self.t = 0
        self.active = True
        
        # state for whether or not hit or miss
        self.done = False
    
    def get_cpos(self):
        return self.gem.cpos
    
    def get_chord(self):
        return self.chord
    
    def set_csize(self, new_size):
        self.csize = (new_size, new_size)
        self.gem.csize = self.csize
    
    def exit(self):
        self.active = False
    
    def reset(self):
        self.active = True
        self.__init__(self.chord, self.beat)
        
    def on_hit(self):
        #self.color.rgb = kGemHit
        self.gem.texture = Image(kNowBarPng).texture
        self.done = True
        
    def on_miss(self):
        self.color.rgb = kGemMiss
        self.done = True
        
    def on_update(self, dt):
        new_size = kGemSize[0] * (1 - exp(-kGemGrowthRate * self.t))
        self.set_csize(new_size)
        self.t = self.t + dt if self.t + dt < 10 else self.t
        if not self.active:
            self.color.a -= kGemDecayRate * dt
            self.ypos -= kGemExitVelocity * dt
            self.gem.cpos = (self.xpos, self.ypos)
            return self.color.a >= .1
        return True
