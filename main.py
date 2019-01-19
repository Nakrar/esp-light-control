import time
import gc

time.sleep(3)
gc.collect()

import web_server
import endpoints

endpoints.register()


def main():
    while True:
        gc.collect()

        try:
            web_server.accept_request()
        except Exception as e:
            print('Exception {}'.format(e))


main()
