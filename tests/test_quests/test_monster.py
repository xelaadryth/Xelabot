import unittest
from unittest.mock import patch

from quest.quests import monster
import settings
from tests.test_quests.base_class import TestBase


class TestMonster(TestBase):
    quest_constructor = monster.Monster
    num_start_players = 1

    def test_timeout(self):
        self.quest_manager.start_quest(self.quest)

        # Simulate timing out and the callback for quest_advance getting called
        self.quest_manager.kill_quest_advance_timer()
        self.quest_manager.quest_advance()

        self.assertEqual(self.player_manager.get_gold(self.player1), self.starting_gold - monster.GOLD_TIMEOUT_PENALTY)
        self.assertEqual(self.player_manager.get_exp(self.player1), self.starting_exp)

    def test_attack_win_hard(self):
        self.quest_manager.start_quest(self.quest)

        with patch('quest.quests.monster.randint', return_value=settings.LEVEL_CAP):
            self.quest_manager.commands.execute_command(self.player1, '!attack')

        self.assertEqual(self.player_manager.get_gold(self.player1),
                         self.starting_gold + monster.GOLD_RISKY_REWARD_BIG + settings.LEVEL_CAP)
        self.assertEqual(self.player_manager.get_exp(self.player1), self.starting_exp + monster.EXP_RISKY_REWARD_BIG)

    def test_attack_win(self):
        self.quest_manager.start_quest(self.quest)

        self.quest_manager.commands.execute_command(self.player1, '!attack')

        self.assertEqual(self.player_manager.get_gold(self.player1), self.starting_gold + monster.GOLD_RISKY_REWARD)
        self.assertEqual(self.player_manager.get_exp(self.player1), self.starting_exp + monster.EXP_RISKY_REWARD)

    def test_attack_lose(self):
        self.quest_manager.start_quest(self.quest)

        with patch('quest.quests.monster.randint', return_value=-1):
            self.quest_manager.commands.execute_command(self.player1, '!attack')

        self.assertEqual(self.player_manager.get_gold(self.player1) - 1,
                         self.starting_gold - monster.GOLD_RISKY_PENALTY)
        self.assertEqual(self.player_manager.get_exp(self.player1), self.starting_exp)

    def test_attack_lose_hard(self):
        self.quest_manager.start_quest(self.quest)

        with patch('quest.quests.monster.randint', return_value=-settings.LEVEL_CAP):
            self.quest_manager.commands.execute_command(self.player1, '!attack')

        self.assertEqual(self.player_manager.get_gold(self.player1) - settings.LEVEL_CAP,
                         self.starting_gold - monster.GOLD_RISKY_PENALTY)
        self.assertEqual(self.player_manager.get_exp(self.player1), self.starting_exp)

    def test_flee_win(self):
        self.quest_manager.start_quest(self.quest)

        with patch('quest.quests.monster.getrandbits', return_value=1):
            self.quest_manager.commands.execute_command(self.player1, '!flee')

        self.assertEqual(self.player_manager.get_gold(self.player1), self.starting_gold + monster.GOLD_SAFE_REWARD)
        self.assertEqual(self.player_manager.get_exp(self.player1), self.starting_exp + monster.EXP_SAFE_REWARD)

    def test_flee_lose(self):
        self.quest_manager.start_quest(self.quest)

        with patch('quest.quests.monster.getrandbits', return_value=0):
            self.quest_manager.commands.execute_command(self.player1, '!flee')

        self.assertEqual(self.player_manager.get_gold(self.player1), self.starting_gold - monster.GOLD_SAFE_REWARD)
        self.assertEqual(self.player_manager.get_exp(self.player1), self.starting_exp)

if __name__ == '__main__':
    unittest.main()
