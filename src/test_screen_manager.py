

import sys
sys.path.append('..')
import mido

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
from src.pianotutor import KeyboardGui
from src.notedetector import NoteDetector

from src.buttonwidget import *
from src.crectangle import *

from test.main import MainWidget as Game
from test.main import patterns
from src.chord import Key


from time import sleep


MAJ = 0
MIN = 1
AUG = 2
DIM = 3



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
    midiInput = None
    mixer = Mixer()
    playerSynth = Synth('../data/FluidR3_GM.sf2')
    def __init__(self):
        super(RootWidget, self).__init__()
        # config
        self.audio = Audio(2)
        self.audio.set_generator(self.mixer)
        self.mixer.add(self.playerSynth)
        self.note_detector = NoteDetector(self.playerSynth)

        self.home = HomeScreen()

        self.home_button = ButtonWidget((0, Window.height-40), '../images/home.png', self.switchScreen, 'home')
        self.info = ButtonWidget((40, Window.height-40), '../images/information.png', self.switchScreen, 'info')
        self.calibrate = ButtonWidget((80, Window.height-40), '../images/piano.png', self.switchScreen, 'calibrate')
        



        self.add_widget(self.home_button)
        # save state and initialize home screen
        self.widget = None
        self.switchScreen('home')
        self.pattern = None
        self.key = None
    

    def switchScreen(self, screenName, **kwargs):
        '''
        Change screen to specified widget
        Return: None
        '''
        self._initialize_controller()
        new_widget = self.generateWidget(screenName, **kwargs)
        
        if self.info in self.children and self.calibrate in self.children:
            self.remove_widget(self.info)
            self.remove_widget(self.calibrate)

        if self.widget:
            self.remove_widget(self.widget)
            del self.widget
            self.widget = None
        
        if new_widget:
            if isinstance(new_widget, HomeScreen):
                self.add_widget(self.info)
                self.add_widget(self.calibrate)
            self.widget = new_widget
            self.add_widget(self.widget, index=len(self.children)+1)


    def generateWidget(self, screenName, **kwargs):
        '''
        Fetch and return instance of the widget that is to be dislayed
        Returns: Widget() or None
        '''
        if screenName == 'game':
            if not self._has_midi_input():
                return self.home
            if 'pattern' in kwargs and 'key' in kwargs:
                print(kwargs['pattern'])
                return Game( masterPattern=kwargs['pattern']\
                    , key=kwargs['key']\
                    , noteDetector=self.note_detector\
                    , mixer=self.mixer)

            
        elif screenName == 'score':
            return ScoreCard()
        elif screenName == 'home':
            return self.home
        elif screenName == 'info':
            return InformationPage()
        elif screenName == 'calibrate':
            return PianoCalibrator()
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
        self.audio.on_update()
        for child in self.children:
            try:
                child.on_update()
            except:
                pass


    def _initialize_controller(self):
        if self._has_midi_input():
            print('has midi input')
            return True
        inport = None
        try: 
            inport = mido.open_input(virtual=False, callback=self.note_detector.callback)
            print('port initialized')
        except Exception as e:
            print('no input attached ', e)
            return False

        self.midiInput = inport
        return True
    

    def _has_midi_input(self):
        return self.midiInput is not None




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
        self.patterns_dict = {'Pattern 1': patterns, 
                              'Pattern 2': patterns, 
                              'Pattern 3': patterns}
        self.pattern = None
        # Create dropdown for patterns
        ddp_anchor = (Window.width//4 - buttonSize[0]//2, buttonAnchor[1])
        self.mb_p, self.dd_p = create_dropdown(['Select Pattern'] + list(self.patterns_dict), *buttonSize, ddp_anchor)
        self.add_widget(self.mb_p)
        self.dd_p.bind(on_select=self.set_pattern)

        # Load keys information and create dropdown
        self.keys_dict = {'A Major':     Key(key='A', quality=MAJ), 
                          'A#/Bb Major': Key(key='Bb', quality=MAJ), 
                          'B Major':     Key(key='B', quality=MAJ), 
                          'C Major':     Key(key='C', quality=MAJ), 
                          'C#/Db Major': Key(key='C#', quality=MAJ), 
                          'D Major':     Key(key='D', quality=MAJ), 
                          'D#/Eb Major': Key(key='Eb', quality=MAJ), 
                          'E Major':     Key(key='E', quality=MAJ), 
                          'F Major':     Key(key='F', quality=MAJ), 
                          'F#/Gb Major': Key(key='F#', quality=MAJ), 
                          'G Major':     Key(key='G', quality=MAJ), 
                          'G#/Ab Major': Key(key='Ab', quality=MAJ),
                          
                          'A Minor':     Key(key='A', quality=MIN), 
                          'A#/Bb Minor': Key(key='Bb', quality=MIN), 
                          'B Minor':     Key(key='B', quality=MIN), 
                          'C Minor':     Key(key='C', quality=MIN), 
                          'C#/Db Minor': Key(key='C#', quality=MIN), 
                          'D Minor':     Key(key='D', quality=MIN), 
                          'D#/Eb Minor': Key(key='Eb', quality=MIN), 
                          'E Minor':     Key(key='E', quality=MIN), 
                          'F Minor':     Key(key='F', quality=MIN), 
                          'F#/Gb Minor': Key(key='F#', quality=MIN), 
                          'G Minor':     Key(key='G', quality=MIN), 
                          'G#/Ab Minor': Key(key='Ab', quality=MIN)}
        

        ALL_KEYS = ['C', 'C#', 'D', 'Eb', 'E', "F", 'F#', 'G', 'Ab', 'A', 'Bb', 'B']

        self.key = None
        # Create dropdown for keys
        ddk_anchor = (ddp_anchor[0], ddp_anchor[1] - buttonSize[1])
        self.mb_k, self.dd_k = create_dropdown(['Select Key'] + list(self.keys_dict), *buttonSize, ddk_anchor)
        self.add_widget(self.mb_k)
        self.dd_k.bind(on_select=self.set_key)

        print('homescreen buttons initialized')


    def set_pattern(self, obj, txt):
        self.pattern = self.patterns_dict[txt]
        print("Pattern changed to:", self.pattern)


    def set_key(self, obj, txt):
        self.key = self.keys_dict[txt]
        print("Key changed to:", self.key)


    def switch_to_game_screen(self, button):
        '''Callback to switch to game screen'''
        if self.pattern and self.key:
            self.parent.switchScreen('game', pattern=self.pattern, key=self.key)
        else:
            print('Please select a pattern and a key signature')


    def switch_to_score_card(self, button):
        '''Callback to switch to stats card'''
        print('running')
        self.parent.switchScreen('score')






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






class PianoCalibrator(Widget):
    def __init__(self):
        super(PianoCalibrator, self).__init__(size=(Window.width, Window.height))

        cpos = (self.width//2, self.height//2)
        csize = (self.width, self.height)
        bg = CRectangle(cpos=cpos, csize=csize)

        self.canvas.add(Color(.3,.3,.3))
        self.canvas.add(bg)
        self.gui = KeyboardGui(self.parent.note_detector)
        self.canvas.add(self.gui)
        self.calibration_step = 0


        self.info = topleft_label()
        self.add_widget(self.info)


    def on_key_down(self, keycode, modifiers):
        if keycode[1] == '1':
            return False


    def on_update(self):
        self.info.text = 'Piano Calibration'
        self.info.text += '\t\tPress "1" to return home'

        if self.calibration_step == 0:
            if self.parent._had_midi_input():
                self.info.text += '\n\n No Keyboard Connected - Press c to connect'
            else:
                self.info.text += '\n\n Keyboard Connected - Press SPACE to begin calibration'
        elif self.calibration_step == 1:
            self.info.text += '\n\n Press the lowest button on your keyboard'
        elif self.calibration_step == 2:
            pass







class SavedGameData(object):
    def __init__(self, pattern, scores, notes):
        self.pattern = pattern # array of array of tuples in format (roman numeral, beat)
        self.scores = scores # array of scores for each bar in the pattern
        self.notes = notes # list of notes played for each bar in the pattern

        max_score = sum([len(bar) for bar in pattern])
        self.total_accuracy = sum(self.scores)/max_score

        self.idx = 0


    def add_notes_and_score(self, notes, score):
        self.notes.append(notes)
        self.scores.append(score)


    def generate_bar_info(self):
        bar = self.pattern[self.idx]
        bar_accuracy = self.score[self.idx]/len(bar)
        bar_notes = self.notes[self.idx]
        return tuple(bar, bar_accuracy, bar_notes)


    def generate_next_bar(self):
        if self.idx + 1 < len(self.pattern):
            self.idx += 1
            self.generate_bar_info()


    def generate_previous_bar(self):
        if self.idx - 1 >= 0:
            self.idx -= 1
            self.generate_bar_info()




class ScoreCard(Widget):
    def __init__(self, all_patterns, all_keys, note_detector)
        super(ScoreCard, self).__init__()

###########################################################
#                                                         #
#               MISCELLANEOUS CLASSES BELOW               # 
#                                                         #
###########################################################


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


run(RootWidget)



    

