from random import choice, randint

from ..quest import Quest
from ..quest_segment import QuestSegment
from utils.command_set import CommandSet


GOLD_REWARD = 300
GOLD_VARIANCE = 27
EXP_REWARD = 3
EXP_PACIFIST_REWARD = 5


class Duel(Quest):
    def __init__(self, quest_manager):
        super().__init__(quest_manager)

        self.starting_segment = Start

        # Randomize the duel word so you can't macro it
        self.duel_word = choice(['!attack', '!fight', '!strike', '!charge'])


class Start(QuestSegment):
    def set_commands(self):
        self.commands = CommandSet(exact_match_commands={
            self.quest.duel_word: self.attack
        })

    def play(self):
        self.channel.send_msg(
            '{} and {} end up in a duel over some loot! The first to {} will be the victor!'.format(
                self.quest.party[0], self.quest.party[1], self.quest.duel_word))

        self.timeout_advance(Timeout)

    def attack(self, display_name):
        if display_name in self.quest.party:
            winner = display_name
            loser = self.quest.party[0] if self.quest.party[0] != winner else self.quest.party[1]

            gold = GOLD_REWARD + randint(-GOLD_VARIANCE, GOLD_VARIANCE)

            self.channel.send_msg(
                '{0} was quicker on the draw! There\'s nothing left of {1} but a smoking pile of flesh. '
                '{0} gains {2} exp and steals {3} gold from {1}!'.format(winner, loser, EXP_REWARD, gold))
            self.player_manager.add_exp(winner, EXP_REWARD)
            self.player_manager.add_gold(winner, gold)
            self.player_manager.remove_gold(loser, gold)

            self.complete_quest()


class Timeout(QuestSegment):
    def play(self):
        self.channel.send_msg(
            '{0} and {1} are apparently pacifists and neither raises a weapon. Both gain {2} exp!'.format(
                self.quest.party[0]), self.quest.party[1], EXP_PACIFIST_REWARD)
        self.player_manager.add_exp(self.quest.party[0], EXP_PACIFIST_REWARD)
        self.player_manager.add_exp(self.quest.party[1], EXP_PACIFIST_REWARD)

        self.complete_quest()
