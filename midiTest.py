import mido
# from mido.ports import open_input
from mido import Message, MidiFile, MidiTrack
import numpy as np
import time
from LRUDict import LRUDict


import sys
from common.core import *
from common.audio import *
from common.mixer import *
from common.wavegen import *
from common.wavesrc import *
from common.gfxutil import *
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

    def __init__(self):
        self.playingNotes = LRUDict(maxduration=self.noteTimeout, maxsize=self.noteCap) # holds a tuple of what notes are playing and how long they have been playing
        self.playedNotes = []
        self.chords = self.initializeChords()
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
        elif message.type == 'note_off':
            if message.note in self.playingNotes.keys():
                start = self.playingNotes.pop(message.note)
                self.playedNotes.append((message, self.clock() - start))
        self.checkForChords('C')
    
    def updateGui(self):
        pass

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
    white = (1,1,1)
    black = (0,0,0)

    def __init__(self, keyWidth=15, blackKey=False, pos=(0,0)):
        super(GuiKey, self).__init__()
        size = (keyWidth, 6*keyWidth)
        pos = (pos[0], pos[1]-size[1]) #flip y down the width of the key
        
        self.anchor = pos

        if blackKey:
             self.inactiveColor = self.black
        else:
            self.inactiveColor = self.white

        self.color = Color(*self.inactiveColor)
        self.state = "inactive"
        self.time = 5
        self.timeout = .1

        self.disactivateAnim = KFAnim((0, *self.activeColor), (self.timeout, *self.inactiveColor))
        self.activateAnim = KFAnim((0, *self.inactiveColor), (self.timeout, *self.activeColor))
        self.rect = Rectangle(pos=self.anchor, size=size)
        self.add(self.color)
        self.add(self.rect)

    def set_state(self, state):
        if state not in ['active', 'inactive']:
            return
        self.state = state
        self.time = 0


    def on_update(self, dt):
        self.time += dt

        if self.state == "active":
            if self.hitAnim.is_active(self.time):
                self.color.rgba = self.activateAnim.eval(self.time)
            else:
                self.color.rgba = self.activeColor
        else:
            self.color.rgb = self.disactivateAnim.eval(self.time)
        


        

class KeyboardGui(InstructionGroup):
    blackKey = [False, True, True, False, True, True, True, False]

    def __init__(self):
        super(KeyboardGui, self).__init__()
        self.numOctaves = 1
        self.keys = []
        self.blackKeys = []
        self.keyWidth = 50
        self.anchor = (100, Window.height*(6.0/8))
        self.objects = AnimGroup()
        self.add(self.objects)
        self.initializeKeys()

    def initializeKeys(self):
        padding = 10
        x, y = self.anchor
        for i in range(7):

            key = GuiKey(pos=(x,y), keyWidth=self.keyWidth)
            self.keys.append(key)
            self.objects.add(key)
            x += self.keyWidth + padding

        x, y = self.anchor
        x -= self.keyWidth//2
        x += padding/2
        for i in range(7):
            if self.blackKey[i]:
                print('adding black key)')
                blackKey = GuiKey(blackKey=True, pos=(x,y), keyWidth=self.keyWidth//1.7)
                self.blackKeys.append(blackKey)
                self.objects.add(blackKey)
            x += self.keyWidth + padding

    def on_update(self):
        self.objects.on_update()




# try: 
#     note_class = NoteDetector()
#     inport = mido.open_input(virtual=False, callback=note_class.callback)
#     print('port initialized')
#     # msg = inport.receive()
#     while True:
#         pass
# except KeyboardInterrupt as e:
#     print(e)
    
# except Exception as e:
#     print('no input attached ', e)
# finally:
#     del inport

# note_class = NoteDetector()




class MainWidget(BaseWidget) :
    def __init__(self):
        super(MainWidget, self).__init__()
        self.info = topleft_label()
        self.add_widget(self.info)
        self.objects = AnimGroup()
        self.key_gui = KeyboardGui()
        self.canvas.add(self.key_gui)
        #Audio Setup
        self.audio = Audio(2)
        self.mixer = Mixer()
        self.audio.set_generator(self.mixer)


        #Modifier setup NOTE: I am not sure how to initialize one of these to default value so it causes some
        self.modifier = Modifier()

    def on_key_down(self, keycode, modifiers):
        pass
        
    def on_key_up(self, keycode):
        if keycode[1] in self.modifier.mods.keys():
            self.modifier.on_key_up(keycode[1])

    def on_update(self):
        self.objects.on_update()
        self.audio.on_update()
        self.modifier.on_update()
        self.key_gui.on_update()
        self.info.text = '\nfps:%d' % kivyClock.get_fps()

run(MainWidget)





#parsing mido.Message.from_bytes()
#  mido.parse_all([0x92, 0x10, 0x20, 0x82, 0x10, 0x20])
# p.feed_byte(0x90) for callback?
# make a buffer for midi inputs