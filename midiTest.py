import mido
# from mido.ports import open_input
from mido import Message, MidiFile, MidiTrack
import numpy as np
import time
from LRUDict import LRUDict


import sys
# from common.core import *
# from common.audio import *
# from common.mixer import *
# from common.wavegen import *
# from common.wavesrc import *
# from common.gfxutil import *
# from kivy.graphics.instructions import InstructionGroup
# from kivy.graphics import Color, Ellipse, Line, Rectangle
# from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale, Rotate
# from kivy.clock import Clock as kivyClock


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



try: 
    note_class = NoteDetector()
    inport = mido.open_input(virtual=False, callback=note_class.callback)
    print('port initialized')
    # msg = inport.receive()
    while True:
        pass
except KeyboardInterrupt as e:
    print(e)
    
except Exception as e:
    print('no input attached ', e)
finally:
    del inport

# note_class = NoteDetector()





#parsing mido.Message.from_bytes()
#  mido.parse_all([0x92, 0x10, 0x20, 0x82, 0x10, 0x20])
# p.feed_byte(0x90) for callback?
# make a buffer for midi inputs