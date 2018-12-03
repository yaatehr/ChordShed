import sys
sys.path.append('..')

from common.gfxutil import CEllipse

from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Line

from kivy.clock import Clock as kivyClock
from kivy.core.image import Image

from math import exp

from .test_constants import *



'''
Gem
'''

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
        fp_png = '../images/' + chord.key.lower() + '-' + QUALITIES_FP[chord.quality] + '.png'
        print(fp_png)
        
        cpos = (self.xpos, self.ypos)
        self.gem = CEllipse(cpos=cpos, csize=self.csize, texture=Image(fp_png).texture)
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
        self.gem.texture = Image(kGemHitPng).texture
        self.done = True
        
    def on_miss(self):
        self.gem.texture = Image(kGemMissPng).texture
        self.done = True
        
    def focus(self):
        pass #TODO decaying glow animation
        
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
'''


class Gem(InstructionGroup):
    def __init__(self, cpos, timeout_len, chord='t'):
        super(Gem, self).__init__()
        
        # save position
        self.gem = Timed_CEllipse(cpos)
        self.add(self.gem)
        
        # save timeout time
        self.timeout_len = timeout_len
        
        # save state
        self.active = True
        
        self.on_update(0)
        
    def set_cpos(self, cpos):
        '''Set position of gem'''
        self.gem.set_cpos(cpos)
        
        
    def on_hit(self):
        '''Change the color of the ring to green'''
        self.gem.set_angle(720)
        self.gem.set_ring_color(kGemRingHit)
        
    
    def on_miss(self):
        '''Change the color of the ring to red'''
        self.gem.set_angle(720)
        self.gem.set_ring_color(kGemRingMiss)
        
    
    def check_timeout(self):
        '''Return True if a timeout has occured'''
        return self.gem.get_angle() >= 360       
    
    
    def exit(self):
        self.active = False
        
    
    def on_update(self, dt):
        '''Timer should count down'''
        if self.active:
            if not self.check_timeout():
                angle = self.gem.get_angle() + 360/self.timeout_len * dt
                self.gem.set_angle(angle)
            else:
                self.on_miss()
        else:
            pass
        
        
        
    
    

'''
Timed_CEllipse
- CEllipse with a ring
'''
class Timed_CEllipse(InstructionGroup):
    def __init__(self, cpos):
        super(Timed_CEllipse, self).__init__()
        
        # save position
        self.cpos = cpos
        
        # code for creating the Line
        self.color = Color(*(1,1,0))
        self.add(self.color)
        self.angle = 0
        self.ring = Line(circle=(*self.cpos, kGemRingRadius, self.angle, 360), width=kGemRingWidth, cap='none')
        self.add(self.ring)
        
        # code for creating the circle
        self.add( Color(kGemRingColor) )
        self.circ = CEllipse(cpos=cpos, csize=kGemCircleSize)
        self.add(self.circ)

  
    def set_cpos(self, cpos):
        '''Set the centered position of the shape'''
        self.cpos = cpos
        self.circ.set_cpos(cpos)
        self.ring.circle = (*cpos, kGemRingRadius, self.angle, 360)
        
    
    def get_cpos(self):
        '''Returned centered position of the shape'''
        return self.circ.cpos


    def set_ring_color(self, color):
        '''Set the ring color to indicate correct/incorrect input'''
        self.color.rgb = color
    
    
    def set_angle(self, angle):
        '''Set the new angle of the ring'''
        self.angle = angle
        self.ring.circle = (*self.cpos, kGemRingRadius, self.angle, 360)
        
    
    def get_angle(self):
        '''Get the current angle of the ring'''
        return self.angle
    
    
    
    
