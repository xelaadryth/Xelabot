import unittest
from unittest.mock import MagicMock, patch

from quest_bot.quest_player_manager import QuestPlayerManager
import settings


@patch('twitch.player_manager.PlayerManager.save_player_data')
class TestPlayerManager(unittest.TestCase):
    def setUp(self):
        bot = MagicMock()
        with patch('twitch.player_manager.PlayerManager.load_player_stats_from_db'):
            self.player_manager = QuestPlayerManager(bot)

        self.existing_player = 'Existing_Player'
        self.new_player = 'New_Player'

        with patch('twitch.player_manager.PlayerManager.save_player_data'):
            self.player_manager.add_gold(self.existing_player, 256)

    def test_exp_to_level(self, _):
        self.assertEqual(self.player_manager.exp_to_level(0), 1)
        self.assertEqual(self.player_manager.exp_to_level(settings.EXP_LEVELS[1]), 1)
        self.assertEqual(self.player_manager.exp_to_level(settings.EXP_LEVELS[5]), 5)
        self.assertEqual(self.player_manager.exp_to_level(settings.EXP_LEVELS[settings.LEVEL_CAP]), settings.LEVEL_CAP)
        self.assertEqual(self.player_manager.exp_to_level(settings.EXP_LEVELS[settings.LEVEL_CAP] + 1),
                         settings.LEVEL_CAP)
        self.assertEqual(self.player_manager.exp_to_level(settings.EXP_LEVELS[settings.LEVEL_CAP] + 9999999),
                         settings.LEVEL_CAP)

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

    def test_prestige(self, _):
        self.assertFalse(self.player_manager.prestige(self.new_player))
        self.assertEqual(self.player_manager.get_prestige(self.new_player), 0)

        self.player_manager.reward(self.new_player, gold=settings.PRESTIGE_COST,
                                   exp=settings.EXP_LEVELS[settings.LEVEL_CAP], )
        self.player_manager.prestige(self.new_player)

        self.assertEqual(self.player_manager.get_prestige(self.new_player), 1)
        self.assertEqual(self.player_manager.get_gold(self.new_player), 0)
        self.assertEqual(self.player_manager.get_exp(self.new_player), 0)

        # Check gold increase rate bonus
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


if __name__ == '__main__':
    unittest.main()
