import mido
from mido import Message, MidiFile, MidiTrack
import numpy as np
import time
from LRUDict import LRUDict
import sys
sys.path.append('..')
from common.core import *
from common.audio import *
from common.mixer import *
from common.wavegen import *
from common.wavesrc import *
from common.gfxutil import *
from common.synth import *
from src.MusicUtil import *
from common.modifier import Modifier
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale, Rotate
from kivy.clock import Clock as kivyClock



class KeyboardGui(InstructionGroup):
    blackKey = [True, True, False, True, True, True, False]
    borderColor = (.5,.5,.5,1)
    padding = 10

    def __init__(self, note_detector):
        super(KeyboardGui, self).__init__()
        self.numOctaves = 2
        self.keys = []
        # self.blackKeys = []
        self.keyWidth = 50
        self.anchor = (100, Window.height*(6.0/8))
        self.objects = AnimGroup()
        self.add(self.objects)
        self.initializeFrame()
        self.initializeKeys()
        self.noteDetector = note_detector

    def updateGui(self):
        activeKeys = [x%(12*self.numOctaves) for x in self.noteDetector.getActiveNotes()]
        for index in activeKeys:
            self.keys[index].keyPress()

    def initializeKeys(self):
        blackKeys = []
        x, y = self.anchor
        for i in range(7*self.numOctaves):
            key = GuiKey(pos=(x,y), keyWidth=self.keyWidth)
            self.keys.append(key)
            self.objects.add(key)
            if self.blackKey[i%7]:
                blackKey = GuiKey(blackKey=True, pos=(x + self.keyWidth - self.padding,y), keyWidth=self.keyWidth//1.7)
                blackKeys.append(blackKey)
                self.keys.append(blackKey)
            x += self.keyWidth + self.padding
        #layer black keys on top
        for key in blackKeys:
            self.objects.add(key)

    def initializeFrame(self):
        width = self.numOctaves*7*(self.keyWidth+self.padding) - self.padding
        height = self.keyWidth*6
        borderWidth = 20
        x,y = self.anchor
        y -= height
        self.color = Color(*self.borderColor, mode="rgb")
        self.add(self.color)
        topRect = Rectangle(pos=(x, y+height), size=(width, borderWidth))
        botRect = Rectangle(pos=(x, y-borderWidth), size=(width, borderWidth))
        leftRect = Rectangle(pos=(x-borderWidth, y-borderWidth), size=(borderWidth, height+2*borderWidth))
        rightRect = Rectangle(pos=(x+width, y-borderWidth), size=(borderWidth, height+2*borderWidth))
        self.border = [topRect, botRect, leftRect, rightRect]
        [self.add(x) for x in self.border]

    def on_update(self):
        self.objects.on_update()
        self.updateGui()



class MainWidget(BaseWidget) :
    '''
    Current shell for the midi tutor
    This widget will liekly develop into our game instance (or one of the variants

    Next Steps:
        link the nowbar gui to this setup
        import chord detection patterj

    '''
    def __init__(self):
        super(MainWidget, self).__init__()
        self.info = topleft_label()
        self.add_widget(self.info)
        self.objects = AnimGroup()
                #Audio Setup
        self.audio = Audio(2)
        self.synth = Synth('../data/FluidR3_GM.sf2')
        self.audio.set_generator(self.synth)
        self.noteDetector = NoteDetector(self.synth)
        self.key_gui = KeyboardGui(self.noteDetector)
        self.canvas.add(self.key_gui)
        self.midiInput = None


        #Modifier setup NOTE: I am not sure how to initialize one of these to default value so it causes some
        self.modifier = Modifier()
        self.modifier.add('e', 'Current Key: ', ALL_KEYS, self._set_key)

    def _set_key(self, key):
        self.noteDetector.setDetectingKey(key)

    def initialize_controller(self):
        inport = None
        try: 
            inport = mido.open_input(virtual=False, callback=self.key_gui.noteDetector.callback)
            print('port initialized')
            # msg = inport.receive()            
        except Exception as e:
            print('no input attached ', e)
        return inport


    def on_key_down(self, keycode, modifiers):
        if keycode[1] == 'r' and self.midiInput is None:
            self.midiInput = self.initialize_controller()
            self.synth.start()
            # self.mixer.add()
        if keycode[1] in self.modifier.mods.keys():
            self.modifier.on_key_down(keycode[1])
    def on_key_up(self, keycode):
        if keycode[1] in self.modifier.mods.keys():
            self.modifier.on_key_up(keycode[1])

    def on_update(self):
        self.objects.on_update()
        self.audio.on_update()
        self.modifier.on_update()
        self.key_gui.on_update()
        self.info.text = '\nfps:%d' % kivyClock.get_fps()
        self.info.text = '\n r to initialize keyboard'
        self.info.text += '\n'+self.modifier.get_txt()

run(MainWidget)





#parsing mido.Message.from_bytes()
#  mido.parse_all([0x92, 0x10, 0x20, 0x82, 0x10, 0x20])
# p.feed_byte(0x90) for callback?
# make a buffer for midi inputs