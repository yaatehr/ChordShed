

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
#from rep.patterns import *


class MainWidget(BaseWidget) :
    def __init__(self, callback=None):
        super(MainWidget, self).__init__()
        
        self.test = Gem((100,100), 1)
        self.canvas.add(self.test)
        
   
    def on_key_up(self, keycode):
        pass
        
    
    def on_update(self) :
        self.test.on_update(kivyClock.frametime)
        
if __name__ == '__main__':
     run(MainWidget)
