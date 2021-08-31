from enum import Enum

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    RIGHT = (1, 0)
    LEFT = (-1, 0)

DIRECTION_TO_KEY = {}
DIRECTION_TO_KEY[Direction.UP] = "up"
DIRECTION_TO_KEY[Direction.DOWN] = "down"
DIRECTION_TO_KEY[Direction.RIGHT] = "right"
DIRECTION_TO_KEY[Direction.LEFT] = "left"

def getKey(direction):
    return DIRECTION_TO_KEY[direction]


def translate(position, direction):
    return (position[0] + direction.value[0], position[1] + direction.value[1])


def getDirection(base_position, new_position):
    if base_position[0] < new_position[0]:
        return Direction.RIGHT
    if new_position[0] < base_position[0]:
        return Direction.LEFT
    if base_position[1] < new_position[1]:
        return Direction.DOWN
    if base_position[1] > new_position[1]:
        return Direction.UP
