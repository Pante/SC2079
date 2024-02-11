from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Set

from pathfinding.world.primitives import Point


class MiscInstruction(Enum):
    CAPTURE_IMAGE = 1
    RESET_GYROSCOPE = 2


@dataclass(frozen=True)
class MoveInstruction:
    move: Move
    amount: int


class Move(Enum):
    FORWARD = 1
    BACKWARD = 2


@dataclass(frozen=True)
class TurnInstruction:
    turn: turn
    points: Set[Point]


class Turn(Enum):
    FORWARD_LEFT = 1
    FORWARD_RIGHT = 2
    BACKWARD_LEFT = 3
    BACKWARD_RIGHT = 4
