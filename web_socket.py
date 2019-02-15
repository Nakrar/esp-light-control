
import strips
from ws_connection import ClientClosedError
from ws_server import WebSocketServer, WebSocketClient


class TestClient(WebSocketClient):
    def __init__(self, conn):
        super().__init__(conn)
        self.rgb = strips.STRIPS.get('rgb')

    def process(self):
        try:
            msg = self.connection.read()
            if not msg:
                return
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
                    self.rgb._np.fill(color)
                    self.rgb._np.write()
            if cmd == "rgbd":
                print(items)
                if len(items) == 4:
                    color = tuple(int(x) for x in items[1:])
                    self.rgb._np.fill(color)
                    self.rgb._np.write()
                    self.connection.write('set')
        except Exception as e:
            self.connection.close()
            raise e


class TestServer(WebSocketServer):
    def __init__(self):
        super().__init__(None, 2)

    def _make_client(self, conn):
        return TestClient(conn)
