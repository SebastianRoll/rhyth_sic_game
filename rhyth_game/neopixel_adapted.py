from neopixel import NeoPixel


class NeoPixelAdapted(NeoPixel):

    def adapt(self, color):
        if len(color) == 3 and self.bpp == 4:
            color = list(color) + [0]
        return color

    def __setitem__(self, key, value):
        super().__setitem__(key, self.adapt(value))

    def fill(self, color):
        super().fill(self.adapt(color))