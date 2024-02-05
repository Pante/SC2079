from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from itertools import pairwise, islice, groupby
from typing import List, Tuple, Generator, TypeVar

from pathfinding.world.world import Point, Robot, Direction

"""
The turning radius (in grid cells). The turning radius is assumed to be 25cm / (5cm per cell).
"""
TURNING_RADIUS = 5


def parse(robot: Robot, segment: List[Point]) -> List[MiscInstruction | TurnInstruction | MoveInstruction]:
    uncompressed = __parse(robot, segment)
    __verify(uncompressed)
    __remove_moves_surrounding_turns(uncompressed)
    return __compress(uncompressed)


def __parse(robot: Robot, segment: List[Point]) -> List[TurnInstruction | Move]:
    """
    Parses the points in the segment into an uncompressed list of moves. It does not append any additional instructions
    required to capture images. In addition, TURNING_RADIUS number of moves need to be removed before and after a turnn.

    :param robot: the robot
    :param segment: A path between several objectives is broken down into multiple segments. Each segment starts with the
        robot's current point and ends with an objective's point.
    :return: an uncompressed list of moves that the robot should perform to reach the objective
    """
    instructions = []
    for a, b, c in __window(segment):
        #  [c] [ ] [ ]   [b] [c] [ ]   [a] [b] [c]
        #  [b]           [a]           [ ]
        #  [a]           [ ]           [ ]
        #
        first_direction = a.direction(to=b)
        assert robot.direction.same_axis(first_direction)

        move = Move.FORWARD if robot.direction == first_direction else Move.BACKWARD
        if c is not None:
            robot.direction = b.direction(to=c)
            move = __move(move, first_direction, robot.direction)

        instructions.append(move)

    return instructions


def __window(points: List[Point]) -> Generator[Tuple[Point, Point, Point | None], None, None]:
    """
    Creates a window over the points. Emits a partial window only if there are 2 points left. No partial window is
    emitted is only 1 point is left.

    :param points: The points.
    :return: A sliding window over the points.
    """
    iterator = iter(points)
    result = tuple(islice(iterator, 3))
    if len(result) >= 2:
        yield result

    for element in iterator:
        result = result[1:] + (element,)
        yield result


def __move(move: Move, first_direction: Direction, second_direction: Direction) -> TurnInstruction | Move:
    match (move, first_direction):
        case (_, first_direction) if first_direction == second_direction:
            return move

        case (Move.FORWARD, first_direction) if (first_direction.value + 1) % 4 == second_direction:
            return TurnInstruction.FORWARD_RIGHT

        case (Move.FORWARD, _):
            return TurnInstruction.FORWARD_LEFT

        case (Move.BACKWARD, first_direction) if (first_direction.value + 1) % 4 == second_direction:
            return TurnInstruction.BACKWARD_LEFT

        case (Move.BACKWARD, _):
            return TurnInstruction.BACKWARD_RIGHT


def __verify(instructions: List[TurnInstruction | Move]):
    turn_indices = [i for i, instruction in enumerate(instructions) if isinstance(instruction, TurnInstruction)]
    for a, b in pairwise(turn_indices):
        if (b - a) < (TURNING_RADIUS * 2):
            raise ValueError(f"Another TurnInstruction found within TURNING_RADIUS at index: {b}")


def __remove_moves_surrounding_turns(instructions: List[TurnInstruction | Move]) -> None:
    """
    Removes the moves surrounding a turn to ensure that it adheres to the turning radius. It assumes that there are no
    other turn instructions in the moves surrounding another turn instruction.

    :param instructions: The instructions.
    """
    i = len(instructions) - 1
    while i >= 0:
        if isinstance(instructions[i], TurnInstruction):
            end = min(len(instructions), i + TURNING_RADIUS + 1)
            del instructions[i + 1:end]

            start = max(0, i - (TURNING_RADIUS - 1))
            del instructions[start:i]
            i = start

        else:
            i -= 1


def __compress(instructions: List[TurnInstruction | Move]) -> List[MiscInstruction | TurnInstruction | MoveInstruction]:
    compressed = []
    for instruction, group in groupby(instructions):
        if isinstance(instruction, (MiscInstruction, TurnInstruction)):
            compressed.append(instruction)

        else:
            compressed.append(MoveInstruction(instruction, len(list(group))))

    compressed.append(MiscInstruction.CAPTURE_IMAGE)

    return compressed


class MiscInstruction(Enum):
    CAPTURE_IMAGE = 1
    RESET_GYROSCOPE = 2


class TurnInstruction(Enum):
    FORWARD_LEFT = 1
    FORWARD_RIGHT = 2
    BACKWARD_LEFT = 3
    BACKWARD_RIGHT = 4


@dataclass
class MoveInstruction:
    """
    Attributes:
        :param move The amount to move the robot by in centimeters.
    """
    move: Move
    amount: int


class Move(Enum):
    FORWARD = 1
    BACKWARD = 2
