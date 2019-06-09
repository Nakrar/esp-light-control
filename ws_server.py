# based on https://github.com/BetaRavener/upy-websocket-server
import logging
import os
import socket
import network
import websocket_helper
import uselect
from time import sleep
from ws_connection import WebSocketConnection, ClientClosedError


class WebSocketClient:
    def __init__(self, conn):
        self.connection = conn

    def process(self):
        try:
            msg = self.connection.read()
            if not msg:
                return
            self._process(msg)
            return True
        except ClientClosedError:
            self.connection.close()
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
                print("Web started on ws://%s:%d" % (iface.ifconfig()[0], port))

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
        print("Client connection from:", remote_addr)

        if len(self._clients) >= self._max_connections:
            # Maximum connections limit reached
            conn.setblocking(True)
            conn.sendall("HTTP/1.1 503 Too many connections\n\n")
            conn.sendall("\n")
            # TODO: Make sure the data is sent before closing
            sleep(0.1)
            conn.close()
            return

        # try establish websocket connection
        try:
            websocket_helper.server_handshake(conn)
        except OSError:
            # Not a websocket connection, serve webpage
            self._serve_page(conn)
            return

        ws_conn = WebSocketConnection(remote_addr, conn, self.remove_connection)
        ws_client = self._ws_client(ws_conn)
        self._clients.append(ws_client)

    def _serve_page(self, client):
        try:
            client.sendall('HTTP/1.1 202 OK\nConnection: close\nServer: Web Server\nContent-Type: text/html\n')
        except OSError:
            # Error while serving webpage
            pass
        client.close()

    def stop(self):
        if self._listen_poll:
            self._listen_poll.unregister(self._listen_s)
        self._listen_poll = None
        if self._listen_s:
            self._listen_s.close()
        self._listen_s = None

        for client in self._clients:
            client.connection.close()
        print("Stopped Web server.")

    def start(self, port=80):
        if self._listen_s:
            self.stop()
        self._setup_conn(port)
        print("Started Web server.")

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
