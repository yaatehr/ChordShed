

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
from src.chord import Key, Chord


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
    key_range = [48, 72]
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
        
        if self.info in self.children:
            self.remove_widget(self.info)

        if self.calibrate in self.children:
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
            self.home._generate_keys()
            return self.home
        elif screenName == 'info':
            return InformationPage()
        elif screenName == 'calibrate':
            print()
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
        self.note_detector.reset(hard=True)
        if self._has_midi_input():
            print('has midi input')
            self.midiInput.callback = self.note_detector.callback
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

    def set_keyboard_range(self, key_range):
        chord = Chord(customMidi = key_range)
        self.note_detector.updateTargetChord(chord)
        self.key_range = key_range




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
        self.patterns_dict = {'Pattern 1': patterns, 'Pattern 2': patterns, 'Pattern 3': patterns}
        self.pattern = None
        # Create dropdown for patterns
        ddp_anchor = (Window.width//4 - buttonSize[0]//2, buttonAnchor[1])
        self.mb_p, self.dd_p = create_dropdown(['Select Pattern'] + list(self.patterns_dict), *buttonSize, ddp_anchor)
        self.add_widget(self.mb_p)
        self.dd_p.bind(on_select=self.set_pattern)

        # Load keys information and create dropdown
        self._generate_keys()

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


    def _generate_keys(self):
        if self.parent:
            key_range = self.parent.key_range
        else:
            key_range = [48, 72]

        self.keys_dict = {'A Major': Key(range=key_range, key='A', quality=MAJ), 
                'A#/Bb Major': Key(range=key_range, key='Bb', quality=MAJ), 
                'B Major':     Key(range=key_range, key='B', quality=MAJ), 
                'C Major':     Key(range=key_range, key='C', quality=MAJ), 
                'C#/Db Major': Key(range=key_range, key='C#', quality=MAJ), 
                'D Major':     Key(range=key_range, key='D', quality=MAJ), 
                'D#/Eb Major': Key(range=key_range, key='Eb', quality=MAJ), 
                'E Major':     Key(range=key_range, key='E', quality=MAJ), 
                'F Major':     Key(range=key_range, key='F', quality=MAJ), 
                'F#/Gb Major': Key(range=key_range, key='F#', quality=MAJ), 
                'G Major':     Key(range=key_range, key='G', quality=MAJ), 
                'G#/Ab Major': Key(range=key_range, key='Ab', quality=MAJ),
                
                'A Minor':     Key(range=key_range, key='A', quality=MIN), 
                'A#/Bb Minor': Key(range=key_range, key='Bb', quality=MIN), 
                'B Minor':     Key(range=key_range, key='B', quality=MIN), 
                'C Minor':     Key(range=key_range, key='C', quality=MIN), 
                'C#/Db Minor': Key(range=key_range, key='C#', quality=MIN), 
                'D Minor':     Key(range=key_range, key='D', quality=MIN), 
                'D#/Eb Minor': Key(range=key_range, key='Eb', quality=MIN), 
                'E Minor':     Key(range=key_range, key='E', quality=MIN), 
                'F Minor':     Key(range=key_range, key='F', quality=MIN), 
                'F#/Gb Minor': Key(range=key_range, key='F#', quality=MIN), 
                'G Minor':     Key(range=key_range, key='G', quality=MIN), 
                'G#/Ab Minor': Key(range=key_range, key='Ab', quality=MIN)}
        


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

        self.calibration_note = 0
        self.key_range = [48, 72]

        self.canvas.add(Color(.3,.3,.3))
        self.canvas.add(bg)
        self.gui = None
        # self.canvas.add(self.gui)
        self.calibration_step = 0


        self.info = topleft_label()
        self.add_widget(self.info)
    
    def get_key(self, message):
        if message.type == 'note_on' or message.type == 'note_off':
            self.calibration_note = message.note
            self.parent.note_detector.callback(message)

    def on_update(self):

        if not self.parent:
            return
        if not self.gui:
            self.gui = KeyboardGui(self.parent.note_detector)
            self.canvas.add(self.gui)
        self.gui.on_update(kivyClock.frametime)


        self.info.text = 'Calibrate Your Piano'
        self.info.text += '                 Press "1" to return home'

        if self.calibration_step == 0:
            if not self.parent._has_midi_input():
                self.info.text += '\n\n No Keyboard Connected - Press c to connect'
            else:
                self.info.text += '\n\n Keyboard Connected - Press SPACE to begin calibration'
        elif self.calibration_step == 1:
            self.info.text += '\n\n Press the lowest button on your keyboard then press SPACE to continue'
        elif self.calibration_step == 2:
            self.info.text += '\n\n Press the highest button on your keyboard then SPACE to continue.'
        elif self.calibration_step == 3:
            self.info.text += '\n\n If you\'re happy with the piano gui config, press SPACE to complete calibration'
            self.info.text += '\n Press r to reset'
        else:
            self.calibration_step = 0

    def wizard_step(self):
        print('wizard step - state %d' % self.calibration_step)
        inport = self.parent.midiInput

        if self.calibration_step == 0:
            if self.parent._has_midi_input():
                self.calibration_step += 1
                inport.callback = self.get_key
                return
            else:
                print('NO KEYBOARD DETECTED - restarting the application may help.')
        elif self.calibration_step == 1:
            self.key_range[0] = self.calibration_note
            self.calibration_step += 1
            return
        elif self.calibration_step == 2:
            self.key_range[1] = self.calibration_note
            self.parent.set_keyboard_range(self.key_range)
            self.calibration_step += 1
            return
        elif self.calibration_step == 3:
            self.calibration_step = 0
            inport.callback = self.parent.note_detector.callback
        else:
            inport.callback = self.parent.note_detector.callback
            self.calibration_step = 0

    def restart_wizard(self):
        self.calibration_step = 1
        self.parent.midiInput.callback = self.get_key

    def on_key_down(self, keycode, modifiers):

        if keycode[1] == 'spacebar':
            self.wizard_step()
        
        if keycode[1] == 'r':
            self.restart_wizard()

        if keycode[1] == 'c' and self.midiInput is None:
            self.parent._initialize_controller()
        
        if  keycode[1] == '1':
            return False

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



    
