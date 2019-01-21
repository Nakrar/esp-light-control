import time
import web_server

import endpoints

endpoints.register()


def main():
    server = web_server.Server()

    while True:
        try:
            server.accept_request()
        except Exception as e:
            print('Exception {}'.format(e))
        print('new cycle')
        time.sleep(0.01)

main()
