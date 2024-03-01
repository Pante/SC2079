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

    def same_axis(self, direction: Direction) -> bool:
        """
        Determines if both directions are on the same axis, i.e. NORTH and SOUTH, EAST and WEST, or NORTH and NORTH.

        :param direction: The other direction.
        :return: True if both directions are on the same axis.
        """
        return self == direction or self == direction.opposite

    @property
    def opposite(self) -> Direction:
        match self:
            case Direction.NORTH:
                return Direction.SOUTH
            case Direction.EAST:
                return Direction.WEST
            case Direction.WEST:
                return Direction.EAST
            case Direction.SOUTH:
                return Direction.NORTH
