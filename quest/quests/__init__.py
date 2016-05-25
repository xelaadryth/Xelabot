from .doors import Doors
from .monster import Monster
from .duel import Duel
from .archer import Archer
from .run import Run
from .gates import Gates
from .prison import Prison


# The index corresponds to the number of players a quest can take
QUEST_LIST = [
    [],
    [Doors, Monster],
    [Duel, Archer],
    [Run],
    [Run, Prison],
    [Run, Prison, Gates],
    [Run, Prison, Gates]
]
