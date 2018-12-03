from common.clock import quantize_tick_up, AudioScheduler, TempoMap
from common.synth import Synth

class Ticker(object):
    ''' 
    Maps beat patterns to ticks (time stamps) and plays the call of the call and response (if enabled)
    This class assumes quarter notes as beats.
    becase every loop in this game is 4 measures, we will assume a loop to last 16 beats.  (4/4)
    '''
    bpm = 120
    numRepeats = 2
    measuresPerCall = 4

    def __init__(self, patterns):
        self.patterns = patterns
        self.synth = Synth('../data/FluidR3_GM.sf2')
        
        data = [(0,0), ()]
        self.tempo = TempoMap()
        self.scheduler = AudioScheduler()
    def timeToTick(self, time):
        ''' convert kivy frametime (in seconds) to ticks'''
        currentTick = 