import unittest
from unittest.mock import MagicMock, patch

from quest.quest_manager import QuestManager
from quest.quests import doors
from quest_bot.quest_player_manager import QuestPlayerManager


@patch('twitch.player_manager.PlayerManager.save_player_data')
class TestDoors(unittest.TestCase):
    def setUp(self):
        bot = MagicMock()
        with patch('twitch.player_manager.PlayerManager.load_player_stats_from_db'):
            self.player_manager = QuestPlayerManager(bot)
        self.channel = MagicMock()
        self.channel.channel_manager.bot.player_manager = self.player_manager
        self.starting_gold = 1000
        self.starting_exp = 100

        self.player1 = 'Player1'
        self.party = [self.player1]
        with patch('twitch.player_manager.PlayerManager.save_player_data'):
            self.player_manager.reward(self.party, gold=self.starting_gold, exp=self.starting_exp)

        self.quest_manager = QuestManager(self.channel)
        self.quest_manager.party = self.party
        self.quest = doors.Doors(self.quest_manager)

    def test_timeout(self, _):
        self.quest_manager.start_quest(self.quest)

        # Simulate timing out and the callback for quest_advance getting called
        self.quest_manager.kill_quest_advance_timer()
        with patch('quest.quests.doors.randint', return_value=0):
            self.quest_manager.quest_advance()

        self.assertEqual(self.player_manager.get_gold(self.player1), self.starting_gold - doors.GOLD_TIMEOUT_PENALTY)
        self.assertEqual(self.player_manager.get_exp(self.player1), self.starting_exp)

    def test_win(self, _):
        self.quest_manager.start_quest(self.quest)

        with patch('quest.quests.doors.getrandbits', return_value=1):
            with patch('quest.quests.doors.randint', return_value=0):
                self.quest_manager.commands.execute_command(self.player1, '!left')

        self.assertEqual(self.player_manager.get_gold(self.player1), self.starting_gold + doors.GOLD_REWARD)
        self.assertEqual(self.player_manager.get_exp(self.player1), self.starting_exp + doors.EXP_REWARD)

    def test_lose(self, _):
        self.quest_manager.start_quest(self.quest)

        with patch('quest.quests.doors.getrandbits', return_value=0):
            with patch('quest.quests.doors.randint', return_value=0):
                self.quest_manager.commands.execute_command(self.player1, '!right')

        self.assertEqual(self.player_manager.get_gold(self.player1), self.starting_gold - doors.GOLD_REWARD)
        self.assertEqual(self.player_manager.get_exp(self.player1), self.starting_exp)

if __name__ == '__main__':
    unittest.main()
