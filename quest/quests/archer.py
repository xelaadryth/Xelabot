from random import randint

from ..quest import Quest
from ..quest_segment import QuestSegment
from utils.command_set import CommandSet


GOLD_REWARD = 190
GOLD_PENALTY = 315
GOLD_REWARD_BIG = 240
GOLD_PENALTY_SMALL = 75
GOLD_PENALTY_WAIT = 150
GOLD_VARIANCE = 22
EXP_REWARD = 2


class Archer(Quest):
    def __init__(self, quest_manager):
        super().__init__(quest_manager)

        self.starting_segment = Start

        self.first_player = None
        self.first_action = None


class Start(QuestSegment):
    def set_commands(self):
        self.commands = CommandSet(exact_match_commands={
            '!left': lambda display_name: self.move(display_name, 'left'),
            '!right': lambda display_name: self.move(display_name, 'right')
        })

    def play(self):
        self.channel.send_msg(
            '{} and {} are pinned down by a Noxian archer! '
            'One of you go !left and the other go !right to flank him!'.format(
                self.quest.party[0], self.quest.party[1]
            )
        )

    def move(self, display_name, direction):
        # Has to be a new player to be valid input
        if display_name not in self.quest.party or display_name == self.quest.first_player:
            return

        if self.quest.first_action:
            # Second action, this ends the quest
            if direction == self.quest.first_action:
                # Same direction
                gold = GOLD_PENALTY + randint(-GOLD_VARIANCE, GOLD_VARIANCE)

                self.channel.send_msg(
                    '{0} and {1} apparently suck at coordination and both ended up going the same direction. '
                    'At least you got the archer an achievement for a double kill with a single arrow! '
                    'Both of you lose {2} gold.'.format(self.quest.party[0], self.quest.party[1], gold)
                )
                self.penalize(self.quest.party, gold=gold)
            else:
                # Flanked correctly
                gold = GOLD_REWARD + randint(-GOLD_VARIANCE, GOLD_VARIANCE)

                self.channel.send_msg(
                    '{0} and {1} skillfully flank the archer and eviscerate him! Easy games easy life. '
                    'Both of you gain {2} gold and {3} exp!'.format(
                        self.quest.party[0], self.quest.party[1], gold, EXP_REWARD
                    )
                )
                self.reward(self.quest.party, gold=gold, exp=EXP_REWARD)

            self.complete_quest()
        else:
            self.quest.first_player = display_name
            self.quest.first_action = direction

    def timeout(self):
        if self.quest.first_action:
            loser = self.quest.party[0] if self.quest.party[0] != self.quest.first_player else self.quest.party[1]
            gold_gained = GOLD_REWARD_BIG + randint(-GOLD_VARIANCE, GOLD_VARIANCE)
            gold_lost = GOLD_PENALTY_SMALL + randint(-GOLD_VARIANCE, GOLD_VARIANCE)

            self.channel.send_msg(
                '{0} didn\'t move and just used {1} as a decoy to distract the archer while making off with the loot! '
                'What a scoundrel! {0} gains {2} exp and {3} gold while {1} loses {4} gold.'.format(
                    self.quest.first_player, loser, EXP_REWARD, gold_gained, gold_lost
                )
            )
            self.reward(self.quest.first_player, gold=gold_gained, exp=EXP_REWARD)
            self.penalize(loser, gold=gold_lost)
        else:
            gold = GOLD_PENALTY_WAIT + randint(-GOLD_VARIANCE, GOLD_VARIANCE)
            self.channel.send_msg(
                'Neither {0} nor {1} want to make a move, and eventually both get picked off like sitting ducks. Rekt.'
                'Both lose {2} gold.'.format(self.quest.party[0], self.quest.party[1])
            )
            self.penalize(self.quest.party, gold)

        self.complete_quest()
