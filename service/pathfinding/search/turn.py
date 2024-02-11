from pathfinding.search.instructions import TurnInstruction
from pathfinding.world.primitives import Direction, Point, Vector
from pathfinding.world.world import GRID_CELL_SIZE

# The turning radius (in grid cells). The turning radius is assumed to be 25cm.
TURNING_RADIUS = 25 // GRID_CELL_SIZE


def turn(vector: Vector, instruction: TurnInstruction) -> tuple[Vector, set[Point]]:
    centre_x, centre_y, result, quadrant = __turn(vector, instruction)
    points = __curve(centre_x, centre_y, quadrant)
    return result, points


def __turn(vector: Vector, instruction: TurnInstruction) -> tuple[int, int, Vector, int]:
    """
    Performs a turn.

    :param vector: The initial vector.
    :param instruction: The turn instruction.
    :return:
        The x & y coordinates of the centre of the turning radius,
        the vector after executing the turn
        the quadrant of the turn,
    """
    match (vector.direction, instruction):
        # Initially facing north
        case (Direction.NORTH, TurnInstruction.FORWARD_LEFT):
            return (
                vector.x - TURNING_RADIUS,
                vector.y,
                Vector(Direction.WEST, vector.x - TURNING_RADIUS, vector.y + TURNING_RADIUS),
                1,
            )

        case (Direction.NORTH, TurnInstruction.FORWARD_RIGHT):
            return (
                vector.x + TURNING_RADIUS,
                vector.y,
                Vector(Direction.EAST, vector.x + TURNING_RADIUS, vector.y + TURNING_RADIUS),
                2,
            )

        case (Direction.NORTH, TurnInstruction.BACKWARD_LEFT):
            return (
                vector.x - TURNING_RADIUS,
                vector.y,
                Vector(Direction.EAST, vector.x - TURNING_RADIUS, vector.y - TURNING_RADIUS),
                4,
            )

        case (Direction.NORTH, TurnInstruction.BACKWARD_RIGHT):
            return (
                vector.x + TURNING_RADIUS,
                vector.y,
                Vector(Direction.WEST, vector.x + TURNING_RADIUS, vector.y - TURNING_RADIUS),
                3,
            )

        # Initially facing east
        case (Direction.EAST, TurnInstruction.FORWARD_LEFT):
            return (
                vector.x,
                vector.y + TURNING_RADIUS,
                Vector(Direction.NORTH, vector.x + TURNING_RADIUS, vector.y + TURNING_RADIUS),
                4,
            )

        case (Direction.EAST, TurnInstruction.FORWARD_RIGHT):
            return (
                vector.x,
                vector.y - TURNING_RADIUS,
                Vector(Direction.SOUTH, vector.x + TURNING_RADIUS, vector.y - TURNING_RADIUS),
                1,
            )

        case (Direction.EAST, TurnInstruction.BACKWARD_LEFT):
            return (
                vector.x,
                vector.y + TURNING_RADIUS,
                Vector(Direction.SOUTH, vector.x - TURNING_RADIUS, vector.y + TURNING_RADIUS),
                3,
            )

        case (Direction.EAST, TurnInstruction.BACKWARD_RIGHT):
            return (
                vector.x,
                vector.y - TURNING_RADIUS,
                Vector(Direction.NORTH, vector.x - TURNING_RADIUS, vector.y - TURNING_RADIUS),
                2,
            )

        # Initially facing south
        case (Direction.SOUTH, TurnInstruction.FORWARD_LEFT):
            return (
                vector.x + TURNING_RADIUS,
                vector.y,
                Vector(Direction.EAST, vector.x + TURNING_RADIUS, vector.y - TURNING_RADIUS),
                3,
            )

        case (Direction.SOUTH, TurnInstruction.FORWARD_RIGHT):
            return (
                vector.x - TURNING_RADIUS,
                vector.y,
                Vector(Direction.WEST, vector.x - TURNING_RADIUS, vector.y - TURNING_RADIUS),
                4,
            )

        case (Direction.SOUTH, TurnInstruction.BACKWARD_LEFT):
            return (
                vector.x + TURNING_RADIUS,
                vector.y,
                Vector(Direction.WEST, vector.x + TURNING_RADIUS, vector.y + TURNING_RADIUS),
                2,
            )

        case (Direction.SOUTH, TurnInstruction.BACKWARD_RIGHT):
            return (
                vector.x - TURNING_RADIUS,
                vector.y,
                Vector(Direction.EAST, vector.x - TURNING_RADIUS, vector.y + TURNING_RADIUS),
                1,
            )

        # Initially facing west
        case (Direction.WEST, TurnInstruction.FORWARD_LEFT):
            return (
                vector.x,
                vector.y + TURNING_RADIUS,
                Vector(Direction.SOUTH, vector.x - TURNING_RADIUS, vector.y - TURNING_RADIUS),
                2,
            )

        case (Direction.WEST, TurnInstruction.FORWARD_RIGHT):
            return (
                vector.x,
                vector.y + TURNING_RADIUS,
                Vector(Direction.NORTH, vector.x - TURNING_RADIUS, vector.y + TURNING_RADIUS),
                3,
            )

        case (Direction.WEST, TurnInstruction.BACKWARD_LEFT):
            return (
                vector.x,
                vector.y + TURNING_RADIUS,
                Vector(Direction.NORTH, vector.x + TURNING_RADIUS, vector.y - TURNING_RADIUS),
                1,
            )

        case (Direction.WEST, TurnInstruction.BACKWARD_RIGHT):
            return (
                vector.x,
                vector.y + TURNING_RADIUS,
                Vector(Direction.SOUTH, vector.x + TURNING_RADIUS, vector.y + TURNING_RADIUS),
                4,
            )


def __curve(centre_x: int, centre_y, quadrant: int) -> set[Point]:
    """
    Uses Bresenham's circle drawing algorithm to determine the curved path of a robot when turning.

    :param centre_x: The centre of the turning radius's x value.
    :param centre_y: The centre of the turning radius's y value.
    :param radius: The turning radius.
    :param quadrant: The quadrant of the circle.
        Quadrants:
              2 | 1
            ----+----
              3 | 4
    :return: the points in the curve
    """
    assert 1 <= quadrant <= 4

    x = TURNING_RADIUS
    y = 0
    err = 0
    points = set[Point]()

    first = None
    second = None
    match quadrant:
        case 1:
            first = lambda _x, _y: Point(centre_x + _x, centre_y + _y)
            second = lambda _x, _y: Point(centre_x + _y, centre_y + _x)
        case 2:
            first = lambda _x, _y: Point(centre_x - _y, centre_y + _x)
            second = lambda _x, _y: Point(centre_x - _x, centre_y + _y)
        case 3:
            first = lambda _x, _y: Point(centre_x - _x, centre_y - _y)
            second = lambda _x, _y: Point(centre_x - _y, centre_y - _x)
        case 4:
            first = lambda _x, _y: Point(centre_x + _y, centre_y - _x)
            second = lambda _x, _y: Point(centre_x + _x, centre_y - _y)

    while x >= y:
        points.add(first(x, y))
        points.add(second(x, y))

        y += 1
        err += 1 + 2 * y
        if 2 * (err - x) + 1 > 0:
            x -= 1
            err += 1 - 2 * x

    return points
