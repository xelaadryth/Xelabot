import unittest
from unittest.mock import patch

from quest.quests import gates
from tests.test_quests.base_class import TestBase


class TestGates(TestBase):
    quest_constructor = gates.Gates
    num_start_players = 5

    def test_timeout_frostguard(self):
        self.quest_manager.start_quest(self.quest)

        # Simulate timing out and the callback for quest_advance getting called
        self.quest_manager.kill_quest_advance_timer()
        self.quest_manager.quest_advance()

        for player in self.party:
            self.assertEqual(self.player_manager.get_gold(player), self.starting_gold + gates.GOLD_REWARD_BIG)
            self.assertEqual(self.player_manager.get_exp(player), self.starting_exp + gates.EXP_REWARD_BIG)

    def test_timeout_fail(self):
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
        self.quest_manager.quest_advance()

        for player in self.party:
            self.assertEqual(self.player_manager.get_gold(player), self.starting_gold - gates.GOLD_PENALTY)
            self.assertEqual(self.player_manager.get_exp(player), self.starting_exp)

    def test_success(self):
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
        self.quest_manager.commands.execute_command(self.player4, '!south')

        for player in self.party:
            self.assertEqual(self.player_manager.get_gold(player), self.starting_gold + gates.GOLD_REWARD)
            self.assertEqual(self.player_manager.get_exp(player), self.starting_exp + gates.EXP_REWARD)

    def test_fail(self):
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
