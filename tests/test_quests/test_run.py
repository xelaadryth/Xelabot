import unittest
from unittest.mock import MagicMock, patch

from quest.quest_manager import QuestManager
from quest.quests import run
from quest_bot.quest_player_manager import QuestPlayerManager
import settings


@patch('twitch.player_manager.PlayerManager.save_player_data')
class TestRun(unittest.TestCase):
    def setUp(self):
        bot = MagicMock()
        with patch('os.makedirs'):
            with patch('os.listdir'):
                self.player_manager = QuestPlayerManager(bot)
        self.channel = MagicMock()
        self.channel.channel_manager.bot.player_manager = self.player_manager
        self.starting_gold = 1000
        # Everyone is max level
        self.starting_exp = settings.EXP_LEVELS[settings.LEVEL_CAP-1]

        self.level_difference3 = run.MONSTER_LEVEL - (3 * settings.LEVEL_CAP)
        self.level_difference4 = run.MONSTER_LEVEL - (4 * settings.LEVEL_CAP)

        self.player1 = 'Player1'
        self.player2 = 'Player2'
        self.player3 = 'Player3'
        self.player4 = 'Player4'
        self.party = [self.player1, self.player2, self.player3, self.player4]
        with patch('twitch.player_manager.PlayerManager.save_player_data'):
            self.player_manager.reward(self.party, gold=self.starting_gold, exp=self.starting_exp)

        self.quest_manager = QuestManager(self.channel)
        self.quest_manager.party = self.party
        self.quest = run.Run(self.quest_manager)

    def test_escape(self, _):
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
        with patch('quest.quests.run.randint', return_value=0):
            self.quest_manager.commands.execute_command(self.player3, self.quest.escape_word)

        for player in self.party:
            if player == self.player4:
                self.assertEqual(self.player_manager.get_gold(player), self.starting_gold - run.GOLD_PENALTY)
                self.assertEqual(self.player_manager.get_exp(player), self.starting_exp)
            else:
                self.assertEqual(self.player_manager.get_gold(player), self.starting_gold + run.GOLD_REWARD)
                self.assertEqual(self.player_manager.get_exp(player), self.starting_exp + run.EXP_REWARD)

    def test_escape_timeout(self, _):
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
        with patch('quest.quests.run.randint', return_value=0):
            self.quest_manager.quest_advance()

        for player in self.party:
            if player in [self.player3, self.player4]:
                self.assertEqual(self.player_manager.get_gold(player), self.starting_gold - run.GOLD_PENALTY)
                self.assertEqual(self.player_manager.get_exp(player), self.starting_exp)
            else:
                self.assertEqual(self.player_manager.get_gold(player), self.starting_gold + run.GOLD_REWARD)
                self.assertEqual(self.player_manager.get_exp(player), self.starting_exp + run.EXP_REWARD)

    def test_boss_battle_timeout(self, _):
        self.quest_manager.start_quest(self.quest)

        # Simulate timing out and the callback for quest_advance getting called
        self.quest_manager.kill_quest_advance_timer()
        self.quest_manager.quest_advance()

        for player in self.party:
            self.assertEqual(self.player_manager.get_gold(player), self.starting_gold)
            self.assertEqual(self.player_manager.get_exp(player), self.starting_exp)

        # Simulate timing out and the callback for quest_advance getting called
        self.quest_manager.kill_quest_advance_timer()
        with patch('quest.quests.run.randint', return_value=0):
            self.quest_manager.quest_advance()

        for player in self.party:
            self.assertEqual(self.player_manager.get_gold(player), self.starting_gold - run.GOLD_PENALTY)
            self.assertEqual(self.player_manager.get_exp(player), self.starting_exp)

    def test_boss_battle_try_timeout(self, _):
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
        with patch('quest.quests.run.randint', return_value=0):
            self.quest_manager.quest_advance()

        for player in self.party:
            self.assertEqual(self.player_manager.get_gold(player), self.starting_gold - run.GOLD_PENALTY)
            self.assertEqual(self.player_manager.get_exp(player), self.starting_exp)

    def test_boss_battle_surround_fail(self, _):
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

        with patch('quest.quests.run.randint', return_value=0):
            self.quest_manager.commands.execute_command(self.player4, '!left')

        for player in self.party:
            self.assertEqual(self.player_manager.get_gold(player), self.starting_gold - run.GOLD_PENALTY)
            self.assertEqual(self.player_manager.get_exp(player), self.starting_exp)

    def test_boss_battle_fight_fail_hard(self, _):
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

    def test_boss_battle_fight_fail_slight(self, _):
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

    def test_boss_battle_fight_win(self, _):
        self.quest_manager.start_quest(self.quest)

        # Simulate timing out and the callback for quest_advance getting called
        self.quest_manager.kill_quest_advance_timer()
        self.quest_manager.quest_advance()

        self.quest_manager.commands.execute_command(self.player1, '!left')
        self.quest_manager.commands.execute_command(self.player2, '!right')
        self.quest_manager.commands.execute_command(self.player3, '!front')

        # Simulate timing out and the callback for quest_advance getting called
        self.quest_manager.kill_quest_advance_timer()
        with patch('quest.quests.run.randint', return_value=self.level_difference3):
            self.quest_manager.quest_advance()

        for player in self.party:
            self.assertEqual(self.player_manager.get_gold(player),
                             self.starting_gold + run.GOLD_REWARD_BIG - self.level_difference3)
            self.assertEqual(self.player_manager.get_exp(player), self.starting_exp + run.EXP_REWARD_BIG)


if __name__ == '__main__':
    unittest.main()
