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
    def __init__(self, name="test", gemSequence=gems, score=100):
        self.gemSequence = gemSequence

        self.gemHits = dict()
        self.score = 0
        self.name = name
        for gem in self.gemSequence:
            self.addGem(gem, math.floor((rand.random()*2) == 0))

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
        chord = gem.chord.toString()
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
    



class SaveData(object):
    def __init__(self, name, gemSequence):
        self.gemSequence = gemSequence
        self.gemHits = dict()
        self.name = gemSequence

    def loadSaves(self):
        try:
            with open(pathToSaves+name, 'r') as saveData:
                for line in saveData.readLines():
                    label, numHit, totalAppearances = line.split(',')
                    self.gemHits[label] = np.array(numHit,totalAppearances)
        except Error as a:
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
        
    def saveFiles(self):
        try:
            with open(pathToSaves+name+".txt", 'w+') as saveData:
                for key, val in self.gemHits.items():
                    string = key + "," + val.join(',')
                    saveData.write(string + "\n")
        except Error as a:
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
        

class ScoreScreen(BaseWidget):
    def __init__(self, scoreCard=ScoreCard(), callBack=None):
        super(ScoreScreen, self).__init__()
        w = Window.width//3
        buttonSize = (w, w//3)
        buttonAnchor = (3*Window.width//4, Window.height//4)
        self.scoreCard = scoreCard
        titleString= "Score Card"
        title = Rectangle(pos=(Window.width//4, 3*Window.height//4), size=(2*Window.width//4, Window.height//5))
        label = CoreLabel(text=titleString, font_size=56)
        label.refresh()
        text = label.texture
        title.texture = text
        self.objects = AnimGroup()
        self.cards = self.generateTiles(self.scoreCard.getAllStrings())
        self.canvas.add(Rectangle(size=(Window.width,Window.height)))
        self.canvas.add(self.objects)
        self.canvas.add(Color(*(.05,.28,.1)))
        self.canvas.add(title)
        [self.objects.add(card) for card in self.cards]
        print('ScoreScreen Initialized')
        
    def generateTiles(self, scoreStrings):
        print(scoreStrings)
        xa,ya = (10,0)
        x = xa
        y = ya
        padding = 10
        tile = Card(scoreStrings[0])

        w,h = tile.getSize()
        outputs = [tile]
        for i in range(1, len(scoreStrings)):
            if i % 5 == 0:
                y += h + padding
                x = xa - w- padding
            x += w + padding
            outputs.append(Card(scoreStrings[i], pos=(x,y), size=(w,h)))
        return outputs

    def on_update(self):
        self.objects.on_update()
        # print('homescreenUpdate')
    
    def on_key_down(self, keycode, modifiers):
        pass








# run(ScoreScreen)