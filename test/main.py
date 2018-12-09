

import mido
import sys
sys.path.append('..')
from common.core import *
from common.audio import *
from common.mixer import *
from common.wavegen import *
from common.wavesrc import *
from common.gfxutil import *
from common.synth import *
from common.clock import Clock as GameClock

from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale, Rotate

from kivy.core.window import Window
from kivy.core.text import Label as CoreLabel

from rep.gem import Gem
from rep.player import Player
from src.notedetector import NoteDetector
from src.pianotutor import KeyboardGui
from src.ticker import Ticker
from src.chord import *

from rep.constants import *
from rep.patterns import *

import random
import numpy as np
import bisect


patterns = patternReader('./testpattern.txt')

defaultKey = Key()



class MainWidget(BaseWidget) :
    playing = False
    midiInput = None
    info = topleft_label()
    mixer = Mixer()
    audio = Audio(2)
    playerSynth = Synth('../data/FluidR3_GM.sf2')

    def __init__(self, masterPattern=patterns, key=defaultKey, fileName='testoutput.txt', callback=None):
        super(MainWidget, self).__init__()
        '''
        The main game instance, the pattern and keys are loaded before the screen is initialized
        ALL graphical components are controlled by the clock (update isnt' run if clock isn't playing)
         '''


        self.pattern = masterPattern
        self.key = key

        #Audio
        self.audio.set_generator(self.mixer)
        self.mixer.add(self.playerSynth)
        self.clock = GameClock()

        nd = NoteDetector(self.playerSynth)
        self.gui = KeyboardGui(nd)

        self.detector = nd
        self.ticker = Ticker(self.pattern, key, self.clock)
        self.mixer.add(self.ticker.synth)
        self.player = Player(self.ticker, self.clock, nd.updateTargetChord)
        self.ticker.initialize_callbacks(self.player.increment_bar, self.player.catch_passes)
        self.detector.initializePlayer(self.player)
        self.canvas.add(self.player)
        self.canvas.add(self.gui)
        
        #midi input state
        self.add_widget(self.info)
        self.switchScreens = callback


    def initialize_controller(self):
        if self.hasMidiInput():
            return True
        inport = None
        try: 
            inport = mido.open_input(virtual=False, callback=self.detector.callback)
            print('port initialized')
        except Exception as e:
            return False
            print('no input attached ', e)
        self.midiInput = inport
        return True

    def hasMidiInput(self):
        return self.midiInput is not None

    def on_key_down(self, keycode, modifiers):
        if keycode[1] == 't':
            self.player.load_pattern(Test_Pattern)
            print('loading stuff')
            
        elif keycode[1] == 'p':
            self.pause_game()
            
        elif keycode[1] == 'o':
            self.play_game()

        elif keycode[1] == 'c' and self.midiInput is None:
            self.initialize_controller()
            # self.playerSynth.start()

        # else:
        #     self.player.on_input(keycode[1])
        

    def play_game(self):
        self.clock.start()
        self.player.play_game()
        self.playing = True

    def pause_game(self):
        self.player.pause_game()
        self.clock.stop()
        self.playing = False
    
    def on_update(self) :
        if self.playing:
            self.player.on_update()
        self.audio.on_update()
        self.gui.on_update()
        # check for midi input and add onscreen indicator

        if self.hasMidiInput():
            self.info.text = "\nKeyboard Connected"
        else:
            self.info.text = "\nNO Keyboard Found"


        # update personal clock
        # self.t += kivyClock.frametime
        '''
        if not self.paused:
            self.player.on_update()
        
        self.info.text = '"More Than A Feelng" - Boston'
        self.info.text += '\nSCORE: %d' %(self.player.score) +'    %.2f / 5 STARS' %(self.player.score/34700) # 34700 is max score, in this case 5 stars is a perfect score
        
        if self.paused:
            self.info.text += '\n~PAUSED~ (press "P" to resume)'
        else:
            self.info.text += '\n\npress "P" to pause'
        '''
        

if __name__ == '__main__':
    run(MainWidget)
