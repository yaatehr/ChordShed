import sys
sys.path.append('..')
from common.core import *
from common.audio import *
from common.mixer import *
from common.wavegen import *
from common.wavesrc import *
from common.gfxutil import *
from common.synth import *
from kivy.clock import Clock as kivyClock
from kivy.core.image import Image
from kivy.core.text import Label as CoreLabel
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Rectangle
from rep.gem import Gem
from src.chord import Chord, Key
from rep.patterns import Pattern
from random import Random
import math


pathToSaves = "../local/"
rand = Random()

def getAllGems(pattern):
    output = []
    while pattern.next_bar():
        output.extend(pattern.generate_bar())
    return output




    # different song patterns
kTest_pattern = ( ((2,2),), ((5,4),), ((1,2),), ((3,1),(6,3)), ((4,2),(1,4)), ((2,2),), ((5,4),), ((1,2),), ((3,1),(6,3)) )
# declarations of the progressions that will be used in the game
key = Key(key='C')
Test_Pattern = Pattern(kTest_pattern, key)
gems = getAllGems(Test_Pattern)



class ScoreCard(object):
    '''
    Holds the score for a particular pattern in a particular key
    '''
    def __init__(self, pattern, name="test", gemSequence=gems, score=100):
        self.pattern = pattern # array of array of tuples in format (roman numeral, beat)
        self.bars = [] # array of scores for each bar in the pattern
        # self.notes = [] # list of notes played for each bar in the pattern
        max_score = 0

        for i,bar in enumerate(pattern):
            max_score += len(bar)
            self.bars.append(BarData(i, bar))
        self.total_accuracy = sum([bar.getScore() for bar in self.bars])/max_score
        # self.idx = 0
        self.score = 0
        self.name = name


    def on_chord_miss(self, barIndex, gem, notes=None):
        print('scorecard miss')
        self.bars[barIndex].addChordMiss(gem, notes)

    def on_chord_hit(self, barIndex, gem, notes):
        print('scorecard hit')

        self.bars[barIndex].addChordHit(gem, notes=notes)

    def on_misc_miss(self, barIndex, note):
        print('misc scorehard miss')

        self.bars[barIndex].addMiscMiss(note)

    def perfect_bar(self, barIndex, responsesRemaining):
        print('scorehard perfect')

        self.bars[barIndex].addPerfectBar(responsesRemaining) 

    def setScore(self, score):
        self.score = score
    def getScore(self):
        return self.score
    
    def gemToString(self, key):
        val = self.gemHits[key]
        return key + "\n" + "/".join([str(item) for item in val])
    
    def getAllStrings(self):
        output = []
        for key in self.gemHits.keys():
            output.append(self.gemToString(key))
        print(output)
        return output
        
    def addGem(self, gem, wasHit):
        chord = gem.chord.__str__()
        hit = 0
        total = 0
        if chord in self.gemHits.keys():
            hit, total = self.gemHits[chord]
            if wasHit:
                hit += 1
            total += 1
            self.gemHits[chord] = np.array([hit, total])
        else:
            if wasHit:
                hit += 1
            total += 1
            self.gemHits[chord] = np.array([hit, total])
    


class BarData(object):
    '''
    Abstraction for the score data of each bar
    '''
    beatsPerMeasure = 4

    def __init__(self, index, barPattern):
        self.noteMisses = dict()
        self.chordHits = dict()
        for degree, beat in barPattern:
            self.noteMisses[beat] = dict()
            self.chordHits[beat] = dict()

        self.numGems = self.chordHits.keys()
        self.noteMisses[-1] = dict() # for miscelaneous misses
        self.score = 0

    def addChordMiss(self, gem, notes):
        print('chord miss ', notes)
        if isinstance(notes, int):
            note = notes
            if note in self.noteMisses.keys():
                self.noteMisses[gem.beat][note] += 1
            else:
                self.noteMisses[gem.beat][note] = 1
            self.score -= 10
        elif isinstance(notes, list):
            for note in notes:
                if note in self.noteMisses.keys():
                    self.noteMisses[gem.beat][note] += 1
                else:
                    self.noteMisses[gem.beat][note] = 1
                self.score -= 10
        elif isinstance(notes, tuple):
            #they have already been penalized for individual
            correct, incorrect = notes
            if len(correct):
                self.addChordHit(gem, correct)
            if len(incorrect):
                self.addChordMiss(gem, incorrect)

    def addChordHit(self, gem, notes=None):
        print('chord hit ', notes)

        if not notes:
            for note in gem._getMidiNotes():
                self.chordHits[gem.beat]
        else:
            for note in notes:
                if note in self.chordHits.keys():
                    self.chordHits[gem.beat][note] += 1
                else:
                    self.chordHits[gem.beat][note] = 1
        self.score += 100

    def addMiscMiss(self, note):
        self.score -= 10
        if note in self.noteMisses[-1].keys():
            self.noteMisses[-1][note] += 1
        else:
            self.noteMisses[-1][note] = 1

    def addPerfectBar(self, responsesRemaining):
        print('perfect bar! ', notes)

        for beat in self.chordHits.keys():
            for note in self.chordHits[beat].keys():
                self.chordHits[beat][note] = responsesRemaining + 1
        self.score += 100*(responsesRemaining*self.numGems)*1.5 + 100

    def getHistogram(self, beat, showMisc=False):
        '''
        return a histogram with form
        dict[note] = [hits, totalAppearances]
        '''
        noteMisses = self.noteMisses[beat]
        noteHits = self.chordHits[beat]
        missedKeys = noteMisses.keys()
        hitKeys = noteHits.keys()
        histogram = dict()
        for key in missedKeys.intersection(hitKeys):
            entry = [0,0]
            if key in missedKeys:
                entry[1] = noteMisses[key]
            if key in hitKeys:
                entry[0] = noteHits[key]
                entry[1] += noteHits[key]
            histogram[key] = entry
        return histogram 

    def getScore(self):
        return self.score

