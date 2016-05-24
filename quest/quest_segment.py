import settings
from utils.command_set import CommandSet


class QuestSegment:
    def __init__(self, quest):
        self.quest = quest
        self.quest_manager = self.quest.quest_manager
        self.channel = self.quest_manager.channel
        self.channel_manager = self.channel.channel_manager
        self.bot = self.channel_manager.bot
        self.player_manager = self.bot.player_manager

        self.commands = None

        self.set_commands()
        self.update_commands()

    def set_commands(self):
        """
        Sets the commands available to players when they reach this quest segment. By default, nothing. Override this!
        """
        self.commands = CommandSet()

    def update_commands(self):
        """
        Adds our command set as a child of the quest's command set.
        """
        self.quest.commands.add_command_set(self.commands)

    def play(self):
        """
        Performs the actions when players reach this quest segment. Override this!
        """
        raise NotImplementedError('Quest segment not implemented!')

    def timeout_advance(self, timeout_segment, duration=settings.QUEST_DURATION):
        """
        Sets the timer until the quest auto-advances.
        :param timeout_segment: Function<Quest, QuestSegment> - The segment to instantiate if we time out
        :param duration: float - Seconds until we time out
        """
        self.quest.next_segment = timeout_segment

        self.quest_manager.start_quest_advance_timer(duration)

    def advance(self, next_segment):
        """
        Advances the quest to the specified segment immediately.
        :param next_segment: Function<Quest, QuestSegment> - The next segment to execute immediately
        """
        self.quest.next_segment = next_segment
        self.quest.advance()

    def complete_quest(self):
        """
        End the quest.
        """
        self.advance(None)
