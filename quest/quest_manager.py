import random

from .quest_state import QuestState
from .quests import QUEST_LIST
import settings
from utils.command_set import CommandSet
from utils.timing import Timer


class QuestManager:
    """
    Manages the quest currently running in a given channel.
    """
    def __init__(self, channel):
        self.channel = channel
        self.channel_settings = self.channel.channel_manager.channel_settings[self.channel.owner]

        self.quest = None
        self.party = []
        self.quest_timer = None
        self.quest_state = QuestState.ready
        self.commands = CommandSet()

        # Channel is guaranteed to be initialized at this point
        if self.channel_settings['quest_enabled']:
            self.enable_questing()
        else:
            self.disable_questing()

    def start_quest_advance_timer(self, duration=settings.QUEST_DURATION):
        """
        Starts a timer until the quest advances.
        :param duration: int - Number of seconds until the current quest advances.
        """
        self.kill_quest_advance_timer()
        self.quest_timer = Timer(duration, self.quest_advance)

    def kill_quest_advance_timer(self):
        """
        Stops the quest advancement timer and clears it from the update loop and from this manager.
        """
        if self.quest_timer:
            # Removes the timer from the update loop
            self.quest_timer.cancel()
            self.quest_timer = None

    def enable_questing(self):
        """
        Enables quest party formation.
        """
        self.kill_quest_advance_timer()
        self.quest_state = QuestState.ready
        self.commands = CommandSet(exact_match_commands={
            '!quest': self.create_party})

    def disable_questing(self):
        """
        Disables quest mode. Any currently running quest is canceled. Don't have to clear out instance variables
        since they will be overwritten by the next quest that is started.
        """
        self.kill_quest_advance_timer()

        self.quest_state = QuestState.disabled
        self.commands = CommandSet(exact_match_commands={
            '!quest': self.disabled_message})

    def quest_cooldown(self):
        """
        Puts quest mode on cooldown.
        """
        self.quest_state = QuestState.on_cooldown
        self.commands = CommandSet(exact_match_commands={
            '!quest': self.recharging_message})
        self.start_quest_advance_timer(self.channel_settings['quest_cooldown'])

    def quest_advance(self):
        """
        Advances the current quest.
        """
        if self.quest_state is QuestState.on_cooldown:
            self.enable_questing()
        elif self.quest_state is QuestState.forming_party:
            self.start_quest(random.choice(QUEST_LIST[len(self.party)])(self))
        elif self.quest_state is QuestState.active:
            self.quest.advance()

    def start_quest(self, quest):
        """
        Starts a random quest depending on the number of party members.
        :param quest: Quest - The quest that we are preparing
        """
        self.quest_state = QuestState.active
        self.quest = quest
        self.commands = CommandSet(children={self.quest.commands})
        self.quest.advance(self.quest.starting_segment)

    def disabled_message(self, display_name):
        """
        Tells users that !quest is currently disabled.
        :param display_name: str - The user that requested quest mode.
        """
        self.channel.send_msg(
            'Sorry {}, questing is currently disabled. Ask a mod to type !queston to re-enable questing.'.format(
                display_name))

    def recharging_message(self, display_name):
        """
        Tells users that !quest is currently on cooldown.
        :param display_name: str - The user that requested quest mode.
        """
        self.channel.send_msg('Sorry {}, quest take {} seconds to recharge. ({} seconds remaining.)'.format(
            display_name, self.channel_settings['quest_cooldown'], self.quest_timer.remaining()))

    def create_party(self, display_name):
        """
        Creates a party with the given player as the leader.
        :param display_name: str - The user that started the quest.
        """
        self.quest_state = QuestState.forming_party
        self.party = [display_name]
        self.commands = CommandSet(exact_match_commands={
            '!quest': self.join_quest})

        self.channel.send_msg(display_name + ' wants to attempt a quest. Type "!quest" to join!')

        self.start_quest_advance_timer(settings.QUEST_DURATION)

    def join_quest(self, display_name):
        """
        Joins the existing quest party.
        :param display_name: str - The user trying to join the quest party.
        """
        if display_name not in self.party:
            self.party.append(display_name)
            # The index of the quest list is the max number of players, so if we've reached it then start the quest
            if len(self.party) >= len(QUEST_LIST) - 1:
                self.quest_advance()
