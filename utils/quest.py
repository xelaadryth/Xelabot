import random

import settings
from .timer_thread import TimerThread


class Quest:

    def __init__(self, channel, bot):
        self.channel = channel
        self.bot = bot

        self.commands = {'!quest': self.create_party}
        self.adventurers = []
        self.main_adventurers = []
        self.other_adventurers = []
        self.end_quest = None
        self.adventurer_actions = {}

        self.quest_state = 0

        self.timer = None

        # quest_lists takes a number of main_adventurers
        self.quest_lists = [
            [],
            [self.quest_chamber, self.quest_monster],
            [self.quest_duel, self.quest_archer],
            [self.quest_escape],
            [self.quest_prison, self.quest_escape],
            [self.quest_prison, self.quest_escape, self.quest_gates],
            [self.quest_prison, self.quest_escape, self.quest_gates]
        ]

    def update(self):
        if self.timer is not None and self.timer.is_complete():
            self.quest_advance()

    def check_commands(self, user, original_msg):
        msg = original_msg.lower()
        if msg in self.commands:
            self.commands[msg](user, original_msg)

    def start_timer(self, duration):
        self.timer = TimerThread(duration)

    def kill_timer(self):
        if self.timer is not None:
            self.timer.stop()
            self.timer = None

    def quest_cooldown(self):
        self.commands = {'!quest': self.quest_recharging}
        self.quest_state = 0
        self.start_timer(self.channel.channel_settings['quest_cooldown'])

    def quest_advance(self):
        self.timer = None

        # Completed cooldown
        if self.quest_state == 0:
            self.ready_quest()
        # Adventurers gathered and quest beginning
        elif self.quest_state == 1:
            self.start_quest()
        elif self.quest_state == 2:
            self.end_quest()

    def ready_quest(self):
        self.adventurers = []
        self.main_adventurers = []
        self.other_adventurers = []
        self.commands = {'!quest': self.create_party}
        self.adventurer_actions = {}
        self.quest_state = 1

    def start_quest(self):
        self.generate_quest()

        self.quest_state = 2
        self.start_timer(settings.QUEST_DURATION)

    def generate_quest(self, ):
        # Set the default quest
        cur_quest = random.choice(self.quest_lists[len(self.adventurers)])

        cur_quest()

    def quest_recharging(self, user, msg):
        self.channel.send_msg('Sorry ' + user + ', quests take ' +
                              str(self.channel.channel_settings['quest_cooldown']) + ' seconds to recharge. (' +
                              str(self.timer.remaining()) + ' seconds remaining.)')

    def create_party(self, user, msg):
        self.channel.send_msg(user + ' wants to attempt a quest. Type "!quest" to join!')
        self.adventurers = [user]

        self.commands = {
            '!quest': self.join_quest
        }

        self.quest_state = 1

        self.start_timer(settings.QUEST_DURATION)

    def join_quest(self, user, msg):
        if self.quest_state == 1:
            if user not in self.adventurers:
                self.adventurers.append(user)
                if len(self.adventurers) >= len(self.quest_lists) - 1:
                    self.kill_timer()
                    self.quest_advance()

    def separate_main_adventurers(self, num_main_adventurers):
        self.main_adventurers = [self.adventurers[0]]

        self.main_adventurers += random.sample(self.adventurers[1:], num_main_adventurers-1)

        temp_set = set(self.main_adventurers)
        self.other_adventurers = [x for x in self.adventurers if x not in temp_set]

    def list_out_items(self, some_list, join_word='and', prefix=''):
        list_length = len(some_list)
        if list_length == 0:
            return 'no one'
        elif list_length == 1:
            return prefix + str(some_list[0])
        elif list_length == 2:
            return prefix + str(some_list[0]) + ' ' + join_word + ' ' + prefix + str(some_list[1])
        else:
            list_string = ''
            for item in some_list[:-1]:
                list_string += prefix + str(item) + ', '
            list_string += join_word + ' ' + prefix + some_list[-1]
            return list_string

    # ==================================================================================================================
    # ==================================================================================================================
    # ============================================== QUESTS BELOW ======================================================
    # ==================================================================================================================
    # ==================================================================================================================

    def quest_chamber(self):
        self.separate_main_adventurers(1)
        self.channel.send_msg('While running from a massive frost troll, ' + self.main_adventurers[0] +
                              ' finds two doors. Do you take the !left or the !right door?')
        self.commands = {
            '!left': self.quest_chamber_result,
            '!right': self.quest_chamber_result
        }
        self.end_quest = self.quest_chamber_timeout

    def quest_chamber_result(self, user, msg):
        if user in self.main_adventurers:
            self.kill_timer()
            if bool(random.getrandbits(1)):
                self.channel.send_msg(user + ' dashes through the door and is immediately swallowed by a giant poro. ' +
                                      user + ' loses 150 gold.')
                self.bot.player_manager.add_gold(user, -150)
            else:
                self.channel.send_msg(user + ' opens the door and discovers a treasure chest! ' + user +
                                      ' gains 3 exp and gains 300 gold.')
                self.bot.player_manager.add_exp(user, 3)
                self.bot.player_manager.add_gold(user, 300)

            self.quest_cooldown()

    def quest_chamber_timeout(self):
        self.channel.send_msg(self.main_adventurers[0] + ' hesitated too long, and is nommed to death by the frost ' +
                              'troll. RIP in peace. ' + self.main_adventurers[0] + ' loses 400 gold.')
        self.bot.player_manager.add_gold(self.main_adventurers[0], -400)

        self.quest_cooldown()

    # ==================================================================================================================

    def quest_monster(self):
        self.separate_main_adventurers(1)
        self.channel.send_msg('In the treasure room of an abandoned ruin, a strange Void creature materializes in ' +
                              'front of ' + self.main_adventurers[0] + '. Do you !attack or !flee?')
        self.commands = {
            '!attack': self.quest_monster_attack_result,
            '!flee': self.quest_monster_flee_result
        }
        self.end_quest = self.quest_monster_timeout

    def quest_monster_attack_result(self, user, msg):
        if user in self.main_adventurers:
            self.kill_timer()
            level = random.randint(0, 40) + self.bot.player_manager.get_level(user)
            if level < 26:
                self.channel.send_msg(user + ' charges towards the Void creature and gets immediately vaporized by ' +
                                      'lazers. Pew Pew! ' + user + ' loses 175 gold.')
                self.bot.player_manager.add_gold(user, -175)
            elif level < 40:
                self.channel.send_msg(user + ' manages to slay the Void creature after a long struggle and some ' +
                                      'celebratory crumpets. ' + user + ' gains 3 exp and 275 gold.')
                self.bot.player_manager.add_exp(user, 3)
                self.bot.player_manager.add_gold(user, 275)
            else:
                self.channel.send_msg(user + ' dismembers the Void creature with almost surgical precision, ' +
                                      'and even discovers a new class of alien organ. Hurrah! ' + user +
                                      ' gains 2 exp and 400 gold.')
                self.bot.player_manager.add_exp(user, 2)
                self.bot.player_manager.add_gold(user, 400)

            self.quest_cooldown()

    def quest_monster_flee_result(self, user, msg):
        if user in self.main_adventurers:
            self.kill_timer()
            if bool(random.getrandbits(1)):
                self.channel.send_msg(user + ' tries to run away but is torn to shreds by blade-like arms. Owie! ' +
                                      user + ' loses 75 gold.')
                self.bot.player_manager.add_gold(user, -75)
            else:
                self.channel.send_msg(user + ' manages to bravely run away in the face of overwhelming power, ' +
                                      'and even manages to snatch a few coins on the way out! ' + user +
                                      ' gains 2 exp and 160 gold.')
                self.bot.player_manager.add_exp(user, 2)
                self.bot.player_manager.add_gold(user, 160)

            self.quest_cooldown()

    def quest_monster_timeout(self):
        self.channel.send_msg(self.main_adventurers[0] + ' makes no motion to attack or flee, and instead stands ' +
                              'motionless in the face of the enemy. ' + self.main_adventurers[0] +
                              ' becomes covered by caustic spittled, digested alive, and slowly devoured. ' +
                              self.main_adventurers[0] + ' loses 300 gold.')
        self.bot.player_manager.add_gold(self.main_adventurers[0], -300)

        self.quest_cooldown()

    # ==================================================================================================================
    # ==================================================================================================================

    def quest_duel(self):
        self.separate_main_adventurers(2)

        # Randomize the duel word so you can't macro it
        duel_words = ['!attack', '!fight', '!strike', '!slay']
        duel_word = random.choice(duel_words)

        self.channel.send_msg(self.main_adventurers[0] + ' and ' + self.main_adventurers[1] +
                              ' end up in a duel over some loot! The first to type ' + duel_word + ' is the victor!')
        self.commands = {
            duel_word: self.quest_duel_result
        }
        self.end_quest = self.quest_duel_timeout

    def quest_duel_result(self, user, msg):
        if user in self.main_adventurers:
            opponent = self.main_adventurers[0]
            if user == opponent:
                opponent = self.main_adventurers[1]
            self.kill_timer()
            self.channel.send_msg(user + " was quicker on the draw! There's nothing left of " + opponent +
                                  " except a smoking pile of flesh. " + user + " gains 3 exp and steals 300 gold!")
            self.bot.player_manager.add_exp(user, 3)
            self.bot.player_manager.add_gold(user, 300)
            self.bot.player_manager.add_gold(opponent, -300)

            self.quest_cooldown()

    def quest_duel_timeout(self):
        self.channel.send_msg(self.main_adventurers[0] + ' and ' + self.main_adventurers[1] +
                              ' are apparently pacifists and neither make a move. Both gain 2 exp!')
        self.bot.player_manager.add_exp(self.main_adventurers[0], 2)
        self.bot.player_manager.add_exp(self.main_adventurers[1], 2)

        self.quest_cooldown()

    # ==================================================================================================================

    def quest_archer(self):
        self.separate_main_adventurers(2)
        self.channel.send_msg(self.main_adventurers[0] + ' and ' + self.main_adventurers[1] +
                              ' are pinned down by a Noxian archer! One of you go !left and one of you go ' +
                              '!right to flank and defeat him!')
        self.commands = {
            '!left': self.quest_archer_result,
            '!right': self.quest_archer_result
        }
        self.end_quest = self.quest_archer_timeout

    def quest_archer_result(self, user, msg):
        if user in self.main_adventurers and user not in list(self.adventurer_actions.keys()):
            self.adventurer_actions[user] = msg[1:].lower()
            if len(self.adventurer_actions) == 2:
                self.kill_timer()
                self.quest_archer_timeout()

    def quest_archer_timeout(self):
        if len(self.adventurer_actions) == 2:
            if self.adventurer_actions[self.main_adventurers[0]] != self.adventurer_actions[self.main_adventurers[1]]:
                self.channel.send_msg(self.main_adventurers[0] + ' and ' + self.main_adventurers[1] +
                                      ' successfully flank the archer! Easy games easy life. Both gain 2 exp and ' +
                                      '200 gold.')
                self.bot.player_manager.add_exp(self.main_adventurers[0], 2)
                self.bot.player_manager.add_gold(self.main_adventurers[0], 200)
                self.bot.player_manager.add_exp(self.main_adventurers[1], 2)
                self.bot.player_manager.add_gold(self.main_adventurers[1], 200)
            else:
                self.channel.send_msg(self.main_adventurers[0] + ' and ' + self.main_adventurers[1] +
                                      ' apparently suck at coordination and ended up going the same direction. ' +
                                      'At least you got the archer an achievement for a double kill with a single ' +
                                      'arrow! Both of you lose 200 gold.')
                self.bot.player_manager.add_gold(self.main_adventurers[0], -200)
                self.bot.player_manager.add_gold(self.main_adventurers[1], -200)
        elif len(self.adventurer_actions) == 1:
            user = list(self.adventurer_actions.keys())[0]
            other = self.main_adventurers[0]
            if user == other:
                other = self.main_adventurers[1]
            self.channel.send_msg(other + " didn't move and just used " + user + ' as a decoy to distract the archer ' +
                                  'while making off with the loot! What a meanie. ' + other +
                                  ' gains 2 exp, 250 gold, ' + user + ' loses 100 gold.')
            self.bot.player_manager.add_exp(other, 2)
            self.bot.player_manager.add_gold(other, 250)
            self.bot.player_manager.add_gold(user, -100)
        else:
            self.channel.send_msg('Neither ' + self.main_adventurers[0] + ' nor ' + self.main_adventurers[1] +
                                  ' want to make a move, and eventually both get picked off like sitting ducks. ' +
                                  ' Dumpstered. Both lose 150 gold.')
            self.bot.player_manager.add_gold(self.main_adventurers[0], -75)
            self.bot.player_manager.add_gold(self.main_adventurers[1], -75)

        self.quest_cooldown()

    # ==================================================================================================================
    # ==================================================================================================================

    def quest_escape(self):
        self.separate_main_adventurers(len(self.adventurers))

        # Randomize the duel word so you can't macro it
        escape_words = ['!run', '!flee', '!hide', '!escape']
        escape_word = random.choice(escape_words)

        self.channel.send_msg(self.list_out_items(self.main_adventurers) + ' are all running from an ' +
                              "enraged Vilemaw! Quickly, type " + escape_word + " to get away!")
        self.commands = {
            escape_word: self.quest_escape_result
        }
        self.end_quest = self.quest_escape_timeout

    def quest_escape_result(self, user, msg):
        if user in self.main_adventurers:
            self.adventurer_actions[user] = True

            if len(self.adventurer_actions) >= len(self.main_adventurers) - 1:
                self.quest_escape_timeout()

    def quest_escape_timeout(self):
        escaped = list(self.adventurer_actions.keys())
        temp_set = set(escaped)
        left_behind = [x for x in self.main_adventurers if x not in temp_set]

        self.channel.send_msg('In the end, ' + self.list_out_items(escaped) + ' managed to escape from Vilemaw ' +
                              'unscathed! Vilemaw munches happily on ' + self.list_out_items(left_behind) +
                              ' with terrifying crunches, snaps, and some odd purring noises. Those that escaped ' +
                              'gain 3 exp and 300 gold, and those left behind lose 100 gold.')
        for adventurer in escaped:
            self.bot.player_manager.add_exp(adventurer, 3)
            self.bot.player_manager.add_gold(adventurer, 300)
        for adventurer in left_behind:
            self.bot.player_manager.add_gold(adventurer, -100)

        self.quest_cooldown()

    # ==================================================================================================================

    def quest_gates(self):
        self.channel.send_msg(self.list_out_items(self.adventurers) + ' have been recruited to defend the gates ' +
                              'of a small town from Frostguard forces. You must split up to hold the gates by ' +
                              'defending the !north, !south, !west, and !east entrances!')
        self.commands = {
            '!north': self.quest_gates_result,
            '!south': self.quest_gates_result,
            '!west': self.quest_gates_result,
            '!east': self.quest_gates_result,
        }
        self.end_quest = self.quest_gates_timeout

    def quest_gates_result(self, user, msg):
        if user in self.adventurers and user not in list(self.adventurer_actions.keys()):
            self.adventurer_actions[user] = msg[1:].lower()
            if len(self.adventurer_actions) == len(self.adventurers):
                self.kill_timer()
                self.quest_gates_timeout()

    def quest_gates_timeout(self):
        action_list = []
        for user, action in self.adventurer_actions.items():
            if action not in action_list:
                action_list.append(action)
        if len(action_list) == 4:
            self.channel.send_msg(self.list_out_items(self.adventurers) + ' have successfully held the gates! '
                                  'Huzzah! 3 exp and 250 gold for all!')
            for user in self.adventurers:
                self.bot.player_manager.add_exp(user, 3)
                self.bot.player_manager.add_gold(user, 250)
        elif len(action_list) == 0:
            self.channel.send_msg(self.list_out_items(self.adventurers) + ' have secretly managed to collaborate ' +
                                  'with the Frostguard raiders letting them all in without opposition. ' +
                                  'For your devious work, everyone is rewarded with 5 exp and 400 gold!')
            for user in self.adventurers:
                self.bot.player_manager.add_exp(user, 5)
                self.bot.player_manager.add_gold(user, 400)
        else:
            gate_conjugated = 'gates'
            if len(action_list) == 1:
                gate_conjugated = 'gate'
            self.channel.send_msg(self.list_out_items(self.adventurers) + ' only managed to defend the ' +
                                  self.list_out_items(action_list) + ' ' + gate_conjugated +
                                  '. Pretty pitiful. The Frostguard storm ' +
                                  'the city and murdalize all the people. Everyone loses 80 gold.')
            for user in self.adventurers:
                self.bot.player_manager.add_gold(user, -80)

        self.quest_cooldown()

    # ==================================================================================================================
    # ==================================================================================================================

    def quest_prison(self):
        self.separate_main_adventurers(1)
        self.channel.send_msg('In the Castle of the Mad Yordle, ' + self.main_adventurers[0] +
                              " stumbles across a prison. But the castle is collapsing and there's only time to " +
                              "save one! Do you save " + self.list_out_items(self.other_adventurers, 'or', '!') + '?')
        for adventurer in self.other_adventurers:
            adventurer_command = '!' + adventurer
            self.commands[adventurer_command] = self.quest_prison_result
        self.end_quest = self.quest_prison_timeout

    def quest_prison_result(self, user, msg):
        if user in self.main_adventurers:
            self.kill_timer()
            saved_adventurer = msg[1:].lower()
            forsaken_adventurers = [x for x in self.other_adventurers if x != saved_adventurer]
            self.channel.send_msg(user + ' decided to save ' + saved_adventurer + '! ' +
                                  self.list_out_items(forsaken_adventurers) + ' are left '
                                  'behind and crushed under the rubble of the collapsing castle, losing 50 gold. ' +
                                  user + ' and ' + saved_adventurer + ' gain 4 exp and 350 gold!')
            self.bot.player_manager.add_exp(self.main_adventurers[0], 4)
            self.bot.player_manager.add_gold(self.main_adventurers[0], 350)
            self.bot.player_manager.add_exp(saved_adventurer, 4)
            self.bot.player_manager.add_gold(saved_adventurer, 350)
            for forsaken_adventurer in forsaken_adventurers:
                self.bot.player_manager.add_gold(forsaken_adventurer, -50)

            self.quest_cooldown()

    def quest_prison_timeout(self):
        self.channel.send_msg(self.main_adventurers[0] + ' took too long deciding who to save, and everyone ended ' +
                              'up crushed by the collapsing castle. ' + self.main_adventurers[0] + ', ' +
                              self.list_out_items(self.other_adventurers) + ' all lose 75 gold. Ouch.')
        self.bot.player_manager.add_gold(self.main_adventurers[0], -75)
        for adventurer in self.other_adventurers:
            self.bot.player_manager.add_gold(adventurer, -75)

        self.quest_cooldown()