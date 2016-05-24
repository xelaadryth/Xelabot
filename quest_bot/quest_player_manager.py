from collections import defaultdict
from copy import deepcopy

import settings
from twitch.player_manager import PlayerManager


class QuestPlayerManager(PlayerManager):
    default_player = deepcopy(PlayerManager.default_player)

    def __init__(self, bot):
        self.default_player.update({
            'exp': 0,
            'prestige': 0,
            'gold': 0,
            'items': defaultdict(lambda: 0)
        })
        super().__init__(bot)

    # When a player entry is missing, create and save it
    class PlayerDict(dict):
        def __missing__(self, key):
            value = deepcopy(QuestPlayerManager.default_player)
            value['name'] = key
            self['name'] = value
            QuestPlayerManager.save_player_data(key, value)
            return value

    def __add_gold(self, username, gold, prestige_benefits=True):
        """
        Gives gold to the specified player.
        :param username: str - The player who you are modifying
        :param gold: float - How much gold to give that player
        :param prestige_benefits: bool - Whether this gold increase is affected by prestige bonuses
        """
        username = username.lower()

        # Don't magnify negative amounts of gold
        if prestige_benefits and gold > 0:
            gold *= 1 + self.players[username]['prestige'] * settings.PRESTIGE_GOLD_AMP

        self.players[username]['gold'] += gold
        if self.players[username]['gold'] < 0:
            self.players[username]['gold'] = 0

    def add_gold(self, username, gold, prestige_benefits=True):
        """
        Gives gold to the specified player.
        :param username: str - The player who you are modifying
        :param gold: float - How much gold to give that player
        :param prestige_benefits: bool - Whether this gold increase is affected by prestige bonuses
        """
        self.__add_gold(username, gold, prestige_benefits=prestige_benefits)
        self.save_player(username)

    def __add_exp(self, username, exp):
        """
        Gives exp to the specified player.
        :param username: str - The player who you are modifying
        :param exp: float - How much exp to give that player
        """
        username = username.lower()
        self.players[username]['exp'] += exp

    def add_exp(self, username, exp):
        """
        Gives exp to the specified player.
        :param username: str - The player who you are modifying
        :param exp: float - How much exp to give that player
        """
        self.__add_exp(username, exp)
        self.save_player(username)

    def __add_item(self, username, item):
        """
        Item to give to the specified player.
        :param item: str - The name of the item we are giving to the player
        """
        username = username.lower()
        self.players[username]['items'][item] += 1

    def add_item(self, username, item):
        """
        Item to give to the specified player.
        :param item: str - The name of the item we are giving to the player
        """
        self.__add_item(username, item)
        self.save_player(username)

    def __remove_item(self, username, item):
        """
        Item to take from the specified player.
        :param item: str - The name of the item we are taking from the player
        """
        username = username.lower()
        self.players[username]['items'][item] -= 1

        if self.players[username]['items'][item] <= 0:
            del self.players[username]['items'][item]

    def remove_item(self, username, item):
        """
        Item to take from the specified player.
        :param item: str - The name of the item we are taking from the player
        """
        self.__remove_item(username, item)
        self.save_player(username)

    def __reward(self, username, gold=0, exp=0, item=None, prestige_benefits=True):
        """
        Gives gold and exp to the specified player.
        :param username: str - The player who you are modifying
        :param gold: float - How much gold to give that player
        :param exp: float - How much exp to give that player
        """
        self.__add_gold(username, gold, prestige_benefits=prestige_benefits)
        self.__add_exp(username, exp)
        if item:
            self.__add_item(username, item)

    def reward(self, username, gold=0, exp=0, item=None, prestige_benefits=True):
        """
        Gives gold and exp to the specified player.
        :param username: str - The player who you are modifying
        :param gold: float - How much gold to give that player
        :param exp: float - How much exp to give that player
        """
        self.__reward(username, gold=gold, exp=exp, item=item, prestige_benefits=prestige_benefits)
        self.save_player(username)

    def penalize(self, username, gold=0, exp=0, item=None, prestige_benefits=True):
        """
        Gives gold and exp to the specified player.
        :param username: str - The player who you are modifying
        :param gold: float - How much gold to give that player
        :param exp: float - How much exp to give that player
        """
        self.__reward(username, gold=-gold, exp=-exp, item=None, prestige_benefits=prestige_benefits)
        if item:
            self.__remove_item(username, item)
        self.save_player(username)

    def get_gold(self, username):
        """
        Gets how much gold a given player has.
        :param username: str - The player who you are modifying
        """
        username = username.lower()
        return self.players[username]['gold']

    def get_exp(self, username):
        """
        Gets how much exp a given player has.
        :param username: str - The player who you are modifying
        """
        username = username.lower()
        return self.players[username]['exp']

    def get_level(self, username):
        """
        Gets what level a given player is.
        :param username: str - The player who you are modifying
        """
        username = username.lower()
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
        username = username.lower()
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
        username = username.lower()
        player = self.players[username]
        msg = '{}Level: {} ({} Exp), Gold: {}'.format(
            'Prestige: {}, '.format(player['prestige']) if player['prestige'] else '',
            self.get_level(username), player['exp'], player['gold'])
        self.bot.send_whisper(username, msg)
