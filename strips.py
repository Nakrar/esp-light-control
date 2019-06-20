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


class StripNEO:

    def __init__(self, pin_id):
        pin = machine.Pin(pin_id, machine.Pin.OUT)
        self._np = neopixel.NeoPixel(pin, RGB_COUNT)  # create NeoPixel driver on GPIO0 for 8 pixels
        self.set_brightness(0)

    def set_brightness(self, value):
        target = (int(255 * (value / 100)),) * 3
        self._np.fill(target)
        self._np.write()

    def set_color(self, color):
        self._np.fill(color)
        self._np.write()


STRIPS = {
    'ceil': StripPWM(22),  # 5
    'window': StripPWM(23),  # 14
    'wall': StripPWM(18),  # 13
    'rgb': StripNEO(21),  # 2
}
