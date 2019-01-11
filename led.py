import machine
from machine import Timer

_led = machine.Pin(2, machine.Pin.OUT, value=1)


def blink(on_time, count=1, off_time=None):
    if count < 1:
        return

    if count == 1:
        toggle()
        tim = Timer(-1)
        tim.init(period=on_time, mode=Timer.ONE_SHOT, callback=lambda t: toggle())
    else:
        tim = Timer(-1)

        counter = count
        period = on_time + off_time

        def _callback(t):
            nonlocal counter

            if counter == 0:
                tim.deinit()
            else:
                counter -= 1
                blink(on_time)

        tim.init(period=period, mode=Timer.PERIODIC, callback=_callback)


def off():
    _led.on()


def on():
    _led.off()


def toggle():
    _led.value(not _led.value())
