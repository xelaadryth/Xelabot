import unittest
from unittest.mock import patch

from quest.quests import run
import settings
from tests.test_quests.base_class import TestBase


class TestRun(TestBase):
    quest_constructor = run.Run
    num_start_players = 4
    starting_gold = 1000
    starting_exp = settings.EXP_LEVELS[settings.LEVEL_CAP]

    level_difference3 = run.MONSTER_LEVEL - (3 * settings.LEVEL_CAP)
    level_difference4 = run.MONSTER_LEVEL - (4 * settings.LEVEL_CAP)

    def test_escape(self):
        self.quest_manager.start_quest(self.quest)

        self.quest_manager.commands.execute_command(self.player1, self.quest.escape_word)
        self.quest_manager.commands.execute_command(self.player2, self.quest.escape_word)
        self.quest_manager.commands.execute_command(self.player1, self.quest.escape_word)
        self.quest_manager.commands.execute_command(self.player1, self.quest.escape_word)
        self.quest_manager.commands.execute_command(self.player1, self.quest.escape_word)
        self.quest_manager.commands.execute_command(self.player2, self.quest.escape_word)
        for player in self.party:
            self.assertEqual(self.player_manager.get_gold(player), self.starting_gold)
            self.assertEqual(self.player_manager.get_exp(player), self.starting_exp)
        self.quest_manager.commands.execute_command(self.player3, self.quest.escape_word)

        for player in self.party:
            if player == self.player4:
                self.assertEqual(self.player_manager.get_gold(player), self.starting_gold - run.GOLD_PENALTY)
                self.assertEqual(self.player_manager.get_exp(player), self.starting_exp)
            else:
                self.assertEqual(self.player_manager.get_gold(player), self.starting_gold + run.GOLD_REWARD)
                self.assertEqual(self.player_manager.get_exp(player), self.starting_exp + run.EXP_REWARD)

    def test_escape_timeout(self):
        self.quest_manager.start_quest(self.quest)

        self.quest_manager.commands.execute_command(self.player1, self.quest.escape_word)
        self.quest_manager.commands.execute_command(self.player2, self.quest.escape_word)
        self.quest_manager.commands.execute_command(self.player1, self.quest.escape_word)
        self.quest_manager.commands.execute_command(self.player1, self.quest.escape_word)
        self.quest_manager.commands.execute_command(self.player1, self.quest.escape_word)
        self.quest_manager.commands.execute_command(self.player2, self.quest.escape_word)
        for player in self.party:
            self.assertEqual(self.player_manager.get_gold(player), self.starting_gold)
            self.assertEqual(self.player_manager.get_exp(player), self.starting_exp)

        # Simulate timing out and the callback for quest_advance getting called
        self.quest_manager.kill_quest_advance_timer()
        self.quest_manager.quest_advance()

        for player in self.party:
            if player in [self.player3, self.player4]:
                self.assertEqual(self.player_manager.get_gold(player), self.starting_gold - run.GOLD_PENALTY)
                self.assertEqual(self.player_manager.get_exp(player), self.starting_exp)
            else:
                self.assertEqual(self.player_manager.get_gold(player), self.starting_gold + run.GOLD_REWARD)
                self.assertEqual(self.player_manager.get_exp(player), self.starting_exp + run.EXP_REWARD)

    def test_boss_battle_timeout(self):
        self.quest_manager.start_quest(self.quest)

        # Simulate timing out and the callback for quest_advance getting called
        self.quest_manager.kill_quest_advance_timer()
        self.quest_manager.quest_advance()

        for player in self.party:
            self.assertEqual(self.player_manager.get_gold(player), self.starting_gold)
            self.assertEqual(self.player_manager.get_exp(player), self.starting_exp)

        # Simulate timing out and the callback for quest_advance getting called
        self.quest_manager.kill_quest_advance_timer()
        self.quest_manager.quest_advance()

        for player in self.party:
            self.assertEqual(self.player_manager.get_gold(player), self.starting_gold - run.GOLD_PENALTY)
            self.assertEqual(self.player_manager.get_exp(player), self.starting_exp)

    def test_boss_battle_try_timeout(self):
        self.quest_manager.start_quest(self.quest)

        # Simulate timing out and the callback for quest_advance getting called
        self.quest_manager.kill_quest_advance_timer()
        self.quest_manager.quest_advance()

        self.quest_manager.commands.execute_command(self.player1, '!front')
        self.quest_manager.commands.execute_command(self.player1, '!left')
        self.quest_manager.commands.execute_command(self.player1, '!right')
        self.quest_manager.commands.execute_command(self.player2, '!left')
        self.quest_manager.commands.execute_command(self.player3, '!front')
        self.quest_manager.commands.execute_command(self.player2, '!front')
        self.quest_manager.commands.execute_command(self.player2, '!right')

        for player in self.party:
            self.assertEqual(self.player_manager.get_gold(player), self.starting_gold)
            self.assertEqual(self.player_manager.get_exp(player), self.starting_exp)

        # Simulate timing out and the callback for quest_advance getting called
        self.quest_manager.kill_quest_advance_timer()
        self.quest_manager.quest_advance()

        for player in self.party:
            self.assertEqual(self.player_manager.get_gold(player), self.starting_gold - run.GOLD_PENALTY)
            self.assertEqual(self.player_manager.get_exp(player), self.starting_exp)

    def test_boss_battle_surround_fail(self):
        self.quest_manager.start_quest(self.quest)

        # Simulate timing out and the callback for quest_advance getting called
        self.quest_manager.kill_quest_advance_timer()
        self.quest_manager.quest_advance()

        self.quest_manager.commands.execute_command(self.player1, '!left')
        self.quest_manager.commands.execute_command(self.player1, '!front')
        self.quest_manager.commands.execute_command(self.player1, '!right')
        self.quest_manager.commands.execute_command(self.player3, '!front')
        self.quest_manager.commands.execute_command(self.player2, '!left')
        self.quest_manager.commands.execute_command(self.player2, '!front')
        self.quest_manager.commands.execute_command(self.player2, '!right')

        for player in self.party:
            self.assertEqual(self.player_manager.get_gold(player), self.starting_gold)
            self.assertEqual(self.player_manager.get_exp(player), self.starting_exp)

        self.quest_manager.commands.execute_command(self.player4, '!left')

        for player in self.party:
            self.assertEqual(self.player_manager.get_gold(player), self.starting_gold - run.GOLD_PENALTY)
            self.assertEqual(self.player_manager.get_exp(player), self.starting_exp)

    def test_boss_battle_fight_fail_hard(self):
        self.quest_manager.start_quest(self.quest)

        # Simulate timing out and the callback for quest_advance getting called
        self.quest_manager.kill_quest_advance_timer()
        self.quest_manager.quest_advance()

        self.quest_manager.commands.execute_command(self.player1, '!left')
        self.quest_manager.commands.execute_command(self.player2, '!right')
        self.quest_manager.commands.execute_command(self.player3, '!front')

        for player in self.party:
            self.assertEqual(self.player_manager.get_gold(player), self.starting_gold)
            self.assertEqual(self.player_manager.get_exp(player), self.starting_exp)
        self.assertEqual(len(self.quest.attacking_players), 3)

        level_difference = self.level_difference4 - run.MONSTER_LEVEL / 2 - 1
        with patch('quest.quests.run.randint', return_value=level_difference):
            self.quest_manager.commands.execute_command(self.player4, '!front')

        self.assertEqual(len(self.quest.attacking_players), 4)
        for player in self.party:
            self.assertEqual(self.player_manager.get_gold(player),
                             self.starting_gold - run.GOLD_PENALTY_SMALL - level_difference)
            self.assertEqual(self.player_manager.get_exp(player), self.starting_exp)

    def test_boss_battle_fight_fail_slight(self):
        self.quest_manager.start_quest(self.quest)

        # Simulate timing out and the callback for quest_advance getting called
        self.quest_manager.kill_quest_advance_timer()
        self.quest_manager.quest_advance()

        self.quest_manager.commands.execute_command(self.player1, '!left')
        self.quest_manager.commands.execute_command(self.player2, '!right')
        self.quest_manager.commands.execute_command(self.player3, '!front')

        for player in self.party:
            self.assertEqual(self.player_manager.get_gold(player), self.starting_gold)
            self.assertEqual(self.player_manager.get_exp(player), self.starting_exp)
        self.assertEqual(len(self.quest.attacking_players), 3)

        level_difference = self.level_difference3 - 1

        # Simulate timing out and the callback for quest_advance getting called
        self.quest_manager.kill_quest_advance_timer()
        with patch('quest.quests.run.randint', return_value=level_difference):
            self.quest_manager.quest_advance()

        self.assertEqual(len(self.quest.attacking_players), 3)
        for player in self.party:
            if player in self.quest.attacking_players:
                self.assertEqual(self.player_manager.get_gold(player),
                                 self.starting_gold - run.GOLD_PENALTY_SMALL - level_difference)
                self.assertEqual(self.player_manager.get_exp(player), self.starting_exp)
            else:
                self.assertEqual(self.player_manager.get_gold(player),
                                 self.starting_gold + run.GOLD_REWARD_MEDIUM + level_difference)
                self.assertEqual(self.player_manager.get_exp(player), self.starting_exp + run.EXP_REWARD_MEDIUM)

    def test_boss_battle_fight_win_item(self):
        self.quest_manager.start_quest(self.quest)

        # Simulate timing out and the callback for quest_advance getting called
        self.quest_manager.kill_quest_advance_timer()
        self.quest_manager.quest_advance()

        self.quest_manager.commands.execute_command(self.player1, '!left')
        self.quest_manager.commands.execute_command(self.player2, '!right')
        self.quest_manager.commands.execute_command(self.player3, '!front')

        # Simulate timing out and the callback for quest_advance getting called
        self.quest_manager.kill_quest_advance_timer()
        with patch('quest.quest_segment.random', return_value=run.DROP_CHANCE - 0.01):
            with patch('quest.quest_segment.choice', return_value='Player2'):
                with patch('quest.quests.run.randint', return_value=self.level_difference3):
                    self.quest_manager.quest_advance()

        for player in self.party:
            self.assertEqual(self.player_manager.get_gold(player),
                             self.starting_gold + run.GOLD_REWARD_BIG - self.level_difference3)
            self.assertEqual(self.player_manager.get_exp(player), self.starting_exp + run.EXP_REWARD_BIG)

        # Received item and whisper
        items = self.player_manager.get_items(self.player2)
        self.assertEqual(items[run.DROP_ITEM], 1)
        self.assertEqual(self.bot.send_whisper.call_count, 1)

    def test_boss_battle_fight_win_no_item(self):
        self.quest_manager.start_quest(self.quest)

        # Simulate timing out and the callback for quest_advance getting called
        self.quest_manager.kill_quest_advance_timer()
        self.quest_manager.quest_advance()

        self.quest_manager.commands.execute_command(self.player1, '!left')
        self.quest_manager.commands.execute_command(self.player2, '!right')
        self.quest_manager.commands.execute_command(self.player3, '!front')

        # Simulate timing out and the callback for quest_advance getting called
        self.quest_manager.kill_quest_advance_timer()
        with patch('quest.quest_segment.random', return_value=run.DROP_CHANCE):
            with patch('quest.quest_segment.choice', return_value='Player2'):
                with patch('quest.quests.run.randint', return_value=self.level_difference3):
                    self.quest_manager.quest_advance()

        for player in self.party:
            self.assertEqual(self.player_manager.get_gold(player),
                             self.starting_gold + run.GOLD_REWARD_BIG - self.level_difference3)
            self.assertEqual(self.player_manager.get_exp(player), self.starting_exp + run.EXP_REWARD_BIG)

        # Received item and whisper
        items = self.player_manager.get_items(self.player2)
        self.assertNotIn(run.DROP_ITEM, items)
        self.assertEqual(self.bot.send_whisper.call_count, 0)


if __name__ == '__main__':
    unittest.main()
