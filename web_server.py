import socket
import sys

import routes

RESPONSE_200 = b'HTTP/1.1 200 OK\n'
RESPONSE_204 = b'HTTP/1.1 200 NO CONTENT\n'
RESPONSE_404 = b'HTTP/1.1 404 NOT FOUND\n'
RESPONSE_500 = b'HTTP/1.1 500 INTERNAL SERVER ERROR\n'


class Server:

    def __init__(self, blocking=True):
        addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
        s = socket.socket()
        s.bind(addr)
        s.listen(1)
        s.setblocking(blocking)
        self.s = s

    def accept_request(self):
        try:
            conn, addr = self.s.accept()
        except Exception:
            # todo make proper exception
            return

        request = parse_request(conn)

        if request:
            response, body = process_request(request)
        else:
            response, body = RESPONSE_204, None

        # reply as server
        conn.send(response)

        # send headers and body
        if body:
            if type(body) != bytes:
                body = body.encode()
            headers = b'Content-Type: text/html; encoding=utf8\n' + \
                      'Content-Length: {}\n'.format(len(body)).encode() + \
                      b'Connection: close\n'

            conn.send(headers)
            conn.send(b'\n')
            conn.send(body)

        conn.close()


def parse_request(conn):
    conn_data = conn.recv(1024).decode().strip().split()

    if not conn_data:
        return {}

    path_args = conn_data[1].split('?', 1)

    request = {
        'method': conn_data[0],
        'path': path_args[0],
        'args': {},
    }

    try:
        args_str = path_args[1]
    except IndexError:
        args_str = None

    if args_str is not None:
        for arg_str in args_str.split('&'):
            arg = arg_str.split('=', 1)
            if len(arg) > 1:
                value = arg[1]
            else:
                value = None
            request['args'][arg[0]] = value

    print(request)
    return request


def get_handler(path):
    for x in range(path.count('/')):
        handler = routes.ROUTES.get(path)
        if handler:
            return handler
        sep_ind = path.rfind("/")
        path = path[:sep_ind + 1] + '*'

    return routes.ROUTES.get(path)


def process_request(request):
    body = None
    if request:
        handler = get_handler(request['path'])

        if not handler:
            # 404
            return RESPONSE_404, None

        try:
            body = handler(request)
        except Exception as e:
            # 500
            sys.print_exception(e)
            return RESPONSE_500, str(e).encode()
    # 200
    return RESPONSE_200, body
