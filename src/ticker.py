from common.clock import quantize_tick_up, Scheduler, TempoMap
from common.synth import Synth
from rep.gem import Gem
import sys
sys.path.append('..')
from src.chord import Chord, Key
from kivy.core.window import Window
kTicksPerQuarter = 480


def ticks_to_time(ticks, bpm):
    return 60*ticks/kTicksPerQuarter/bpm
def beats_to_time(beats, bpm):
    return 60*beats/bpm

class Ticker(object):
    ''' 
    Maps beat patterns to ticks (time stamps) and plays the call of the call and response (if enabled)
    This class assumes quarter notes as beats.
    becase every loop in this game is 4 measures, we will assume a loop to last 16 beats.  (4/4)
    '''
    bpm = 60
    numRepeats = 3
    measuresPerCall = 1
    channel = 0
    vel = 80
    playQueues = 1
    noteDuration = 1
    nowBarHeight = Window.height//2
    endBarTicks = kTicksPerQuarter*.5
    barLenTicks = kTicksPerQuarter*4 + endBarTicks
    gemRadius = 100
    padding = gemRadius + 50

    def __init__(self, songPattern, key, clock):
        self.slack_timout = beats_to_time(.5, self.bpm)
        self.gems, self.bars = self._initialize_bars(songPattern, key)
        self.synth = Synth('../data/FluidR3_GM.sf2')
        totalBeats = self.measuresPerCall*self.numRepeats*len(self.bars)*4
        totalTime = beats_to_time(totalBeats, self.bpm)
        totalOffsetTicks = self.endBarTicks*totalBeats/4
        totalTicks = totalBeats/4*self.barLenTicks
        data = [(0,0), ((totalTime + ticks_to_time(totalOffsetTicks, self.bpm))*2, totalTicks*2)]
        self.tempo = TempoMap(data=data)
        self.num_bars = len(data)
        self.scheduler = Scheduler(clock, self.tempo)
        self.increment_bar = None
        self.catch_passes = None
        self.on_commands = [] # commands for a bar of call and response
        self.off_commands = []
        self.active_gems = []
        self.gem_commands = []
        self.bar_tick = 0
        self.bar_index = 0
    
    def reset(self):
        #TODO
        for i in range(len(self.num_bars)):
            self.clear_bar(i)
        self.bar_index = 0
    
    def create_bar(self, barIndex):
        self.bar_tick = quantize_tick_up(self.scheduler.get_tick())
        self.active_gems = self.gems[barIndex]
        # print(list(map(lambda x: x.beat, self.active_gems)))
        # [gem.activate() for gem in self.active_gems]
        self._initializeBarAudio(barIndex)
        self._initializeBarGems(barIndex)
        # self.increment_bar

    def clear_bar(self, barIndex):
        self._clearBarAudio(barIndex)
        self._clearBarGems()

    def getRelativeTick(self):
        tick = quantize_tick_up(self.scheduler.get_tick())
        tick = (tick - self.bar_tick)%self.barLenTicks
        return tick
    
    def getTick(self):
        return quantize_tick_up(self.scheduler.get_tick())

    def getTargetGem(self):
        tick = self.getRelativeTick()
        beatApprox = (tick/self.barLenTicks)*4
        #find gem by tick
        targetGem = None
        minDist = 9999999999
        for gem in self.active_gems:
            if gem.hit or gem.miss:
                # print("skipping hit gem (target) ", tick)
                continue
            gemDist = min(abs(gem.beat - beatApprox), abs(beatApprox - gem.beat))
            if  gemDist < minDist:
                minDist = gemDist
                targetGem = gem
        # print("minimum dist: ", minDist)
        # print("targetGem: ", gem.beat)
        # print("beat approx: ", beatApprox)
        return targetGem

    def on_update(self):
        self.scheduler.on_update()
        tick = self.getTick()
        ticksEllapsed = (tick - self.bar_tick)%(self.barLenTicks*4)
        if ticksEllapsed <= self.barLenTicks:
            return "call"
        elif ticksEllapsed <= self.numRepeats*self.barLenTicks:
            return "response"
        else:
            # print("tick %f, ticksEll %f, barTick %f, barLen %f " % (tick, ticksEllapsed, self.bar_tick, self.barLenTicks))
            # print('nextStatus')
            return "next"


    def _initialize_bars(self, pattern, key):
        gem_bars = []
        chord_bars = []

        for bar in pattern:
            numGems = len(bar)
            assert numGems > 1
            w = (Window.width)//5
            x = self.padding
            y = self.nowBarHeight
            chords_and_ticks = []
            gems = []
            for b in bar:
                assert b[1] <= self.measuresPerCall*4 and b[1] > 0
                chord  = key.generateChord(b[0])
                chords_and_ticks.append((chord, b[1]))
                x = w*b[1]
                gem = Gem(chord, (x,y), self.gemRadius, self.slack_timout, b[1])
                gems.append(gem)     

            chord_bars.append(chords_and_ticks)
            gem_bars.append(gems)
        return gem_bars, chord_bars

    def _initializeBarAudio(self, barIndex):
        bar_tick = int(self.bar_tick)
        bar = self.bars[barIndex]
        # print(self.bar_tick)
        assert self.numRepeats >= self.playQueues
        for i in range(self.playQueues):
            for chord, beat in bar:
                tick = bar_tick + beat*kTicksPerQuarter
                # print('audio ', tick)
                self.on_commands.append(self.scheduler.post_at_tick(self._playChord, tick, chord))
                self.off_commands.append(self.scheduler.post_at_tick(self._endChord, tick+kTicksPerQuarter*self.noteDuration, chord))
            bar_tick += self.barLenTicks

    def _clearBarAudio(self, barIndex):
        for c in self.on_commands:
            self.scheduler.remove(c)
        for c in self.off_commands:
            self.scheduler.remove(c)
            c.execute()

    def _initializeBarGems(self, barIndex):
        slackWinOffset = quantize_tick_up(float(self.slack_timout)/2*kTicksPerQuarter)
        bar_tick = int(self.bar_tick)
        bar = self.gems[barIndex]
        for i in range(self.numRepeats):
            for gem in bar:
                tick = bar_tick + gem.beat*kTicksPerQuarter
                if i > 0:
                    self.gem_commands.append(self.scheduler.post_at_tick(self._startGemTimer, tick - slackWinOffset, gem))
                    ticks_to_time(tick - slackWinOffset, self.bpm)
            bar_tick += self.barLenTicks
            self.gem_commands.append(self.scheduler.post_at_tick(self._onCompleteMeasure, bar_tick))

    def _refreshBarGems(self):
        for gem in self.active_gems:
            gem.on_reset()
            # gem.activate()

    def _clearBarGems(self):
        for gem in self.active_gems:
            # pass
            gem.exit()
        
    def _onCompleteMeasure(self, tick, temp=None):
        allHit = True
        for gem in self.active_gems:
            allHit = allHit and gem.hit
        if allHit:
            self.increment_bar()
            print('increment bar')
        else:
            # print("measure over, resetting gems - %f" % self.getRelativeTick())
            self.catch_passes(True)
            self._refreshBarGems()

    def _startGemTimer(self, tick, gem):
        ''' starts the gem timer'''
        # print("start gem timer %f " % self.getRelativeTick())
        if not gem.hit:
            gem.activate()

    def _playChord(self, tick, chord):
        for note in chord._getMidiTones():
            self.synth.noteon(self.channel, note, self.vel)
    
    def _endChord(self, tick, chord):
        for note in chord._getMidiTones():
            self.synth.noteoff(self.channel, note)

    def initialize_callbacks(self, increment, catch_passes):
        self.increment_bar = increment
        self.catch_passes = catch_passes