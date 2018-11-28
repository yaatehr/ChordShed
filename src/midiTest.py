import mido
#from mido.ports import open_input
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
from common.modifier import Modifier
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale, Rotate
from kivy.clock import Clock as kivyClock


ALL_KEYS = ['C', 'C#', 'D', 'Eb', 'E', "F", 'F#', 'G', 'Ab', 'A', 'Bb', 'B']

def createKeyVariants(chord):
    allKeys = np.repeat(range(12), 3, axis=0).reshape(12,-1)
    chordList = np.repeat(chord, 12, axis=0).reshape(3,-1)
    chordList += allKeys.T
    output = [set(chordNotes) for chordNotes in chordList.T]
    return output

class NoteDetector(object):
    clock = time.clock
    noteTimeout = 300
    noteCap = 10

    def __init__(self, synth):
        self.playingNotes = LRUDict(maxduration=self.noteTimeout, maxsize=self.noteCap) 
        # holds a tuple of what notes are playing and how long they have been playing
        self.playedNotes = []
        self.chords = self.initializeChords()
        self.synth = synth
        self.detectingKey = 'C'
        # self.song = MidiFile('./major_chords.mid')

    def initializeChords(self):
        roots = createKeyVariants([60, 64, 67])
        first_inversions = createKeyVariants([64, 67, 72])
        second_inversions = createKeyVariants([67, 72, 76])
        chordDict = dict()
        for i in range(len(roots)):
            chordDict[ALL_KEYS[i]] = [roots[i], first_inversions[i], second_inversions[i]]
        return chordDict

    def callback(self, message):
        if message.type == 'note_on':
            if message.note not in self.playingNotes.keys():
                self.playingNotes.update({message.note: self.clock()})
                self.synth.noteon(0, message.note, message.velocity)
        elif message.type == 'note_off':
            if message.note in self.playingNotes.keys():

                start = self.playingNotes.pop(message.note)
                self.playedNotes.append((message, self.clock() - start))
                self.synth.noteoff(0, message.note)

        self.checkForChords(self.detectingKey)
    
    def getActiveNotes(self):
        return self.playingNotes.keys()

    def setDetectingKey(self, key):
        if key not in ALL_KEYS:
            return 
        self.detectingKey = key

    def checkForChords(self, key):
        notes = set(self.playingNotes.keys())
        if len(notes) < 3:
            return False
        # scan for chords
        for chord in self.chords[key]: 
            if len(notes.intersection(chord)) == 3:
                print('found chord in ', key, '!')
        return True

class GuiKey(InstructionGroup):
    '''
    Key class, keys are drawn from the top down.
    '''
    activeColor = (.2,.3,.2,.2)
    white = (1,1,1, 1)
    black = (0,0,0, 1)

    def __init__(self, keyWidth=15, blackKey=False, pos=(0,0)):
        super(GuiKey, self).__init__()
        size = (keyWidth, 6*keyWidth)
        pos = (pos[0], pos[1]-size[1]) #flip y down the width of the key
        
        self.anchor = pos

        if blackKey:
             self.inactiveColor = self.black
        else:
            self.inactiveColor = self.white

        self.color = Color(*self.inactiveColor, mode='rgba')
        self.state = "inactive"
        self.time = 5
        self.timeout = .2

        self.disactivateAnim = KFAnim((0, *self.activeColor), (self.timeout, *self.inactiveColor))
        self.activateAnim = KFAnim((0, *self.inactiveColor), (self.timeout, *self.activeColor))
        self.rect = Rectangle(pos=self.anchor, size=size)
        self.add(self.color)
        self.add(self.rect)

    def keyPress(self):
        self.color.rgba = self.activeColor
        self.time = 0

    def on_update(self, dt):
        self.time += dt

        if self.disactivateAnim.is_active(self.time):
            self.color.rgba = self.disactivateAnim.eval(self.time)
        else:
            self.color.rgba = self.inactiveColor
        

class KeyboardGui(InstructionGroup):
    blackKey = [True, True, False, True, True, True, False]

    def __init__(self, note_detector):
        super(KeyboardGui, self).__init__()
        self.numOctaves = 2
        self.keys = []
        # self.blackKeys = []
        self.keyWidth = 50
        self.anchor = (100, Window.height*(6.0/8))
        self.objects = AnimGroup()
        self.add(self.objects)
        self.initializeKeys()
        self.noteDetector = note_detector

    def updateGui(self):
        activeKeys = [x%(12*self.numOctaves) for x in self.noteDetector.getActiveNotes()]
        # print(activeKeys)
        for index in activeKeys:
            self.keys[index].keyPress()






    def initializeKeys(self):
        padding = 10
        blackKeys = []
        x, y = self.anchor
        for i in range(7*self.numOctaves):
            key = GuiKey(pos=(x,y), keyWidth=self.keyWidth)
            self.keys.append(key)
            self.objects.add(key)
            if self.blackKey[i%7]:
                blackKey = GuiKey(blackKey=True, pos=(x + self.keyWidth - padding,y), keyWidth=self.keyWidth//1.7)
                blackKeys.append(blackKey)
                self.keys.append(blackKey)
            x += self.keyWidth + padding
        
        print(self.keys[0].color.rgba, self.keys[1].color.rgba)

        #layer black keys on top
        for key in blackKeys:
            self.objects.add(key)

    def on_update(self):
        self.objects.on_update()
        self.updateGui()








class MainWidget(BaseWidget) :
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
