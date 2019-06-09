import strips
from ws_connection import ClientClosedError
from ws_server import WebServer, WebSocketClient


class WsClient(WebSocketClient):
    def __init__(self, conn):
        super().__init__(conn)
        self.rgb = strips.STRIPS.get('rgb')

    def _process(self, msg):
        msg = msg.decode("utf-8")
        items = msg.split(" ")
        cmd = items[0]
        if cmd == "Hello":
            self.connection.write(cmd + " World")
            print("Hello World")
        if cmd == "rgb":
            if len(items) == 4:
                color = tuple(int(x) for x in items[1:])
                self.rgb._np.fill(color)
                self.rgb._np.write()
        if cmd == "rgbf":
            # https://github.com/micropython/micropython/blob/master/ports/esp8266/modules/neopixel.py
            if len(items) == 4:
                color = tuple(int(x) for x in items[1:])
                self.rgb._np.buf = bytearray((color[1], color[0], color[2]) * strips.RGB_COUNT)
                self.rgb._np.write()
            elif len(items) == 10:
                color = tuple(int(x) for x in items[1:])
                part = int(strips.RGB_COUNT / 6)
                self.rgb._np.buf = bytearray((color[1], color[0], color[2]) * part) + \
                                   bytearray((color[4], color[3], color[5]) * part * 2) + \
                                   bytearray((color[7], color[6], color[8]) * part * 3)
                self.rgb._np.write()
        if cmd == "rgbd":
            print(items)
            if len(items) == 4:
                color = tuple(int(x) for x in items[1:])
                self.rgb._np.fill(color)
                self.rgb._np.write()
                self.connection.write('set')
