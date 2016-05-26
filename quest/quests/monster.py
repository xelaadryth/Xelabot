from random import getrandbits, randint

from ..quest import Quest
from ..quest_segment import QuestSegment
import settings
from utils.command_set import CommandSet


GOLD_SAFE_REWARD = 75
GOLD_VARIANCE_SAFE = 21
EXP_SAFE_REWARD = 2
GOLD_RISKY_PENALTY = 200
GOLD_RISKY_REWARD = 300
GOLD_RISKY_REWARD_BIG = 400
GOLD_VARIANCE_RISKY = GOLD_VARIANCE_SAFE * 2
EXP_RISKY_REWARD = EXP_SAFE_REWARD * 2
EXP_RISKY_REWARD_BIG = EXP_SAFE_REWARD + 1
GOLD_TIMEOUT_PENALTY = 300
MONSTER_LEVEL = 12
LEVEL_VARIANCE = 15


class Monster(Quest):
    def __init__(self, quest_manager):
        super().__init__(quest_manager)

        self.starting_segment = Start


class Start(QuestSegment):
    def set_commands(self):
        self.commands = CommandSet(exact_match_commands={
            '!attack': self.attack,
            '!flee': self.flee
        })

    def play(self):
        msg = (
            'In the treasure room of an abandoned ruin, a strange Void creature materializes in front of {}. '
            'Do you !attack or !flee?'.format(self.quest.party[0]))
        self.channel.send_msg(msg)

    def attack(self, display_name):
        if display_name not in self.quest.party:
            return

        level = randint(-LEVEL_VARIANCE, LEVEL_VARIANCE) + self.player_manager.get_level(display_name)

        if level < -2:
            gold = GOLD_RISKY_PENALTY + randint(-GOLD_VARIANCE_RISKY, GOLD_VARIANCE_RISKY)
            msg = (
                '{0} never stood a chance, getting immediately suppressed and mobbed to death by Voidlings without '
                'so much as a chance to twitch. Maybe try leveling up! {0} loses {1} gold.'.format(display_name, gold))
            self.channel.send_msg(msg)
            self.penalize(display_name, gold=gold)
        elif level < MONSTER_LEVEL:
            gold = GOLD_RISKY_PENALTY + randint(-GOLD_VARIANCE_RISKY, GOLD_VARIANCE_RISKY)
            msg = (
                '{0} charges towards the Void creature and gets immediately vaporized by lazers. Pew Pew! '
                '{0} loses {1} gold.'.format(display_name, gold))
            self.channel.send_msg(msg)
            self.penalize(display_name, gold=gold)
        elif level < settings.LEVEL_CAP + LEVEL_VARIANCE / 3:
            gold = GOLD_RISKY_REWARD + randint(GOLD_VARIANCE_RISKY, GOLD_VARIANCE_RISKY)
            msg = (
                '{0} manages to slay the Void creature after a long struggle and some celebratory crumpets. '
                '{0} gains {1} gold and {2} exp.'.format(display_name, gold, EXP_RISKY_REWARD))
            self.channel.send_msg(msg)
            self.reward(display_name, gold=gold, exp=EXP_RISKY_REWARD)
        else:
            gold = GOLD_RISKY_REWARD_BIG + randint(GOLD_VARIANCE_RISKY, GOLD_VARIANCE_RISKY)
            msg = (
                '{0} dismembers the creature with almost surgical precision, and even discovers a new class of '
                'organ in the process. Hurrah! '
                '{0} gains {1} gold and {2} exp.'.format(display_name, gold, EXP_RISKY_REWARD_BIG))
            self.channel.send_msg(msg)
            self.reward(display_name, gold=gold, exp=EXP_RISKY_REWARD_BIG)

        self.complete_quest()

    def flee(self, display_name):
        if display_name not in self.quest.party:
            return

        gold = GOLD_SAFE_REWARD + randint(-GOLD_VARIANCE_SAFE, GOLD_VARIANCE_SAFE)

        if bool(getrandbits(1)):
            msg = (
                '{0} manages to bravely run away in the face of overwhelming power, '
                'and even manages to snatch a few coins on the way out! '
                '{0} gains {1} gold and {2} exp.'.format(display_name, gold, EXP_SAFE_REWARD))
            self.reward(display_name, gold=gold, exp=EXP_SAFE_REWARD)
            self.channel.send_msg(msg)
        else:
            msg = ('{0} tries to run away but is torn to shreds by blade-like arms. Owie! '
                   '{0} loses {1} gold.'.format(display_name, gold))
            self.channel.send_msg(msg)
            self.penalize(display_name, gold=gold)

        self.complete_quest()

    def timeout(self):
        self.channel.send_msg(
            '{0} makes no motion to attack or flee, and instead stands motionless in the face of the enemy. '
            '{0} becomes covered by caustic spittle, digested alive, and slowly devoured. '
            '{0} loses {1} gold.'.format(self.quest.party[0], GOLD_TIMEOUT_PENALTY))
        self.penalize(self.quest.party[0], gold=GOLD_TIMEOUT_PENALTY)

        self.complete_quest()
