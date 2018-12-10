
from kivy.core.image import Image
from common.clock import Clock
from rep.constants import *
from src.notedetector import NoteDetector
from src.score import ScoreCard
from src.ticker import Ticker
from kivy.graphics.instructions import InstructionGroup
from common.gfxutil import *
import copy


class Player(InstructionGroup):
    def __init__(self, ticker, clock, pattern, targetCallback = None, pull_gems=None):
        super(Player, self).__init__()
        self.score = 0
        self.play = False
        self.scoreCard = None
        self.pattern = pattern
        self.update_target = targetCallback
        self.mode = "call"
        self.ticker = ticker
        self.clock = clock
        self.barNum = -1
        self.slackWin = self.ticker.slack_timout
        self.objects = AnimGroup()
        self.add(self.objects)
        self.status = "startup"
        #end callback (at the end of measure)
        self.targetGem = None
        self.pull_active_gems = pull_gems
    
    def check_bar_over(self):
        '''
        return no bars left
        '''
        pass

    def play_game(self):
        self.play = True
        if not self.scoreCard:
            self.scoreCard = ScoreCard(self.pattern)
            # self.scoreCard.clear()
        if self.barNum == -1:
            self.status = "next"

    def pause_game(self):
        # self.clock.stop()
        self.play = False

    def increment_bar(self, perfect=False):
        if self.objects.size(): #wrap up last bar
            if perfect:
                self.scoreCard.perfect_bar(self.barNum, self.ticker.bars_remaining())
            self.scoreCard.increment_score(self.barNum)
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
        if self.mode == "call": #don't score during call mode
            return
        if not correct:
            self.on_miss_input(note)

    def on_hit(self, noteVals):
        '''
        Called if the note detector finds a match with target gem's chord.
        This checks if the hit was within the slack window (if necessary), and
        updates the gem record and score appropriately
        '''
        if self._temporal_hit():
            print('past temp hit')
            if self.scoreCard:
                self.scoreCard.on_chord_hit(
                    self.barNum, self.targetGem.copy_gem(), noteVals)

            self.targetGem = None
            allHit = True
            for gem in self.ticker.active_gems:
                allHit = allHit and gem.hit
            if len(self.ticker.active_gems) == 1:
                #we just finished a round
                self.increment_bar()
        #TODO add scoring logic
        self.score += 1

    def on_miss_input(self, note):
        '''
        Called if note detector finds a note not currently in target gem.
        Updates score record appropriately
        '''
        self.score -= 1
        # self.score.add
        if self.targetGem:
            self.scoreCard.on_chord_miss(self.barNum, self.targetGem.copy_gem(), note)
        else:
            self.scoreCard.on_misc_miss(self.barNum, note)
        pass
            
    def on_update(self):
        if self.barNum != -1:
            self.status = self.ticker.on_update()
        
        if self.status == "next":
            return self.increment_bar()

        if self.play:
            self._find_nearest_gem()
            if self.status != "call":
                self.catch_passes()
            self.objects.on_update()
            # self.display.on_update()

    def nextBar(self):
        #TODO add terminal conditions
        pass
        # self.catch_passes()
        
    def catch_passes(self, tickerCall=False):
        if self.status == "call" or not self.targetGem:
            self.targetGem = None
            return
        for gem in self.ticker.active_gems:
            currentBeat = self.ticker.getRelativeTick()/(480)
            targetBeat = gem.beat
            # eps = .3
   
            if not (gem.hit or gem.miss) and currentBeat - targetBeat > self.slackWin/2:
                # print("caught pass - curr %f, target %f, slackWin %f, relativeTick %f" % (currentBeat, targetBeat, self.slackWin*480, self.ticker.getRelativeTick()))
                self.score -= 1 #TODO add scoring logic
                gem.on_miss()
                if self.scoreCard:
                    self.scoreCard.on_chord_miss(self.barNum, self.targetGem.copy_gem(), self.pull_active_gems())
                self.targetGem = None

    def _find_nearest_gem(self):
        # tick = self.ticker.getTick()
        targetGem = self.ticker.getTargetGem()
        if targetGem is None:
            # print('no target gem: ', tick)
            return
        if not targetGem.focused:
            currentBeat = self.ticker.getRelativeTick()/(480)
            targetBeat = targetGem.beat
            if abs(currentBeat - targetBeat) < self.slackWin:
                self.targetGem.focus()
        if targetGem is not self.targetGem:
            self.targetGem = targetGem
            # print('new target chord %d, on beat %d' % (tick, self.targetGem.beat))
            chord = targetGem.get_chord()
            self.update_target(chord)

    def _temporal_hit(self):
        if not self.targetGem:
            return False
        currentBeat = self.ticker.getRelativeTick()/(480)
        targetBeat = self.targetGem.beat
        print(currentBeat, targetBeat)
        if abs(currentBeat - targetBeat) < self.slackWin/2:
            self.targetGem.on_hit()
            return True
        return False
