import copy
import json
import os

import settings


class PlayerManager:
    default_player = {
        'name': None
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
        self.players = self.PlayerDict()

        # Load up all the existing channel information
        if not os.path.exists(settings.PLAYER_DATA_PATH):
            os.makedirs(settings.PLAYER_DATA_PATH)
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
