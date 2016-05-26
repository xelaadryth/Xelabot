import unittest
from unittest.mock import MagicMock, patch

from quest.quest_manager import QuestManager
from quest.quests import gates
from quest_bot.quest_player_manager import QuestPlayerManager


@patch('twitch.player_manager.PlayerManager.save_player_data')
class TestGates(unittest.TestCase):
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
        self.quest = gates.Gates(self.quest_manager)

    def test_timeout_frostguard(self, _):
        self.quest_manager.start_quest(self.quest)

        # Simulate timing out and the callback for quest_advance getting called
        self.quest_manager.kill_quest_advance_timer()
        with patch('quest.quests.gates.randint', return_value=0):
            self.quest_manager.quest_advance()

        for player in self.party:
            self.assertEqual(self.player_manager.get_gold(player), self.starting_gold + gates.GOLD_REWARD_BIG)
            self.assertEqual(self.player_manager.get_exp(player), self.starting_exp + gates.EXP_REWARD_BIG)

    def test_timeout_fail(self, _):
        self.quest_manager.start_quest(self.quest)

        self.quest_manager.commands.execute_command(self.player1, '!north')
        self.quest_manager.commands.execute_command(self.player2, '!east')
        self.quest_manager.commands.execute_command(self.player1, '!south')
        self.quest_manager.commands.execute_command(self.player3, '!west')
        self.quest_manager.commands.execute_command(self.player4, '!west')
        self.quest_manager.commands.execute_command(self.player1, '!east')
        self.quest_manager.commands.execute_command(self.player1, '!west')
        self.quest_manager.commands.execute_command(self.player2, '!south')
        for player in self.party:
            self.assertEqual(self.player_manager.get_gold(player), self.starting_gold)
            self.assertEqual(self.player_manager.get_exp(player), self.starting_exp)

        # Simulate timing out and the callback for quest_advance getting called
        self.quest_manager.kill_quest_advance_timer()
        with patch('quest.quests.gates.randint', return_value=0):
            self.quest_manager.quest_advance()

        for player in self.party:
            self.assertEqual(self.player_manager.get_gold(player), self.starting_gold - gates.GOLD_PENALTY)
            self.assertEqual(self.player_manager.get_exp(player), self.starting_exp)

    def test_success(self, _):
        self.quest_manager.start_quest(self.quest)

        self.quest_manager.commands.execute_command(self.player1, '!north')
        self.quest_manager.commands.execute_command(self.player2, '!east')
        self.quest_manager.commands.execute_command(self.player1, '!south')
        self.quest_manager.commands.execute_command(self.player3, '!west')
        self.quest_manager.commands.execute_command(self.player1, '!east')
        self.quest_manager.commands.execute_command(self.player1, '!west')
        self.quest_manager.commands.execute_command(self.player2, '!south')
        for player in self.party:
            self.assertEqual(self.player_manager.get_gold(player), self.starting_gold)
            self.assertEqual(self.player_manager.get_exp(player), self.starting_exp)
        with patch('quest.quests.gates.randint', return_value=0):
            self.quest_manager.commands.execute_command(self.player4, '!south')

        for player in self.party:
            self.assertEqual(self.player_manager.get_gold(player), self.starting_gold + gates.GOLD_REWARD)
            self.assertEqual(self.player_manager.get_exp(player), self.starting_exp + gates.EXP_REWARD)

    def test_fail(self, _):
        self.quest_manager.start_quest(self.quest)

        self.quest_manager.commands.execute_command(self.player1, '!north')
        self.quest_manager.commands.execute_command(self.player2, '!east')
        self.quest_manager.commands.execute_command(self.player1, '!south')
        self.quest_manager.commands.execute_command(self.player3, '!west')
        self.quest_manager.commands.execute_command(self.player1, '!east')
        self.quest_manager.commands.execute_command(self.player1, '!west')
        self.quest_manager.commands.execute_command(self.player2, '!south')
        self.quest_manager.commands.execute_command(self.player4, '!east')
        for player in self.party:
            self.assertEqual(self.player_manager.get_gold(player), self.starting_gold)
            self.assertEqual(self.player_manager.get_exp(player), self.starting_exp)
        with patch('quest.quests.gates.randint', return_value=0):
            self.quest_manager.commands.execute_command(self.player5, '!east')

        for player in self.party:
            self.assertEqual(self.player_manager.get_gold(player), self.starting_gold - gates.GOLD_PENALTY)
            self.assertEqual(self.player_manager.get_exp(player), self.starting_exp)




if __name__ == '__main__':
    unittest.main()
