

import sys
sys.path.append('..')

from common.gfxutil import CEllipse

from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Line
from kivy.core.image import Image

from kivy.clock import Clock as kivyClock

from math import exp

from .test_constants import *
from .constants import *


'''
Gem Representation using a TimedCEllipse
- outline will turn disappear and then turn red with a given timeout length
- when struck correctly, the outline will turn green
- when struck incorrectly, the shape will vibrate
'''
class Gem(InstructionGroup):
    def __init__(self, chord, cpos, radius, timeout_len):
        super(Gem, self).__init__()
        
        # save initial position and create gem
        self.cpos = cpos
        self.gem = TimedCEllipse(cpos, radius)
        self.add(self.gem)
        
        # save chord
        self.chord = chord
        
        # save timeout time
        self.timeout_len = timeout_len
        
        # save state
        self.exiting = False
        self.hit = False
        self.miss = False
        self.active = False
        self.t = 10
        
        # draw on the canvas
        self.on_update(0)
        
        
    def set_radius(self, r):
        '''set size of the gem'''
        self.gem.set_radius(r)
    
    
    def on_hit(self):
        '''Change the color of the ring to green'''
        if not self.miss and self.active:
            self.gem.set_angle(721)
            self.gem.set_ring_color(kGemRingHit)
            self.hit = True
        
    
    def on_miss(self):
        '''Change the color of the ring to red'''
        if not self.hit and self.active:
            self.gem.set_angle(721)
            self.gem.set_ring_color(kGemRingMiss)
            self.miss = True
    
    
    def wiggle(self):
        '''Animate by wiggling if an attempted input is incorrect'''
        pass
    
    
    def get_chord(self):
        return self.chord
    
    
    def on_reset(self):
        self.gem.set_ring_color(kGemRingColor)
        self.gem.set_angle(0)
        self.hit = False
        self.miss = False
        self.active = False
        self.exiting = False
        self.gem.set_cpos(self.cpos)
    
    
    def check_timeout(self):
        '''Return True if a timeout has occured'''
        return self.gem.get_angle() >= 360       
    
    
    def activate(self):
        '''Start the timer count down'''
        self.active = True


    def deactivate(self):
        '''Stop the timer count down'''
        self.active = False


    def exit(self):
        '''Indicator to animate off of the screen'''
        self.exiting = True
        
    
    def on_update(self, dt):
        '''Timer should count down'''
        if self.active:
            if not self.check_timeout():
                angle = self.gem.get_angle() + 360/self.timeout_len * dt
                self.gem.set_angle(angle)
            elif not self.hit:
                self.on_miss()
            
        if self.exiting:
            # decrease the alpha
            a = self.gem.rcolor.a - kGemDecayRate * dt
            self.gem.set_alpha(a)
            # set the new position
            x, y = self.gem.get_cpos()
            y -= kGemExitVelocity * dt
            self.gem.set_cpos((x,y))
            # stop drawing once it is transparent enough
            return a >= .01
        return True
            
        
        
        
    
    

'''
TimedCEllipse
- CEllipse with a ring around it
- Can set the start and end angle of the ring to create a timing effect
'''
class TimedCEllipse(InstructionGroup):
    def __init__(self, cpos, radius, texture=None):
        super(TimedCEllipse, self).__init__()
        # save position
        self.cpos = cpos
        self.r = radius
        self.width = radius * .2
        
        # code for creating the Line
        self.rcolor = Color(*kGemRingColor)
        self.add(self.rcolor)
        self.angle = 0
        self.ring = Line(circle=(*self.cpos, self.r, self.angle, 360), width=self.width, cap='none')
        self.add(self.ring)
        
        # code for creating the circle
        self.ccolor = Color(*kGemCircleColor)
        self.add( self.ccolor )
        csize = (2 * radius - self.width,) * 2
        self.circ = CEllipse(cpos=cpos, csize=csize, texture=texture)
        self.add(self.circ)

  
    def set_cpos(self, cpos):
        '''Set the centered position of the shape'''
        self.cpos = cpos
        self.circ.set_cpos(cpos)
        self.ring.circle = (*cpos, self.r, self.angle, 360)
        
    
    def get_cpos(self):
        '''Returned centered position of the shape'''
        return self.cpos

    
    def set_radius(self, r):
        '''Set radius of the shape'''
        self.r = r
        self.ring.circle = (*self.cpos, self.r, self.angle, 360)
        self.width = self.r * .2
        self.ring.width = self.width
        
        csize = (2 * r - self.width,) * 2
        self.circ.csize = csize
    
    
    def set_ring_color(self, color):
        '''Set the ring color to indicate correct/incorrect input'''
        self.rcolor.rgb = color
    
    
    def set_alpha(self, a):
        '''Set the alpha for the sake of animating off the screen'''
        self.rcolor.a = a
        self.ccolor.a = a
        
    
    def set_angle(self, angle):
        '''Set the new angle of the ring'''
        self.angle = angle
        self.ring.circle = (*self.cpos, self.r, self.angle, 360)
        
    
    def get_angle(self):
        '''Get the current angle of the ring'''
        return self.angle
    
    
    
    



# old gem representation
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
