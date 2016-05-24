from .doors import Doors
from .monster import Monster
from .duel import Duel


# The index corresponds to the number of players a quest can take
QUEST_LIST = [
    [],
    [Doors, Monster],
    [Duel]
]
