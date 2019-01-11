import time
import gc

time.sleep(3)
gc.collect()

import web_server

while True:
    gc.collect()

    try:
        web_server.accept_request()
    except Exception as e:
        print('Exception {}'.format(e))
