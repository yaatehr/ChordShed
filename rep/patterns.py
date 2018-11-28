from rep.gem import Gem

import sys
sys.path.append('..')

from src.chord import Chord, Key


# helper function(s)
def create_gem_pattern(pattern, key):
    gem_pattern = []
    for bar in pattern:
        gems = [ Gem( key.generateChord(b[0]), b[1] ) for b in bar ]
        gem_pattern.append( tuple(gems) )
    return tuple( gem_pattern ) + tuple([None])


class Pattern(object):
    def __init__(self, pattern, key):
        self.pattern = create_gem_pattern(pattern, key)
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

            
