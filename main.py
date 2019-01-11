from endpoints import *
from web_server import accept_request

while True:
    try:
        accept_request()
    except Exception as e:
        print('Exception {}'.format(e))