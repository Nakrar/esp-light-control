import unittest

import routes
import web_server


class WevServerHandlerTest(unittest.TestCase):

    def tearDown(self):
        routes.ROUTES.clear()

    def test_route_register(self):
        if len(routes.ROUTES) != 0:
            self.fail("there is endpoint where is should be empty")

        routes.register('test/route')(None)

        if 'test/route' not in routes.ROUTES:
            self.fail("there is no endpoint after adding it")

    def test_get_simple_handler(self):

        if web_server.get_handler('test/route') is not None:
            self.fail("there should not be any handler")

        @routes.register('test/route')
        def endpoint_test_route():
            pass

        if web_server.get_handler('test/route') is None:
            self.fail("there should be handler")

    def test_get_asterisk_handler(self):

        if web_server.get_handler('test/route') is not None:
            self.fail("there should not be any handler")

        @routes.register('test/*')
        def endpoint_test_route():
            pass

        if web_server.get_handler('test/un-registered-route') is None:
            self.fail("there should be handler")

        if web_server.get_handler('un-registered-route') is not None:
            self.fail("there should not be any handler")


