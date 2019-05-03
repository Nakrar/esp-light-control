import machine
import neopixel
import time

# 5
# 14

FREQ = 1000000
MAX_PWM = 1023
RGB_COUNT = 174


class StripPWM:

    def __init__(self, pin_id):
        pin = machine.Pin(pin_id)
        self._pwm = machine.PWM(pin, freq=FREQ, duty=0)

    def set_brightness(self, value):
        if value == 0:
            target = 0
        elif value == 100:
            target = MAX_PWM
        else:
            target = int(MAX_PWM / 100 * value)

        self._pwm.duty(target)


class StripNEO:

    def __init__(self, pin_id):
        pin = machine.Pin(pin_id, machine.Pin.OUT)
        self._np = neopixel.NeoPixel(pin, RGB_COUNT)  # create NeoPixel driver on GPIO0 for 8 pixels
        self.set_brightness(0)

    def set_brightness(self, value):
        if value == 100:
            target = (255, 255, 255)
        else:
            target = (int(MAX_PWM / 100 * value),) * 3
        for i in range(self._np.n):
            self._np[i] = target
        self._np.write()

    def set_color(self, color):
        self._np.fill(color)
        self._np.write()


STRIPS = {
    'ceil': StripPWM(22), # 5
    'wall': StripPWM(23), # 14
    'window': StripPWM(18), # 13
    'rgb': StripNEO(21), # 2
}
