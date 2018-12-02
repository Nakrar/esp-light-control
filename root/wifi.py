import time
import network

from root import led


def do_connect():
    sta_if = network.WLAN(network.STA_IF)

    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect('***REMOVED***', '***REMOVED***')

        for x in range(5):
            led.blink(300)
            time.sleep_ms(1500)
            if sta_if.isconnected():
                led.blink(720)
                print('network config:', sta_if.ifconfig())
                break
        else:
            print('could not connect')
            led.blink(160, count=3, off_time=80)


def disable_ap():
    network.WLAN(network.AP_IF).active(False)
