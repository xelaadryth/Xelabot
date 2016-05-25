import unittest
from unittest.mock import MagicMock, patch

from quest.quest_manager import QuestManager
from quest.quests import duel
from quest_bot.quest_player_manager import QuestPlayerManager


@patch('twitch.player_manager.PlayerManager.save_player_data')
class TestDuel(unittest.TestCase):
    def setUp(self):
        bot = MagicMock()
        with patch('os.makedirs'):
            with patch('os.listdir'):
                self.player_manager = QuestPlayerManager(bot)
        self.channel = MagicMock()
        self.channel.channel_manager.bot.player_manager = self.player_manager
        self.starting_gold = 1000
        self.starting_exp = 100

        self.player1 = 'Player1'
        self.player2 = 'Player2'
        self.party = [self.player1, self.player2]
        with patch('twitch.player_manager.PlayerManager.save_player_data'):
            self.player_manager.reward(self.party, gold=self.starting_gold, exp=self.starting_exp)

        self.quest_manager = QuestManager(self.channel)
        self.quest_manager.party = self.party
        self.quest = duel.Duel(self.quest_manager)

    def test_timeout(self, _):
        self.quest_manager.start_quest(self.quest)

        # Simulate timing out and the callback for quest_advance getting called
        self.quest_manager.kill_quest_advance_timer()
        with patch('quest.quests.duel.randint', return_value=0):
            self.quest_manager.quest_advance()

        self.assertEqual(self.player_manager.get_gold(self.player1), self.starting_gold)
        self.assertEqual(self.player_manager.get_gold(self.player2), self.starting_gold)
        self.assertEqual(self.player_manager.get_exp(self.player1), self.starting_exp + duel.EXP_PACIFIST_REWARD)
        self.assertEqual(self.player_manager.get_exp(self.player2), self.starting_exp + duel.EXP_PACIFIST_REWARD)

    def test_attack(self, _):
        self.quest_manager.start_quest(self.quest)

        with patch('quest.quests.duel.randint', return_value=0):
            self.quest_manager.commands.execute_command(self.player1, self.quest.duel_word)

        self.assertEqual(self.player_manager.get_gold(self.player1), self.starting_gold + duel.GOLD_REWARD)
        self.assertEqual(self.player_manager.get_gold(self.player2), self.starting_gold - duel.GOLD_REWARD)
        self.assertEqual(self.player_manager.get_exp(self.player1), self.starting_exp + duel.EXP_REWARD)
        self.assertEqual(self.player_manager.get_exp(self.player2), self.starting_exp)




if __name__ == '__main__':
    unittest.main()
