from random import choice, randint, random

from ..quest import Quest
from ..quest_segment import QuestSegment
import settings
from utils.command_set import CommandSet


GOLD_REWARD = 160
GOLD_PENALTY_SMALL = 80
GOLD_PENALTY = GOLD_PENALTY_SMALL * 2
GOLD_REWARD_BIG = 440
GOLD_VARIANCE = 22
EXP_REWARD = 2
EXP_REWARD_BIG = 6
DROP_CHANCE = 0.2
DROP_ITEM = 'Massive Fang'

MONSTER_NAME = 'Vilemaw'
MONSTER_LEVEL = settings.LEVEL_CAP * 4
LEVEL_VARIANCE = settings.LEVEL_CAP / 2


class Run(Quest):
    def __init__(self, quest_manager):
        super().__init__(quest_manager)

        self.starting_segment = Start

        # Randomize the escape word so it can't be copy-pasted
        self.escape_word = choice(['!run', '!flee', '!hide', '!escape', '!stealth'])
        # People that have already escaped
        self.escaped = []

        self.attacked_sides = []
        self.attacking_players = []


class Start(QuestSegment):
    def set_commands(self):
        self.commands = CommandSet(exact_match_commands={
            self.quest.escape_word: self.escape
        })

    def play(self):
        self.channel.send_msg(
            '{0} are all running away from a rampaging {1}! Quick, type {2} to get away!'.format(
                self.list_out_items(self.quest.party), MONSTER_NAME, self.quest.escape_word
            )
        )

        self.timeout_advance(Timeout)

    def escape(self, display_name):
        # Has to be a new player to be valid input
        if display_name not in self.quest.party or display_name in self.quest.escaped:
            return

        self.quest.escaped.append(display_name)

        if len(self.quest.escaped) == len(self.quest.party) - 1:
            self.advance(Timeout)


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
                self.list_out_items(self.quest.party), MONSTER_NAME
            )
        )
        self.timeout_advance(Defeat)

    def attack(self, display_name, direction):
        # Has to be a new player to be valid input
        if display_name not in self.quest.party or display_name in self.quest.attacking_players:
            return

        self.quest.attacking_players.append(display_name)
        self.quest.attacked_sides.append(direction)

        if len(self.quest.attacked_sides) == 3:
            self.battle()
        elif len(self.quest.attacking_players) == len(self.quest.party):
            self.advance(Defeat)

    def battle(self):
        level = randint(-LEVEL_VARIANCE, LEVEL_VARIANCE) + self.sum_levels(self.quest.attacking_players)
        gold = GOLD_PENALTY_SMALL + randint(-GOLD_VARIANCE, GOLD_VARIANCE)

        if level < MONSTER_LEVEL / 2:
            self.channel.send_msg(
                '{0} barely managed to surround {1}, but their power wasn\'t nearly enough and they were swatted down '
                'like flies. And then eaten. And then regurgitated and eaten again. Everyone loses {2} gold.'.format(
                    self.list_out_items(self.quest.party), MONSTER_NAME, gold
                )
            )
            self.penalize(self.quest.party, gold=gold)
        elif level < MONSTER_LEVEL:
            self.channel.send_msg(
                '{0} surrounded {1} and seemed like they had a chance to win, but then {1} started trying '
                'and crushed them mercilessly. Better luck next time! Everyone loses {2} gold.'.format(
                    self.list_out_items(self.quest.party), MONSTER_NAME, gold
                )
            )
            self.penalize(self.quest.party, gold=gold)
        else:
            gold = GOLD_REWARD_BIG + randint(-GOLD_VARIANCE, GOLD_VARIANCE)
            self.channel.send_msg(
                '{0} gracefully and brilliantly surrounded {1}, launching devastating blow after blow in a coordinated '
                'joint assault! {1} has been defeated! Woohoo! Everyone gains {2} gold and {3} exp!'.format(
                    self.list_out_items(self.quest.party), MONSTER_NAME, gold, EXP_REWARD_BIG
                )
            )
            self.reward(self.quest.party, gold=gold, exp=EXP_REWARD_BIG)

            self.drop_item(self.quest.party, DROP_ITEM, DROP_CHANCE,
                           'After the battle, you manage to salvage something valuable from the corpse of {0}!'.format(
                               MONSTER_NAME))

        self.complete_quest()


class Defeat(QuestSegment):
    def play(self):
        gold = GOLD_PENALTY + randint(-GOLD_VARIANCE, GOLD_VARIANCE)

        self.channel.send_msg(
            '{0} just attacked {1}, so their power wasn\'t enough. The aftermath of the "battle" was pretty brutal, '
            'but everyone wound up as a mixture of fine paste and dust. Everyone loses {2} gold.'.format(
                self.list_out_items(self.quest.party),
                self.list_out_items(self.quest.attacked_sides, prefix='the ', empty_word='nothing'), gold
            )
        )
        self.penalize(self.quest.party, gold=gold)

        self.complete_quest()


class Timeout(QuestSegment):
    def play(self):
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
                self.list_out_items(self.quest.escaped), MONSTER_NAME, losers, gold_gained, EXP_REWARD, gold_lost
            )
        )
        self.reward(self.quest.escaped, gold=gold_gained, exp=EXP_REWARD)
        self.penalize(losers, gold=gold_lost)

        self.complete_quest()
