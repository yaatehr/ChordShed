from kivy.graphics.instructions import InstructionGroup
from common.gfxutil import *

from rep.gem import Gem
from rep.patterns import Pattern
from src.pianotutor import KeyboardGui
from time import sleep


class GameDisplay(InstructionGroup):
    def __init__(self, cursor, gembar, mode=None):
        super(GameDisplay, self).__init__()
        
        # create AnimGroup to take care of drawing gems
        self.objects = AnimGroup()
        self.add( self.objects )
        
        # add the NowBar cursor and the gembar
        self.gembar = gembar
        self.cursor = cursor
                
        # save the gem pattern to be used
        self.pattern = None
        
        # keep track of the gems that need to be drawn on the screen 
        self.active_gems = []
        
        # create an instance of the tutor to be drawn
        self.tutor = None 
        
        # save game state
        self.game_over = False
    
    def reset(self):
        self._clear_gems()
        self.gembar.activate(True)
        self.cursor.restart()
        self.game_over = False
        self.objects.add( self.gembar )
        self.objects.add( self.cursor )
    
    def load_pattern(self, pattern):
        self.pattern = pattern
        self.pattern.reset()
        self.reset()
        
    def next_bar(self):
        # clear out gems and animate them off the screen, draw new gems
        self._clear_gems()
        self._draw_new_gems()
    
    def is_game_over(self):
        return self.game_over
        
    def gem_hit(self, gem_idx):
        pass
        
    def gem_miss(self, gem_idx):
        pass
        
    def on_update(self):
        # update all of the objects in the GameManager
        self.objects.on_update()
    
    
    
    
    def _draw_new_gems(self):
        generate = self.pattern.next_bar()
        if generate:
            self.active_gems = self.pattern.generate_bar()
            for gem in self.active_gems:
                self.objects.add(gem)
        else:
            self.cursor.activate(False)
            self._game_over()
        
    def _clear_gems(self):
        for gem in self.active_gems:
            gem.exit()
        self.active_gems = []
            
    def _game_over(self):
        # stop drawing the gembar and the now bar
        self.gembar.activate(False)
        self.cursor.activate(False)
        self.active_gems = []
        self.game_over = True
