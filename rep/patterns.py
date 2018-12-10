from rep.gem import Gem

import sys
sys.path.append('..')

from src.chord import Chord, Key
from kivy.core.window import Window


def create_bars(pattern, key):
    '''
    Turn tuple syntax into chord,beat , and gem, beat bar tuples
    return (gem_bars, chord_bars)
    '''
    gem_bars = []
    chord_bars = []
    for bar in pattern:
        chords_and_ticks = [(key.generateChord(int(b[0]), inversion = round(10*(b[0]%1))), b[1]) for b in bar]
        gems = [ Gem(chord, (Window.width // 2, Window.height // 2), 50, 1, beat) for chord, beat in chords_and_ticks ]
        chord_bars.append(chords_and_ticks)
        gem_bars.append(gems)
    return gem_bars, chord_bars


def patternReader(fileInput):
    '''
    Input takes one call (4 bars) per line. Entries will be parse as #chord, #beat

    return an Array of tuples
    '''
    output = []
    with open(fileInput, 'r') as inputFile:
        for line in inputFile.readlines():
            tokens = line.strip().split(',')
            tokens = list(map(int, tokens))
            pattern = list(zip(tokens[0::2], tokens[1::2]))
            output.append(pattern)
    return output

# helper function(s)
def create_gem_pattern_old(pattern, key):
    gem_pattern = []
    for bar in pattern:
        gems = [ Gem( key.generateChord(b[0]), (50,50), 50, 1,  b[1]) for b in bar ]
        gem_pattern.append( tuple(gems) )
    return tuple( gem_pattern ) + tuple([None])


class Pattern(object):
    def __init__(self, pattern, key):
        self.pattern = create_gem_pattern_old(pattern, key)
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





# declarations of the progressions that will be used in the game
key = Key(key='C')
Test_Pattern = Pattern(kTest_pattern, key)