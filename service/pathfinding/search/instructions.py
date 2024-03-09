from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field

from pathfinding.world.primitives import Vector


class MiscInstruction(str, Enum):
    CAPTURE_IMAGE = 'CAPTURE_IMAGE'


class MoveInstruction(BaseModel):
    move: Straight
    amount: int = Field(
        ge=1, description="The amount to move the robot in centimetres."
    )


@dataclass
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


@dataclass
class Turn:
    turn: TurnInstruction
    vectors: list[Vector]
