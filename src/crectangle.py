from kivy.graphics import Rectangle

class CRectangle(Rectangle):
    def __init__(self, **kwargs):
        super(CRectangle, self).__init__(**kwargs)
        if 'cpos' in kwargs:
            self.cpos = kwargs['cpos']

        if 'csize' in kwargs:
            self.csize = kwargs['csize']

    def get_cpos(self):
        return (self.pos[0] + self.size[0]/2, self.pos[1] + self.csize[1]/2)

    def set_cpos(self, p):
        self.pos = (p[0] - self.csize[0]/2 , p[1] - self.csize[1]/2)

    def get_csize(self) :
        return self.size

    def set_csize(self, p) :
        cpos = self.get_cpos()
        self.size = p
        self.set_cpos(cpos)

    cpos = property(get_cpos, set_cpos)
    csize = property(get_csize, set_csize)
