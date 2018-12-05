
from kivy.core.image import Image
from common.clock import Clock
from rep.constants import *
from src.notedetector import NoteDetector
from src.score import ScoreCard
from src.ticker import Ticker
from kivy.graphics.instructions import InstructionGroup
from common.gfxutil import *


class Player(InstructionGroup):
    def __init__(self, ticker, clock, targetCallback = None):
        super(Player, self).__init__()
        self.score = 0
        self.play = False
        self.saveData = None
        self.pattern = None
        self.update_target = targetCallback
        self.mode = "call"
        self.ticker = ticker
        self.clock = clock
        self.barNum = -1
        self.slackWin = self.ticker.slack_timout/2
        self.objects = AnimGroup()
        self.add(self.objects)
        self.status = "next"
        #end callback (at the end of measure)
        self.targetGem = None
        self.active_gems = []
    
    def check_bar_over(self):
        '''
        return no bars left
        '''
        pass

    def play_game(self):
        self.play = True
        # self.clock.start()
        if not self.saveData:
            self.saveData = ScoreCard()
            # self.saveData.clear()

    def pause_game(self):
        # self.clock.stop()
        self.play = False

    def increment_bar(self):
        if self.objects.size():
            self.ticker.clear_bar(self.barNum)
            [self.objects.remove(gem) for gem in self.ticker.active_gems]
            
        self.barNum += 1
        self.ticker.create_bar(self.barNum)
        [self.objects.add(gem) for gem in self.ticker.active_gems]
        
    def on_input(self, note, correct):
        '''
        calls the appropriate on hit or on miss function
        let notes that belong in a chord slide
        '''
        if self.mode == "call":
            return
        if not correct:
            self.on_miss(note)

    def on_hit(self):
        '''
        Called if the note detector finds a match with target gem's chord.
        This checks if the hit was within the slack window (if necessary), and
        updates the gem record and score appropriately
        '''
        if self._temporal_hit():
            print('past temp hit')
            if self.saveData:
                self.saveData.addGem(self.targetGem, True)
            self.targetGem = None
            if len(self.ticker.active_gems) == 1:
                #we just finished a round
                self.resetCallback()
        self.score += 1

    def on_miss(self, note):
        '''
        Called if note detector finds a note not currently in target gem.
        Updates score record appropriately
        '''
        self.score -= 1
        # self.saveData.missedNote(note, self.targetGem) TODO
        pass
            
    def on_update(self):
        if self.barNum != -1:
            self.status = self.ticker.barStatus()
        
        if self.status == "next":
            self.increment_bar()

        if self.play:
            self._find_nearest_gem()
            # self.display.on_update()

    def nextBar(self):
        #TODO add terminal conditions
        self._catch_passes()
        
    def _catch_passes(self):
        for gem in self.ticker.active_gems:
            currentBeat = self.timer.getRelativeTick()/(480*4)
            targetBeat = self.targetGem.beat
            if not gem.done and abs(currentBeat - targetBeat) < self.slackWin:
                self.score -= 1
                gem.on_miss()
                if self.saveData:
                    self.saveData.addGem(self.targetGem, False)
                self.targetGem = None

    def _find_nearest_gem(self):
        if not self.ticker.active_gems:
            return
        targetGem = self.ticker.getTargetGem()
        if targetGem is not self.targetGem:
            self.targetGem = targetGem
            # print('new target chord')
            # targetGem.focus() #TODO
            chord = targetGem.get_chord()
            self.update_target(chord)

    def _temporal_hit(self):
        if not len(self.ticker.active_gems):
            return
        currentBeat = self.timer.getRelativeTick()/(480*4)
        targetBeat = self.targetGem.beat
        if abs(currentBeat - targetBeat) < self.slackWin:
            # if chord == str(gem.get_chord()):
            #     hit = True
                self.targetGem.on_hit()
                return True
        return False
