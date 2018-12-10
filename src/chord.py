
import numpy as np

MAJ = 0
MIN = 1
AUG = 2
DIM = 3

QUALITIES = (AUG, MAJ, MIN, DIM)

def createKeyVariants(chord):
    allKeys = np.repeat(range(12), 3, axis=0).reshape(12,-1)
    chordList = np.repeat(chord, 12, axis=0).reshape(3,-1)
    chordList += allKeys.T
    output = [np.array(chordNotes) for chordNotes in chordList.T]
    return tuple(output)


ALL_KEYS = ['C', 'C#', 'D', 'Eb', 'E', "F", 'F#', 'G', 'Ab', 'A', 'Bb', 'B']

'''
MAJOR_CHORD_QUALITIES = [(True, False), (False, False), (False, False), (True, False), (True, False), (False, False), (False, True)] #format, isMajor, isDiminished
MINOR_CHORD_QUALITIES = [(True, False), (False, True), (True, False), (False, False), (False, False), (True, False), (True, False)] #format, isMajor, isDiminished
'''

MAJOR_CHORD_QUALITIES = (MAJ, MIN, MIN, MAJ, MAJ, MIN, DIM)
MINOR_CHORD_QUALITIES = (MIN, DIM, MAJ, MIN, MAJ, MAJ, DIM)


MAJOR_CHORDS = createKeyVariants([60, 64, 67])
MINOR_CHORDS = createKeyVariants([60, 63, 67])
AUGMENTED_CHORDS = createKeyVariants([60, 64, 68])
DIMINISHED_CHORDS = createKeyVariants([60, 63, 66])

ALL_CHORDS = ( MAJOR_CHORDS, MINOR_CHORDS, AUGMENTED_CHORDS, DIMINISHED_CHORDS )

MAJOR_STEPS = (0, 2, 4, 5, 7, 9, 11)
MINOR_STEPS = (0, 2, 3, 5, 7, 8, 11)

class Chord(object):
    def __init__(self, key='C',  octave=0, inversion=0, quality=MAJ, keyAnchor=60, customMidi=None):
        self.keyOffset = 60-keyAnchor
        key = 'C' if key not in ALL_KEYS else key
        self.key = key
        self.key_idx = ALL_KEYS.index(self.key) 
        self.octave = octave
        self.inversion = np.clip(inversion, 0, 2)
        self.quality = quality
        self.customMidi = customMidi
        self.midiRep = None
        self.midiRep = self._getMidiTones()
            
    def __str__(self):
        '''Create string representation of chord'''
        note_idx = np.array(self.midiRep) % 12
        string_rep = ""
        for idx in note_idx:
            string_rep += ALL_KEYS[idx] + ":"
        return string_rep
    
    def _getMidiTones(self):
        if self.customMidi:
            return self.customMidi
        elif self.midiRep is not None:
            return self.midiRep
        midiRep = np.copy(ALL_CHORDS[self.quality][self.key_idx])
        midiRep += 12*self.octave
        midiRep[:self.inversion] += 12 + self.keyOffset
        return sorted(midiRep)


class Key(object):
    def __init__(self, range=[48,72], key='C', quality=MAJ):
        key = 'C' if key not in ALL_KEYS else key
        self.key = key
        self.quality = np.clip(quality, MAJ, MIN)
        self.range = range
        tonic = ALL_KEYS.index(self.key)
        baseChord = Chord(key=ALL_KEYS[tonic%12])
        tones = baseChord._getMidiTones()
        self.octaveOffset = (tones[0] - self.range[0])//12


    def generateChord(self, degree, octave=0, inversion=0):
        degree = np.clip(degree, 1, 7)
        tonic = ALL_KEYS.index(self.key)
        
        if self.quality == MAJ:
            chord_quality = MAJOR_CHORD_QUALITIES[degree-1]
            steps = MAJOR_STEPS[degree-1]
        elif self.quality == MIN:
            chord_quality = MINOR_CHORD_QUALITIES[degree-1]
            steps = MINOR_STEPS[degree-1]
        
        chordKey = ALL_KEYS[(tonic+steps)%12]
        return Chord(key=chordKey, octave=octave-self.octaveOffset, inversion=inversion, quality=chord_quality)
    
    def parsePhrase(self, arr):
        # Pass in dicts with the definitions here. We can automate the dict creating process
        return [self.generateChord(*tup) for tup in arr]

    def __str__(self):
        return "Key-"+self.key

def compare_chords(chord1, chord2):
    return chord1.toString() == chord2.toString()       




        
'''
for i in range(12):
    key = Key(key=ALL_KEYS[i])
    print("\nKey of " + ALL_KEYS[i] + " Major")
    for j in range(1,8):
        print(key.generateChord(j).toString())

#print(MAJOR_CHORDS)   
'''             
