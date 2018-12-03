from common.clock import quantize_tick_up, Scheduler, TempoMap
from common.synth import Synth
from rep.gem import Gem
import sys
sys.path.append('..')
from src.chord import Chord, Key

kTicksPerQuarter = 480

class Ticker(object):
    ''' 
    Maps beat patterns to ticks (time stamps) and plays the call of the call and response (if enabled)
    This class assumes quarter notes as beats.
    becase every loop in this game is 4 measures, we will assume a loop to last 16 beats.  (4/4)
    '''
    bpm = 120
    numRepeats = 2
    measuresPerCall = 4
    channel = 1
    vel = 80
    playQueues = 1
    noteDuration = 1

    def __init__(self, songPattern, key, clock, nextBar=None):
        self.gems, self.bars = self.initialize_bars(songPattern, key)
        self.synth = Synth('../data/FluidR3_GM.sf2')
        totalBeats = self.measuresPerCall*self.numRepeats*len(self.bars)*4
        totalTime = totalBeats/self.bpm
        data = [(0,0), (totalTime, totalBeats)]
        self.tempo = TempoMap(data=data)
        self.scheduler = Scheduler(clock, self.tempo)
        self.nextBar = nextBar
        self.on_commands = [] # commands for a bar of call and response
        self.off_commands = []
        self.active_gems = []
        self.gem_commands = []
        self.barTick = 0
        self.currentbar = 0
        # self.scheduler.set_generator(self.synth)
    
    
    def reset(self):
        self._clear_gems()
        self.gembar.activate(True)
        self.cursor.restart()
        self.game_over = False
        self.objects.add( self.gembar )
        self.objects.add( self.cursor )
        self.objects.add(self.tutor)
    
    def create_bar(self, barIndex):
        self.barTick = self.scheduler.get_tick()
        self.initializeBarAudio(barIndex)
        self.initializeBarGems(barIndex)

    def clear_bar(self, barIndex):
        self.clearBarAudio(barIndex)
        self.clearBarGems(barIndex)


    def getRelativeTick(self, tick):
        tick = self.scheduler.get_tick()
        barLenTicks = kTicksPerQuarter*4
        tick = (tick - self.barTick)%barLenTicks

    def getTargetGem(self, tick):
        tick = self.getRelativeTick()
        beatApprox = round(tick/barLenTicks)

        #find gem by tick
        minDist = 9999999999
        for gem in active_gems:
            gemDist = abs(gem.beat - beatApprox)
            if  gemDist < minDist:
                minDist = gemDist
                targetGem = gem
            
        return targetGem


    def initialize_bars(self, pattern, key):
        gem_bars = []
        chord_bars = []

        for bar in pattern:
            assert len(bar) > 1
            chords_and_ticks = []
            for b in bar:
                assert b[1] <= self.measuresPerCall*4 and b[1] > 0
                chords_and_ticks.append((key.generateChord(b[0]), b[1]))
            
            gems = [ Gem(chord, beat) for chord, beat in chords_and_ticks ]
            chord_bars.append(chords_and_ticks)
            gem_bars.append(gems)
        return gem_bars, chord_bars

    def initializeBarAudio(self, barIndex):
        barTick = self.scheduler.get_tick()
        bar = self.bars[barIndex]
        assert self.numRepeats >= self.playQueues
        for i in range(self.playQueues):
            for chord, beat in bar:
                tick = barTick + beat*kTicksPerQuarter
                self.on_commands.append(self.scheduler.post_at_tick(self._playChord, tick, chord))
                self.off_commands.append(self.scheduler.post_at_tick(self._endChord, tick+kTicksPerQuarter*self.noteDuration, chord))
            barTick += kTicksPerQuarter*4
        # barTick += (self.numRepeats- self.playQueues)*4*kTicksPerQuarter

    def clearBarAudio(self, barIndex):
        for c in self.on_commands:
            self.scheduler.remove(c)
        for c in self.off_commands:
            self.scheduler.remove(c)
            c.execute()

    def initializeBarGems(self, barIndex):
        barTick = self.scheduler.get_tick()
        bar = self.gems[barIndex]
        for i in range(self.numRepeats):
            for gem in bar:
                tick = barTick + gem.beat*kTicksPerQuarter
                # self.gem_commands.append(self.)

    def refreshBarGems(self, barIndex):
        pass

    def clearBarGems(self, barIndex):
        pass
        

    def _drawGems(self, gems)
        self.active_gems = [Gem()]
    def _playChord(self, chord):
        for note in chord:
            self.synth.noteon(self.channel, note, self.vel)
    
    def _endChord(self, chord):
        for note in chord:
            self.synth.noteoff(self.channel, note)