class SaveData(object):
    def __init__(self, name, gemSequence):
        self.gemSequence = gemSequence
        self.gemHits = dict()
        self.name = name

    def loadSaves(self):
        try:
            with open(pathToSaves+self.name, 'r') as saveData:
                for line in saveData.readLines():
                    label, numHit, totalAppearances = line.split(',')
                    self.gemHits[label] = np.array(numHit,totalAppearances)
        except Exception as a:
            print(a)
    
    def gemAverages(self):
        output = []
        for key, val in self.gemHits.items():
            output.append((key, val[0]/val[1]))
    
    def addScoreCard(self, card):
        if card.name != self.name:
            return print('INCOMPATIBLE SONGS')
        for key, val in card.gemHits.items():
            self.gemHits[key] += val
        
    def clear(self):
        self.gemHits = dict()
        
    def saveFiles(self):
        try:
            with open(pathToSaves + self.name +".txt", 'w+') as saveData:
                for key, val in self.gemHits.items():
                    string = key + "/".join([str(item) for item in val])
                    saveData.write(string + "\n")
        except Exception as a:
            print(a)
    




class Card(InstructionGroup):
    backColor = (.8, .7, .8, .7)

    def __init__(self, labelString, pos=(0,0), size=((Window.width-6*10)//5,Window.height//3)):
        super(Card, self).__init__()
        self.pos= pos
        self.size=size
        self.color = Color(*self.backColor, mode='rgba')
        self.outline = Rectangle(pos=pos, size=size)
        self.rect = Rectangle(pos=pos, size=size)
        label = CoreLabel(text=labelString, font_size=62)
        label.refresh()
        self.rect.texture = label.texture
        self.add(self.color)
        self.add(self.outline)
        self.add(Color(*(0,0,0)))
        self.add(self.rect)
    def getSize(self):
        return self.size

    def on_update(self, dt):
        pass
        # print('homescreenUpdate')
        

# class ScoreScreen(BaseWidget):
#     def __init__(self, scoreCard=ScoreCard(), callBack=None):
#         super(ScoreScreen, self).__init__()
#         w = Window.width//3
#         buttonSize = (w, w//3)
#         buttonAnchor = (3*Window.width//4, Window.height//4)
#         self.scoreCard = scoreCard
#         titleString= "Score Card"
#         title = Rectangle(pos=(Window.width//4, 3*Window.height//4), size=(2*Window.width//4, Window.height//5))
#         label = CoreLabel(text=titleString, font_size=56)
#         label.refresh()
#         text = label.texture
#         title.texture = text
#         self.objects = AnimGroup()
#         self.cards = self.generateTiles(self.scoreCard.getAllStrings())
#         self.canvas.add(Rectangle(size=(Window.width,Window.height)))
#         self.canvas.add(self.objects)
#         self.canvas.add(Color(*(.05,.28,.1)))
#         self.canvas.add(title)
#         [self.objects.add(card) for card in self.cards]
#         print('ScoreScreen Initialized')
        
#     def generateTiles(self, scoreStrings):
#         print(scoreStrings)
#         xa,ya = (10,0)
#         x = xa
#         y = ya
#         padding = 10
#         tile = Card(scoreStrings[0])

#         w,h = tile.getSize()
#         outputs = [tile]
#         for i in range(1, len(scoreStrings)):
#             if i % 5 == 0:
#                 y += h + padding
#                 x = xa - w- padding
#             x += w + padding
#             outputs.append(Card(scoreStrings[i], pos=(x,y), size=(w,h)))
#         return outputs

#     def on_update(self):
#         self.objects.on_update()
#         # print('homescreenUpdate')
    
#     def on_key_down(self, keycode, modifiers):
#         pass








# run(ScoreScreen)