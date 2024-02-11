from pathfinding.world.primitives import Vector, Direction
from pathfinding.instructions.instructions import Move


def move(vector: Vector, instruction: Move) -> Vector:
    match (vector.direction, instruction):
        case (Direction.NORTH, Move.FORWARD):
            return Vector(vector.direction, vector.x, vector.y + 1)
        case (Direction.NORTH, Move.BACKWARD):
            return Vector(vector.direction, vector.x, vector.y - 1)

        case (Direction.SOUTH, Move.FORWARD):
            return Vector(vector.direction, vector.x, vector.y - 1)
        case (Direction.SOUTH, Move.BACKWARD):
            return Vector(vector.direction, vector.x, vector.y + 1)

        case (Direction.EAST, Move.FORWARD):
            return Vector(vector.direction, vector.x + 1, vector.y)
        case (Direction.EAST, Move.BACKWARD):
            return Vector(vector.direction, vector.x - 1, vector.y)

        case (Direction.WEST, Move.FORWARD):
            return Vector(vector.direction, vector.x - 1, vector.y)
        case (Direction.WEST, Move.BACKWARD):
            return Vector(vector.direction, vector.x + 1, vector.y)
