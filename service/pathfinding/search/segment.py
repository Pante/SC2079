import heapq
import math
from typing import List, Generator

from pathfinding.instructions.instructions import TurnInstruction, Move, Turn
from pathfinding.search.move import move
from pathfinding.search.turn import turn
from pathfinding.world.objective import generate_objectives
from pathfinding.world.primitives import Vector, Direction, Point
from pathfinding.world.world import World, Robot, Obstacle


def segment(world: World, initial: Vector, objective: Vector) -> tuple[int, List[tuple[Vector, TurnInstruction | Move]]]:
    """
    Finds the shortest path of a segment of the overall path.

    Uses an annotated A* pathfinding algorithm with a modified function for returning a vector's neighbour.
    The Euclidean distance between two vectors is used as the heuristic function.
    https://harablog.wordpress.com/2009/02/05/hierarchical-clearance-based-pathfinding/

    :param world: The world.
    :param initial: The initial vector.
    :param objective: The goal vector.
    :return:
        The cost of the segment,
        The
    """
    frontier = __PriorityQueue()
    source: dict[Vector, Vector | None] = {}
    instructions: dict[Vector, TurnInstruction | Move | None] = {}
    cost: dict[Vector, int] = {}

    frontier.add(0, initial)
    source[initial] = None
    instructions[initial] = None
    cost[initial] = 0

    while not frontier.empty():
        current = frontier.pop()

        if current == objective:
            break

        for next, instruction in __neighbours(world, current):
            new_cost = cost[current]
            match instruction:
                case Move():
                    new_cost += + 1
                case TurnInstruction():
                    new_cost += len(instruction.points)

            if next not in cost or new_cost < cost[next]:
                frontier.add(new_cost + __heuristic(next, objective), next)
                source[next] = current
                instructions[next] = instruction
                cost[next] = new_cost

    path = []
    current = objective

    while current is not None:
        path.append((current, instructions[current]))
        current = source[current]

    path.reverse()

    return cost[objective], path


class __PriorityQueue:
    elements: List[tuple[int, Vector]] = []

    def empty(self):
        return not self.elements

    def add(self, priority: int, vector: Vector) -> None:
        heapq.heappush(self.elements, (priority, vector))

    def pop(self) -> Vector:
        return heapq.heappop(self.elements)[1]


def __neighbours(world: World, current: Vector) -> Generator[tuple[Vector, TurnInstruction | Move], None, None]:
    robot = world.robot
    for instruction in Turn:
        next, path = turn(current, instruction)
        if all(map(lambda p: world.contains(robot.set_point(p)), path)) and world.contains(robot.set_vector(next)):
            yield next, TurnInstruction(instruction, path)

    for instruction in Move:
        next = move(current, instruction)
        if world.contains(robot.set_vector(next)):
            yield next, instruction


def __heuristic(a: Vector, b: Vector) -> int:
    """
    The Euclidean distance between two vectors. This is preferred over Manhattan distance which is not admissible.
    """
    return int(math.sqrt((b.x - a.x) ** 2 + (b.y - a.y) ** 2))


# Create a Robot instance
robot = Robot(Direction.NORTH, Point(0, 0), Point(2, 2))

# Create some Obstacle instances
obstacle1 = Obstacle(Direction.NORTH, Point(2, 2), Point(3, 3), 1)
obstacle2 = Obstacle(Direction.SOUTH, Point(3, 4), Point(4, 5), 2)

# Create a list of obstacles


# Create a World instance
world = World(15, 15, robot, [obstacle1, obstacle2])
objectives = generate_objectives(world)
print(robot.clearance)

print(objectives)
