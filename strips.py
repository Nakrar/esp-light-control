import math

import machine
import neopixel

FREQ = 100000
MAX_PWM = 1023
RGB_COUNT = 174


class StripPWM:

    def __init__(self, pin_id):
        pin = machine.Pin(pin_id)
        self._pwm = machine.PWM(pin, freq=FREQ, duty=0)

    def set_brightness(self, value):
        target = int(MAX_PWM * (value / 100))

        self._pwm.duty(target)

    def get_brightness(self):
        return int(100 * (self._pwm.duty() / MAX_PWM) + 0.5)


class StripNEO:

    def __init__(self, pin_id):
        pin = machine.Pin(pin_id, machine.Pin.OUT)
        self._np = neopixel.NeoPixel(pin, RGB_COUNT)  # create NeoPixel driver on GPIO0 for 8 pixels
        self.set_brightness(0)

    def set_brightness(self, value):
        target = (int(255 * (value / 100)),) * 3
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
    'window': StripPWM(22),  # 5
    'wall': StripPWM(23),  # 14
    'ceil': StripPWM(18),  # 13
    'rgb': StripNEO(21),  # 2
}
