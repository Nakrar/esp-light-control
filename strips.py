import machine
import neopixel
import time

# 5
# 14

FREQ = 1000
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

    def demo(self):
        # demo from https://docs.micropython.org/en/v1.8/esp8266/esp8266/tutorial/neopixel.html
        np = self._np
        n = np.n

        # cycle
        for i in range(4 * n):
            for j in range(n):
                np[j] = (0, 0, 0)
            np[i % n] = (255, 255, 255)
            np.write()
            time.sleep_ms(25)

        # bounce
        for i in range(4 * n):
            for j in range(n):
                np[j] = (0, 0, 128)
            if (i // n) % 2 == 0:
                np[i % n] = (0, 0, 0)
            else:
                np[n - 1 - (i % n)] = (0, 0, 0)
            np.write()
            time.sleep_ms(60)

        # fade in/out
        for i in range(0, 4 * 256, 8):
            for j in range(n):
                if (i // 256) % 2 == 0:
                    val = i & 0xff
                else:
                    val = 255 - (i & 0xff)
                np[j] = (val, 0, 0)
            np.write()

        # clear
        for i in range(n):
            np[i] = (0, 0, 0)
        np.write()


STRIPS = {
    'ceil': StripPWM(5),
    'wall': StripPWM(14),
    'window': StripPWM(13),
    'rgb': StripNEO(2),
}
