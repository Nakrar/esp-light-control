import socket
import gc

import led
from routes import ROUTES

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(1)

RESPONSE_200 = b'HTTP/1.1 200 OK\n'
RESPONSE_204 = b'HTTP/1.1 200 NO CONTENT\n'
RESPONSE_404 = b'HTTP/1.1 404 NOT FOUND\n'
RESPONSE_500 = b'HTTP/1.1 500 INTERNAL SERVER ERROR\n'


def parse_requset(conn):
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


def process_request(request):
    body = None
    if request:
        path = request['path']
        handler = ROUTES.get(path)

        if not handler:
            # 404
            return RESPONSE_404, None

        try:
            body = handler(request)
        except Exception as e:
            # 500
            return RESPONSE_500, str(e).encode()
    # 200
    return RESPONSE_200, body


def accept_request():
    conn, addr = s.accept()

    led.blink(100)

    request = parse_requset(conn)

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
        headers = b'Content-Type: text/html; encoding=utf8\n' +\
        'Content-Length: {}\n'.format(len(body)).encode() +\
        b'Connection: close\n'

        conn.send(headers)
        conn.send(b'\n')
        conn.send(body)

    conn.close()
    gc.collect()


if __name__ == '__main__':
    from endpoints import *
    while True:
        try:
            accept_request()
        except Exception as e:
            print('Exception {}'.format(e))

