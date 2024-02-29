from pathfinding.search.instructions import TurnInstruction
from pathfinding.world.primitives import Direction, Vector
from pathfinding.world.world import World


def turn(world: World, start: Vector, instruction: TurnInstruction) -> list[Vector]:
    """
    Performs a turn.

    :param world: The world.
    :param start: The initial vector.
    :param instruction: The turn instruction.
    :return:
        The x & y coordinates of the centre of the turning radius,
        the vector after executing the turn
        the quadrant of the turn,
    """

    # The turning radius (in grid cells). The turning radius is assumed to be 25cm.
    turning_radius = (25 // world.cell_size) + 2

    match (start.direction, instruction):
        # Initially facing north
        case (Direction.NORTH, TurnInstruction.FORWARD_LEFT):
            return __curve(
                start,
                turning_radius,
                Vector(Direction.WEST, start.x - turning_radius, start.y + turning_radius),
                start.x - turning_radius,
                start.y,
                1,
            )

        case (Direction.NORTH, TurnInstruction.FORWARD_RIGHT):
            return __curve(
                start,
                turning_radius,
                Vector(Direction.EAST, start.x + turning_radius, start.y + turning_radius),
                start.x + turning_radius,
                start.y,
                2,
            )

        case (Direction.NORTH, TurnInstruction.BACKWARD_LEFT):
            return __curve(
                start,
                turning_radius,
                Vector(Direction.EAST, start.x - turning_radius, start.y - turning_radius),
                start.x - turning_radius,
                start.y,
                4,
            )

        case (Direction.NORTH, TurnInstruction.BACKWARD_RIGHT):
            return __curve(
                start,
                turning_radius,
                Vector(Direction.WEST, start.x + turning_radius, start.y - turning_radius),
                start.x + turning_radius,
                start.y,
                3,
            )

        # Initially facing east
        case (Direction.EAST, TurnInstruction.FORWARD_LEFT):
            return __curve(
                start,
                turning_radius,
                Vector(Direction.NORTH, start.x + turning_radius, start.y + turning_radius),
                start.x,
                start.y + turning_radius,
                4,
            )

        case (Direction.EAST, TurnInstruction.FORWARD_RIGHT):
            return __curve(
                start,
                turning_radius,
                Vector(Direction.SOUTH, start.x + turning_radius, start.y - turning_radius),
                start.x,
                start.y - turning_radius,
                1,
            )

        case (Direction.EAST, TurnInstruction.BACKWARD_LEFT):
            return __curve(
                start,
                turning_radius,
                Vector(Direction.SOUTH, start.x - turning_radius, start.y + turning_radius),
                start.x,
                start.y + turning_radius,
                3,
            )

        case (Direction.EAST, TurnInstruction.BACKWARD_RIGHT):
            return __curve(
                start,
                turning_radius,
                Vector(Direction.NORTH, start.x - turning_radius, start.y - turning_radius),
                start.x,
                start.y - turning_radius,
                2,
            )

        # Initially facing south
        case (Direction.SOUTH, TurnInstruction.FORWARD_LEFT):
            return __curve(
                start,
                turning_radius,
                Vector(Direction.EAST, start.x + turning_radius, start.y - turning_radius),
                start.x + turning_radius,
                start.y,
                3,
            )

        case (Direction.SOUTH, TurnInstruction.FORWARD_RIGHT):
            return __curve(
                start,
                turning_radius,
                Vector(Direction.WEST, start.x - turning_radius, start.y - turning_radius),
                start.x - turning_radius,
                start.y,
                4,
            )

        case (Direction.SOUTH, TurnInstruction.BACKWARD_LEFT):
            return __curve(
                start,
                turning_radius,
                Vector(Direction.WEST, start.x + turning_radius, start.y + turning_radius),
                start.x + turning_radius,
                start.y,
                2,
            )

        case (Direction.SOUTH, TurnInstruction.BACKWARD_RIGHT):
            return __curve(
                start,
                turning_radius,
                Vector(Direction.EAST, start.x - turning_radius, start.y + turning_radius),
                start.x - turning_radius,
                start.y,
                1,
            )

        # Initially facing west
        case (Direction.WEST, TurnInstruction.FORWARD_LEFT):
            return __curve(
                start,
                turning_radius,
                Vector(Direction.SOUTH, start.x - turning_radius, start.y - turning_radius),
                start.x,
                start.y - turning_radius,
                2,
            )

        case (Direction.WEST, TurnInstruction.FORWARD_RIGHT):
            return __curve(
                start,
                turning_radius,
                Vector(Direction.NORTH, start.x - turning_radius, start.y + turning_radius),
                start.x,
                start.y + turning_radius,
                3,
            )

        case (Direction.WEST, TurnInstruction.BACKWARD_LEFT):
            return __curve(
                start,
                turning_radius,
                Vector(Direction.NORTH, start.x + turning_radius, start.y - turning_radius),
                start.x,
                start.y - turning_radius,
                1,
            )

        case (Direction.WEST, TurnInstruction.BACKWARD_RIGHT):
            return __curve(
                start,
                turning_radius,
                Vector(Direction.SOUTH, start.x + turning_radius, start.y + turning_radius),
                start.x,
                start.y + turning_radius,
                1,
            )


def __curve(start: Vector, turning_radius: int, end: Vector, centre_x: int, centre_y, quadrant: int) -> list[Vector]:
    """
    Uses a modified Midpoint circle algorithm to determine the curved path of a robot when turning.

    :param start: The starting vector.
    :param centre_x: The centre of the turning radius's x value.
    :param centre_y: The centre of the turning radius's y value.
    :param quadrant: The quadrant of the circle.
        Quadrants:
              2 | 1
            ----+----
              3 | 4
    :return: the vectors in the curve, may contain duplicates
    """
    assert 1 <= quadrant <= 4

    x = turning_radius
    y = 0
    err = 0

    # The original Midpoint circle algorithm fills in quadrants from two extremes. We store them in separate lists to
    # ensure an ordered list of vectors starting from the starting vector is returned.
    a = []
    b = []
    a_map = None
    b_map = None
    match quadrant:
        case 1:
            a_map = lambda _x, _y: Vector(None, centre_x + _x, centre_y + _y)
            b_map = lambda _x, _y: Vector(None, centre_x + _y, centre_y + _x)
        case 2:
            a_map = lambda _x, _y: Vector(None, centre_x - _y, centre_y + _x)
            b_map = lambda _x, _y: Vector(None, centre_x - _x, centre_y + _y)
        case 3:
            a_map = lambda _x, _y: Vector(None, centre_x - _x, centre_y - _y)
            b_map = lambda _x, _y: Vector(None, centre_x - _y, centre_y - _x)
        case 4:
            a_map = lambda _x, _y: Vector(None, centre_x + _y, centre_y - _x)
            b_map = lambda _x, _y: Vector(None, centre_x + _x, centre_y - _y)

    while x >= y:
        a.append(a_map(x, y))
        b.append(b_map(x, y))

        y += 1
        err += 1 + 2 * y
        if 2 * (err - x) + 1 > 0:
            x -= 1
            err += 1 - 2 * x

    first_part, second_part = __order(start, a, b)
    second_part.reverse()
    for vector in first_part:
        vector.direction = start.direction

    for vector in second_part:
        vector.direction = end.direction

    # The start & end may contain vectors with the same coordinates but different directions.
    if first_part[-1].x == second_part[0].x and first_part[-1].y == second_part[0].y:
        first_part.pop()

    if second_part[-1] != end:
        second_part.append(end)

    return first_part + second_part


def __order(start: Vector, a: list[Vector], b: list[Vector]) -> tuple[list[Vector], list[Vector]]:
    return (a, b) if __manhattan_distance(start, a[0]) < __manhattan_distance(start, b[0]) else (b, a)


def __manhattan_distance(a: Vector, b: Vector) -> int:
    return abs(a.x - b.x) + abs(a.y - b.y)
