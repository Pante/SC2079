import heapq
import math
from typing import Generator

from pathfinding.search.instructions import Turn, Move, TurnInstruction, Straight
from pathfinding.search.straight import straight
from pathfinding.search.turn import turn
from pathfinding.world.primitives import Vector
from pathfinding.world.world import World, Obstacle


def segment(world: World, initial: Vector, objectives: dict[Obstacle, tuple[Vector, set[Vector]]]) -> None | tuple[Obstacle, int, list[tuple[Vector, Turn | Move | None]]]:
    """
    Finds the shortest path of a segment of the overall path.

    Uses an annotated A* pathfinding algorithm with a modified function for returning a vector's neighbour. Each grid
    cell contains a "true clearance" value which denotes the distance from an obstacle. These values are pre-computed to
    avoid re-computation during each run.

    See https://harablog.wordpress.com/2009/02/05/hierarchical-clearance-based-pathfinding/

    The possible neighbours are constrained by the current vector's direction and moves, i.e. FORWARD_LEFT, BACKWARD.
    Vectors that share the same x & y coordinates but different direction are considered different cells.

    The Euclidean distance between two vectors is used as the heuristic function.

    :param world: The world.
    :param initial: The initial vector. Always the south-west corner of the robot.
    :param objectives: The possible objective vectors. Always the south-west corner of objectives.
    :return:
        The cost of the segment.
        The vectors and corresponding instructions from the initial vector to the objective vector. Vectors that form
        a curve when turning are embedded inside the instruction
    """
    frontier = __PriorityQueue()
    source: dict[Vector, Vector | None] = {}
    moves: dict[Vector, Turn | Move | None] = {}
    costs: dict[Vector, int] = {}

    frontier.add(0, initial)
    source[initial] = None
    moves[initial] = None
    costs[initial] = 0

    while not frontier.empty():
        current = frontier.pop()

        for obstacle, (_, vectors) in objectives.items():
            if current in vectors:
                return __trace(source, moves, costs, obstacle, current)

        for next, move in __neighbours(world, current):
            new_cost = costs[current]
            match move:
                case Turn():
                    new_cost += move.turn.arc_length(world.cell_size)
                case Move():
                    new_cost += len(move.vectors)

            if next not in costs or new_cost < costs[next]:
                frontier.add(new_cost, next)
                source[next] = current
                moves[next] = move
                costs[next] = new_cost

    return None


def __trace(
    source: dict[Vector, Vector | None],
    moves: dict[Vector, Turn | Move | None],
    costs: dict[Vector, int],
    obstacle: Obstacle,
    current: Vector
) -> tuple[Obstacle, int, list[tuple[Vector, Turn | Move | None]]]:
    path = []
    objective = current

    while current is not None:
        path.append((current, moves.get(current)))
        current = source.get(current)

    path.reverse()
    return obstacle, costs.get(objective, -1), path


class __PriorityQueue:
    def __init__(self):
        self.elements: list[tuple[int, Vector]] = []

    def empty(self):
        return not self.elements

    def add(self, priority: int, vector: Vector) -> None:
        heapq.heappush(self.elements, (priority, vector))

    def pop(self) -> Vector:
        return heapq.heappop(self.elements)[1]


def __neighbours(world: World, current: Vector) -> Generator[tuple[Vector, Turn | Move], None, None]:
    for move in TurnInstruction:
        path = turn(world, current, move)
        if path is not None:
            yield path[-1], Turn(move, path)

    for move in Straight:
        modifier = 1 if move == Straight.FORWARD else -1
        for length in [5]:
            path = straight(current, modifier, length)
            if all(map(lambda p: world.contains(p), path)):
                yield path[-1], Move(move, path)


def __heuristic(current: Vector, objectives: dict[Obstacle, tuple[Vector, set[Vector]]]) -> int:
    """
    This function takes longer than the actual time it saves in reality.

    The Euclidean distance between two vectors. This is preferred over Manhattan distance which is not admissible.
    """
    if len(objectives) == 0:
        return 0

    return min(int(math.sqrt((vector.x - current.x) ** 2 + (vector.y - current.y) ** 2)) for vector, _ in objectives.values())
