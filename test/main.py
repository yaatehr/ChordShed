

import mido
import sys
sys.path.append('..')
from common.core import *
from common.audio import *
from common.mixer import *
from common.wavegen import *
from common.wavesrc import *
from common.gfxutil import *
from common.synth import *

from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics import PushMatrix, PopMatrix, Translate, Scale, Rotate
from kivy.clock import Clock as kivyClock

from kivy.core.window import Window
from kivy.core.text import Label as CoreLabel


from rep.nowbar import NowBar
from rep.gembar import GemBar
from rep.gem import Gem
from rep.gamedisplay import GameDisplay
from rep.player import Player
from src.notedetector import NoteDetector
from src.pianotutor import KeyboardGui

from rep.constants import *
from rep.patterns import *

import random
import numpy as np
import bisect




class MainWidget(BaseWidget) :
    def __init__(self, callback=None):
        super(MainWidget, self).__init__()
        
        #self.bg = Rectangle(pos=(0,0), size=(Window.width, Window.height), color=Color(*(1,1,1)) )
        #self.canvas.add(self.bg)
        
        #Audio
        self.audio = Audio(2)
        self.playerSynth = Synth('../data/FluidR3_GM.sf2')
        self.audio.set_generator(self.playerSynth)
        self.clock= Clock()

        nd = NoteDetector(self.playerSynth)
        kg = KeyboardGui(nd)

        self.detector = nd

        # Create Gem Bar over which our Now Bar cursor will scroll
        gb = GemBar()
        
        # Create Now Bar to scroll across Gem Bar
        nb = NowBar(100)
        #self.canvas.add(self.nb)
        self.clock = Clock()
        self.ticker = Ticker(self.pattern, key, self.clock)

        # gm = GameDisplay(nb, gb, nd, kg)
        self.canvas.add(gm)
        
        self.player = Player(nb, gm, self.ticker, self.clock, nd.updateTargetChord)
        self.detector.initializePlayer(self.player)

        # self.callback = callBack
        
        #midi input state
        self.midiInput = None
        self.info = topleft_label()
        self.add_widget(self.info)

        self.switchScreens = callback



        '''
        # set up audio
        self.audio = AudioController(fp_mtaf)
        
        # get song data
        self.song_data = SongData()
        self.song_data.read_data(fp_mtaf_solo, fp_mtaf_bg)
        
        # set up game display
        self.display = BeatMatchDisplay( (self.song_data.barlines, self.song_data.gems) )
        self.canvas.add(self.display)
        
        # create player instance
        self.player = Player(self.song_data, self.display, self.audio)
        
        # keep state
        self.paused = True
    '''
    def initialize_controller(self):
        if self.hasMidiInput():
            return True
        inport = None
        try: 
            inport = mido.open_input(virtual=False, callback=self.detector.callback)
            print('port initialized')
        except Exception as e:
            return False
            print('no input attached ', e)
        self.midiInput = inport
        return True

    def hasMidiInput(self):
        return self.midiInput is not None

    def on_key_down(self, keycode, modifiers):
        if keycode[1] == 't':
            self.player.load_pattern(Test_Pattern)
            print('loading stuff')
            
        elif keycode[1] == 'p':
            self.player.pause_game()
            
        elif keycode[1] == 'o':
            self.player.play_game()

        elif keycode[1] == 'c' and self.midiInput is None:
            self.initialize_controller()
            # self.playerSynth.start()

        # else:
        #     self.player.on_input(keycode[1])
        
    
    def on_update(self) :
        self.player.on_update()
        self.audio.on_update()
        # check for midi input and add onscreen indicator

        if self.hasMidiInput():
            self.info.text = "\nKeyboard Connected"
        else:
            self.info.text = "\nNO Keyboard Found"


        # update personal clock
        # self.t += kivyClock.frametime
        '''
        if not self.paused:
            self.player.on_update()
        
        self.info.text = '"More Than A Feelng" - Boston'
        self.info.text += '\nSCORE: %d' %(self.player.score) +'    %.2f / 5 STARS' %(self.player.score/34700) # 34700 is max score, in this case 5 stars is a perfect score
        
        if self.paused:
            self.info.text += '\n~PAUSED~ (press "P" to resume)'
        else:
            self.info.text += '\n\npress "P" to pause'
        '''
        








