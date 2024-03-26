from pathfinding.search.instructions import TurnInstruction
from pathfinding.world.primitives import Direction, Vector
from pathfinding.world.world import World


# This turning function does not properly account for different points of the robot having different turning radii.
# I'm too lazy to fix it. The workaround is to ensure that the robot is an odd number of cells.
def turn(world: World, start: Vector, instruction: TurnInstruction) -> list[Vector] | None:
    """
    Performs a turn.

    :param world: The world.
    :param start: The initial vector.
    :param instruction: The turn instruction.
    :return: The path of the turn if it is legal, otherwise returns None.
    """

    # The turning radius (in grid cells). The turning radius is assumed to be 25cm.
    turning_radius = instruction.radius(world.cell_size)
    offset = 3 // world.cell_size

    curve: list[Vector] | None
    match (start.direction, instruction):
        # y facing north
        case (Direction.NORTH, TurnInstruction.FORWARD_LEFT):
            x = start.x
            y = start.y - world.robot.south_length + offset
            return __curve(
                world,
                turning_radius,
                Vector(
                    Direction.WEST,
                    x - turning_radius - world.robot.east_length + offset,
                    y + turning_radius,
                ),
                x - turning_radius,
                y,
                1,
            )

        case (Direction.NORTH, TurnInstruction.FORWARD_RIGHT):
            x = start.x
            y = start.y - world.robot.south_length + offset
            return __curve(
                world,
                turning_radius,
                Vector(
                    Direction.EAST,
                    x + turning_radius + world.robot.west_length - offset,
                    y + turning_radius,
                ),
                x + turning_radius,
                y,
                2,
            )

        case (Direction.NORTH, TurnInstruction.BACKWARD_LEFT):
            x = start.x
            y = start.y - world.robot.south_length + offset
            return __curve(
                world,
                turning_radius,
                Vector(
                    Direction.EAST,
                    x - turning_radius + world.robot.west_length - offset,
                    y - turning_radius,
                ),
                x - turning_radius,
                y,
                4,
            )

        case (Direction.NORTH, TurnInstruction.BACKWARD_RIGHT):
            x = start.x
            y = start.y - world.robot.south_length + offset
            return __curve(
                world,
                turning_radius,
                Vector(
                    Direction.WEST,
                    x + turning_radius - world.robot.west_length + offset,
                    y - turning_radius,
                ),
                x + turning_radius,
                y,
                3,
            )

        # y facing east
        case (Direction.EAST, TurnInstruction.FORWARD_LEFT):
            x = start.x - world.robot.west_length + offset
            y = start.y
            return __curve(
                world,
                turning_radius,
                Vector(
                    Direction.NORTH,
                    x + turning_radius,
                    y + turning_radius + world.robot.south_length - offset,
                ),
                x,
                y + turning_radius,
                4,
            )

        case (Direction.EAST, TurnInstruction.FORWARD_RIGHT):
            x = start.x - world.robot.west_length + offset
            y = start.y
            return __curve(
                world,
                turning_radius,
                Vector(
                    Direction.SOUTH,
                    x + turning_radius,
                    y - turning_radius - world.robot.north_length + offset,
                ),
                x,
                y - turning_radius,
                1,
            )

        case (Direction.EAST, TurnInstruction.BACKWARD_LEFT):
            x = start.x - world.robot.west_length + offset
            y = start.y
            return __curve(
                world,
                turning_radius,
                Vector(
                    Direction.SOUTH,
                    x - turning_radius,
                    y + turning_radius - world.robot.north_length + offset,
                ),
                x,
                y + turning_radius,
                3,
            )

        case (Direction.EAST, TurnInstruction.BACKWARD_RIGHT):
            x = start.x - world.robot.west_length + offset
            y = start.y
            return __curve(
                world,
                turning_radius,
                Vector(Direction.NORTH, x - turning_radius, y - turning_radius),
                x,
                y - turning_radius + world.robot.south_length - offset,
                2,
            )

        # y facing south
        case (Direction.SOUTH, TurnInstruction.FORWARD_LEFT):
            x = start.x
            y = start.y + world.robot.north_length - offset
            return __curve(
                world,
                turning_radius,
                Vector(
                    Direction.EAST,
                    x + turning_radius + world.robot.west_length - offset,
                    y - turning_radius,
                ),
                x + turning_radius,
                y,
                3,
            )

        case (Direction.SOUTH, TurnInstruction.FORWARD_RIGHT):
            x = start.x
            y = start.y + world.robot.north_length - offset
            return __curve(
                world,
                turning_radius,
                Vector(
                    Direction.WEST,
                    x - turning_radius - world.robot.east_length + offset,
                    y - turning_radius,
                ),
                x - turning_radius,
                y,
                4,
            )

        case (Direction.SOUTH, TurnInstruction.BACKWARD_LEFT):
            x = start.x
            y = start.y + world.robot.north_length - offset
            return __curve(
                world,
                turning_radius,
                Vector(
                    Direction.WEST,
                    x + turning_radius - world.robot.east_length + offset,
                    y + turning_radius,
                ),
                x + turning_radius,
                y,
                2,
            )

        case (Direction.SOUTH, TurnInstruction.BACKWARD_RIGHT):
            x = start.x
            y = start.y + world.robot.north_length - offset
            return __curve(
                world,
                turning_radius,
                Vector(
                    Direction.EAST,
                    x - turning_radius + world.robot.west_length - offset,
                    y + turning_radius,
                ),
                x - turning_radius,
                y,
                1,
            )

        # y facing west
        case (Direction.WEST, TurnInstruction.FORWARD_LEFT):
            x = start.x + world.robot.east_length - offset
            y = start.y
            return __curve(
                world,
                turning_radius,
                Vector(
                    Direction.SOUTH,
                    x - turning_radius,
                    y - turning_radius - world.robot.north_length + offset,
                ),
                x,
                y - turning_radius,
                2,
            )

        case (Direction.WEST, TurnInstruction.FORWARD_RIGHT):
            x = start.x + world.robot.east_length - offset
            y = start.y
            return __curve(
                world,
                turning_radius,
                Vector(
                    Direction.NORTH,
                    x - turning_radius,
                    y + turning_radius + world.robot.south_length - offset,
                ),
                x,
                y + turning_radius,
                3,
            )

        case (Direction.WEST, TurnInstruction.BACKWARD_LEFT):
            x = start.x + world.robot.east_length - offset
            y = start.y
            return __curve(
                world,
                turning_radius,
                Vector(
                    Direction.NORTH,
                    x + turning_radius,
                    y - turning_radius + world.robot.south_length - offset,
                ),
                x,
                y - turning_radius,
                1,
            )

        case (Direction.WEST, TurnInstruction.BACKWARD_RIGHT):
            x = start.x + world.robot.east_length - offset
            y = start.y
            return __curve(
                world,
                turning_radius,
                Vector(
                    Direction.SOUTH,
                    x + turning_radius,
                    y + turning_radius - world.robot.north_length + offset,
                ),
                x,
                y + turning_radius,
                4,
            )


