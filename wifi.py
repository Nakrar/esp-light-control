import time
import network

from constants import WIFI_LOGIN, WIFI_PASS


def do_connect():
    sta_if = network.WLAN(network.STA_IF)

    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(WIFI_LOGIN, WIFI_PASS)

        for x in range(5):
            time.sleep(1.5)
            if sta_if.isconnected():
                print('network config:', sta_if.ifconfig())
                break
        else:
            print('could not connect')


def disable_ap():
    network.WLAN(network.AP_IF).active(False)
