from pathfinding.search.instructions import TurnInstruction
from pathfinding.world.primitives import Direction, Vector
from pathfinding.world.world import World


# This turning function does not properly account for different points of the robot having different turning radii.
# I'm too lazy to fix it. The workaround is to ensure that the robot is an odd number of cells.
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
    turning_radius = instruction.radius(world.cell_size)
    offset = 3 // world.cell_size

    match (start.direction, instruction):
        # Initially facing north
        case (Direction.NORTH, TurnInstruction.FORWARD_LEFT):
            initial = Vector(start.direction, start.x, start.y - world.robot.south_length + offset)
            destination = Vector(Direction.WEST, initial.x - turning_radius, initial.y + turning_radius)
            curve = __curve(
                initial,
                turning_radius,
                destination,
                initial.x - turning_radius,
                initial.y,
                1,
            )
            curve.append(Vector(Direction.WEST, curve[-1].x - world.robot.east_length + offset, curve[-1].y))
            return curve

        case (Direction.NORTH, TurnInstruction.FORWARD_RIGHT):
            initial = Vector(start.direction, start.x, start.y - world.robot.south_length + offset)
            destination = Vector(Direction.EAST, initial.x + turning_radius, initial.y + turning_radius)
            curve = __curve(
                initial,
                turning_radius,
                destination,
                initial.x + turning_radius,
                initial.y,
                2,
            )
            curve.append(Vector(Direction.EAST, curve[-1].x + world.robot.west_length - offset, curve[-1].y))
            return curve

        case (Direction.NORTH, TurnInstruction.BACKWARD_LEFT):
            initial = Vector(start.direction, start.x, start.y - world.robot.south_length + offset)
            destination = Vector(Direction.EAST, initial.x - turning_radius, initial.y - turning_radius)
            curve = __curve(
                initial,
                turning_radius,
                destination,
                initial.x - turning_radius,
                initial.y,
                4,
            )
            curve.append(Vector(Direction.EAST, curve[-1].x + world.robot.west_length - offset, curve[-1].y))
            return curve

        case (Direction.NORTH, TurnInstruction.BACKWARD_RIGHT):
            initial = Vector(start.direction, start.x, start.y - world.robot.south_length + offset)
            destination = Vector(Direction.WEST, initial.x + turning_radius, initial.y - turning_radius)
            curve = __curve(
                initial,
                turning_radius,
                destination,
                initial.x + turning_radius,
                initial.y,
                3,
            )
            curve.append(Vector(Direction.WEST, curve[-1].x - world.robot.west_length + offset, curve[-1].y))
            return curve

        # Initially facing east
        case (Direction.EAST, TurnInstruction.FORWARD_LEFT):
            initial = Vector(start.direction, start.x - world.robot.west_length + offset, start.y)
            destination = Vector(Direction.NORTH, initial.x + turning_radius, initial.y + turning_radius)
            curve = __curve(
                initial,
                turning_radius,
                destination,
                initial.x,
                initial.y + turning_radius,
                4,
            )
            curve.append(Vector(Direction.NORTH, curve[-1].x, curve[-1].y + world.robot.south_length - offset))
            return curve
            # rest of the code remains the same

        case (Direction.EAST, TurnInstruction.FORWARD_RIGHT):
            initial = Vector(start.direction, start.x - world.robot.west_length + offset, start.y)
            destination = Vector(Direction.SOUTH, initial.x + turning_radius, initial.y - turning_radius)
            curve = __curve(
                initial,
                turning_radius,
                destination,
                initial.x,
                initial.y - turning_radius,
                1,
            )
            curve.append(Vector(Direction.SOUTH, curve[-1].x, curve[-1].y - world.robot.north_length + offset))
            return curve
            # rest of the code remains the same

        case (Direction.EAST, TurnInstruction.BACKWARD_LEFT):
            initial = Vector(start.direction, start.x - world.robot.west_length + offset, start.y)
            destination = Vector(Direction.SOUTH, initial.x - turning_radius, initial.y + turning_radius)
            curve = __curve(
                initial,
                turning_radius,
                destination,
                initial.x,
                initial.y + turning_radius,
                3,
            )
            curve.append(Vector(Direction.SOUTH, curve[-1].x, curve[-1].y - world.robot.north_length + offset))
            return curve

        case (Direction.EAST, TurnInstruction.BACKWARD_RIGHT):
            initial = Vector(start.direction, start.x - world.robot.west_length + offset, start.y)
            destination = Vector(Direction.NORTH, initial.x - turning_radius, initial.y - turning_radius)
            curve = __curve(
                initial,
                turning_radius,
                destination,
                initial.x,
                initial.y - turning_radius,
                2,
            )
            curve.append(Vector(Direction.NORTH, curve[-1].x, curve[-1].y + world.robot.south_length - offset))
            return curve

        # Initially facing south
        case (Direction.SOUTH, TurnInstruction.FORWARD_LEFT):
            initial = Vector(start.direction, start.x, start.y + world.robot.north_length - offset)
            destination = Vector(Direction.EAST, initial.x + turning_radius, initial.y - turning_radius)
            curve = __curve(
                initial,
                turning_radius,
                destination,
                initial.x + turning_radius,
                initial.y,
                3,
            )
            curve.append(Vector(Direction.EAST, curve[-1].x + world.robot.west_length - offset, curve[-1].y))
            return curve

        case (Direction.SOUTH, TurnInstruction.FORWARD_RIGHT):
            initial = Vector(start.direction, start.x, start.y + world.robot.north_length - offset)
            destination = Vector(Direction.WEST, initial.x - turning_radius, initial.y - turning_radius)
            curve = __curve(
                initial,
                turning_radius,
                destination,
                initial.x - turning_radius,
                initial.y,
                4,
            )
            curve.append(Vector(Direction.WEST, curve[-1].x - world.robot.east_length + offset, curve[-1].y))
            return curve

        case (Direction.SOUTH, TurnInstruction.BACKWARD_LEFT):
            initial = Vector(start.direction, start.x, start.y + world.robot.north_length - offset)
            destination = Vector(Direction.WEST, initial.x + turning_radius, initial.y + turning_radius)
            curve = __curve(
                initial,
                turning_radius,
                destination,
                initial.x + turning_radius,
                initial.y,
                2,
            )
            curve.append(Vector(Direction.WEST, curve[-1].x - world.robot.east_length + offset, curve[-1].y))
            return curve

        case (Direction.SOUTH, TurnInstruction.BACKWARD_RIGHT):
            initial = Vector(start.direction, start.x, start.y + world.robot.north_length - offset)
            destination = Vector(Direction.EAST, initial.x - turning_radius, initial.y + turning_radius)
            curve = __curve(
                initial,
                turning_radius,
                destination,
                initial.x - turning_radius,
                initial.y,
                1
            )
            curve.append(Vector(Direction.EAST, curve[-1].x + world.robot.west_length - offset, curve[-1].y))
            return curve

        # Initially facing west
        case (Direction.WEST, TurnInstruction.FORWARD_LEFT):
            initial = Vector(start.direction, start.x + world.robot.east_length - offset, start.y)
            destination = Vector(Direction.SOUTH, initial.x - turning_radius, initial.y - turning_radius)
            curve = __curve(
                initial,
                turning_radius,
                destination,
                initial.x,
                initial.y - turning_radius,
                2,
            )
            curve.append(Vector(Direction.SOUTH, curve[-1].x, curve[-1].y - world.robot.north_length + offset))
            return curve

        case (Direction.WEST, TurnInstruction.FORWARD_RIGHT):
            initial = Vector(start.direction, start.x + world.robot.east_length - offset, start.y)
            destination = Vector(Direction.NORTH, initial.x - turning_radius, initial.y + turning_radius)
            curve = __curve(
                initial,
                turning_radius,
                destination,
                initial.x,
                initial.y + turning_radius,
                3,
            )
            curve.append(Vector(Direction.NORTH, curve[-1].x, curve[-1].y + world.robot.south_length - offset))
            return curve

        case (Direction.WEST, TurnInstruction.BACKWARD_LEFT):
            initial = Vector(start.direction, start.x + world.robot.east_length - offset, start.y)
            destination = Vector(Direction.NORTH, initial.x + turning_radius, initial.y - turning_radius)
            curve = __curve(
                initial,
                turning_radius,
                destination,
                initial.x,
                initial.y - turning_radius,
                1,
            )
            curve.append(Vector(Direction.NORTH, curve[-1].x, curve[-1].y + world.robot.south_length - offset))
            return curve

        case (Direction.WEST, TurnInstruction.BACKWARD_RIGHT):
            initial = Vector(start.direction, start.x + world.robot.east_length - offset, start.y)
            destination = Vector(Direction.SOUTH, initial.x + turning_radius, initial.y + turning_radius)
            curve = __curve(
                initial,
                turning_radius,
                destination,
                initial.x,
                initial.y + turning_radius,
                4,
            )
            curve.append(Vector(Direction.SOUTH, curve[-1].x, curve[-1].y - world.robot.north_length + offset))
            return curve


def __curve(
    start: Vector,
    turning_radius: int,
    end: Vector,
    centre_x: int,
    centre_y,
    quadrant: int,
) -> list[Vector]:
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

    if second_part[-1] != end:
        second_part.append(end)

    return first_part + second_part


def __order(
    start: Vector, a: list[Vector], b: list[Vector]
) -> tuple[list[Vector], list[Vector]]:
    return (
        (a, b)
        if __manhattan_distance(start, a[0]) < __manhattan_distance(start, b[0])
        else (b, a)
    )


def __manhattan_distance(a: Vector, b: Vector) -> int:
    return abs(a.x - b.x) + abs(a.y - b.y)
