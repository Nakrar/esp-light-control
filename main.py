import time

import led
import web_server
import web_socket

import endpoints

endpoints.register()


def main():
    server = web_server.Server(blocking=False)
    ws_server = web_socket.TestServer()
    ws_server.start(8080)

    try:
        while True:
            ws_server.process_all()
            server.accept_request()
    except Exception as e:
        print('Exception {}'.format(e))
    server.stop()
    ws_server.stop()
    # print('new cycle')
    # time.sleep_ms(10)


led.off()

main()
