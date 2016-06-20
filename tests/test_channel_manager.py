import unittest
from unittest.mock import MagicMock, patch

from twitch.channel_manager import ChannelManager


class TestChannelManager(unittest.TestCase):
    def setUp(self):
        channel_save_patcher = patch('twitch.channel_manager.ChannelManager.save_channel_data')
        channel_load_patcher = patch('twitch.channel_manager.ChannelManager.load_channel_data')
        for patcher in [channel_save_patcher, channel_load_patcher]:
            patcher.start()
            self.addCleanup(patcher.stop)

        bot = MagicMock()
        self.channel_manager = ChannelManager(bot)

    def test_chatters(self):
        # Requires internet!
        chatters = self.channel_manager.get_chatters('Xelaadryth')
        self.channel_manager.get_moderators('Xelaadryth')
        self.channel_manager.get_viewers('Xelaadryth')
        self.assertIn('chatters', chatters, 'Chatters not in chatters response.')
        self.assertIn('moderators', chatters['chatters'], 'Moderators not in chatters response.')
        self.assertIn('viewers', chatters['chatters'], 'Moderators not in chatters response.')


if __name__ == '__main__':
    unittest.main()
