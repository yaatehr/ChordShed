

import sys
sys.path.append('..')
from common.core import *
from common.audio import *
from common.mixer import *
from common.wavegen import *
from common.wavesrc import *
from common.gfxutil import *
from common.synth import *


from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale, Rotate
from kivy.clock import Clock as kivyClock

from kivy.core.window import Window
from kivy.core.text import Label as CoreLabel

from rep.gem import *
'''
from rep.nowbar import NowBar
from rep.gembar import GemBar
from rep.gem import Gem
from rep.gamedisplay import GameDisplay
from rep.player import Player
from src.notedetector import NoteDetector
from src.pianotutor import KeyboardGui
'''

from rep.constants import *


class MainWidget(BaseWidget) :
    def __init__(self, callback=None):
        super(MainWidget, self).__init__()
        
        chord = 't'
        self.test = Gem(chord, (400,300), 20, 5)
        self.canvas.add(self.test)
        
   
    def on_key_down(self, keycode, modifiers):
        if keycode[1] == 'q':
            self.test.on_reset()
        if keycode[1] == 'w':
            self.test.on_hit()
        if keycode[1] == '1':
            self.test.set_radius(20)
        if keycode[1] == '2':
            self.test.set_radius(50)
        if keycode[1] == '3':
            self.test.set_radius(100)
        
    
    def on_update(self) :
        self.test.on_update(kivyClock.frametime)




      
if __name__ == '__main__':
     run(MainWidget)
