import unittest
from unittest.mock import patch

from quest.quests import duel
from tests.test_quests.base_class import TestBase


class TestDuel(TestBase):
    quest_constructor = duel.Duel
    num_start_players = 2

    def test_timeout(self):
        self.quest_manager.start_quest(self.quest)

        # Simulate timing out and the callback for quest_advance getting called
        self.quest_manager.kill_quest_advance_timer()
        self.quest_manager.quest_advance()

        self.assertEqual(self.player_manager.get_gold(self.player1), self.starting_gold)
        self.assertEqual(self.player_manager.get_gold(self.player2), self.starting_gold)
        self.assertEqual(self.player_manager.get_exp(self.player1), self.starting_exp + duel.EXP_PACIFIST_REWARD)
        self.assertEqual(self.player_manager.get_exp(self.player2), self.starting_exp + duel.EXP_PACIFIST_REWARD)

    def test_attack(self):
        self.quest_manager.start_quest(self.quest)

        self.quest_manager.commands.execute_command(self.player1, self.quest.duel_word)

        self.assertEqual(self.player_manager.get_gold(self.player1), self.starting_gold + duel.GOLD_REWARD)
        self.assertEqual(self.player_manager.get_gold(self.player2), self.starting_gold - duel.GOLD_REWARD)
        self.assertEqual(self.player_manager.get_exp(self.player1), self.starting_exp + duel.EXP_REWARD)
        self.assertEqual(self.player_manager.get_exp(self.player2), self.starting_exp)




if __name__ == '__main__':
    unittest.main()
