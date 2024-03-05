from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


@dataclass(eq=True, unsafe_hash=True, order=True)
class Vector:
    direction: Direction
    x: int
    y: int


@dataclass(frozen=True)
class Point:
    x: int
    y: int


class Direction(str, Enum):
    NORTH = 'NORTH'
    EAST = 'EAST'
    SOUTH = 'SOUTH'
    WEST = 'WEST'
