# This file is executed on every boot (including wake-boot from deepsleep)

# import esp
# esp.osdebug(None)

print('start boot.py execution')

# activate webrepl
import gc
import webrepl

webrepl.start()

gc.collect()

# dissable AP
import network

network.WLAN(network.AP_IF).active(False)

# connect wifi
import wifi

wifi.do_connect()

print('end boot.py execution')
