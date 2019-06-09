import time

import led
import web_server
import web_socket

import endpoints

endpoints.register()

NO_CONN_SLEEP_THRESHOLD_MS = 15000


def main():
    server = web_server.Server(blocking=False)
    ws_server = web_socket.TestServer()
    ws_server.start(8080)

    last_conn = time.ticks_ms()

    try:
        while True:
            is_any_ws_conn = ws_server.process_clients()
            if not is_any_ws_conn:
                last_conn = time.ticks_ms()
            else:
                ws_server.process_new_connections()
                server.accept_request()

                if time.ticks_diff(time.ticks_ms(), last_conn) > NO_CONN_SLEEP_THRESHOLD_MS:
                    # required for WEB repl on ESP32
                    print('sleep')
                    time.sleep_ms(100)

    except BaseException as e:
        print('Exception {}'.format(e))
        server.stop()
        ws_server.stop()
        raise e

    # print('new cycle')
    # time.sleep_ms(10)


# off by default on esp32
led.on()

main()
