import copy
from random import randint

from ..quest import Quest
from ..quest_segment import QuestSegment
from utils.command_set import CommandSet
from utils.string_parsing import list_to_string


GOLD_REWARD = 350
GOLD_PENALTY = 50
GOLD_PENALTY_WAIT = 120
GOLD_VARIANCE = 26
EXP_REWARD = 3


class Prison(Quest):
    def __init__(self, quest_manager):
        super().__init__(quest_manager)

        self.starting_segment = Start


class Start(QuestSegment):
    def set_commands(self):
        commands = {}
        for party_member in self.quest.party[1:]:
            # Due to party_member changing every iteration, we have to copy the value of party_member
            # to something else, or the same reference will be used for every iteration
            commands['!{}'.format(party_member.lower())] = (
                lambda display_name, target=party_member: self.pick(display_name, target))
        self.commands = CommandSet(exact_match_commands=commands)

    def play(self):
        self.channel.send_msg(
            'In the Castle of the Mad Yordle, {0} stumbles across a prison full of comrades. But the castle is '
            'collapsing with only time to save one! Do you save {1}?'.format(
                self.quest.party[0], list_to_string(self.quest.party[1:], join_word='or', prefix='!')
            )
        )

    def pick(self, display_name, saved):
        # Has to be the first player to be valid input
        if display_name != self.quest.party[0]:
            return

        gold_gained = GOLD_REWARD + randint(-GOLD_VARIANCE, GOLD_VARIANCE)
        gold_lost = GOLD_PENALTY + randint(-GOLD_VARIANCE, GOLD_VARIANCE)

        forsaken_adventurers = [player for player in self.quest.party if player != display_name and player != saved]
        self.channel.send_msg(
            '{0} decided to save {1}! {2} are left behind and crushed under the rubble of the collapsing castle, '
            'losing {3} gold. {0} and {1} gain {4} gold and {5} exp!'.format(
                display_name, saved, list_to_string(forsaken_adventurers), gold_lost, gold_gained, EXP_REWARD
            )
        )
        self.reward([display_name, saved], gold=gold_gained, exp=EXP_REWARD)
        self.penalize(forsaken_adventurers, gold=gold_lost)

        self.complete_quest()

    def timeout(self):
        gold_lost = GOLD_PENALTY_WAIT + randint(-GOLD_VARIANCE, GOLD_VARIANCE)

        self.channel.send_msg(
            '{0} took too long deciding who to save, so everyone ended up crushed by the collapsing castle. {1} '
            'all lose {2} gold. Ouch.'.format(
                self.quest.party[0], self.quest.party, gold_lost
            )
        )
        self.penalize(self.quest.party, gold=gold_lost)

        self.complete_quest()
