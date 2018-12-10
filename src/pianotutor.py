import sys
sys.path.append('..')

from common.core import *
from common.gfxutil import *
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Rectangle



class GuiKey(InstructionGroup):
    '''
    Key class, keys are drawn from the top down.
    '''
    activeColor = (.2,.3,.2,.5)
    correctColor = (.15,.86,.3, .5)
    incorrectColor = (1,.3,.5,.5)
    highlightColor = (1,1,0,.6)

    white = (1,1,1, 1)
    black = (0,0,0, 1)

    def __init__(self, keyWidth=15, blackKey=False, pos=(0,0)):
        super(GuiKey, self).__init__()
        size = (keyWidth, 6*keyWidth)
        pos = (pos[0], pos[1]-size[1]) #flip y down the width of the key
        
        self.anchor = pos

        if blackKey:
             self.inactiveColor = self.black
        else:
            self.inactiveColor = self.white

        self.color = Color(*self.inactiveColor, mode='rgba')
        # self.state = "inactive"
        self.time = 5
        self.timeout = .2

        self.disactivateAnim = KFAnim((0, *self.activeColor), (self.timeout, *self.inactiveColor))
        self.activateAnim = KFAnim((0, *self.inactiveColor), (self.timeout, *self.activeColor))
        self.rect = Rectangle(pos=self.anchor, size=size)
        self.add(self.color)
        self.add(self.rect)

    def setKeyRgba(self, num, denom):
        self.activeColor = [*self.correctColor]
        self.activeColor[3] = num/denom
        self.color.rgba = self.activeColor

    def keyPress(self, correct= False, manualPress=False, showCase = False):
        if showCase:
            self.disactivateAnim = KFAnim((0, *self.activeColor), (self.timeout, *self.inactiveColor))
            self.activateAnim = KFAnim((0, *self.inactiveColor), (self.timeout, *self.activeColor))
            return
        if correct:
            self.activeColor = self.correctColor
            self.disactivateAnim = KFAnim((0, *self.activeColor), (self.timeout, *self.inactiveColor))
            self.activateAnim = KFAnim((0, *self.inactiveColor), (self.timeout, *self.activeColor))
        elif manualPress:
            self.activeColor = self.incorrectColor
            self.disactivateAnim = KFAnim((0, *self.activeColor), (self.timeout, *self.inactiveColor))
            self.activateAnim = KFAnim((0, *self.inactiveColor), (self.timeout, *self.activeColor))
        else:
            self.activeColor = self.highlightColor
            self.disactivateAnim = KFAnim((0, *self.activeColor), (self.timeout, *self.inactiveColor))
            self.activateAnim = KFAnim((0, *self.inactiveColor), (self.timeout, *self.activeColor))
            
        self.color.rgba = self.activeColor
        self.time = 0

    def on_update(self, dt):
        self.time += dt

        if self.disactivateAnim.is_active(self.time):
            self.color.rgba = self.disactivateAnim.eval(self.time)
        else:
            self.color.rgba = self.inactiveColor
        

class KeyboardGui(InstructionGroup):
    blackKey = [True, True, False, True, True, True, False]
    borderColor = (.5,.5,.5,1)
    padding = 10
    def __init__(self, note_detector=None):
        super(KeyboardGui, self).__init__()
        self.numOctaves = 2
        self.keys = []
        # self.blackKeys = []
        self.keyWidth = 50
        self.anchor = (100, Window.height*(0.27))
        self.objects = AnimGroup()
        self.initializeFrame()
        self.add(self.objects)
        self.initializeKeys()
        self.noteDetector = note_detector
        self.previewNotes = None
        self.previewPattern = None
        self.index = 0

    def updateGui(self):
        if not self.noteDetector:
            return
        highlights = self.noteDetector.targetMidi
        correct, incorrect = self.noteDetector.getActiveNotes()

        [self.keys[x%(12*self.numOctaves)].keyPress(correct=True, manualPress=True) for x in correct]
        [self.keys[x%(12*self.numOctaves)].keyPress(correct=False, manualPress=True) for x in incorrect]

        if highlights:
            # print(highlights)
            for note in highlights:
                if note not in correct + incorrect:
                    self.keys[note%(12*self.numOctaves)].keyPress()


    def setPreviewNotes(self, notes, pattern):
        self.previewNotes = notes
        self.previewPattern = pattern


    def preivew(self):

        [key.on_update(100) for key in self.keys] # timeout all the keys
        if not self.previewNotes:
            self.index = 0
            return

        currentDict = self.previewNotes[self.index]
        for note in currentDict.keys():
            if note in self.previewPattern[self.index]:
                num, denom = self.currentDict[note]
                self.keys[x%(12*self.numOctaves)].keyPress(correct=True, manualPress=True)
            else:
                num, denom = self.currentDict[note]
                self.keys[x%(12*self.numOctaves)].keyPress(correct=False, manualPress=True)
        
        self.index += 1
        self.index%= len(self.previewNotes.keys())


    def initializeKeys(self):
        padding = 10
        blackKeys = []
        x, y = self.anchor
        for i in range(7*self.numOctaves):
            key = GuiKey(pos=(x,y), keyWidth=self.keyWidth)
            self.keys.append(key)
            self.objects.add(key)
            if self.blackKey[i%7]:
                blackKey = GuiKey(blackKey=True, pos=(x + self.keyWidth - self.padding,y), keyWidth=self.keyWidth//1.7)
                blackKeys.append(blackKey)
                self.keys.append(blackKey)
            x += self.keyWidth + self.padding
        
        #layer black keys on top
        for key in blackKeys:
            self.objects.add(key)

    def initializeFrame(self):
        width = self.numOctaves*7*(self.keyWidth+self.padding) - self.padding
        height = self.keyWidth*6
        borderWidth = 20
        x,y = self.anchor
        y -= height
        self.color = Color(*self.borderColor, mode="rgb")
        self.add(self.color)
        topRect = Rectangle(pos=(x, y+height), size=(width, borderWidth))
        botRect = Rectangle(pos=(x, y-borderWidth), size=(width, borderWidth))
        leftRect = Rectangle(pos=(x-borderWidth, y-borderWidth), size=(borderWidth, height+2*borderWidth))
        rightRect = Rectangle(pos=(x+width, y-borderWidth), size=(borderWidth, height+2*borderWidth))
        self.border = [topRect, botRect, leftRect, rightRect]
        [self.add(x) for x in self.border]

    def on_update(self, dt=None):
        self.objects.on_update()
        self.updateGui()





