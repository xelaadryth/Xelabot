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
