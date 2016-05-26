from copy import deepcopy
from sqlitedict import SqliteDict


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
        self.player_db = SqliteDict(settings.PLAYER_DB_FILE, tablename='players', autocommit=True)

        self.initialized = False
        self.load_player_stats_from_db()
        self.initialized = True

    def load_player_stats_from_db(self):
        """
        Loads all valid data from database into the PlayerManager.
        """
        for player_name, player_stats in self.player_db.items():
            for key in self.players[player_name]:
                if key in player_stats:
                    self.players[player_name][key] = player_stats[key]

    def save_player_data(self, username, data):
        """
        Saves a specific player's data to persistent storage.
        :param username: str - The player whose data you want to save
        :param data: dict - The player data you are saving
        """
        self.player_db[username] = data

    def save_player(self, username):
        """
        Saves a specific player's data to persistent storage.
        :param username: str - The player whose data you want to save
        """
        username = username.lower()
        player = self.players[username]

        self.save_player_data(username, player)
