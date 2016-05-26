from copy import deepcopy
import json
import os

import settings


class PlayerManager:
    default_player = {
        'name': None
    }

    class PlayerDict(dict):
        """
        A dictionary that, when indexed at a non-existent player username, still returns a default player data
        object that is also saved to persistent storage.
        """
        def __init__(self, player_manager):
            super().__init__()
            self.player_manager = player_manager

        def __missing__(self, key):
            player_data = deepcopy(self.player_manager.default_player)
            player_data['name'] = key
            self[key] = player_data

            if self.player_manager.initialized:
                self.player_manager.save_player_data(key, player_data)
            return player_data

    def __init__(self, bot):
        self.bot = bot
        self.players = self.PlayerDict(self)
        self.initialized = False

        # Load up all the existing channel information
        if not os.path.exists(settings.PLAYER_DATA_PATH):
            os.makedirs(settings.PLAYER_DATA_PATH)
        for filename in os.listdir(settings.PLAYER_DATA_PATH):
            with open(os.path.join(settings.PLAYER_DATA_PATH, filename)) as read_file:
                player_settings = json.load(read_file)

            self.players[player_settings['name']] = player_settings

        self.initialized = True

    @staticmethod
    def save_player_data(username, data):
        """
        Saves a specific player's data to persistent storage.
        :param username: str - The player whose data you want to save
        :param data: dict - The player data you are saving
        """
        with open(os.path.join(settings.PLAYER_DATA_PATH, username + '.txt'), 'w') as player_file:
            json.dump(data, player_file, indent=4, sort_keys=True)

    def save_player(self, username):
        """
        Saves a specific player's data to persistent storage.
        :param username: str - The player whose data you want to save
        """
        username = username.lower()
        player = self.players[username]

        self.save_player_data(username, player)
