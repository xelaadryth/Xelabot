from random import randint, getrandbits

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

        self.starting_segment = Start


class Start(QuestSegment):
    def set_commands(self):
        self.commands = CommandSet(exact_match_commands={
            '!left': self.enter,
            '!right': self.enter
        })

    def play(self):
        self.channel.send_msg(
            'While running from a massive frost troll, {} finds two doors. '
            'Do you take the !left or the !right door?'.format(self.quest.party[0]))

    def enter(self, display_name):
        if display_name not in self.quest.party:
            return

        gold = GOLD_REWARD + randint(-GOLD_VARIANCE, GOLD_VARIANCE)

        if bool(getrandbits(1)):
            self.channel.send_msg('{0} opens the door and discovers a treasure chest! '
                                  '{0} gains {1} gold and gains {2} exp.'.format(display_name, gold, EXP_REWARD))
            self.reward(display_name, gold=gold, exp=EXP_REWARD)
        else:
            self.channel.send_msg('{0} dashes through the door and is immediately swallowed by a giant poro. '
                                  '{0} loses {1} gold.'.format(display_name, gold))
            self.penalize(display_name, gold=gold)

        self.complete_quest()

    def timeout(self):
        self.channel.send_msg(
            '{0} hesitated too long, and is nommed to death by the frost troll. RIP in peace. '
            '{0} loses {1} gold.'.format(self.quest.party[0], GOLD_TIMEOUT_PENALTY))
        self.penalize(self.quest.party[0], gold=GOLD_TIMEOUT_PENALTY)

        self.complete_quest()
