from rep.gem import Gem



# helper function(s)
def create_gem_pattern(pattern):
    gem_pattern = []
    for bar in pattern:
        gems = [ Gem(b[0],b[1]) for b in bar ]
        gem_pattern.append( tuple(gems) )
    return tuple( gem_pattern ) + tuple([None])


class Pattern(object):
    def __init__(self, pattern):
        self.pattern = create_gem_pattern(pattern)
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
kTest_pattern = ( ((1,2),), ((3,4),), ((3,2),), ((3,1),(3,3)), ((3,2),(3,4)) )





# declarations of the progressions that will be used in the game
Test_Pattern = Pattern(kTest_pattern)

            
