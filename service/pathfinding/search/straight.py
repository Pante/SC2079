from pathfinding.world.primitives import Vector, Direction


def straight(start: Vector, modifier: int, length: int) -> list[Vector]:
    match start.direction:
        case Direction.NORTH:
            return [Vector(start.direction, start.x, start.y + i * modifier) for i in range(1, length + 1)]

        case Direction.SOUTH:
            return [Vector(start.direction, start.x, start.y - i * modifier) for i in range(1, length + 1)]

        case Direction.EAST:
            return [Vector(start.direction, start.x + i * modifier, start.y) for i in range(1, length + 1)]

        case Direction.WEST:
            return [Vector(start.direction, start.x - i * modifier, start.y) for i in range(1, length + 1)]
