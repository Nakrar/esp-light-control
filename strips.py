import machine

# 5
# 14
import led

FREQ = 1000
MAX_PWM = 1023

STRIPS = {
    'ceil': machine.PWM(machine.Pin(5), freq=FREQ, duty=0),
    'wall': machine.PWM(machine.Pin(14), freq=FREQ, duty=0),
    'blue': machine.PWM(led._led, freq=FREQ, duty=0),
    # 'rgb': 'None',
}


def set_brightness(strip, value):
    strip.duty(int(MAX_PWM / 100 * value))
