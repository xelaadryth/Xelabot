import unittest
from unittest.mock import MagicMock, patch

from quest.quest_manager import QuestManager
from quest.quests import prison
from quest_bot.quest_player_manager import QuestPlayerManager


@patch('twitch.player_manager.PlayerManager.save_player_data')
class TestPrison(unittest.TestCase):
    def setUp(self):
        bot = MagicMock()
        with patch('twitch.player_manager.PlayerManager.load_player_stats_from_db'):
            self.player_manager = QuestPlayerManager(bot)
        self.channel = MagicMock()
        self.channel.channel_manager.bot.player_manager = self.player_manager
        self.starting_gold = 1000
        self.starting_exp = 100

        self.player1 = 'Player1'
        self.player2 = 'Player2'
        self.player3 = 'Player3'
        self.player4 = 'Player4'
        self.player5 = 'Player5'
        self.party = [self.player1, self.player2, self.player3, self.player4, self.player5]
        with patch('twitch.player_manager.PlayerManager.save_player_data'):
            self.player_manager.reward(self.party, gold=self.starting_gold, exp=self.starting_exp)

        self.quest_manager = QuestManager(self.channel)
        self.quest_manager.party = self.party
        self.quest = prison.Prison(self.quest_manager)

    def test_timeout(self, _):
        self.quest_manager.start_quest(self.quest)

        # Simulate timing out and the callback for quest_advance getting called
        self.quest_manager.kill_quest_advance_timer()
        with patch('quest.quests.prison.randint', return_value=0):
            self.quest_manager.quest_advance()

        self.assertEqual(self.player_manager.get_gold(self.player1), self.starting_gold - prison.GOLD_PENALTY_WAIT)
        self.assertEqual(self.player_manager.get_exp(self.player1), self.starting_exp)

    def test_pick(self, _):
        self.quest_manager.start_quest(self.quest)

        self.quest_manager.commands.execute_command(self.player2, '!player1')
        self.quest_manager.commands.execute_command(self.player3, '!player1')
        self.quest_manager.commands.execute_command(self.player2, '!player2')
        self.assertEqual(self.player_manager.get_gold(self.player1), self.starting_gold)
        self.assertEqual(self.player_manager.get_gold(self.player2), self.starting_gold)
        with patch('quest.quests.prison.randint', return_value=0):
            self.quest_manager.commands.execute_command(self.player1, '!pLaYeR2')

        self.assertEqual(self.player_manager.get_gold(self.player1), self.starting_gold + prison.GOLD_REWARD)
        self.assertEqual(self.player_manager.get_gold(self.player2), self.starting_gold + prison.GOLD_REWARD)

        for player in self.quest.party[2:]:
            self.assertEqual(self.player_manager.get_gold(player), self.starting_gold - prison.GOLD_PENALTY)
            self.assertEqual(self.player_manager.get_exp(player), self.starting_exp)

if __name__ == '__main__':
    unittest.main()
