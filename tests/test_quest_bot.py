import unittest
from unittest.mock import MagicMock, patch
patch.object = patch.object

from utils.irc_bot import IRCBot


class TestQuestBot(unittest.TestCase):
    def setUp(self):
        self.socket_mock = MagicMock()
        with patch('utils.irc_bot.socket.socket', return_value=self.socket_mock):
            self.bot = IRCBot('BotName', 'oauth:something')

    def test_login(self):
        self.bot.connect()

        self.assertEqual(self.socket_mock.connect.call_count, 1, 'Never tried connecting.')
        self.assertGreater(self.socket_mock.send.call_count, 0, 'Login info not sent properly.')

    @patch.object(IRCBot, 'login_failure')
    def test_invalid_login(self, login_failure_mock):
        self.bot.handle_msg(':tmi.twitch.tv NOTICE * :Login unsuccessful')

        self.assertEqual(login_failure_mock.call_count, 1, 'Unsuccessful login not handled.')

    def test_ping_pong(self):
        pong_mock = MagicMock()
        self.bot.send_pong = pong_mock
        self.bot.handle_msg('PING :some.server.com')

        self.assertEqual(pong_mock.call_count, 1, 'Pong not sent after receiving ping.')


if __name__ == '__main__':
    unittest.main()
