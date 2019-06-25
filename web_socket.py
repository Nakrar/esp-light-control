import strips
from web_server import WebSocketClient


class WsClient(WebSocketClient):
    def __init__(self, conn):
        super().__init__(conn)
        self.rgb = strips.STRIPS.get('rgb')

    def _process(self, msg):
        # msg starts with . and ends with #
        msg = msg.split(b'.')[-1].split(b'#')[0]
        color = tuple(int(x, 10) for x in msg.split(b' '))
        # https://github.com/micropython/micropython/blob/master/ports/esp8266/modules/neopixel.py
        part = int(strips.RGB_COUNT / 6)
        self.rgb._np.buf = bytearray((color[1], color[0], color[2]) * part) + \
                           bytearray((color[4], color[3], color[5]) * part * 2) + \
                           bytearray((color[7], color[6], color[8]) * part * 3)
        self.rgb._np.write()
