from random import randint

from ..quest import Quest
from ..quest_segment import QuestSegment
from utils.command_set import CommandSet
from utils.string_parsing import list_to_string


GOLD_REWARD = 250
GOLD_PENALTY = 75
GOLD_REWARD_BIG = 400
GOLD_VARIANCE = 35
EXP_REWARD = 3
EXP_REWARD_BIG = 5


class Gates(Quest):
    def __init__(self, quest_manager):
        super().__init__(quest_manager)

        self.starting_segment = Start

        self.defended_sides = set()
        self.guarding_players = []


class Start(QuestSegment):
    def set_commands(self):
        self.commands = CommandSet(exact_match_commands={
            '!north': lambda display_name: self.guard(display_name, 'north'),
            '!south': lambda display_name: self.guard(display_name, 'south'),
            '!east': lambda display_name: self.guard(display_name, 'east'),
            '!west': lambda display_name: self.guard(display_name, 'west')
        })

    def play(self):
        msg = (
            '{} are defending an Avorosan town from a Frostguard invasion! Split up and defend the '
            '!north, !south, !east, and !west gates!'.format(list_to_string(self.quest.party))
        )
        self.channel.send_msg(msg)

    def guard(self, display_name, direction):
        # Has to be a new player to be valid input
        if display_name not in self.quest.party or display_name in self.quest.guarding_players:
            return

        self.quest.guarding_players.append(display_name)
        self.quest.defended_sides.add(direction)

        if len(self.quest.defended_sides) == 4:
            self.successful_defense()
        elif len(self.quest.guarding_players) == len(self.quest.party):
            self.timeout()

    def successful_defense(self):
        gold = GOLD_REWARD + randint(-GOLD_VARIANCE, GOLD_VARIANCE)
        msg = (
            '{0} have successfully held the gates, huzzah! {1} gold and {2} exp for all!'.format(
                list_to_string(self.quest.party), gold, EXP_REWARD
            )
        )
        self.channel.send_msg(msg)
        self.reward(self.quest.party, gold=gold, exp=EXP_REWARD)

        self.complete_quest()

    def timeout(self):
        if not self.quest.guarding_players:
            gold = GOLD_REWARD_BIG + randint(-GOLD_VARIANCE, GOLD_VARIANCE)

            # Let the invaders in!
            msg = (
                '{0} have secretly managed to collaborate with the Frostguard raiders, letting them all in without '
                'any opposition. For your devious work, everyone is rewarded with {1} gold and {2} exp!'.format(
                    list_to_string(self.quest.party), gold, EXP_REWARD_BIG
                )
            )
            self.channel.send_msg(msg)
            self.reward(self.quest.party, gold=gold, exp=EXP_REWARD_BIG)
        else:
            gold = GOLD_PENALTY + randint(-GOLD_VARIANCE, GOLD_VARIANCE)

            msg = (
                '{0} only managed to defend the {1} {2}. How pitiful. The Frostguard storm the town and murdalize '
                'all the people. Everyone loses {3} gold.'.format(
                    list_to_string(self.quest.party), list_to_string(self.quest.defended_sides),
                    'gate' if len(self.quest.defended_sides) == 1 else 'gates', gold
                )
            )
            self.channel.send_msg(msg)
            self.penalize(self.quest.party, gold=gold)

        self.complete_quest()
