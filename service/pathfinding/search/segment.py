import heapq
import math
from typing import List, Generator

from pathfinding.search.instructions import Turn, Move, TurnInstruction
from pathfinding.search.move import move
from pathfinding.search.turn import turn
from pathfinding.world.primitives import Vector
from pathfinding.world.world import World, Cell


def segment(world: World, initial: Vector, objective: Vector) -> tuple[int, List[tuple[Vector, Turn | Move | None]]]:
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
    :param objective: The goal vector. Always the south-west corner of an objective.
    :return:
        The cost of the segment.
        The vectors and corresponding instructions from the initial vector to the objective vector. Vectors that form
        a curve when turning are embedded inside the instruction
    """
    frontier = __PriorityQueue()
    source: dict[Vector, Vector | None] = {}
    instructions: dict[Vector, Turn | Move | None] = {}
    costs: dict[Vector, int] = {}

    frontier.add(0, initial)
    source[initial] = None
    instructions[initial] = None
    costs[initial] = 0
    cell = Cell(world.robot.direction, world.robot.south_west, world.robot.north_east)

    while not frontier.empty():
        current = frontier.pop()

        if current == objective:
            break

        for next, instruction in __neighbours(world, cell, current):
            new_cost = costs[current]
            match instruction:
                case Move():
                    new_cost += + 1
                case Turn():
                    # TODO: Should diagonals' cost be 2 instead of 1?
                    new_cost += len(instruction.vectors)

            if next not in costs or new_cost < costs[next]:
                frontier.add(new_cost + __heuristic(next, objective), next)
                source[next] = current
                instructions[next] = instruction
                costs[next] = new_cost

    path = []
    current = objective

    while current is not None:
        path.append((current, instructions.get(current)))
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


def __neighbours(world: World, cell: Cell, current: Vector) -> Generator[tuple[Vector, Turn | Move], None, None]:
    for instruction in TurnInstruction:
        path = turn(current, instruction)
        if all(map(lambda p: world.contains(cell.set_vector(p)), path)):
            yield path[-1], Turn(instruction, path)

    for instruction in Move:
        next = move(current, instruction)
        if world.contains(cell.set_vector(next)):
            yield next, instruction


def __heuristic(a: Vector, b: Vector) -> int:
    """
    The Euclidean distance between two vectors. This is preferred over Manhattan distance which is not admissible.
    """
    return int(math.sqrt((b.x - a.x) ** 2 + (b.y - a.y) ** 2))
