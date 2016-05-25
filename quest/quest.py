import settings
from utils.command_set import CommandSet


class Quest:
    def __init__(self, quest_manager):
        self.quest_manager = quest_manager

        self.party = quest_manager.party
        self.commands = CommandSet()

        # Quest segment ordering
        self.starting_segment = None
        self.current_segment = None

    def advance(self, next_segment=None):
        self.commands.clear_children()

        # Create the next segment of the quest as needed
        if next_segment:
            self.current_segment = next_segment(self)
            self.quest_manager.start_quest_advance_timer(settings.QUEST_DURATION)
            self.current_segment.play()
        else:
            self.current_segment.timeout()

    # ==================================================================================================================
    # ==================================================================================================================
    # ============================================== QUESTS BELOW ======================================================
    # ==================================================================================================================
    # ==================================================================================================================
    #
    # def quest_prison(self):
    #     main_adventurers, other_adventurers = Quest.separate_party(self.party, 1)
    #     self.channel.send_msg('In the Castle of the Mad Yordle, ' + main_adventurers[0] +
    #                           " stumbles across a prison. But the castle is collapsing and there's only time to " +
    #                           "save one! Do you save " + self.list_out_items(other_adventurers, 'or', '!') + '?')
    #     for adventurer in other_adventurers:
    #         adventurer_command = '!' + adventurer
    #         self.commands[adventurer_command] = self.quest_prison_result
    #     self.end_quest = self.quest_prison_timeout
    #
    # def quest_prison_result(self, user, msg):
    #     if user in main_adventurers:
    #         self.kill_timer()
    #         saved_adventurer = msg[1:].lower()
    #         forsaken_adventurers = [x for x in other_adventurers if x != saved_adventurer]
    #         self.channel.send_msg(user + ' decided to save ' + saved_adventurer + '! ' +
    #                               self.list_out_items(forsaken_adventurers) + ' are left '
    #                               'behind and crushed under the rubble of the collapsing castle, losing 50 gold. ' +
    #                               user + ' and ' + saved_adventurer + ' gain 4 exp and 350 gold!')
    #         self.bot.player_manager.add_exp(main_adventurers[0], 4)
    #         self.bot.player_manager.add_gold(main_adventurers[0], 350)
    #         self.bot.player_manager.add_exp(saved_adventurer, 4)
    #         self.bot.player_manager.add_gold(saved_adventurer, 350)
    #         for forsaken_adventurer in forsaken_adventurers:
    #             self.bot.player_manager.add_gold(forsaken_adventurer, -50)
    #
    #         self.quest_cooldown()
    #
    # def quest_prison_timeout(self):
    #     self.channel.send_msg(main_adventurers[0] + ' took too long deciding who to save, and everyone ended ' +
    #                           'up crushed by the collapsing castle. ' + main_adventurers[0] + ', ' +
    #                           self.list_out_items(other_adventurers) + ' all lose 75 gold. Ouch.')
    #     self.bot.player_manager.add_gold(main_adventurers[0], -75)
    #     for adventurer in other_adventurers:
    #         self.bot.player_manager.add_gold(adventurer, -75)
    #
    #     self.quest_cooldown()
