import unittest
from unittest.mock import MagicMock, patch

from quest.quest_manager import QuestManager
from quest_bot.quest_player_manager import QuestPlayerManager
from quest.quest import Quest


@patch('twitch.player_manager.PlayerManager.save_player_data')
class TestBase(unittest.TestCase):
    # Overwrite these!
    num_start_players = 5
    quest_constructor = Quest
    starting_gold = 1000
    starting_exp = 100

    def setUp(self):
        self.bot = MagicMock()
        with patch('twitch.player_manager.PlayerManager.load_player_stats_from_db'):
            self.player_manager = QuestPlayerManager(self.bot)
        self.channel = MagicMock()
        self.channel.channel_manager.bot = self.bot
        self.channel.channel_manager.bot.player_manager = self.player_manager

        self.player1 = 'Player1'
        self.player2 = 'Player2'
        self.player3 = 'Player3'
        self.player4 = 'Player4'
        self.player5 = 'Player5'
        self.player6 = 'Player6'
        self.player7 = 'Player7'
        self.player8 = 'Player8'
        self.player9 = 'Player9'
        self.player10 = 'Player10'
        self.all_players = [self.player1, self.player2, self.player3, self.player4, self.player5,
                            self.player6, self.player7, self.player8, self.player9, self.player10]

        self.party = self.all_players[:self.num_start_players]

        with patch('twitch.player_manager.PlayerManager.save_player_data'):
            self.player_manager.reward(self.all_players, gold=self.starting_gold, exp=self.starting_exp)

        self.quest_manager = QuestManager(self.channel)
        self.quest_manager.party = self.party
        if self.quest_constructor:
            self.quest = self.quest_constructor(self.quest_manager)

if __name__ == '__main__':
    unittest.main()
