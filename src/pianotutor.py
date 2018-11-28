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
    activeColor = (.2,.3,.2,.2)
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
        self.state = "inactive"
        self.time = 5
        self.timeout = .2

        self.disactivateAnim = KFAnim((0, *self.activeColor), (self.timeout, *self.inactiveColor))
        self.activateAnim = KFAnim((0, *self.inactiveColor), (self.timeout, *self.activeColor))
        self.rect = Rectangle(pos=self.anchor, size=size)
        self.add(self.color)
        self.add(self.rect)

    def keyPress(self):
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
    def __init__(self, note_detector):
        super(KeyboardGui, self).__init__()
        self.numOctaves = 2
        self.keys = []
        # self.blackKeys = []
        self.keyWidth = 50
        self.anchor = (100, Window.height*(6.0/8))
        self.objects = AnimGroup()
        self.initializeFrame()
        self.add(self.objects)
        self.initializeKeys()
        self.noteDetector = note_detector

    def updateGui(self):
        activeKeys = [x%(12*self.numOctaves) for x in self.noteDetector.getActiveNotes()]
        # print(activeKeys)
        for index in activeKeys:
            self.keys[index].keyPress()

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





