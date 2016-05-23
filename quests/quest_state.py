import enum

@enum.unique
class QuestState(enum.Enum):
    disabled = 0
    on_cooldown = 1
    ready = 2
    forming_party = 3
    active = 4