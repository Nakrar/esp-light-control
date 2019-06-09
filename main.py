import time

import led
import web_server
import ws_server
from web_socket import WsClient

import endpoints
endpoints.register()

# upip.install('micropython-logging')
import logging
logging.basicConfig(level=logging.DEBUG)

NO_CONN_SLEEP_THRESHOLD_MS = 15000


def main():
    logging.debug('startind http server')
    http_s = web_server.Server(blocking=False)

    logging.debug('startind ws server')
    ws_s = ws_server.WebServer(ws_client=WsClient)
    ws_s.start(8080)

    last_conn = time.ticks_ms()

    try:
        while True:
            logging.debug('main cycle start')
            is_any_ws_conn = ws_s.process_clients()
            if not is_any_ws_conn:
                last_conn = time.ticks_ms()
            else:
                ws_s.process_new_connections()
                http_s.accept_request()

                if time.ticks_diff(time.ticks_ms(), last_conn) > NO_CONN_SLEEP_THRESHOLD_MS:
                    # required for WEB repl on ESP32
                    logging.basicConfig(level=logging.INFO)
                    logging.info('sleep')
                    time.sleep_ms(100)
            logging.debug('main cycle end')

    except BaseException as e:
        print('Exception {}'.format(e))
        http_s.stop()
        ws_s.stop()
        raise e

    # print('new cycle')
    # time.sleep_ms(10)


# off by default on esp32
led.on()

main()
