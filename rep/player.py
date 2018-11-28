
from kivy.core.image import Image

from rep.constants import *
from src.notedetector import NoteDetector

class Player(object):
    def __init__(self, cursor, display):
        super(Player, self).__init__()
        
        self.cursor = cursor
        self.display = display
        self.score = 0
        
        self.play = False
        self.iter = 0
        
        self.pattern = None
        
        self.slack_win = self.cursor.v * kWinLen
        self.cursor.install_cb( self.player_input )
    
    def player_input(self):
        if self.iter > 0 and self.iter%2 == 0:
            self.display.next_bar()
        self.iter += 1
    
    def check_game_over(self):
        return self.display.is_game_over()
            
    def play_game(self):
        self.play = True
        
    def pause_game(self):
        self.play = False
        
    def on_input(self, chord):
        if self.iter%2 == 0:
            self.cursor.time_reset()
            self.check_collision(chord)

    def check_collision(self, chord):
        if self._is_hit(chord):
            self.score += 1
        else:
            self.score -= 1
        
    def load_pattern(self, pattern):
            self.pattern = pattern
            self.display.load_pattern(self.pattern)
            
    def on_update(self):
        if self.play:
            self.display.on_update()
        if self.iter%2 == 0:
            self._catch_passes()
        return self.check_game_over()
        
    
    
    
    def _catch_passes(self):
        for gem in self.display.active_gems:
            cursor_xpos = self.cursor.get_xpos()
            if not gem.done and gem.get_cpos()[0] < cursor_xpos - self.slack_win:
                self.score -= 1
                gem.on_miss()

    def _is_hit(self, chord):
        hit = False
        cursor_xpos = self.cursor.get_xpos()
        for gem in self.display.active_gems:
            if cursor_xpos - self.slack_win < gem.get_cpos()[0] < cursor_xpos + self.slack_win:
                print(chord, gem.get_chord())
                if chord == str(gem.get_chord()):
                    hit = True
                    gem.on_hit()
        return hit
