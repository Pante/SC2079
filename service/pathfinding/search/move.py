from pathfinding.world.primitives import Vector, Direction
from pathfinding.search.instructions import Move


def move(vector: Vector, instruction: Move, cells: int) -> list[Vector]:
    vectors = list()
    for i in range(0, cells + 1):
        match (vector.direction, instruction):
            case (Direction.NORTH, Move.FORWARD):
                vectors.append(Vector(vector.direction, vector.x, vector.y + i))
            case (Direction.NORTH, Move.BACKWARD):
                vectors.append(Vector(vector.direction, vector.x, vector.y - i))

            case (Direction.SOUTH, Move.FORWARD):
                vectors.append(Vector(vector.direction, vector.x, vector.y - i))
            case (Direction.SOUTH, Move.BACKWARD):
                vectors.append(Vector(vector.direction, vector.x, vector.y + i))

            case (Direction.EAST, Move.FORWARD):
                vectors.append(Vector(vector.direction, vector.x + i, vector.y))
            case (Direction.EAST, Move.BACKWARD):
                vectors.append(Vector(vector.direction, vector.x - i, vector.y))

            case (Direction.WEST, Move.FORWARD):
                vectors.append(Vector(vector.direction, vector.x - i, vector.y))
            case (Direction.WEST, Move.BACKWARD):
                vectors.append(Vector(vector.direction, vector.x + i, vector.y))

    return vectors
