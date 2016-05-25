from random import choice, randint

from ..quest import Quest
from ..quest_segment import QuestSegment
import settings
from utils.command_set import CommandSet
from utils.string_parsing import list_to_string


GOLD_REWARD = 160
GOLD_PENALTY_SMALL = 80
GOLD_PENALTY = GOLD_PENALTY_SMALL * 2
GOLD_REWARD_MEDIUM = 340
GOLD_REWARD_BIG = 440
GOLD_VARIANCE = 22
EXP_REWARD = 2
EXP_REWARD_MEDIUM = 4
EXP_REWARD_BIG = 6
DROP_CHANCE = 0.2
DROP_ITEM = 'Massive Fang'

MONSTER_NAME = 'Vilemaw'
MONSTER_LEVEL = settings.LEVEL_CAP * 3
LEVEL_VARIANCE = settings.LEVEL_CAP / 2


class Run(Quest):
    def __init__(self, quest_manager):
        super().__init__(quest_manager)

        self.starting_segment = Start

        # Randomize the escape word so it can't be copy-pasted
        self.escape_word = choice(['!run', '!flee', '!hide', '!escape', '!stealth'])
        # People that have already escaped
        self.escaped = []

        self.attacked_sides = set()
        self.attacking_players = []


class Start(QuestSegment):
    def set_commands(self):
        self.commands = CommandSet(exact_match_commands={
            self.quest.escape_word: self.escape
        })

    def play(self):
        self.channel.send_msg(
            '{0} are all running away from a rampaging {1}! Quick, type {2} to get away!'.format(
                list_to_string(self.quest.party), MONSTER_NAME, self.quest.escape_word
            )
        )

    def escape(self, display_name):
        # Has to be a new player to be valid input
        if display_name not in self.quest.party or display_name in self.quest.escaped:
            return

        self.quest.escaped.append(display_name)

        if len(self.quest.escaped) == len(self.quest.party) - 1:
            self.timeout()

    def timeout(self):
        # Some people are left behind
        if self.quest.escaped:
            self.captured()
        else:
            self.advance(BossBattle)

    def captured(self):
        losers = set(self.quest.party) - set(self.quest.escaped)

        gold_gained = GOLD_REWARD + randint(-GOLD_VARIANCE, GOLD_VARIANCE)
        gold_lost = GOLD_PENALTY + randint(-GOLD_VARIANCE, GOLD_VARIANCE)

        self.channel.send_msg(
            'In the end, {0} managed to escape from {1} unscathed! {1} happily munches on {2} with terrifying '
            'crunches, snaps, and some odd purring noises. Those that escaped gain {3} gold and {4} exp, '
            'while those left behind lose {5} gold.'.format(
                list_to_string(self.quest.escaped), MONSTER_NAME, losers, gold_gained, EXP_REWARD, gold_lost
            )
        )
        self.reward(self.quest.escaped, gold=gold_gained, exp=EXP_REWARD)
        self.penalize(losers, gold=gold_lost)

        self.complete_quest()


class BossBattle(QuestSegment):
    def set_commands(self):
        self.commands = CommandSet(exact_match_commands={
            '!front': lambda display_name: self.attack(display_name, 'front'),
            '!left': lambda display_name: self.attack(display_name, 'left'),
            '!right': lambda display_name: self.attack(display_name, 'right')
        })

    def play(self):
        self.channel.send_msg(
            '{0} stand their ground and bravely decide to fight {1}! Surround and attack the !front, !left, and !right '
            'to see if you are strong enough to defeat this massive foe!'.format(
                list_to_string(self.quest.party), MONSTER_NAME
            )
        )

    def attack(self, display_name, direction):
        # Has to be a new player to be valid input
        if display_name not in self.quest.party or display_name in self.quest.attacking_players:
            return

        self.quest.attacking_players.append(display_name)
        self.quest.attacked_sides.add(direction)

        if len(self.quest.attacking_players) == len(self.quest.party):
            if len(self.quest.attacked_sides) == 3:
                self.battle()
            else:
                self.timeout()

    def battle(self):
        level = randint(-LEVEL_VARIANCE, LEVEL_VARIANCE) + self.sum_levels(self.quest.attacking_players)
        gold_penalty = GOLD_PENALTY_SMALL + randint(-GOLD_VARIANCE, GOLD_VARIANCE)
        gold_stolen = GOLD_REWARD_MEDIUM + randint(-GOLD_VARIANCE, GOLD_VARIANCE)

        cowards = set(self.quest.party) - set(self.quest.attacking_players)
        coward_message = '{0} slipped away while pocketing {1} gold in the confusion.'.format(list_to_string(cowards),
                                                                                              gold_stolen)

        if level < MONSTER_LEVEL / 2:
            self.channel.send_msg(
                '{0} barely managed to surround {1}, but they were swatted down like flies against a giant spider '
                'with 8 flyswatters. Each lose {2} gold.{3}'.format(
                    list_to_string(self.quest.attacking_players), MONSTER_NAME, gold_penalty,
                    coward_message if cowards else ''
                )
            )
            self.penalize(self.quest.attacking_players, gold=gold_penalty)
            self.reward(cowards, gold=gold_stolen, exp=EXP_REWARD_MEDIUM)
        elif level < MONSTER_LEVEL:
            self.channel.send_msg(
                '{0} surrounded {1} and seemed like they had a chance to win, but ended up tactically repositioning '
                'somewhere...anywhere else. Each lose {2} gold.{3}'.format(
                    list_to_string(self.quest.party), MONSTER_NAME, gold_penalty, coward_message if cowards else ''
                )
            )
            self.penalize(self.quest.attacking_players, gold=gold_penalty)
            self.reward(cowards, gold=gold_stolen, exp=EXP_REWARD_MEDIUM)
        else:
            gold = GOLD_REWARD_BIG + randint(-GOLD_VARIANCE, GOLD_VARIANCE)
            self.channel.send_msg(
                '{0} gracefully and brilliantly surrounded {1}, launching devastating blow after blow in a coordinated '
                'joint assault! {1} has been defeated! Woohoo! Everyone gains {2} gold and {3} exp!'.format(
                    list_to_string(self.quest.party), MONSTER_NAME, gold, EXP_REWARD_BIG
                )
            )
            self.reward(self.quest.party, gold=gold, exp=EXP_REWARD_BIG)

            self.drop_item(self.quest.attacking_players, DROP_ITEM, DROP_CHANCE,
                           'After the battle, you manage to salvage something valuable from the corpse of {0}!'.format(
                               MONSTER_NAME))

        self.complete_quest()

    def timeout(self):
        if len(self.quest.attacked_sides) == 3:
            self.battle()
            return

        gold = GOLD_PENALTY + randint(-GOLD_VARIANCE, GOLD_VARIANCE)

        if self.quest.attacked_sides:
            self.channel.send_msg(
                '{0} just attacked {1}, so {2} tore everyone to shreds. And then shredded those shreds. '
                'Everyone loses {3} gold.'.format(
                    list_to_string(self.quest.party), list_to_string(self.quest.attacked_sides, prefix='the '),
                    MONSTER_NAME, gold
                )
            )
        else:
            self.channel.send_msg(
                '{0} mistook stupidity for bravery, and rectified the mistake by promptly devouring {1}. '
                'Everyone loses {2} gold'.format(MONSTER_NAME, list_to_string(self.quest.party),  gold)
            )
        self.penalize(self.quest.party, gold=gold)

        self.complete_quest()
