# This file is executed on every boot (including wake-boot from deepsleep)

# import esp
# esp.osdebug(None)

print('start boot.py execution')

# activate webrepl
import webrepl

webrepl.start()

import wifi

wifi.do_connect()
print('do wifi.disable_ap')
wifi.disable_ap()

print('end boot.py execution')
