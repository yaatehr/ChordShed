from kivy.app import App
from os.path import dirname, join
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, BooleanProperty,\
    ListProperty
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.screenmanager import Screen



def widgetGenerator(screenName):
    if screenName == 'home':
        return HomeScreen()
    elif screenName == 'game':
        return GameScreen()
    elif screenName == 'reward'
        return rewardScreen()
    else return HomeScreen()


class RootWidget(BaseWidget):
    screens = ['home', 'game', 'reward', 'gameNoTutor']
    def __init__(self):
        super(RootWidget, self).__init__()
        self.widgets = None
    
    def switchScreen(self, screenName):
        self.widgets = widgetGenerator(screenName)