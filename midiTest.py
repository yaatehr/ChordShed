import mido
# from mido.ports import open_input
from mido.midifiles import MidiFile
import time



try: 
    inport = mido.open_input()
    msg = inport.receive()
except:
    print('no input attached')


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




note_class = notes()


major_chords = MidiFile('./major_chords.mid')

#parsing mido.Message.from_bytes()
#  mido.parse_all([0x92, 0x10, 0x20, 0x82, 0x10, 0x20])
# p.feed_byte(0x90) for callback?
# make a buffer for midi inputs