def __curve(
    world: World,
    turning_radius: int,
    centre_x: int,
    centre_y,
    quadrant: int,
) -> list[Vector] | None:
    """
    Uses a modified Midpoint circle algorithm to determine the curved path of a robot when turning.

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
    path = []
    a_map = None
    b_map = None

    match quadrant:
        case 1:
            a_map = lambda _x, _y: Vector(end.direction, centre_x + _x, centre_y + _y)
            b_map = lambda _x, _y: Vector(end.direction, centre_x + _y, centre_y + _x)
        case 2:
            a_map = lambda _x, _y: Vector(end.direction, centre_x - _y, centre_y + _x)
            b_map = lambda _x, _y: Vector(end.direction, centre_x - _x, centre_y + _y)
        case 3:
            a_map = lambda _x, _y: Vector(end.direction, centre_x - _x, centre_y - _y)
            b_map = lambda _x, _y: Vector(end.direction, centre_x - _y, centre_y - _x)
        case 4:
            a_map = lambda _x, _y: Vector(end.direction, centre_x + _y, centre_y - _x)
            b_map = lambda _x, _y: Vector(end.direction, centre_x + _x, centre_y - _y)

    while x >= y:
        a = a_map(x, y)
        if world.contains(a):
            path.append(a)
        else:
            return None

        b = b_map(x, y)
        if world.contains(b):
            path.append(b)
        else:
            return None

        y += 1
        err += 1 + 2 * y
        if 2 * (err - x) + 1 > 0:
            x -= 1
            err += 1 - 2 * x

    path.append(end)
    return path
