from __future__ import annotations

from enum import Enum

from pathfinding.world.primitives import Direction


class MiscInstruction(Enum):
    CAPTURE_IMAGE = 1
    RESET_GYROSCOPE = 2


class TurnInstruction(Enum):
    FORWARD_LEFT = 1
    FORWARD_RIGHT = 2
    BACKWARD_LEFT = 3
    BACKWARD_RIGHT = 4
