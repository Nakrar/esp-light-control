# upip.install('micropython-logging')
import logging

from constants import DEBUG_IP, NORMAL_IP

logging.basicConfig(level=logging.INFO)

import network

import time

import led
import web_server
import ws_server
from web_socket import WsClient

import endpoints

endpoints.register()

NO_CONN_SLEEP_THRESHOLD_MS = 15000


def main(critical_enabled=True):
    ip = network.WLAN(network.STA_IF).ifconfig()[0]

    if ip == NORMAL_IP:
        logging.info('Normal mode')
    elif ip == DEBUG_IP:
        logging.info('Debug mode')
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.info('Critical mode. '
                     + 'Exit...' if critical_enabled else 'Override enabled, continue...')
        if critical_enabled:
            return

    logging.debug('startind http server')
    http_s = web_server.Server(blocking=False)

    logging.debug('startind ws server')
    ws_s = ws_server.WebServer(ws_client=WsClient)
    ws_s.start(8080)

    last_conn = time.ticks_ms()

    try:
        while True:
            logging.debug('main cycle start')
            work_done = ws_s.process_clients()
            if work_done:
                last_conn = time.ticks_ms()
            else:
                ws_s.process_new_connections()
                http_s.accept_request()

                if time.ticks_diff(time.ticks_ms(), last_conn) > NO_CONN_SLEEP_THRESHOLD_MS:
                    # required for WEB repl on ESP32
                    logging.info('sleep')
                    time.sleep_ms(100)
            logging.debug('main cycle end')

    except BaseException as e:
        logging.warning('Exception {}'.format(e))
        http_s.stop()
        ws_s.stop()
        raise e

    # print('new cycle')
    # time.sleep_ms(10)


# off by default on esp32
led.on()

main()
