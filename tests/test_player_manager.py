import unittest
from unittest.mock import MagicMock, patch

from quest_bot.quest_player_manager import QuestPlayerManager


@patch('twitch.player_manager.PlayerManager.save_player_data')
class TestPlayerManager(unittest.TestCase):
    def setUp(self):
        bot = MagicMock()
        with patch('os.makedirs'):
            with patch('os.listdir'):
                self.player_manager = QuestPlayerManager(bot)

        self.existing_player = 'Existing_Player'
        self.new_player = 'New_Player'

        with patch('twitch.player_manager.PlayerManager.save_player_data'):
            self.player_manager.add_gold(self.existing_player, 256)

    def test_default_player(self, _):
        self.assertEqual(self.player_manager.get_gold(self.existing_player), 256)
        self.assertEqual(self.player_manager.get_exp(self.existing_player), 0)

        self.assertEqual(self.player_manager.get_gold(self.new_player), 0)
        self.assertEqual(self.player_manager.get_exp(self.new_player), 0)

    def test_gold(self, _):
        self.player_manager.add_gold(self.new_player, 128)
        self.assertEqual(self.player_manager.get_gold(self.new_player), 128)
        self.assertEqual(self.player_manager.get_exp(self.new_player), 0)

        self.player_manager.add_gold(self.new_player, -64)
        self.assertEqual(self.player_manager.get_gold(self.new_player), 64)
        self.assertEqual(self.player_manager.get_exp(self.new_player), 0)

        self.player_manager.add_gold(self.new_player, -77)
        self.assertEqual(self.player_manager.get_gold(self.new_player), 0)
        self.assertEqual(self.player_manager.get_exp(self.new_player), 0)

    def test_rewards(self, _):
        self.player_manager.reward(self.new_player, gold=64, exp=100, item='ItemName', prestige_benefits=False)
        self.assertEqual(self.player_manager.get_gold(self.new_player), 64)
        self.assertEqual(self.player_manager.get_exp(self.new_player), 100)
        level = self.player_manager.get_level(self.new_player)
        self.assertGreater(level, 1)
        self.assertLess(level, 30)


if __name__ == '__main__':
    unittest.main()
