from __future__ import absolute_import
import mock
import unittest
from typing import Any
from zulip_botserver import server
from .server_test_lib import BotServerTestCase

class BotServerTests(BotServerTestCase):
    class MockMessageHandler(object):
        def handle_message(self, message, bot_handler):
            # type: (Any, Any, Any) -> None
            assert message == {'key': "test message"}

    class MockLibModule(object):
        def handler_class(self):
            # type: () -> Any
            return BotServerTests.MockMessageHandler()

    @mock.patch('zulip_botserver.server.ExternalBotHandler')
    def test_successful_request(self, mock_ExternalBotHandler):
        # type: (mock.Mock) -> None
        available_bots = ['helloworld']
        bots_config = {
            'helloworld': {
                'email': 'helloworld-bot@zulip.com',
                'key': '123456789qwertyuiop',
                'site': 'http://localhost',
            }
        }
        self.assert_bot_server_response(available_bots=available_bots,
                                        bots_config=bots_config,
                                        check_success=True)

    def test_bot_module_not_exists(self):
        # type: () -> None
        self.assert_bot_server_response(available_bots=[],
                                        payload_url="/bots/not_supported_bot",
                                        check_success=False)

    @mock.patch('logging.error')
    def test_wrong_bot_credentials(self, mock_LoggingError):
        # type: (mock.Mock) -> None
        available_bots = ['helloworld']
        bots_config = {
            'helloworld': {
                'email': 'helloworld-bot@zulip.com',
                'key': '123456789qwertyuiop',
                'site': 'http://localhost',
            }
        }
        server.available_bots = available_bots
        server.load_bot_handlers()
        mock_LoggingError.assert_called_with("Cannot fetch user profile, make sure you have set up the zuliprc file correctly.")


if __name__ == '__main__':
    unittest.main()
