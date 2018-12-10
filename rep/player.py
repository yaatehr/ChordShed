
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
        self.slackWin = self.ticker.slack_timout
        self.objects = AnimGroup()
        self.add(self.objects)
        self.status = "startup"
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
        if not self.saveData:
            self.saveData = ScoreCard()
            # self.saveData.clear()
        if self.barNum == -1:
            self.status = "next"

    def pause_game(self):
        # self.clock.stop()
        self.play = False

    def increment_bar(self):
        if self.objects.size(): #clear last bar
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
            self.on_miss_input(note)

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
        # self.saveData.missedNote(note, self.targetGem) TODO add score logic
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
            return
        for gem in self.ticker.active_gems:
            currentBeat = self.ticker.getRelativeTick()/(480)
            targetBeat = gem.beat
            # eps = .3
   
            if not (gem.hit or gem.miss) and currentBeat - targetBeat > self.slackWin/2:
                print("caught pass - curr %f, target %f, slackWin %f, relativeTick %f" % (currentBeat, targetBeat, self.slackWin*480, self.ticker.getRelativeTick()))
                self.score -= 1 #TODO add scoring logic
                gem.on_miss()
                if self.saveData:
                    self.saveData.addGem(self.targetGem, False)
                # self.targetGem = None

    def _find_nearest_gem(self):
        # tick = self.ticker.getTick()
        targetGem = self.ticker.getTargetGem()
        if not targetGem:
            # print('no target gem: ', tick)
            return
        if targetGem is not self.targetGem:
            self.targetGem = targetGem
            # self.targetGem.focus()
            # print('new target chord %d, on beat %d' % (tick, self.targetGem.beat))
            chord = targetGem.get_chord()
            # self.chordKeys = 
            self.update_target(chord)

    def _temporal_hit(self):
        if not self.targetGem:
            return False
        currentBeat = self.ticker.getRelativeTick()/(480)
        targetBeat = self.targetGem.beat
        if abs(currentBeat - targetBeat) < self.slackWin/2:
            self.targetGem.on_hit()
            return True
        return False
