import unittest
from unittest.mock import MagicMock, patch
patch.object = patch.object

from twitch.twitch_bot import TwitchBot


@patch('twitch.channel_manager.ChannelManager.save_channel_data')
class TestQuestBot(unittest.TestCase):
    def setUp(self):
        self.socket_mock = MagicMock()
        self.player_manager_mock = MagicMock()

        with patch('twitch.channel_manager.ChannelManager.load_settings_from_db'):
            with patch('twitch.twitch_bot.PlayerManager', return_value=self.player_manager_mock):
                with patch('utils.irc_bot.socket.socket', return_value=self.socket_mock):
                    self.bot = TwitchBot('BotName', 'OwnerName', 'oauth:something')

    @patch.object(TwitchBot, 'join_channel')
    def test_login(self, join_channel_mock, _):
        self.bot.connect()

        self.assertEqual(join_channel_mock.call_count, 2, 'Should join broadcaster and bot channels.')
        self.assertEqual(len(self.bot.channel_manager.channels), 2,
                         'ChannelManager should have broadcaster and bot channels.')
        self.assertEqual(self.socket_mock.connect.call_count, 1, 'Never tried connecting.')
        self.assertGreater(self.socket_mock.send.call_count, 0, 'Login info not sent properly.')

    @patch.object(TwitchBot, 'join_channel')
    def test_join_channels(self, join_channel_mock, _):
        self.assertEqual(join_channel_mock.call_count, 0, 'Should not join channels before connecting.')

        self.bot.channel_manager.join_channel('Enabled1')
        self.bot.channel_manager.join_channel('Enabled2')
        self.bot.channel_manager.join_channel('Disabled')
        self.bot.channel_manager.leave_channel('Disabled')
        pre_connect_joined = 3
        self.assertEqual(join_channel_mock.call_count, pre_connect_joined, 'Should join two channels.')
        self.assertEqual(len(self.bot.channel_manager.channels), 3,
                         'ChannelManager should have 2 enabled channels and 1 disabled channel.')
        self.bot.connect()
        connect_joined = 4
        self.assertEqual(join_channel_mock.call_count, pre_connect_joined + connect_joined,
                         'Connecting should join broadcaster, bot, and 2 enabled channels.')
        self.assertEqual(len(self.bot.channel_manager.channels), 5,
                         'ChannelManager should have broadcaster, bot, 2 enabled channels, and 1 disabled channel.')
        self.bot.channel_manager.join_channel('Enabled1')
        self.bot.channel_manager.join_channel('Enabled2')
        self.bot.channel_manager.join_channel('Enabled3')
        self.bot.channel_manager.join_channel('Enabled4')
        self.bot.channel_manager.leave_channel('Enabled1')

        self.assertEqual(len(self.bot.channel_manager.channels), 7,
                         'ChannelManager should have broadcaster, bot, 3 enabled channels and 2 disabled channel.')
        self.assertEqual(self.socket_mock.connect.call_count, 1, 'Never tried connecting.')
        self.assertGreater(self.socket_mock.send.call_count, 0, 'Login info not sent properly.')

    def test_invalid_login(self, _):
        self.assertRaises(RuntimeError, lambda: self.bot.handle_msg(':tmi.twitch.tv NOTICE * :Login unsuccessful'))

    def test_ping_pong(self, _):
        pong_mock = MagicMock()
        self.bot.send_pong = pong_mock
        self.bot.handle_msg('PING :some.server.com')

        self.assertEqual(pong_mock.call_count, 1, 'Pong not sent after receiving ping.')


if __name__ == '__main__':
    unittest.main()
