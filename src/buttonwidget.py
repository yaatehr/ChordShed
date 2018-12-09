
from kivy.core.image import Image

from kivy.uix.widget import Widget

from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Rectangle



class ButtonWidget(Widget):
    '''Button Class for creating Home and Settings buttons'''
    def __init__(self, pos, filepath, cb, param, size=(40,40)):
        super(ButtonWidget, self).__init__( pos=pos, size=size )

        texture = Image(filepath).texture
        self.bg = Rectangle(pos=self.pos, size=self.size, texture=texture)
        self.canvas.add(self.bg)
        self.cb = cb
        self.param = param
        self.pressed = False


    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            self.pressed = True


    def on_touch_up(self, touch):
        if self.pressed:
            if self.collide_point(touch.x, touch.y):
                self.cb(self.param)
        self.pressed = False


    def __str__(self):
        # string representation of the widget when in a print() statement
        return "ButtonWidget"
