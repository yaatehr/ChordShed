
from kivy.core.image import Image

from rep.constants import *
from src.notedetector import NoteDetector
from src.score import SaveData
class Player(object):
    def __init__(self, cursor, display, targetCallback = None):
        super(Player, self).__init__()
        
        self.cursor = cursor
        self.display = display
        self.score = 0
        
        self.play = False
        self.iter = 0
        self.saveData = None
        self.pattern = None
        self.update_target = targetCallback

        self.slack_win = self.cursor.v * kWinLen
        #end callback (at the end of measure)
        self.cursor.install_cb( self.player_input )
        self.targetGem = None
    
    def player_input(self):
        if self.iter > 0 and self.iter%2 == 0:
            self.display.next_bar()
        self.iter += 1
    
    def check_game_over(self):
        return self.display.is_game_over()
            
    def play_game(self):
        self.play = True
        if not self.saveData:
            self.saveData = SaveData('test', self.display.getAllGems())

    def pause_game(self):
        self.play = False
        
    def on_input(self, note, correct):
        if self.iter%2 == 0:
            self.cursor.time_reset() #TODO What does this do?

            if not correct:
                self.on_miss(note)

    def on_hit(self):
        if self._temporal_hit():
            print('past temp hit')
            if self.saveData:
                self.saveData.addGem(self.targetGem, True)
            self.targetGem = None
                # self.gem.a
                # self.update_target(self.gem)
        self.score += 1
        print('past score')



    def on_miss(self, note):
        # print('missed: %d' % note)
        self.score -= 1
        pass
        
    def load_pattern(self, pattern):
            self.pattern = pattern
            self.display.load_pattern(self.pattern)
            
    def on_update(self):
        if self.play:
            self._find_nearest_gem()
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
                if self.saveData:
                    self.saveData.addGem(self.targetGem, False)
                self.targetGem = None

    def _find_nearest_gem(self):
        if not self.display.active_gems:
            return
        minDist = 999999999
        minIndex = 0
        for i, gem in enumerate(self.display.active_gems):
            cursor_xpos = self.cursor.get_xpos()
            dist = abs(gem.get_cpos()[0] - cursor_xpos) 
            if dist < minDist:
                minDist = dist
                minIndex = i

        targetGem = self.display.active_gems[minIndex]
        if targetGem is not self.targetGem:
            self.targetGem = targetGem
            # print('new target chord')
            targetGem.focus() #TODO
            chord = targetGem.get_chord()
            self.update_target(chord)

    def _temporal_hit(self):
        if not self.display.active_gems:
            return
        cursor_xpos = self.cursor.get_xpos()
        if cursor_xpos - self.slack_win < self.targetGem.get_cpos()[0] < cursor_xpos + self.slack_win:
            # if chord == str(gem.get_chord()):
            #     hit = True
                self.targetGem.on_hit()
                return True
        return False
