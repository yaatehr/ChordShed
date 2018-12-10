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
        self.correctNotes = set()
        self.incorrectNotes = set()
        self.onHit = None
        self.onInput = None
        self.octaveBlind = True

    def updateTargetChord(self, chord): #to be called from player class
        self.targetChord = chord
        self.targetMidi = chord._getMidiTones()
        self.reset()        
        #TODO add clearing logic and refresh notes (we still want the mto decay)

    def reset(self):
        self.playingNotes.clear()

    def initializePlayer(self, player): #to initialize player class callbacks
        self.onHit = player.on_hit
        self.onInput = player.on_input

    def callback(self, message):
        print(message)
        if message.type == 'note_off':
            if message.note in self.playingNotes.keys():
                start = self.playingNotes.pop(message.note)
                # self.playedNotes.append((message, self.clock() - start))
                self.synth.noteoff(0, message.note)
                if message.note in self.correctNotes:
                    self.correctNotes.remove()
                if self.onInput:
                    self.onInput(message.note, False)

        elif message.type == 'note_on' or message.type == 'polytouch':
            # print(message)
            if message.note not in self.playingNotes.keys():
                correctNote = False
                if self.targetChord:
                    if self.octaveBlind:
                        targetMidi = np.mod(self.targetMidi, 12)
                        targetMidi += 1
                        targetMidi -= (message.note%12 + 1)
                        correctNote = 0 in targetMidi

                    elif message.note in self.targetMidi:
                        correctNote = True
                self.playingNotes.update({message.note: correctNote})
                try:
                    vel = message.velocity if message.velocity else np.clip(message.value, 0 ,100)
                except Exception as a:
                    vel = np.clip(message.value, 0 ,100)
                    print(message)
                    print("failed to recognize")
                self.synth.noteon(0, message.note, vel)
                if self.targetChord and self.checkForChords():
                    if self.onHit:
                        return self.onHit()
                elif self.onInput:
                    return self.onInput(message.note, correctNote)
    
    def getActiveNotes(self):
        correctNotes = []
        incorrectNotes = []
        for note,val in self.playingNotes.items():
            if val:
                correctNotes.append(note)
            else:
                incorrectNotes.append(note)
        # print(correctNotes, incorrectNotes)
        return correctNotes, incorrectNotes

    def checkForChords(self):
        notes = list(self.playingNotes.values())
        if len(notes) < 3:
            return False
        if self.targetChord:
            return all(notes)