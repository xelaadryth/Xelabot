import random

from utils.command_set import CommandSet


class Quest:
    def __init__(self, quest_manager):
        self.quest_manager = quest_manager

        self.party = quest_manager.party
        self.commands = CommandSet()

        self.started = False

        # Quest segment ordering
        self.starting_segment = None
        self.current_segment = None
        self.next_segment = None

    def advance(self):
        self.commands.clear_children()

        # Create the next segment of the quest as needed
        if not self.started:
            self.started = True
            # noinspection PyCallingNonCallable
            self.current_segment = self.starting_segment(self)
            self.current_segment.play()
        elif self.next_segment:
            # noinspection PyCallingNonCallable
            self.current_segment = self.next_segment(self)
            self.next_segment = None
            self.current_segment.play()
        else:
            self.quest_manager.quest_cooldown()

    @staticmethod
    def separate_party(party, num_main_adventurers):
        main_adventurers = [party[0]]

        main_adventurers += random.sample(party[1:], num_main_adventurers-1)

        temp_set = set(party)
        other_adventurers = [x for x in party if x not in temp_set]

        return main_adventurers, other_adventurers

    @staticmethod
    def list_out_items(some_list, join_word='and', prefix=''):
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
    def quest_duel(self):
        main_adventurers, other_adventurers = Quest.separate_party(self.party, 2)

        # Randomize the duel word so you can't macro it
        duel_words = ['!attack', '!fight', '!strike', '!slay']
        duel_word = random.choice(duel_words)

        self.channel.send_msg(main_adventurers[0] + ' and ' + main_adventurers[1] +
                              ' end up in a duel over some loot! The first to type ' + duel_word + ' is the victor!')
        self.commands = {
            duel_word: self.quest_duel_result
        }
        self.end_quest = self.quest_duel_timeout

    def quest_duel_result(self, user, msg):
        if user in main_adventurers:
            opponent = main_adventurers[0]
            if user == opponent:
                opponent = main_adventurers[1]
            self.kill_timer()
            self.channel.send_msg(user + " was quicker on the draw! There's nothing left of " + opponent +
                                  " except a smoking pile of flesh. " + user + " gains 3 exp and steals 300 gold!")
            self.bot.player_manager.add_exp(user, 3)
            self.bot.player_manager.add_gold(user, 300)
            self.bot.player_manager.add_gold(opponent, -300)

            self.quest_cooldown()

    def quest_duel_timeout(self):
        self.channel.send_msg(main_adventurers[0] + ' and ' + main_adventurers[1] +
                              ' are apparently pacifists and neither make a move. Both gain 2 exp!')
        self.bot.player_manager.add_exp(main_adventurers[0], 2)
        self.bot.player_manager.add_exp(main_adventurers[1], 2)

        self.quest_cooldown()

    # ==================================================================================================================

    def quest_archer(self):
        main_adventurers, other_adventurers = Quest.separate_party(self.party, 2)
        self.channel.send_msg(main_adventurers[0] + ' and ' + main_adventurers[1] +
                              ' are pinned down by a Noxian archer! One of you go !left and one of you go ' +
                              '!right to flank and defeat him!')
        self.commands = {
            '!left': self.quest_archer_result,
            '!right': self.quest_archer_result
        }
        self.end_quest = self.quest_archer_timeout

    def quest_archer_result(self, user, msg):
        if user in main_adventurers and user not in list(self.adventurer_actions.keys()):
            self.adventurer_actions[user] = msg[1:].lower()
            if len(self.adventurer_actions) == 2:
                self.kill_timer()
                self.quest_archer_timeout()

    def quest_archer_timeout(self):
        if len(self.adventurer_actions) == 2:
            if self.adventurer_actions[main_adventurers[0]] != self.adventurer_actions[main_adventurers[1]]:
                self.channel.send_msg(main_adventurers[0] + ' and ' + main_adventurers[1] +
                                      ' successfully flank the archer! Easy games easy life. Both gain 2 exp and ' +
                                      '200 gold.')
                self.bot.player_manager.add_exp(main_adventurers[0], 2)
                self.bot.player_manager.add_gold(main_adventurers[0], 200)
                self.bot.player_manager.add_exp(main_adventurers[1], 2)
                self.bot.player_manager.add_gold(main_adventurers[1], 200)
            else:
                self.channel.send_msg(main_adventurers[0] + ' and ' + main_adventurers[1] +
                                      ' apparently suck at coordination and ended up going the same direction. ' +
                                      'At least you got the archer an achievement for a double kill with a single ' +
                                      'arrow! Both of you lose 200 gold.')
                self.bot.player_manager.add_gold(main_adventurers[0], -200)
                self.bot.player_manager.add_gold(main_adventurers[1], -200)
        elif len(self.adventurer_actions) == 1:
            user = list(self.adventurer_actions.keys())[0]
            other = main_adventurers[0]
            if user == other:
                other = main_adventurers[1]
            self.channel.send_msg(other + " didn't move and just used " + user + ' as a decoy to distract the archer ' +
                                  'while making off with the loot! What a meanie. ' + other +
                                  ' gains 2 exp, 250 gold, ' + user + ' loses 100 gold.')
            self.bot.player_manager.add_exp(other, 2)
            self.bot.player_manager.add_gold(other, 250)
            self.bot.player_manager.add_gold(user, -100)
        else:
            self.channel.send_msg('Neither ' + main_adventurers[0] + ' nor ' + main_adventurers[1] +
                                  ' want to make a move, and eventually both get picked off like sitting ducks. ' +
                                  ' Dumpstered. Both lose 150 gold.')
            self.bot.player_manager.add_gold(main_adventurers[0], -75)
            self.bot.player_manager.add_gold(main_adventurers[1], -75)

        self.quest_cooldown()

    # ==================================================================================================================
    # ==================================================================================================================

    def quest_escape(self):
        main_adventurers, other_adventurers = Quest.separate_party(self.party, len(self.adventurers))

        # Randomize the duel word so you can't macro it
        escape_words = ['!run', '!flee', '!hide', '!escape']
        escape_word = random.choice(escape_words)

        self.channel.send_msg(self.list_out_items(main_adventurers) + ' are all running from an ' +
                              "enraged Vilemaw! Quickly, type " + escape_word + " to get away!")
        self.commands = {
            escape_word: self.quest_escape_result
        }
        self.end_quest = self.quest_escape_timeout

    def quest_escape_result(self, user, msg):
        if user in main_adventurers:
            self.adventurer_actions[user] = True

            if len(self.adventurer_actions) >= len(main_adventurers) - 1:
                self.quest_escape_timeout()

    def quest_escape_timeout(self):
        escaped = list(self.adventurer_actions.keys())
        temp_set = set(escaped)
        left_behind = [x for x in main_adventurers if x not in temp_set]

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
        main_adventurers, other_adventurers = Quest.separate_party(self.party, 1)
        self.channel.send_msg('In the Castle of the Mad Yordle, ' + main_adventurers[0] +
                              " stumbles across a prison. But the castle is collapsing and there's only time to " +
                              "save one! Do you save " + self.list_out_items(other_adventurers, 'or', '!') + '?')
        for adventurer in other_adventurers:
            adventurer_command = '!' + adventurer
            self.commands[adventurer_command] = self.quest_prison_result
        self.end_quest = self.quest_prison_timeout

    def quest_prison_result(self, user, msg):
        if user in main_adventurers:
            self.kill_timer()
            saved_adventurer = msg[1:].lower()
            forsaken_adventurers = [x for x in other_adventurers if x != saved_adventurer]
            self.channel.send_msg(user + ' decided to save ' + saved_adventurer + '! ' +
                                  self.list_out_items(forsaken_adventurers) + ' are left '
                                  'behind and crushed under the rubble of the collapsing castle, losing 50 gold. ' +
                                  user + ' and ' + saved_adventurer + ' gain 4 exp and 350 gold!')
            self.bot.player_manager.add_exp(main_adventurers[0], 4)
            self.bot.player_manager.add_gold(main_adventurers[0], 350)
            self.bot.player_manager.add_exp(saved_adventurer, 4)
            self.bot.player_manager.add_gold(saved_adventurer, 350)
            for forsaken_adventurer in forsaken_adventurers:
                self.bot.player_manager.add_gold(forsaken_adventurer, -50)

            self.quest_cooldown()

    def quest_prison_timeout(self):
        self.channel.send_msg(main_adventurers[0] + ' took too long deciding who to save, and everyone ended ' +
                              'up crushed by the collapsing castle. ' + main_adventurers[0] + ', ' +
                              self.list_out_items(other_adventurers) + ' all lose 75 gold. Ouch.')
        self.bot.player_manager.add_gold(main_adventurers[0], -75)
        for adventurer in other_adventurers:
            self.bot.player_manager.add_gold(adventurer, -75)

        self.quest_cooldown()
