import copy
import json
import os

import settings


class PlayerManager:
    default_player = {
        'name': None,
        'exp': 0,
        'prestige': 0,
        'gold': 0
    }

    # When a player entry is missing, create and save it
    class PlayerDict(dict):
        @staticmethod
        def __missing__(key):
            value = copy.deepcopy(PlayerManager.default_player)
            value['name'] = key
            PlayerManager.save_player_data(key, value)
            return value

    def __init__(self, bot):
        self.bot = bot
        self.players = PlayerManager.PlayerDict()

        # Load up all the existing channel information
        for filename in os.listdir(settings.PLAYER_DATA_PATH):
            with open(os.path.join(settings.PLAYER_DATA_PATH, filename)) as json_data:
                player_settings = json.load(json_data)

            # Fill missing settings with default settings
            player_settings_keys = set(player_settings.keys())
            for key, value in self.default_player.items():
                if key not in player_settings_keys:
                    player_settings[key] = value

            self.players[player_settings['name']] = player_settings

    @staticmethod
    def save_player_data(username, data):
        """
        Saves a specific player's data to persistent storage.
        :param username: str - The player whose data you want to save
        :param data: dict - The player data you are saving
        """
        with open(os.path.join(settings.PLAYER_DATA_PATH, username + '.txt'), 'w') as player_file:
            json.dump(data, player_file)

    def save_player(self, username):
        """
        Saves a specific player's data to persistent storage.
        :param username: str - The player whose data you want to save
        """
        player = self.players[username]

        self.save_player_data(username, player)

    def add_gold(self, username, gold, prestige_benefits=True):
        """
        Gives gold to the specified player.
        :param username: str - The player who you are modifying
        :param gold: float - How much gold to give that player
        :param prestige_benefits: bool - Whether this gold increase is affected by prestige bonuses
        """
        # Don't magnify negative amounts of gold
        if prestige_benefits and gold > 0:
            gold *= 1 + self.players[username]['prestige'] * settings.PRESTIGE_GOLD_AMP

        self.players[username]['gold'] += gold
        if self.players[username]['gold'] < 0:
            self.players[username]['gold'] = 0
        self.save_player(username)

    def get_gold(self, username):
        """
        Gets how much gold a given player has.
        :param username: str - The player who you are modifying
        """
        return self.players[username]['gold']

    def add_exp(self, username, exp):
        """
        Gives exp to the specified player.
        :param username: str - The player who you are modifying
        :param exp: float - How much exp to give that player
        """
        self.players[username]['exp'] += exp
        self.save_player(username)

    def get_exp(self, username):
        """
        Gets how much exp a given player has.
        :param username: str - The player who you are modifying
        """
        return self.players[username]['exp']

    def get_level(self, username):
        """
        Gets what level a given player is.
        :param username: str - The player who you are modifying
        """
        exp = self.players[username]['exp']
        # Due to the two off-by-one errors that cancel each other out, this works out. Our exp check kicks us one level
        # higher, but we index starting at 0
        for level, exp_req in enumerate(settings.EXP_LEVELS):
            if exp < exp_req or level == settings.LEVEL_CAP:
                return level

    def prestige(self, username):
        """
        Prestige advances a player.
        :param username: str - The player who you are modifying
        :return: bool - True if successfully prestiged, False if no change
        """
        if self.players[username]['exp'] >= settings.EXP_LEVELS[settings.LEVEL_CAP-1] and (
                self.players[username]['gold'] >= settings.PRESTIGE_COST):
            self.players[username]['exp'] -= settings.EXP_LEVELS[settings.LEVEL_CAP-1]
            self.players[username]['gold'] -= settings.PRESTIGE_COST
            self.players[username]['prestige'] += 1
            self.save_player(username)
            return True
        else:
            return False

    def whisper_stats(self, username):
        """
        Whispers a player their relevant stats.
        :param username: str - The player who is requesting stat information
        """
        player = self.players[username]
        msg = '{}Level: {} ({} Exp), Gold: {}'.format(
            'Prestige: {}, '.format(player['prestige']) if player['prestige'] else '',
            self.get_level(username), player['exp'], player['gold'])
        self.bot.send_whisper(username, msg)
