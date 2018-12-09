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

from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button

from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Line, Rectangle, Mesh
from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale, Rotate

#from test.main import MainWidget as GameScreen

#from src.score import ScoreScreen

#from rep.gem import *

from src.buttonwidget import *
from src.crectangle import *

from test.main import MainWidget as Game






GenerateFontSize = lambda w, h : (w*h)**.5 * .2

def create_button(text, size, pos):
    btn = Button(text=text, size=size, pos=pos, size_hint=(None,None))
    font_size = GenerateFontSize(*size)
    btn.font_size = font_size
    return btn, font_size

def create_dropdown(options, width, height, pos):
    dd = DropDown()

    # create a big main button. Calculate the proper height.
    mainbutton, font_size = create_button(options[0], (width, height), pos)
    mainbutton.bind(on_release=dd.open)

    for txt in options[1:]:
        btn = Button(text=txt, size_hint_y=None, height=height, font_size=font_size)
        btn.bind(on_release=lambda btn: dd.select(btn.text))
        dd.add_widget(btn)

    dd.bind(on_select=lambda instance, x: setattr(mainbutton, 'text', x) )

    # return mainbutton (for widget addition) and dropdown (for binding to on_select)
    return mainbutton, dd





class RootWidget(BaseWidget) :
    def __init__(self):
        super(RootWidget, self).__init__()

        self.widget = None
        self.home = HomeScreen()
        self.home_button = ButtonWidget((0, Window.height-40), '../images/home.png', self.switchScreen, 'home')
        self.info = ButtonWidget((40, Window.height-40), '../images/information.png', self.switchScreen, 'info')
        self.add_widget(self.home_button)

        # initialize home screen
        self.switchScreen('home')
    

    def switchScreen(self, screenName):
        '''
        Change screen to specified widget
        Return: None
        '''
        new_widget = self.generateWidget(screenName)
        
        if self.info in self.children:
            self.remove_widget(self.info)

        if self.widget:
            self.remove_widget(self.widget)
            '''
            if isinstance(self.widget, Game):
                self.widget.audio.close() # this crashes
            '''
            self.widget = None
        
        if new_widget:
            if isinstance(new_widget, HomeScreen):
                self.add_widget(self.info)
            self.widget = new_widget
            self.add_widget(self.widget, index=len(self.children)+1)


    def generateWidget(self, screenName):
        '''
        Fetch and return instance of the widget that is to be dislayed
        Returns: Widget() or None
        '''
        if screenName == 'game':
            return Game()
        elif screenName == 'score':
            return ScoreCard()
        elif screenName == 'home':
            return self.home
        elif screenName == 'info':
            return InformationPage()
        print('No screen named:', screenName)
        return self.home


    def on_key_down(self, keycode, modifiers):
        '''
        Hands control over to selected widget, if no selected widget, then it runs the controls
        Returns: None
        '''
        if self.widget: # if we have a widget already running, then pass control onto that widget
            try:
                status = self.widget.on_key_down(keycode, modifiers)
                if status == False:
                    self.switchScreen('home')
            except:
                pass
        
        else: # otherwise run the root controls
            print('Program not active')


    def on_touch_down(self, touch):
        '''Returns: None'''
        for child in self.children:
            try:
                child.on_touch_down(touch)
            except:
                pass
        #print(touch.x, touch.y)


    def on_touch_up(self, touch):
        '''Returns: None'''
        for child in self.children:
            try:
                child.on_touch_up(touch)
            except:
                pass


    def on_update(self):
        '''Returns: None'''
        for child in self.children:
            try:
                child.on_update()
            except:
                pass






