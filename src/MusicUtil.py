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
from common.modifier import Modifier
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale, Rotate
from kivy.clock import Clock as kivyClock


ALL_KEYS = ['C', 'C#', 'D', 'Eb', 'E', "F", 'F#', 'G', 'Ab', 'A', 'Bb', 'B']

keyDict = 

class Chord(object):

    def __init__(self, key, octave, inversion):
        self.key = key
        self.octave = octave
        self.inversion = inversion

    def getMidiTones(self):
        return 
    
    

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




def createKeyVariants(chord):
    allKeys = np.repeat(range(12), 3, axis=0).reshape(12,-1)
    chordList = np.repeat(chord, 12, axis=0).reshape(3,-1)
    chordList += allKeys.T
    output = [set(chordNotes) for chordNotes in chordList.T]
    return output 

def initializeChords():
    roots = createKeyVariants([60, 64, 67])
    first_inversions = createKeyVariants([64, 67, 72])
    second_inversions = createKeyVariants([67, 72, 76])
    chordDict = dict()
    for i in range(len(roots)):
        chordDict[ALL_KEYS[i]] = [roots[i], first_inversions[i], second_inversions[i]]
    return chordDict

def transposeBaseChord(midiTones, key, octave)