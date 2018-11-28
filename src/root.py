# from kivy.app import App
# from os.path import dirname, join
# from kivy.lang import Builder
# from kivy.properties import NumericProperty, StringProperty, BooleanProperty,\
#     ListProperty
# from kivy.clock import Clock
# from kivy.animation import Animation
# from kivy.uix.screenmanager import Screen, ScreenManager

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
from kivy.graphics import Color, Ellipse, Line, Rectangle, Mesh
from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale, Rotate
# from test.main import RootWidget as GameScreen




class RootWidget(BaseWidget) :
    screens = ['home', 'game', 'reward', 'gameNoTutor']
    def __init__(self):
        super(RootWidget, self).__init__()
        self.widget = None
        # self.sm = ScreenManager(transition=FadeTransition())
    
    def switchScreen(self, screenName):
        incomingWidget = self.generateWidget(screenName)
        if self.widget:
            self.clear_widgets()
        self.widget = incomingWidget
        self.add_widget(self.widget)

    def on_key_down(self, keycode, modifiers):
        # print('keypress')
        if keycode[1] == '1':
            self.switchScreen('home')
        if keycode[1] == '2':
            self.switchScreen('game')
        if keycode[1] == '3':
            self.switchScreen('reward')

        if self.widget:
            self.widget.on_key_down(keycode, modifiers)

    def generateWidget(self, screenName):
        if screenName == 'home':
            return HomeScreen(self.switchScreen)
        elif screenName == 'game':
            return GameScreen(self.switchScreen)
        # elif screenName == 'reward':
        #     return RewardScreen()
        else:
            return HomeScreen(self.switchScreen)
    def on_key_up(self, keycode):
        pass
    def on_update(self):
        pass




class HomeScreen(BaseWidget):

    def __init__(self, callBack):
        super(HomeScreen, self).__init__()
        w = Window.width//3
        buttonSize = (w, w//3)
        buttonAnchor = (3*Window.width//4, Window.height//4)
        titleString = "ChordShed"

        startButton = Button(pos=buttonAnchor, size=buttonSize, filePath="../images/start-game.png", callback=callBack)
        statsButton = Button(pos=(buttonAnchor[0], buttonAnchor[1] - buttonSize[1]), size=buttonSize, filePath="../images/statistics.png", callback=None)
        title = Rectangle(pos=(150, Window.height//2), size=(3*Window.width//4, Window.height//4))
        label = CoreLabel(text=titleString, font_size=56)
        label.refresh()
        text = label.texture
        title.texture = text
        # self.button = Button(filePath="../images/start-game.png", callback=None)
        self.buttons = [startButton, statsButton]
        self.objects = AnimGroup()
        [self.objects.add(button) for button in self.buttons]
        self.canvas.add(Rectangle(size=(Window.width,Window.height)))
        self.canvas.add(self.objects)
        self.canvas.add(Color(*(.05,.28,.1)))
        self.canvas.add(title)
        # self.canvas.add(Ellipse(pos=(50,50), size=(50,50)))
        print('homescreen buttons initialized')
        
    def on_update(self):
        self.objects.on_update()
        # print('homescreenUpdate')

    def on_key_down(self, keycode, modifiers):
        if keycode[1] == 't':
            self.buttons[0].buttonPress()
        
    
    def callback(self):
        print('vallback')


class Button(InstructionGroup):
    activeColor = (.2,.3,.2,.2)
    inactiveColor = (0,0,0, 1)
    def __init__(self, pos=(500,500), size=(500,500), filePath='../images/start-game.png', callback=None):
        super(Button, self).__init__()
        self.cpos= pos
        self.csize=size
        self.filePath= filePath
        self.callback=callback
        self.color = Color(*self.inactiveColor, mode='rgba')

        self.rect = CRectangle(cpos=pos, csize=size)
        self.image = Image(filePath)
        # label = CoreLabel(text=labelString, font_size=20)
        # label.refresh()
        # text = label.texture
        self.rect.texture = self.image.texture
        self.outline = CRectangle(cpos=pos, csize=(size[0] + 2, size[1] + 3))
        self.state = "inactive"
        self.time = 5
        self.timeout = .2

        # self.disactivateAnim = KFAnim((0, *self.activeColor), (self.timeout, *self.inactiveColor))
        # self.activateAnim = KFAnim((0, *self.inactiveColor), (self.timeout, *self.activeColor))
        # self.add(self.color)
        self.add(self.outline)
        # self.add(Color(1,1,1,0))
        self.add(self.rect)

    def buttonPress(self):
        screen = ""
        if 'game' in self.filePath:
            screen = 'game'
        elif 'statistics' in self.filePath:
            screen = 'reward'
        self.callback(screen)
    #     self.color.rgba = self.activeColor
    #     self.time = 0

    def on_update(self, dt):
        # print('buttonOnupdate')
        self.time += dt
        # if self.disactivateAnim.is_active(self.time):
        #     self.color.rgba = self.disactivateAnim.eval(self.time)
        # else:
        #     self.color.rgba = self.inactiveColor

class CRectangle(Rectangle):
    def __init__(self, **kwargs):
        super(CRectangle, self).__init__(**kwargs)
        if 'cpos' in kwargs:
            self.cpos = kwargs['cpos']

        if 'csize' in kwargs:
            self.csize = kwargs['csize']

    def get_cpos(self):
        return (self.pos[0] + self.size[0]/2, self.pos[1] + self.size[1]/2)

    def set_cpos(self, p):
        self.pos = (p[0] - self.size[0]/2 , p[1] - self.size[1]/2)

    def get_csize(self) :
        return self.size

    def set_csize(self, p) :
        cpos = self.get_cpos()
        self.size = p
        self.set_cpos(cpos)

    cpos = property(get_cpos, set_cpos)
    csize = property(get_csize, set_csize)


run(RootWidget)
    

