import machine

_led = machine.Pin(2, machine.Pin.OUT, value=1)


def blink(on_time, count=1, off_time=None):
    # todo: led causes reset issue
    return
    if count < 1:
        return

    if count == 1:
        toggle()
        tim = machine.Timer(-1)
        tim.init(period=on_time, mode=machine.Timer.ONE_SHOT, callback=lambda t: toggle())
    else:
        tim = machine.Timer(-1)

        counter = count
        period = on_time + off_time

        def _callback(t):
            nonlocal counter

            if counter == 0:
                tim.deinit()
            else:
                counter -= 1
                blink(on_time)

        tim.init(period=period, mode=machine.Timer.PERIODIC, callback=_callback)


def off():
    _led.on()


def on():
    _led.off()


def toggle():
    _led.value(not _led.value())
