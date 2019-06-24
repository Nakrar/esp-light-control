import machine
import neopixel

from constants import FREQ, MAX_PWM, RGB_COUNT


class StripPWM:

    def __init__(self, pin_id):
        pin = machine.Pin(pin_id)
        self._pwm = machine.PWM(pin, freq=FREQ, duty=0)

    def set_brightness(self, value):
        target = int(MAX_PWM * (value / 100) + 0.5)

        self._pwm.duty(target)

    def write(self):
        pass

    def get_brightness(self):
        return int(100 * (self._pwm.duty() / MAX_PWM) + 0.5)


class StripNEO:

    def __init__(self, pin_id):
        pin = machine.Pin(pin_id, machine.Pin.OUT)
        self._np = neopixel.NeoPixel(pin, RGB_COUNT)  # create NeoPixel driver on GPIO0 for 8 pixels
        self.set_brightness(0)
        self._dirty = False

    def __getitem__(self, key):
        if type(key) != int:
            raise TypeError
        if not 0 <= key < RGB_COUNT:
            raise ValueError('N "{}" is out of range "{}"'.format(key, RGB_COUNT))

        return self._np[0]

    def __setitem__(self, key, value):
        if type(key) != int:
            raise TypeError
        if not 0 <= key < RGB_COUNT:
            raise ValueError('N "{}" is out of range "{}"'.format(key, RGB_COUNT))

        if self._np[key] != value:
            self._dirty = True
            self._np[key] = value

    def write(self):
        if self._dirty:
            self._np.write()
            self._dirty = False

    def set_brightness(self, value):
        target = (int(255 * (value / 100) + 0.5),) * 3
        self._fast_fill(target)
        self._np.write()

    def get_brightness(self):
        # returns brightness of first pixel
        return int(100 * (sum(self._np[0]) / 3 / 255) + 0.5)

    def _fast_fill(self, color):
        self._np.buf = bytearray((color[1], color[0], color[2]) * RGB_COUNT)

    def set_color(self, color):
        self._fast_fill(color)
        self._np.write()


STRIPS = {
    'wall': StripPWM(22),  # 5
    'window': StripPWM(23),  # 14
    'ceil': StripPWM(18),  # 13
    'rgb': StripNEO(14),  # 2
}