class HomeScreen(Widget):
    def __init__(self):
        super(HomeScreen, self).__init__()

        # Create Title Background
        title_img = Image('../images/title-screen.png').texture
        title_screen = Rectangle(pos=(0,0), size=(Window.width, Window.height+10), texture=title_img)
        self.canvas.add(title_screen)
        

        w = Window.width//3
        buttonSize = (w, w//3)
        buttonAnchor = (3*Window.width//4 - buttonSize[0]//2, Window.height//4 - buttonSize[1]//2)

        # Create start button
        start_text = 'Start Game'
        startButton = create_button(start_text, buttonSize, buttonAnchor)[0]
        startButton.bind(on_release=self.switch_to_game_screen)
        self.add_widget(startButton)
        
        # Create stats button
        stats_text = 'Statistics'
        statsButton = create_button(stats_text, buttonSize, (buttonAnchor[0], buttonAnchor[1]-buttonSize[1]))[0]
        statsButton.bind(on_release=self.switch_to_score_card)
        self.add_widget(statsButton)
        

        # Load patterns information and create dropdown
        self.pattern_text = ['Pattern 1', 'Pattern 2', 'Pattern 3']
        self.patterns = [1, 2, 3]
        self.pattern = None
        # Create dropdown for patterns
        ddp_anchor = (Window.width//4 - buttonSize[0]//2, buttonAnchor[1])
        self.mb_p, self.dd_p = create_dropdown(['Select Pattern'] + self.pattern_text, *buttonSize, ddp_anchor)
        self.add_widget(self.mb_p)
        self.dd_p.bind(on_select=self.set_pattern)

        # Load keys information and create dropdown
        self.key_text = ['C', 'D', 'E']
        self.keys = ['CMaj', 'DMaj', 'Emaj']
        self.key = None
        # Create dropdown for keys
        ddk_anchor = (ddp_anchor[0], ddp_anchor[1] - buttonSize[1])
        self.mb_k, self.dd_k = create_dropdown(['Select Key'] + self.key_text, *buttonSize, ddk_anchor)
        self.add_widget(self.mb_k)
        self.dd_k.bind(on_select=self.set_key)

        print('homescreen buttons initialized')


    def set_pattern(self, obj, txt):
        idx = self.pattern_text.index(txt)
        self.pattern = self.patterns[idx]
        print("Pattern changed to:", self.pattern)
        if self.key: # if a key has already been selected
            pass # TODO: Set the key of the pattern that has been loaded


    def set_key(self, obj, txt):
        idx = self.key_text.index(txt)
        self.key = self.keys[idx]
        print("Key changed to:", self.key)
        if self.pattern: # if a pattern has already been accepted
            pass # TODO: Set the key of the pattern that has been loaded


    def switch_to_game_screen(self, button):
        '''Callback to switch to game screen'''
        self.parent.switchScreen('game')


    def switch_to_score_card(self, button):
        '''Callback to switch to stats card'''
        print('running')
        self.parent.switchScreen('score')




'''
class Game(Widget):
    def __init__(self):
        super(Game, self).__init__( size=(Window.width, Window.height) )

        self.color = Color(.1,.2,.3)
        self.canvas.add(self.color)
        self.bg = Rectangle(pos=self.pos, size=self.size)
        self.canvas.add(self.bg)

        self.gem = Gem('t', (Window.width//2, Window.height//2), 50, 5)
        self.canvas.add(self.gem)


    def on_key_down(self, keycode, modifiers):
        if keycode[1] == '2':
            self.gem.activate()
        if keycode[1] == '4':
            self.gem.on_hit()


    def on_reset(self):
        self.gem.on_reset()


    def on_update(self):
        self.gem.on_update( kivyClock.frametime )

    
    def __str__(self):
        return "Game"
'''





class ScoreCard(Widget):
    '''
    Dummy widget for testing basic score card functionality
    '''
    def __init__(self):
        super(ScoreCard, self).__init__(size=(Window.width, Window.height))

        self.info = topleft_label()
        self.add_widget(self.info)
        self.info.text = 'Placeholder'

        crect = CRectangle(cpos=(Window.width//2, Window.height//2), csize=(50,50))
        self.canvas.add(crect)

        self.score_dict = {}


    def load_score_card(self, pattern, key):
        pass


    def on_key_down(self, keycode, modifiers):
        print("No method for this input in W")


    def on_update(self):
        pass


    def __str__(self):
        return "ScoreCard"






class InformationPage(Widget):
    def __init__(self):
        super(InformationPage,  self).__init__(size=(Window.width, Window.height))

        cpos = (self.width//2, self.height//2)
        csize = (self.width, self.height)
        bg = CRectangle(cpos=cpos, csize=csize)
        self.canvas.add(Color(.3,.3,.3))
        self.canvas.add(bg)

        self.info = topleft_label()
        self.add_widget(self.info)
        self.info.text = 'This game is focused on teaching people common chord progressions.'
        self.info.text += '\n\nPress "1" or click the home icon to leave this screen'


    def on_key_down(self, keycode, modifiers):
        if keycode[1] == '1':
            return False




###########################################################
#                                                         #
#               MISCELLANEOUS CLASSES BELOW               # 
#                                                         #
###########################################################





run(RootWidget)



    

