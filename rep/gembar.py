class ButtonDisplay(InstructionGroup):
    def __init__(self, pos, color):
        super(ButtonDisplay, self).__init__()

        # add color
        self.rgb = color
        self.color = Color(*self.rgb)
        self.add(self.color)
        
        # draw the button
        self.button = CEllipse(cpos = pos)
        self.button.csize = (50, 50)
        self.add(self.button)

    # displays when button is down (and if it hit a gem)
    def on_down(self, hit):
        self.color.rgb = (int(not hit), int(hit), 0)

    # back to normal state
    def on_up(self):
        self.color.rgb = self.rgb

