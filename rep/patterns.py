from rep.gem import Gem

import sys
sys.path.append('..')

from src.chord import Chord, Key


# helper function(s)
def create_bars(pattern, key):
    gem_bars = []
    chord_bars = []
    for bar in pattern:
        chords_and_ticks = [(key.generateChord(b[0]), b[1]) for b in bar]
        gems = [ Gem(chord, beat) for chord, beat in chords_and_ticks ]
        chord_bars.append(chords_and_ticks)
        gem_bars.append(gems)
    return gem_bars, chord_bars


class Pattern(object):
    def __init__(self, pattern, key):
        gem_bars, chord_bars = create_bars(pattern, key)
        self.gems = gem_bars
        self.chords = chord_bars
        self.idx = -1
    
    def reset(self):
        self.idx = -1
        for bar in self.pattern:
            if bar != None:
                for gem in bar:
                    gem.reset()
    
    def next_bar(self):
        self.idx += 1
        return self.pattern[self.idx] != None
        
    def generate_bar(self):
        return self.pattern[self.idx]


# different song patterns
kTest_pattern = ( ((2,2),), ((5,4),), ((1,2),), ((3,1),(6,3)), ((4,2),(1,4)) )


def patternReader(fileInput):
    '''
    Input takes one call (4 bars) per line. Entries will be parse as #chord, #beat
    '''
    output = []
    with open(fileInput, 'r') as inputFile:
        for line in inputFile.readlines():
            tokens = line.strip().split(',')
            pattern = zip(tokens[0::2], tokens[1::2])
            output.append(pattern)


    return output



# declarations of the progressions that will be used in the game
key = Key(key='C')
Test_Pattern = Pattern(kTest_pattern, key)

            
