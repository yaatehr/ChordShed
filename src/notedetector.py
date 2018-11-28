import mido
#from mido.ports import open_input
from mido import Message, MidiFile, MidiTrack
import numpy as np
import time
from src.LRUDict import LRUDict
# import sys
# sys.path.append('..')


class NoteDetector(object):
    clock = time.clock
    noteTimeout = 300
    noteCap = 10

    def __init__(self, synth):
        self.playingNotes = LRUDict(maxduration=self.noteTimeout, maxsize=self.noteCap) 
        # holds a tuple of what notes are playing and how long they have been playing
        self.playedNotes = []
        # self.chords = self.initializeChords()
        self.synth = synth
        self.detectingKey = 'C'
        self.targetChord = None
        self.targetMidi = None
        # self.song = MidiFile('./major_chords.mid')

    def updateTargetChord(self, chord):
        self.targetChord = chord
        self.targetMidi = set(chord._getMidiTones())
        #TODO add clearing logic and refresh notes (we still want the mto decay)

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
        if self.targetChord:
            self.checkForChords()
    
    def getActiveNotes(self):
        return self.playingNotes.keys()

    def setDetectingKey(self, key):
        if key not in ALL_KEYS:
            return 
        self.detectingKey = key

    def checkForChords(self):
        notes = set(self.playingNotes.keys())
        if len(notes) < 3:
            return False
        # scan for chords
        if self.targetChord:
            if len(notes.difference(self.targetMidi)) == 0:
                print('found chord: ' + chord)
            return True
        return False