'''
# creates the Audio driver
# creates a song and loads it with solo and bg audio tracks
# creates snippets for audio sound fx
class AudioController(object):
    def __init__(self, song_path):
        super(AudioController, self).__init__()
        self.audio = Audio(2)
        self.mixer = Mixer()
        self.audio.set_generator(self.mixer)
        
        self.bg = WaveGenerator( WaveFile(song_path + "bg.wav") ) 
        self.solo = WaveGenerator( WaveFile(song_path + "solo.wav") )
        
        self.mixer.add(self.bg)
        self.mixer.add(self.solo)
        
        self.fp_sfx = "../gh-audio/GuitarHeroIIIMissedNoteSoundEffects.wav"
        self.sfx_start = int(.7 * 44100)
        self.sfx_dur = int(.3 * 44100)

    # start / stop the song
    def toggle(self):
        self.bg.play_toggle()
        self.solo.play_toggle()

    # mute / unmute the solo track
    def set_mute(self, mute):
        self.solo.set_gain(int(not mute))

    # play a sound-fx (miss sound)
    def play_sfx(self):
        
        sfx = WaveGenerator( WaveBuffer(self.fp_sfx, self.sfx_start, self.sfx_dur) )
        self.mixer.add(sfx)

    # needed to update audio
    def on_update(self):
        self.audio.on_update()




def lines_from_file(filename):
    fo = open(filename)
    text = fo.readlines()
    fo.close()
    return text
   
def tokens_from_line(line):
    return line.strip('\n ').split('\t')


def make_gems(regions_path):
    # parses through the lines from the annotation file for the gems
    # returning a dictionary categorizing onsets by their respective lanes
    onsets = {0:[], 1:[], 2:[], 3:[], 4:[]}
    lines = lines_from_file(regions_path)
    lines = [tokens_from_line(line) for line in lines]
    for line in lines:
        time = float(line[0])
        lane = int(line[1])
        onsets[lane].append(time)
    return onsets

def make_barlines(regions_path):
    # parses through lines from annotation file for the barlines
    # returing a list of times corresponding to each barline
    downbeats = []
    lines = lines_from_file(regions_path)
    lines = [tokens_from_line(line) for line in lines]
    for line in lines:
        time = float(line[0])
        downbeats.append(time)
    return downbeats
    




# holds data for gems and barlines.
class SongData(object):
    def __init__(self):
        super(SongData, self).__init__()
        
        self.gems = None 
        self.barlines = None 
        
    # read the gems and song data. You may want to add a secondary filepath
    # argument if your barline data is stored in a different txt file.
    def read_data(self, filepath_gems, filepath_barlines):
    # TODO: figure out how gem and barline data should be accessed...
        self.gems = make_gems(filepath_gems)
        self.barlines = make_barlines(filepath_barlines)


# display for a single gem at a position with a color (if desired)
class GemDisplay(InstructionGroup):
    def __init__(self, xpos, color, time):
        super(GemDisplay, self).__init__()
        
        # add color
        self.color = Color(*color)
        self.add(self.color)
        
        # draw the gem and save position
        self.pos = np.array((xpos, 0))
        self.shape = CEllipse(cpos = self.pos)
        self.shape.csize = (45, 45)
        self.add(self.shape)
        
        # let us know if it hasn't passed the nowbar yet
        self.active = True
        
        # save time
        self.t_g = time # keep track of gem's place in song
        self.t = 0 
        
        self.on_update(kivyClock.frametime)

    # change to display this gem being hit
    def on_hit(self):
        # make inactive to remove from canvas
        self.active = False

    # change to display a passed gem
    def on_pass(self):
        # change to red if the gem is not hit, and then make inactive
        self.color.rgb = (1,.25,.25)

    # find out if the gem is on the screen, if so then we will draw it
    def on_screen(self):
        return True if Y_nb-30 < self.pos[1] <= Window.height else False

    # useful if gem is to animate
    def on_update(self, dt):
        # update position of gem based on time of gem in song and current time
        self.pos[1] = dy/DT * (self.t_g - self.t) + Y_nb
        self.shape.cpos = tuple(self.pos) # update position
        self.t += dt # update time
        return self.active and self.on_screen() # if off screen or inactive, remove from canvas

     
class BarLine(InstructionGroup):
    def __init__(self, time):
        super(BarLine, self).__init__()
        
        # use grey barline
        self.add( Color(.5,.5,.5) )
        
        # draw the barline
        self.line = Line(width = 2.5)
        self.add(self.line)
        
        # save time
        self.t_g = time # same as gem
        self.t = 0
        
        self.ypos = None
        self.on_update(kivyClock.frametime)
        
    def update_pos(self, new_ypos):
        # update the barline to its new y position
        # x should NOT change
        self.line.points = (X1, new_ypos, X2, new_ypos)
        self.ypos = new_ypos
    
    # find out if the barline is on screen, if so we will draw it
    def on_screen(self):
        return True if Y_nb-30 < self.ypos <= Window.height else False
        
    def on_update(self, dt):
        # return whether the bar is active or inactive
        new_ypos = dy/DT * (self.t_g - self.t) + Y_nb
        self.update_pos(new_ypos)
        self.t += dt
        return self.on_screen() 


# Displays one button on the nowbar
class ButtonDisplay(InstructionGroup):
    def __init__(self, pos, color):
        super(ButtonDisplay, self).__init__()

        # add color
        self.rgb = color
        self.color = Color(*self.rgb)
        self.add(self.color)
        
        # draw the button
        self.button = CEllipse(cpos = pos)
        self.button.csize = (50, 50)
        self.add(self.button)

    # displays when button is down (and if it hit a gem)
    def on_down(self, hit):
        self.color.rgb = (int(not hit), int(hit), 0)

    # back to normal state
    def on_up(self):
        self.color.rgb = self.rgb


# Displays and controls all game elements: Nowbar, Buttons, BarLines, Gems.
class BeatMatchDisplay(InstructionGroup):
    def __init__(self, gem_data):
        super(BeatMatchDisplay, self).__init__()
        
        # manage drawing, animation, and object lifetime management
        self.objects = AnimGroup() # automate removal of off-screen gems and barlines
        self.add(self.objects)
        self.not_on_screen = [] # must update things that are not being drawn on the screen
        
        # draw the now bar
        self.nowbar = Line(width = 5)
        self.nowbar.points = (X1, Y_nb, X2, Y_nb)
        self.add(self.nowbar)
        
        # create the 5 buttons
        self.buttons = []
        for i in range(5):
            pos = (125*(i+1) + 25, 50) # calculate x position of buttons based on lane
            color = (.25,.5,.75)
            button = ButtonDisplay(pos, color)
            self.buttons.append(button)
            self.add(button)
        
        # create barlines
        for time in gem_data[0]:
            barline = BarLine(time)
            if barline.on_screen():
                self.objects.add(barline) # if bar is on the screen then we can add to anim group
            else:
                self.not_on_screen.append(barline) # if bar is not on the screen update manually
            
        # create gems and store in dictionary
        self.gems = dict() 
        for lane in gem_data[1]:
            xpos = 25 + 125*(lane+1)
            for time_g in gem_data[1][lane]:
                gem = GemDisplay(xpos, (1,1,1), time_g)
                self.gems[time_g] = gem # this dictionary allows for us to find gems of interest in constant time based on their respective timings in the song
                if gem.on_screen():
                    self.objects.add(gem)
                else:
                    self.not_on_screen.append(gem)
        
        
    # called by Player. Causes the right thing to happen
    def gem_hit(self, gem_idx):
        # if the gem is hit, then deactivate the gem and remove it from dictionary
        self.gems[gem_idx].on_hit()
        del self.gems[gem_idx]

    # called by Player. Causes the right thing to happen
    def gem_pass(self, gem_idx):
        # if gem is missed, change the color to indicate a pass, it will deactivate
        self.gems[gem_idx].on_pass()

    # called by Player. Causes the right thing to happen
    def on_button_down(self, lane, hit):
        # animate the button based on whether or not there was a valid hit
        self.buttons[lane].on_down(hit)

    # called by Player. Causes the right thing to happen
    def on_button_up(self, lane):
        # animate the button, restore back to original color
        self.buttons[lane].on_up()

    # call every frame to make gems and barlines flow down the screen
    def on_update(self) :    
        self.objects.on_update() # update all objects in anim group first
        # any objects no longer on screen will be removed after this
        
        if len(self.not_on_screen) > 0:
            # if there are objects above the screen then manually update each one
            dt = kivyClock.frametime
            obj_rem = [] # objects to be removed from not_on_screen and added to anim group
            
            for obj in self.not_on_screen:
                obj.on_update(dt)
                if obj.on_screen():
                    obj_rem.append(obj)
            
            for obj in obj_rem:
                self.objects.add(obj)
                self.not_on_screen.remove(obj)
                
            
        



# Handles game logic and keeps score.
# Controls the display and the audio
class Player(object):
    def __init__(self, gem_data, display, audio_ctrl):
        super(Player, self).__init__()
        
        # get the gem data game display, audio controller
        self.gem_data = gem_data # gem info organized like { lane0: [time_g1, time_g2, ...], ... }
        self.display = display # instance of beat match display
        self.audio = audio_ctrl # instance of audio controller
        
        # keep track of time
        self.t = 0
        
        # keep track of score
        self.score = 0
        
        # create a timing threshold 
        self.interval = .09
        
        
    # called by MainWidget
    def on_button_down(self, lane):
        hit = False
            
        for time_g in self.gem_data.gems[lane]: # time is idx for each gem
            if self.t-self.interval < time_g < self.t+self.interval: # if pressed within the hit box
                hit = True # then we have a valid hit
                break # we can break because a single gem can be played in a lane at a time
                
        self.display.on_button_down(lane, hit) # do the appropriate animation for specific button
        
        if hit == True:
            self.score += 50
            self.display.gem_hit(time_g) # animate gem and remove from data
            self.gem_data.gems[lane].remove(time_g) # remove time stamp from data
            self.audio.set_mute(False)
        
        else: # if it did NOT hit a note
            self.score -= 20
            self.audio.set_mute(True) # set solo track to mute 
            self.audio.play_sfx() # play "incorrect" sound effect

    # called by MainWidget
    def on_button_up(self, lane):
        self.display.on_button_up(lane)

    # needed to check if for pass gems (ie, went past the slop window)
    def on_update(self):
        # must update the audio and the visual
        self.display.on_update()
        self.audio.on_update()
        
        # update personal clock
        self.t += kivyClock.frametime
        
        kill_list = []
        for lane in self.gem_data.gems:
            for time_g in self.gem_data.gems[lane]:
                if self.t-self.interval > time_g: # if outside of the hit box
                    self.score -= 20
                    self.audio.set_mute(True) # set solo track to mute 
                    self.display.gem_pass(time_g) # animate the gem and remove from data
                    kill_list.append((lane, time_g))
        
        for gem in kill_list: # remove missed gems from gem_data dictionary
            self.gem_data.gems[gem[0]].remove(gem[1])
            
                
        
'''
# if __name__ == '__main__':
#     run(MainWidget)
