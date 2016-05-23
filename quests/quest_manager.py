import random

from .quest_state import QuestState
import settings
from utils.commands import Commands
from utils.timer_thread import TimerThread


class QuestManager:
    """
    Manages the quest currently running in a given channel.
    """
    def __init__(self, channel):
        self.channel = channel

        # If we are in a given state and need to advance, call the function specified
        self.next_quest_event = {
            QuestState.on_cooldown: self.enable_questing,
            QuestState.forming_party: self.start_quest,
            QuestState.active: self.quest.advance
        }

        self.quest = None
        self.party = []
        self.quest_timer = None
        self.quest_state = QuestState.ready
        self.commands = None
        self.enable_questing()

        # The index corresponds to the number of players a quest can take
        self.quest_lists = [
            # [],
            # [self.quest_chamber, self.quest_monster],
            # [self.quest_duel, self.quest_archer],
            # [self.quest_escape],
            # [self.quest_prison, self.quest_escape],
            # [self.quest_prison, self.quest_escape, self.quest_gates],
            # [self.quest_prison, self.quest_escape, self.quest_gates]
        ]

    def start_quest_advance_timer(self, duration):
        """
        Starts a timer until the quest advances.
        :param duration: int - Number of seconds until the current quest advances.
        """
        self.quest_timer = TimerThread(duration, self.quest_advance)

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
        self.quest_state = QuestState.ready
        self.commands = Commands(exact_match_commands={
            '!quest': lambda **kwargs: self.create_party(kwargs['display_name'])})

    def disable_questing(self):
        """
        Disables quest mode. Any currently running quest is canceled.
        """
        self.kill_quest_advance_timer()

        self.quest_state = QuestState.disabled
        self.commands = Commands(exact_match_commands={
            '!quest': lambda **kwargs: self.disabled_message(kwargs['display_name'])})

    def quest_cooldown(self):
        """
        Puts quest mode on cooldown.
        """
        self.quest_state = QuestState.on_cooldown
        self.commands = Commands(exact_match_commands={
            '!quest': lambda **kwargs: self.recharging_message(kwargs['display_name'])})
        self.start_quest_advance_timer(self.channel.channel_settings['quest_cooldown'])

    def quest_advance(self):
        """
        Advances the current quest.
        """
        self.kill_quest_advance_timer()

        quest_event = self.next_quest_event[self.quest_state]
        quest_event()

    def start_quest(self):
        """
        Starts a random quest depending on the number of party members.
        """
        self.quest_state = QuestState.active
        self.quest = random.choice(self.quest_lists[len(self.party)])(self)
        self.quest.advance()
        self.commands = self.quest.commands
        self.start_quest_advance_timer(settings.QUEST_DURATION)

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
        self.channel.send_msg('Sorry {}, quests take {} seconds to recharge. ({} seconds remaining.)'.format(
            display_name, self.channel.channel_settings['quest_cooldown'], self.quest_timer.remaining()))

    def create_party(self, display_name):
        """
        Creates a party with the given player as the leader.
        :param display_name: str - The user that started the quest.
        """
        self.quest_state = QuestState.forming_party
        self.party = [display_name]
        self.commands = Commands(exact_match_commands={
            '!quest': lambda **kwargs: self.join_quest(kwargs['display_name'])})

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
            if len(self.party) >= len(self.quest_lists) - 1:
                self.quest_advance()
