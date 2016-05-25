import unittest
from unittest.mock import MagicMock, patch
patch.object = patch.object

from utils.irc_bot import IRCBot


class TestQuestBot(unittest.TestCase):
    def setUp(self):
        self.bot = IRCBot('BotName', 'oauth:something')

    def test_login(self):
        self.bot.irc_sock = MagicMock()
        self.bot.connect()

        self.assertEquals(self.bot.irc_sock.connect.call_count, 1, 'Never tried connecting.')
        self.assertGreater(self.bot.irc_sock.send.call_count, 0, 'Login info not sent properly.')

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
