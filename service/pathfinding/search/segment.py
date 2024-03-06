import heapq
import math
from typing import List, Generator

from pathfinding.search.instructions import Turn, Move, TurnInstruction, MoveInstruction, Straight
from pathfinding.search.straight import straight
from pathfinding.search.turn import turn
from pathfinding.world.primitives import Vector
from pathfinding.world.world import World


def segment(world: World, initial: Vector, objectives: set[Vector]) -> tuple[int, List[tuple[Vector, Turn | Move | None]]]:
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
    current = initial

    while not frontier.empty():
        current = frontier.pop()

        if current in objectives:
            break

        for next, move in __neighbours(world, current):
            new_cost = costs[current] + len(move.vectors)
            if next not in costs or new_cost < costs[next]:
                frontier.add(new_cost + __heuristic(next, objectives), next)
                source[next] = current
                moves[next] = move
                costs[next] = new_cost

    path = []
    objective = current

    while current is not None:
        path.append((current, moves.get(current)))
        current = source.get(current)

    path.reverse()

    return costs.get(objective, -1), path


class __PriorityQueue:
    def __init__(self):
        self.elements: List[tuple[int, Vector]] = []

    def empty(self):
        return not self.elements

    def add(self, priority: int, vector: Vector) -> None:
        heapq.heappush(self.elements, (priority, vector))

    def pop(self) -> Vector:
        return heapq.heappop(self.elements)[1]


def __neighbours(world: World, current: Vector) -> Generator[tuple[Vector, Turn | Move], None, None]:
    for move in TurnInstruction:
        path = turn(world, current, move)
        if all(map(lambda p: world.contains(p), path)):
            yield path[-1], Turn(move, path)

    for move in Straight:
        for cells in [10, 5, 1]:
            path = straight(current, move, cells)
            if all(map(lambda p: world.contains(p), path)):
                yield path[-1], Move(move, cells)


def __heuristic(current: Vector, objectives: set[Vector]) -> int:
    """
    The Euclidean distance between two vectors. This is preferred over Manhattan distance which is not admissible.
    """
    return min(int(math.sqrt((objective.x - current.x) ** 2 + (objective.y - current.y) ** 2)) for objective in objectives)
