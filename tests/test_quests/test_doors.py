import unittest
from unittest.mock import patch

from quest.quests import doors
from tests.test_quests.base_class import TestBase


class TestDoors(TestBase):
    quest_constructor = doors.Doors
    num_start_players = 1

    def test_timeout(self):
        self.quest_manager.start_quest(self.quest)

        # Simulate timing out and the callback for quest_advance getting called
        self.quest_manager.kill_quest_advance_timer()
        self.quest_manager.quest_advance()

        self.assertEqual(self.player_manager.get_gold(self.player1), self.starting_gold - doors.GOLD_TIMEOUT_PENALTY)
        self.assertEqual(self.player_manager.get_exp(self.player1), self.starting_exp)

    def test_win(self):
        self.quest_manager.start_quest(self.quest)

        with patch('quest.quests.doors.getrandbits', return_value=1):
            self.quest_manager.commands.execute_command(self.player1, '!left')

        self.assertEqual(self.player_manager.get_gold(self.player1), self.starting_gold + doors.GOLD_REWARD)
        self.assertEqual(self.player_manager.get_exp(self.player1), self.starting_exp + doors.EXP_REWARD)

    def test_lose(self):
        self.quest_manager.start_quest(self.quest)

        with patch('quest.quests.doors.getrandbits', return_value=0):
            self.quest_manager.commands.execute_command(self.player1, '!right')

        self.assertEqual(self.player_manager.get_gold(self.player1), self.starting_gold - doors.GOLD_REWARD)
        self.assertEqual(self.player_manager.get_exp(self.player1), self.starting_exp)

if __name__ == '__main__':
    unittest.main()
