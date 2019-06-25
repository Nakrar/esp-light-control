# based on https://github.com/BetaRavener/upy-websocket-server
import binascii
import gc
import hashlib
import logging
import os
import socket
import sys

import network
import uselect
from time import sleep

import routes
from constants import RESPONSE_204, RESPONSE_404, RESPONSE_500, RESPONSE_200
from ws_connection import WebSocketConnection, ClientClosedError


class WebSocketClient:
    def __init__(self, conn):
        self.connection = conn

    def process(self):
        try:
            msg = self.connection.read()
            if not msg:
                return False
            self._process(msg)
            return True
        except ClientClosedError:
            # just print exception, so execution would continue normally
            self.connection.close()
            logging.info('ClientClosedError')
        except Exception as e:
            self.connection.close()
            raise e

    def _process(self, msg):
        raise NotImplementedError


class WebServer:
    def __init__(self, max_connections=2, ws_client=WebSocketClient):
        self._listen_s = None
        self._listen_poll = None
        self._clients = []
        self._max_connections = max_connections
        self._ws_client = ws_client

    def _setup_conn(self, port):
        logging.debug("ws _setup_conn")
        self._listen_s = socket.socket()
        self._listen_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._listen_poll = uselect.poll()

        # bind it to ("0.0.0.0", port)
        ai = socket.getaddrinfo("0.0.0.0", port)
        addr = ai[0][4]
        self._listen_s.bind(addr)

        self._listen_s.listen(0)
        self._listen_poll.register(self._listen_s)

        # print address for AccessPoint and Station modes
        for i in (network.AP_IF, network.STA_IF):
            iface = network.WLAN(i)
            if iface.active():
                logging.info("Web started on ws://%s:%d" % (iface.ifconfig()[0], port))

    def _check_new_connections(self):
        poll_events = self._listen_poll.poll(0)
        if not poll_events:
            return

        #  take first (file descriptor, event) and event from there
        if poll_events[0][1] & uselect.POLLIN:
            self._accept_conn()

    def _accept_conn(self):
        logging.debug("ws _accept_conn")
        conn, remote_addr = self._listen_s.accept()
        logging.info("Client connection from: {}".format(remote_addr))

        if len(self._clients) >= self._max_connections:
            # Maximum connections limit reached
            conn.setblocking(True)
            conn.sendall("HTTP/1.1 503 Too many connections\n\n")
            conn.sendall("\n")
            # TODO: Make sure the data is sent before closing
            sleep(0.1)
            conn.close()
            return

        conn.settimeout(1)
        data = parse_request_data(conn)
        webkey = data.get('webkey')

        if webkey:
            ws_server_handshake(conn, webkey)
            ws_conn = WebSocketConnection(remote_addr, conn, self.remove_connection)
            ws_client = self._ws_client(ws_conn)
            self._clients.append(ws_client)

        else:
            process_http_request(conn, data)
            conn.close()

    def stop(self):
        if self._listen_poll:
            self._listen_poll.unregister(self._listen_s)
        self._listen_poll = None
        if self._listen_s:
            self._listen_s.close()
        self._listen_s = None

        for client in self._clients:
            client.connection.close()
        logging.info("Stopped Web server.")

    def start(self, port=80):
        if self._listen_s:
            self.stop()
        self._setup_conn(port)
        logging.info("Started Web server.")

    def process_all(self):
        self.process_new_connections()
        self.process_clients()

    def process_new_connections(self):
        self._check_new_connections()

    def process_clients(self):
        logging.debug("ws process_clients")
        work_done = False
        for client in self._clients:
            work_done = client.process() or work_done
        return work_done

    def remove_connection(self, conn):
        logging.debug("ws remove_connection")
        for client in self._clients:
            if client.connection is conn:
                self._clients.remove(client)
                return


def get_handler(path):
    for x in range(path.count('/')):
        handler = routes.ROUTES.get(path)
        if handler:
            return handler
        sep_ind = path.rfind("/")
        path = path[:sep_ind + 1] + '*'

    return routes.ROUTES.get(path)


def process_request(request_data):
    logging.debug("process_request")

    body = None
    if request_data:
        handler = get_handler(request_data['path'])

        if not handler:
            # 404
            return RESPONSE_404, None

        try:
            body = handler(request_data)
        except Exception as e:
            # 500
            sys.print_exception(e)
            return RESPONSE_500, str(e).encode()
    # 200
    return RESPONSE_200, body


def process_http_request(conn, request_data):
    logging.debug("process_http_request")

    if request_data:
        response, body = process_request(request_data)
    else:
        response, body = RESPONSE_204, None

    if body:
        if type(body) != bytes:
            body = body.encode()
        headers = b'Content-Type: text/html; encoding=utf8\n' + \
                  'Content-Length: {}\n'.format(len(body)).encode() + \
                  b'Connection: close\n'

        response += headers + b'\n' + body

    try:
        conn.sendall(response)
    except OSError:
        # timeout
        pass


def ws_server_handshake(conn, webkey):
    # modified version of:
    # https://github.com/micropython/micropython/blob/master/ports/esp8266/modules/websocket_helper.py
    # purpose is to reuse initial data to serve HTTP, if not WS request

    d = hashlib.sha1(webkey)
    # todo change it?
    d.update(b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11")
    respkey = d.digest()
    respkey = binascii.b2a_base64(respkey)[:-1]

    try:
        conn.send(b"""\
HTTP/1.1 101 Switching Protocols\r
Upgrade: websocket\r
Connection: Upgrade\r
Sec-WebSocket-Accept: """)
        conn.send(respkey)
        conn.send("\r\n\r\n")
    except OSError:
        # timeout
        return


def parse_request_data(conn):
    # ['GET', '/', 'HTTP/1.1', 'Host:', '***REMOVED***', 'Upgrade:', 'websocket', 'Connection:', 'Upgrade',
    #  'Sec-WebSocket-Key:', 'fZ6G/yw4gc1roSlJcdkJJA==', 'Sec-WebSocket-Version:', '13', 'Sec-WebSocket-Extensions:',
    #  'permessage-deflate;', 'client_max_window_bits', 'User-Agent:', 'Python/3.7', 'websockets/7.0']

    try:
        conn_data = conn.recv(1024).decode().strip().split()
    except OSError:
        # timeout
        return {}

    if not conn_data:
        return {}

    data = {
        'method': conn_data[0]
    }

    path = conn_data[1]

    # extract separate URL path and query
    if '?' in path:
        data['args'] = {}
        path, args = conn_data[1].split('?', 1)

        for arg in args.split('&'):
            if '=' in arg:
                k, v = arg.split('=', 1)
                data['args'][k] = v
            else:
                data['args'][arg] = None

    data['path'] = path

    # extract webkey for WS handshake
    try:
        data['webkey'] = conn_data[conn_data.index('Sec-WebSocket-Key:') + 1]
    except ValueError:
        # conn_data.index fail
        pass

    return data
