from pathfinding.world.primitives import Vector, Direction
from pathfinding.search.instructions import Straight


def straight(vector: Vector, movement: Straight, cells: int) -> list[Vector]:
    vectors = list()
    for i in range(1, cells + 1):
        match (vector.direction, movement):
            case (Direction.NORTH, Straight.FORWARD):
                vectors.append(Vector(vector.direction, vector.x, vector.y + i))
            case (Direction.NORTH, Straight.BACKWARD):
                vectors.append(Vector(vector.direction, vector.x, vector.y - i))

            case (Direction.SOUTH, Straight.FORWARD):
                vectors.append(Vector(vector.direction, vector.x, vector.y - i))
            case (Direction.SOUTH, Straight.BACKWARD):
                vectors.append(Vector(vector.direction, vector.x, vector.y + i))

            case (Direction.EAST, Straight.FORWARD):
                vectors.append(Vector(vector.direction, vector.x + i, vector.y))
            case (Direction.EAST, Straight.BACKWARD):
                vectors.append(Vector(vector.direction, vector.x - i, vector.y))

            case (Direction.WEST, Straight.FORWARD):
                vectors.append(Vector(vector.direction, vector.x - i, vector.y))
            case (Direction.WEST, Straight.BACKWARD):
                vectors.append(Vector(vector.direction, vector.x + i, vector.y))

    return vectors
