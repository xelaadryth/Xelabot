from random import choice, random, sample

import settings
from utils.command_set import CommandSet


class QuestSegment:
    def __init__(self, quest):
        self.quest = quest
        self.quest_manager = self.quest.quest_manager
        self.channel = self.quest_manager.channel
        self.channel_manager = self.channel.channel_manager
        self.bot = self.channel_manager.bot
        self.player_manager = self.bot.player_manager

        self.commands = None

        self.set_commands()
        self.__update_commands()

    def set_commands(self):
        """
        Sets the commands available to players when they reach this quest segment. By default, nothing. Override this!
        """
        self.commands = CommandSet()

    def play(self):
        """
        Performs the actions when players reach this quest segment. Override this!
        """
        raise NotImplementedError('Quest segment not implemented!')

    def timeout(self):
        """
        The function that executes when this segment times out.
        """
        raise NotImplementedError('Timeout for quest segment not implemented!')

    def __update_commands(self):
        """
        Adds our command set as a child of the quest's command set.
        """
        self.quest.commands.add_command_set(self.commands)

    def advance(self, next_segment):
        """
        Advances the quest to the specified segment immediately.
        :param next_segment: Function<Quest, QuestSegment> - The next segment to execute immediately
        """
        self.quest.advance(next_segment)

    def complete_quest(self):
        """
        End the quest.
        """
        self.quest_manager.quest_cooldown()

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
                self.reward(user, gold, exp, prestige_benefits)
        else:
            self.player_manager.reward(username, gold=gold, exp=exp, item=item, prestige_benefits=prestige_benefits)

    def penalize(self, username, gold=0, exp=0, item=None, prestige_benefits=True):
        """
        Takes gold and exp from the specified player.
        :param username: str - The player who you are modifying
        :param gold: float - How much gold to take from that player
        :param exp: float - How much exp to take from that player
        """
        self.player_manager.penalize(username, gold=gold, exp=exp, item=item, prestige_benefits=prestige_benefits)

    def sum_levels(self, party):
        """
        Given a party, add together their combined levels.
        :param party: list<str> - A list of player display names
        :return: int - The sum of all player levels
        """
        total_level = 0
        for player in party:
            total_level += self.player_manager.get_level(player)

        return total_level

    def drop_item(self, party, item, chance, msg):
        """
        Randomly have a chance of dropping someone in the party an item.
        :param party: list<str> - A list of players who are eligible for the drop
        :param item: str - The name of an item being dropped
        :param chance: float - A percent chance of an item dropping between 0 and 1
        :param msg: str - The message that will be whispered to the receiver of the item
        """
        if random() < chance:
            recipient = choice(party)

            self.player_manager.add_item(recipient, item)
            self.bot.send_whisper(recipient, '{} Received: {}'.format(msg, item))

    @staticmethod
    def separate_party(party, num_main_adventurers):
        main_adventurers = [party[0]]

        main_adventurers += sample(party[1:], num_main_adventurers-1)

        temp_set = set(party)
        other_adventurers = [x for x in party if x not in temp_set]

        return main_adventurers, other_adventurers

    @staticmethod
    def list_out_items(some_list, join_word='and', prefix='', empty_word='no one'):
        list_length = len(some_list)
        if list_length == 0:
            return empty_word
        elif list_length == 1:
            return '{0}{1}'.format(prefix, some_list[0])
        elif list_length == 2:
            return '{0}{1} {2} {0}{3}'.format(prefix, some_list[0], join_word, some_list[1])
        else:
            list_string = ''
            for item in some_list[:-1]:
                list_string += prefix + str(item) + ', '
            list_string += join_word + ' ' + prefix + some_list[-1]
            return list_string
