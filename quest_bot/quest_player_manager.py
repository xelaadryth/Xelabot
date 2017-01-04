from copy import deepcopy

import settings
from twitch.player_manager import PlayerManager


class QuestPlayerManager(PlayerManager):
    """
    Functions like add_gold perform a raw store action and then save. __add_gold is the raw store action in this case.
    Properties of raw store actions:
        - Call username.lower()
        - Touch self.players with that name
        - Do not save to file

    Properties of store actions:
        - Do nothing other than call a raw action and then save

    Some actions can also take a list of elements. These are all of the form:

    def foo(username **kwargs):
        if not (isinstance(username), str):
            for user in username:
                foo(username, **kwargs)
        else:
            ORIGINAL FUNCTION BODY

    Note that both store actions and raw store actions qualify for this.
    """
    default_player = deepcopy(PlayerManager.default_player)
    default_player.update({
        'exp': 0,
        'prestige': 0,
        'gold': 0,
        'items': {}
    })

    def __add_gold(self, username, gold, prestige_benefits=True):
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
        :param username: str - The player who you are modifying
        :param item: str or list<str> - The name of the item(s) we are giving to the player
        """
        if not isinstance(item, str):
            # We must be a list of items
            for single_item in item:
                self.__add_item(username, single_item)
        else:
            if item not in self.players[username]['items']:
                self.players[username]['items'][item] = 1
            else:
                self.players[username]['items'][item] += 1

    def add_item(self, username, item):
        """
        Item to give to the specified player.
        :param username: str - The player who you are modifying
        :param item: str or list<str> - The name of the item(s) we are giving to the player
        """
        self.__add_item(username, item)
        self.save_player(username)

    def __remove_item(self, username, item):
        """
        Item to take from the specified player.
        :param username: str - The player who you are modifying
        :param item: str or list<str> - The name of the item(s) we are giving to the player
        """
        if not isinstance(item, str):
            # We must be a list of items
            for single_item in item:
                self.__remove_item(username, single_item)
        else:
            # If we don't have the item, do nothing
            if item in self.players[username]['items']:
                self.players[username]['items'][item] -= 1

                if self.players[username]['items'][item] <= 0:
                    del self.players[username]['items'][item]

    def remove_item(self, username, item):
        """
        Item to take from the specified player.
        :param username: str - The player who you are modifying
        :param item: str or list<str> - The name of the item(s) we are giving to the player
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
        if not isinstance(username, str):
            # We must be a list of users
            for user in username:
                self.__reward(user, gold=gold, exp=exp, item=item, prestige_benefits=prestige_benefits)
        else:
            self.__add_gold(username, gold, prestige_benefits=prestige_benefits)
            self.__add_exp(username, exp)
            if item:
                self.__add_item(username, item)

    def reward(self, username, gold=0, exp=0, item=None, prestige_benefits=True):
        """
        Gives gold and exp to the specified player(s).
        :param username: str or list<str> - The player(s) who you are modifying
        :param gold: float - How much gold to give that player
        :param exp: float - How much exp to give that player
        """
        if not isinstance(username, str):
            # We must be a list of users
            for user in username:
                self.reward(user, gold=gold, exp=exp, item=item, prestige_benefits=prestige_benefits)
        else:
            self.__reward(username, gold=gold, exp=exp, item=item, prestige_benefits=prestige_benefits)
            self.save_player(username)

    def __penalize(self, username, gold=0, exp=0, item=None, prestige_benefits=True):
        """
        Gives gold and exp to the specified player(s).
        :param username: str or list<str> - The player(s) who you are modifying
        :param gold: float - How much gold to give that player
        :param exp: float - How much exp to give that player
        """
        if not isinstance(username, str):
            # We must be a list of users
            for user in username:
                self.__penalize(user, gold=gold, exp=exp, item=item, prestige_benefits=prestige_benefits)
        else:
            self.__reward(username, gold=-gold, exp=-exp, item=None, prestige_benefits=prestige_benefits)
            if item:
                self.__remove_item(username, item)

    def penalize(self, username, gold=0, exp=0, item=None, prestige_benefits=True):
        """
        Gives gold and exp to the specified player(s).
        :param username: str or list<str> - The player(s) who you are modifying
        :param gold: float - How much gold to give that player
        :param exp: float - How much exp to give that player
        """
        if not isinstance(username, str):
            # We must be a list of users
            for user in username:
                self.penalize(user, gold=gold, exp=exp, item=item, prestige_benefits=prestige_benefits)
        else:
            self.__penalize(username, gold=gold, exp=exp, item=item, prestige_benefits=prestige_benefits)
            self.save_player(username)

    def get_gold(self, username):
        """
        Gets how much gold a given player has.
        :param username: str - The player who you are modifying
        """
        return self.players[username]['gold']

    def get_exp(self, username):
        """
        Gets how much exp a given player has.
        :param username: str - The player who you are modifying
        """
        return self.players[username]['exp']

    @staticmethod
    def exp_to_level(exp):
        # The value for every member of the list is the minimum experience to be a given level
        for level, exp_req in enumerate(settings.EXP_LEVELS, start=-1):
            if exp < exp_req:
                return level
        return settings.LEVEL_CAP

    def get_level(self, username):
        """
        Gets what level a given player is.
        :param username: str - The player who you are modifying
        """
        exp = self.players[username]['exp']

        return self.exp_to_level(exp)

    def get_prestige(self, username):
        """
        Gets what prestige level a given player is.
        :param username: str - The player who you are modifying
        """
        return self.players[username]['prestige']

    def get_items(self, username):
        """
        Gets the items of a given player.
        :param username: str - The player who you are modifying
        """
        return self.players[username]['items']

    def prestige(self, username):
        """
        Prestige advances a player.
        :param username: str - The player who you are modifying
        :return: bool - True if successfully prestiged, False if no change
        """
        if self.players[username]['exp'] >= settings.EXP_LEVELS[settings.LEVEL_CAP] and (
                self.players[username]['gold'] >= settings.PRESTIGE_COST):
            self.players[username]['exp'] -= settings.EXP_LEVELS[settings.LEVEL_CAP]
            self.players[username]['gold'] -= settings.PRESTIGE_COST
            self.players[username]['prestige'] += 1
            self.save_player(username)
            return True
        else:
            return False

    @staticmethod
    def list_items(items):
        msg = ''
        for item, quantity in items.items():
            if quantity <= 0:
                continue
            if quantity == 1:
                msg += '{}, '.format(item)
            else:
                msg += '{} ({}), '.format(item, quantity)

        msg = msg.rstrip(', ')
        return msg

    def whisper_stats(self, username):
        """
        Whispers a player their relevant stats.
        :param username: str - The player who is requesting stat information
        """
        player = self.players[username]
        msg = '{}Level: {} ({} Exp), Gold: {}{}'.format(
            'Prestige: {}, '.format(player['prestige']) if player['prestige'] else '',
            self.get_level(username), round(player['exp'], 1), round(player['gold'], 1),
            ', Items: {}'.format(self.list_items(player['items'])) if player['items'] else '')
        self.bot.send_whisper(username, msg)

    def save_player(self, username):
        """
        Saves a specific player's data to persistent storage. Deletes items with quantity 0 or less.
        :param username: str - The player whose data you want to save
        """
        # Remove duplicate items. Doesn't use a dict comprehension because items is a custom dict type
        remove_items = []
        for item, quantity in self.players[username]['items'].items():
            if quantity <= 0:
                remove_items.append(item)
        for remove_item in remove_items:
            del self.players[username]['items'][remove_item]

        super().save_player(username)
