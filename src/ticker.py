from common.clock import quantize_tick_up, Scheduler, TempoMap
from common.synth import Synth
from rep.gem import Gem
import sys
sys.path.append('..')
from src.chord import Chord, Key
from kivy.core.window import Window
kTicksPerQuarter = 480

class Ticker(object):
    ''' 
    Maps beat patterns to ticks (time stamps) and plays the call of the call and response (if enabled)
    This class assumes quarter notes as beats.
    becase every loop in this game is 4 measures, we will assume a loop to last 16 beats.  (4/4)
    '''
    bpm = 60
    numRepeats = 3
    measuresPerCall = 4
    channel = 0
    vel = 80
    playQueues = 1
    noteDuration = 1
    nowBarHeight = Window.height//2
    barLenTicks = kTicksPerQuarter*4
    gemRadius = 50
    padding = gemRadius + 50

    def __init__(self, songPattern, key, clock, increment_bar=None):
        self.slack_timout = .2/(self.bpm/60)

        self.gems, self.bars = self._initialize_bars(songPattern, key)
        self.synth = Synth('../data/FluidR3_GM.sf2')
        totalBeats = self.measuresPerCall*self.numRepeats*len(self.bars)*4
        totalTime = totalBeats/(self.bpm/60)
        data = [(0,0), (totalTime, totalBeats*kTicksPerQuarter)]
        self.tempo = TempoMap(data=data)
        self.num_bars = len(data)
        self.scheduler = Scheduler(clock, self.tempo)
        self.increment_bar = increment_bar
        self.on_commands = [] # commands for a bar of call and response
        self.off_commands = []
        self.active_gems = []
        self.gem_commands = []
        self.bar_tick = 0
        self.bar_index = 0

        # self.scheduler.set_generator(self.synth)
    
    
    def reset(self):
        #TODO
        for i in range(len(self.num_bars)):
            self.clear_bar(i)

        self.bar_index = 0
    
    def create_bar(self, barIndex):
        # print('creating bar number %d' % barIndex)
        self.clear_bar(barIndex)
        self.bar_tick = quantize_tick_up(self.scheduler.get_tick())
        self.active_gems = self.gems[barIndex]
        print(list(map(lambda x: x.beat, self.active_gems)))
        # [gem.activate() for gem in self.active_gems]
        self._initializeBarAudio(barIndex)
        self._initializeBarGems(barIndex)

    def clear_bar(self, barIndex):
        self._clearBarAudio(barIndex)
        self._clearBarGems()


    def getRelativeTick(self):
        tick = self.scheduler.get_tick()
        tick = (tick - self.bar_tick)%self.barLenTicks
        return tick

    def getTargetGem(self):
        tick = self.getRelativeTick()
        beatApprox = (tick/kTicksPerQuarter)

        #find gem by tick
        targetGem = None

        minDist = 9999999999
        for gem in self.active_gems:
            # print(gem.beat)
            # print(beatApprox, gem.beat)
            gemDist = min(gem.beat - beatApprox, beatApprox - gem.beat)
            # print(gemDist)
            if  gemDist < minDist:
                minDist = gemDist
                targetGem = gem
        
        # print("minimum dist: ", minDist)
        # print("targetGem: ", gem.beat)
        # print("beat approx: ", beatApprox)
            
        return targetGem

    def on_update(self):
        self.scheduler.on_update()
        ticksEllapsed = self.scheduler.get_tick() - self.bar_tick

        if ticksEllapsed <= self.barLenTicks:
            return "call"
        elif ticksEllapsed <= self.numRepeats*self.barLenTicks:
            return "response"
        else:
            return "next"


    def _initialize_bars(self, pattern, key):
        gem_bars = []
        chord_bars = []

        for bar in pattern:
            numGems = len(bar)
            assert numGems > 1
            w = (Window.width - self.padding*numGems)//numGems
            # h = Window.height//len(gems)
            x = self.padding
            y = self.nowBarHeight
            chords_and_ticks = []
            gems = []
            for b in bar:
                assert b[1] <= self.measuresPerCall*4 and b[1] > 0
                chord  = key.generateChord(b[0])
                chords_and_ticks.append((chord, b[1]))
                gem = Gem(chord, (x,y), self.gemRadius, self.slack_timout, b[1])
                gems.append(gem)
                x += w + self.padding

            chord_bars.append(chords_and_ticks)
            gem_bars.append(gems)
        return gem_bars, chord_bars

    def _initializeBarAudio(self, barIndex):
        bar_tick = self.bar_tick
        bar = self.bars[barIndex]
        # print(self.bar_tick)
        assert self.numRepeats >= self.playQueues
        for i in range(self.playQueues):
            for chord, beat in bar:
                tick = bar_tick + beat*kTicksPerQuarter
                self.on_commands.append(self.scheduler.post_at_tick(self._playChord, tick, chord))
                self.off_commands.append(self.scheduler.post_at_tick(self._endChord, tick+kTicksPerQuarter*self.noteDuration, chord))
            bar_tick += kTicksPerQuarter*4

    def _clearBarAudio(self, barIndex):
        for c in self.on_commands:
            self.scheduler.remove(c)
        for c in self.off_commands:
            self.scheduler.remove(c)
            c.execute()

    def _initializeBarGems(self, barIndex):
        bar_tick = self.bar_tick
        bar = self.gems[barIndex]
        for i in range(self.numRepeats):
            for gem in bar:
                tick = bar_tick + gem.beat*kTicksPerQuarter
                if i > 0:
                    self.gem_commands.append(self.scheduler.post_at_tick(self._startGemTimer, tick, gem))
            bar_tick += kTicksPerQuarter*4
            self.gem_commands.append(self.scheduler.post_at_tick(self._onCompleteMeasure, tick))



    def _refreshBarGems(self):
        for gem in self.active_gems:
            gem.on_reset()
            gem.activate()

    def _clearBarGems(self):
        for gem in self.active_gems:
            gem.exit()
        
    def _onCompleteMeasure(self, tick, temp=None):
        if self.on_update() == "call":
            return

        allHit = True
        for gem in self.active_gems:
            allHit = allHit and gem.hit
        if allHit:
            # self.increment_bar()
            print('increment bar')
        else:
            print('measure over, resetting gems')
            self._refreshBarGems()


    def _startGemTimer(self, tick, gem):
        ''' starts the gem timer'''
        gem.activate()

    def _playChord(self, tick, chord):
        for note in chord._getMidiTones():
            self.synth.noteon(self.channel, note, self.vel)
    
    def _endChord(self, tick, chord):
        for note in chord._getMidiTones():
            self.synth.noteoff(self.channel, note)


    # def _drawGems(self, gems):
    #     padding = 50
    #     w = (Window.width - padding*len(gems))//len(gems)
    #     # h = Window.height//len(gems)
    #     x = padding
    #     y = self.nowBarHeight
    #     for gem in gems:
    #         gem.set_pos((x,y))
    #         x += w + padding
