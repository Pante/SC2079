from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from pathfinding.world.primitives import Vector


class MiscInstruction(str, Enum):
    CAPTURE_IMAGE = 'CAPTURE_IMAGE'


@dataclass
class MoveInstruction:
    move: Straight
    amount: int

    def __post_init__(self):
        assert 0 <= self.amount


@dataclass(frozen=True)
class Move:
    move: Straight
    vectors: list[Vector]


class Straight(str, Enum):
    FORWARD = 'FORWARD'
    BACKWARD = 'BACKWARD'


class TurnInstruction(str, Enum):
    FORWARD_LEFT = 'FORWARD_LEFT'
    FORWARD_RIGHT = 'FORWARD_RIGHT'
    BACKWARD_LEFT = 'BACKWARD_LEFT'
    BACKWARD_RIGHT = 'BACKWARD_RIGHT'


@dataclass(frozen=True)
class Turn:
    turn: TurnInstruction
    vectors: list[Vector]
