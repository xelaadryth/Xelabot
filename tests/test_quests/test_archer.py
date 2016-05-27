import unittest
from unittest.mock import patch

from quest.quests import archer
from tests.test_quests.base_class import TestBase


@patch('twitch.player_manager.PlayerManager.save_player_data')
class TestArcher(TestBase):
    quest_constructor = archer.Archer
    num_start_players = 2

    def test_timeout(self, _):
        self.quest_manager.start_quest(self.quest)

        # Simulate timing out and the callback for quest_advance getting called
        self.quest_manager.kill_quest_advance_timer()
        with patch('quest.quests.archer.randint', return_value=0):
            self.quest_manager.quest_advance()

        self.assertEqual(self.player_manager.get_gold(self.player1), self.starting_gold - archer.GOLD_PENALTY_WAIT)
        self.assertEqual(self.player_manager.get_gold(self.player2), self.starting_gold - archer.GOLD_PENALTY_WAIT)
        self.assertEqual(self.player_manager.get_exp(self.player1), self.starting_exp)
        self.assertEqual(self.player_manager.get_exp(self.player2), self.starting_exp)

    def test_betrayal_timeout(self, _):
        self.quest_manager.start_quest(self.quest)

        self.quest_manager.commands.execute_command(self.player1, '!left')
        self.quest_manager.commands.execute_command(self.player1, '!right')
        self.quest_manager.commands.execute_command(self.player1, '!right')
        self.assertEqual(self.player_manager.get_gold(self.player1), self.starting_gold)
        self.assertEqual(self.player_manager.get_gold(self.player2), self.starting_gold)
        self.assertEqual(self.player_manager.get_exp(self.player1), self.starting_exp)
        self.assertEqual(self.player_manager.get_exp(self.player2), self.starting_exp)

        # Simulate timing out and the callback for quest_advance getting called
        self.quest_manager.kill_quest_advance_timer()
        with patch('quest.quests.archer.randint', return_value=0):
            self.quest_manager.quest_advance()

        self.assertEqual(self.player_manager.get_gold(self.player1), self.starting_gold + archer.GOLD_REWARD_BIG)
        self.assertEqual(self.player_manager.get_gold(self.player2), self.starting_gold - archer.GOLD_PENALTY_SMALL)
        self.assertEqual(self.player_manager.get_exp(self.player1), self.starting_exp + archer.EXP_REWARD)
        self.assertEqual(self.player_manager.get_exp(self.player2), self.starting_exp)

    def test_same_direction(self, _):
        self.quest_manager.start_quest(self.quest)

        self.quest_manager.commands.execute_command(self.player1, '!left')
        self.quest_manager.commands.execute_command(self.player1, '!right')
        self.quest_manager.commands.execute_command(self.player1, '!right')
        with patch('quest.quests.archer.randint', return_value=0):
            self.quest_manager.commands.execute_command(self.player2, '!left')

        self.assertEqual(self.player_manager.get_gold(self.player1), self.starting_gold - archer.GOLD_PENALTY)
        self.assertEqual(self.player_manager.get_gold(self.player2), self.starting_gold - archer.GOLD_PENALTY)
        self.assertEqual(self.player_manager.get_exp(self.player1), self.starting_exp)
        self.assertEqual(self.player_manager.get_exp(self.player2), self.starting_exp)

    def test_different_directions(self, _):
        self.quest_manager.start_quest(self.quest)

        self.quest_manager.commands.execute_command(self.player1, '!left')
        self.quest_manager.commands.execute_command(self.player1, '!right')
        self.quest_manager.commands.execute_command(self.player1, '!right')
        with patch('quest.quests.archer.randint', return_value=0):
            self.quest_manager.commands.execute_command(self.player2, '!right')

        self.assertEqual(self.player_manager.get_gold(self.player1), self.starting_gold + archer.GOLD_REWARD)
        self.assertEqual(self.player_manager.get_gold(self.player2), self.starting_gold + archer.GOLD_REWARD)
        self.assertEqual(self.player_manager.get_exp(self.player1), self.starting_exp + archer.EXP_REWARD)
        self.assertEqual(self.player_manager.get_exp(self.player2), self.starting_exp + archer.EXP_REWARD)




if __name__ == '__main__':
    unittest.main()
