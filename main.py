# upip.install('micropython-logging')
import logging

import animations
from constants import DEBUG_IP, NORMAL_IP

logging.basicConfig(level=logging.INFO)

import network

import time

import led
import web_server
from web_socket import WsClient

import endpoints

endpoints.register()

NO_CONN_SLEEP_THRESHOLD_MS = 1500


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

    logging.debug('startind ws server')
    ws_s = web_server.WebServer(ws_client=WsClient)
    ws_s.start(80)

    last_conn = time.ticks_ms()

    try:
        while True:
            logging.debug('main cycle start')
            work_done = ws_s.process_clients()
            if work_done:
                last_conn = time.ticks_ms()
            else:
                ws_s.process_new_connections()
                animations_left = animations.animation_cycle()
                if animations_left:
                    time.sleep(0.009)
                else:
                    if time.ticks_diff(time.ticks_ms(), last_conn) > NO_CONN_SLEEP_THRESHOLD_MS:
                        # required for WEB repl on ESP32
                        logging.debug('sleep')
                        time.sleep_ms(100)
            logging.debug('main cycle end')

    except BaseException as e:
        ws_s.stop()
        raise e


# off by default on esp32
led.on()

main()
