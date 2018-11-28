# import mido
# from mido import Message, MidiFile, MidiTrack
import numpy as np
# import time
# from LRUDict import LRUDict
# import sys
# sys.path.append('..')
# from common.core import *
# from common.audio import *
# from common.mixer import *
# from common.wavegen import *
# from common.wavesrc import *
# from common.gfxutil import *
# from common.synth import *
# from common.modifier import Modifier
# from kivy.graphics.instructions import InstructionGroup
# from kivy.graphics import Color, Ellipse, Line, Rectangle
# from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale, Rotate
# from kivy.clock import Clock as kivyClock



def createKeyVariants(chord):
    allKeys = np.repeat(range(12), 3, axis=0).reshape(12,-1)
    chordList = np.repeat(chord, 12, axis=0).reshape(3,-1)
    chordList += allKeys.T
    output = [sorted(chordNotes) for chordNotes in chordList.T]
    return tuple(output)

ALL_KEYS = ['C', 'C#', 'D', 'Eb', 'E', "F", 'F#', 'G', 'Ab', 'A', 'Bb', 'B']


MAJOR_CHORD_QUALITIES = [(True, False), (False, False), (False, False), (True, False), (True, False), (False, False), (False, True)] #format, isMajor, isDiminished
MINOR_CHORD_QUALITIES = [(True, False), (False, True), (True, False), (False, False), (False, False), (True, False), (True, False)] #format, isMajor, isDiminished

MAJOR_CHORDS = createKeyVariants([60, 64, 67])


def scaleToRomanNumeral():
    pass #TODO or just skip this and make a graphical rep.

class Chord(object):

    def __init__(self, key='C', octave=0, inversion=0, augmented=False, diminished=False, major=True):
        key = 'C' if key not in ALL_KEYS else key
        self.key = key
        self.octave = octave
        self.inversion = inversion
        self.isAugmented = augmented
        self.isDiminished = diminished and not augmented #TODO make this more clear??
        self.isMajor = major
        self.midiRep = None
    def getMidiTones(self):
        if self.midiRep == None:
            midiRep = MAJOR_CHORDS[ALL_KEYS.index(self.key)]
            if self.octave != 0:
                midiRep += 12*self.octave
            if self.isAugmented:
                midiRep[2] = midiRep[2] + 1
            if self.isDiminished:
                midiRep[1] = midiRep[1] - 1
                midiRep[2] = midiRep[2] - 1
            if not self.isMajor:
                midiRep[1] = midiRep[1] - 1
            
            if self.inversion > 0:
                midiRep = midiRep.toList()
                while self.inversion > 0:
                    noteVal = midiRep.pop(0)
                    noteVal += 12
                    midiRep.append(noteVal)
                    self.inversion -= 1

            self.midiRep = midiRep

            return self.midiRep
        else:
            return self.midiRep 
    def toString(self):
        return 'TODO'
    
class Key(object):
    def __init__(self, key='C', major=True):
        key = 'C' if key not in ALL_KEYS else key
        self.key = key
        self.isMajor = major        

    def generateChord(self, degree, octave=0, inversion=0, augmented=False):
        assert degree > 0
        conf = MAJOR_CHORD_QUALITIES[degree] if self.isMajor else MINOR_CHORD_QUALITIES[degree]
        isMajor, isDimnished = conf
        tonic = ALL_KEYS.index(self.key)
        chordKey = ALL_KEYS[(tonic+(degree - 1))%12]
        return Chord(key=chordKey, octave=octave, inversion=inversion, augmented=augmented, diminished=isDimnished, major=isMajor)
    def parsePhrase(self, arr):
        # Pass in dicts with the definitions here. We can automate the dict creating process
        return [self.generateChord(*tup) for tup in arr]



#key = Key(key='C')

#print(key.generateChord(1))

print(MAJOR_CHORDS)
