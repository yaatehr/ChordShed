import mido
# from mido.ports import open_input
from mido.midifiles import MidiFile
import time



class notes(object):
    clock = time.clock
    def __init__(self):
        # self.noteBuffer = []
        self.playingNotes = dict() # holds a tuple of what notes are playing and how long they have been playing
        # better way to do this?
        self.playedNotes = []

    def callback(self, message):
        if message.type == 'note_on':
            if message.note not in self.playingNotes.keys():
                self.playingNotes.update({message.note: self.clock()})
        elif message.type == 'note_off':
            if message.note in self.playingNotes.keys():
                start = self.playingNotes.pop(message.note)
                self.playedNotes.append((message, self.clock() - start))



try: 
    note_class = notes()
    inport = mido.open_input(virtual=True, name="testInput", callback=note_class.callback)
    print('port initialized')
    # msg = inport.receive()
except Exception as e:
    print('no input attached ', e)
finally:
    del inport


major_chords = MidiFile('./major_chords.mid')

#parsing mido.Message.from_bytes()
#  mido.parse_all([0x92, 0x10, 0x20, 0x82, 0x10, 0x20])
# p.feed_byte(0x90) for callback?
# make a buffer for midi inputs