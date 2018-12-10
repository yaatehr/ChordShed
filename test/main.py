

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


#run_main_widget = True # uncomment if this module is being run within the test/ directory
run_main_widget = False # uncomment if this module is being run NOT within the test/ directory

if run_main_widget:
    fp1 = './testpattern.txt'
    fp2 = './testpattern2.txt'
    fp3 = './testpattern3.txt'
else: 
    fp1 = '../test/testpattern.txt'
    fp2 = '../test/testpattern2.txt'
    fp3 = '../test/testpattern3.txt'

pattern1 = patternReader(fp1)
pattern2 = patternReader(fp2)
pattern3 = patternReader(fp3)


def loadPaths():
    for (dirpath, dirnames, filenames) in os.walk(os.path.join(os.path.dirname('__file__'), '../patterns')):
        patternDict = {file: patternReader(os.path.join(dirpath, file)) for file in filenames}
        print(patternDict.keys())
    return patternDict

loadPaths()

patterns = (pattern1, pattern2, pattern3)

defaultKey = Key()


class MainWidget(BaseWidget) :
    playing = False
    info = topleft_label()

    def __init__(self, masterPattern=patterns, key=None, fileName='testoutput.txt', noteDetector=None, mixer=None, callback=None):
        super(MainWidget, self).__init__()
        '''
        The main game instance, the pattern and keys are loaded before the screen is initialized
        ALL graphical components are controlled by the clock (update isnt' run if clock isn't playing)
         '''
        self.mixer = mixer
        self.pattern = masterPattern
        self.key = key

        #Audio     
        self.clock = GameClock()

        self.gui = KeyboardGui(noteDetector)

        self.detector = noteDetector
        self.ticker = Ticker(self.pattern, key, self.clock)
        self.mixer.add(self.ticker.synth)
        self.player = Player(self.ticker, self.clock, self.pattern, noteDetector.updateTargetChord, noteDetector.getActiveNotes)
        self.ticker.initialize_callbacks(self.player.increment_bar, self.player.catch_passes)
        self.detector.initializePlayer(self.player)
        self.canvas.add(self.player)
        self.canvas.add(self.gui)
        #midi input state
        self.info.parent = None # make sure the label widget does not have a parent
        self.add_widget(self.info)
        self.switchScreens = callback

    
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
        if not self.parent:
            return
        if self.playing:
            self.player.on_update()
        self.gui.on_update()
        # check for midi input and add onscreen indicator

        if not self.parent._has_midi_input():
            self.info.text = "No Keyboard Connected"
        else:
            if self.player.scoreCard:
                self.info.text = "Score: %d" % self.player.scoreCard.getScore()
        


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
