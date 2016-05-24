import random

from ..quest import Quest
from ..quest_segment import QuestSegment
from utils.command_set import CommandSet


GOLD_REWARD = 150
GOLD_VARIANCE = 27
EXP_REWARD = 3
GOLD_TIMEOUT_PENALTY = 400


class Doors(Quest):
    def __init__(self, quest_manager):
        super().__init__(quest_manager)

        self.starting_segment = LeftOrRight


class LeftOrRight(QuestSegment):
    def set_commands(self):
        self.commands = CommandSet(exact_match_commands={
            '!left': self.enter,
            '!right': self.enter
        })

    def play(self):
        self.channel.send_msg(
            'While running from a massive frost troll, {} finds two doors. '
            'Do you take the !left or the !right door?'.format(self.quest.party[0]))

        self.timeout_advance(Timeout)

    def enter(self, display_name):
        if display_name in self.quest.party:
            gold = GOLD_REWARD + random.randint(-GOLD_VARIANCE, GOLD_VARIANCE)

            if bool(random.getrandbits(1)):
                self.channel.send_msg('{0} dashes through the door and is immediately swallowed by a giant poro. '
                                      '{0} loses {1} gold.'.format(display_name, gold))
                self.player_manager.remove_gold(display_name, gold)
            else:
                self.channel.send_msg('{0} opens the door and discovers a treasure chest! '
                                      '{0} gains {1} exp and gains {2} gold.'.format(display_name, EXP_REWARD, gold))
                self.player_manager.add_exp(display_name, EXP_REWARD)
                self.player_manager.add_gold(display_name, gold)

            self.complete_quest()


class Timeout(QuestSegment):
    def play(self):
        self.channel.send_msg(
            '{0} hesitated too long, and is nommed to death by the frost troll. RIP in peace. '
            '{0} loses {1} gold.'.format(self.quest.party[0]), GOLD_TIMEOUT_PENALTY)
        self.bot.player_manager.remove_gold(self.quest.party[0], GOLD_TIMEOUT_PENALTY)

        self.complete_quest()
