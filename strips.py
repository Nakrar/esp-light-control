import machine

# 5
# 14

FREQ = 1000
MAX_PWM = 1023

STRIPS = {
    'ceil': machine.PWM(machine.Pin(5), freq=FREQ, duty=MAX_PWM),
    'wall': machine.PWM(machine.Pin(14), freq=FREQ, duty=MAX_PWM),
}

def set_brightness(strip, value):
    # PWM is inverted. MAX_PWM is off, 0 is on
    if value == 0:
        target = 0
    elif value == 100:
        target = MAX_PWM
    else:
        target = int(MAX_PWM / 100 * value)

    strip.duty(target)
