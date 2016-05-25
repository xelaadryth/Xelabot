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

    def test_prestige_gold(self, _):
        self.assertFalse(self.player_manager.prestige(self.new_player))
        self.player_manager.players[self.new_player.lower()]['prestige'] = 1
        self.player_manager.add_gold(self.new_player, 128)
        self.assertGreater(self.player_manager.get_gold(self.new_player), 128)

    def test_rewards(self, _):
        item = 'ItemName'
        missing_item = 'NonexistentItem'
        self.player_manager.reward(self.new_player, gold=64, exp=100, item=[item, item, item], prestige_benefits=True)
        self.assertEqual(self.player_manager.get_gold(self.new_player), 64)
        self.assertEqual(self.player_manager.get_exp(self.new_player), 100)
        level = self.player_manager.get_level(self.new_player)
        self.assertGreater(level, 1)
        self.assertLess(level, 30)
        items = self.player_manager.get_items(self.new_player)
        self.assertEqual(items[item], 3)
        self.assertNotIn(missing_item, items)
        self.assertEqual(items[missing_item], 0)

        self.player_manager.penalize(self.new_player, 32, 25, item=[item, missing_item, item], prestige_benefits=True)
        self.assertEqual(self.player_manager.get_gold(self.new_player), 32)
        self.assertEqual(self.player_manager.get_exp(self.new_player), 75)
        items = self.player_manager.get_items(self.new_player)
        self.assertEqual(items[item], 1)
        self.assertNotIn(missing_item, items)

        self.player_manager.penalize(self.new_player, 32, 25, item=item, prestige_benefits=True)
        self.assertEqual(self.player_manager.get_gold(self.new_player), 0)
        self.assertEqual(self.player_manager.get_exp(self.new_player), 50)
        items = self.player_manager.get_items(self.new_player)
        self.assertNotIn(item, items)
        self.assertNotIn(missing_item, items)
        self.assertEqual(items[item], 0)
        self.assertEqual(items[missing_item], 0)


if __name__ == '__main__':
    unittest.main()
