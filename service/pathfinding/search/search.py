import heapq
import math
from typing import List, Dict

import numpy as np
from python_tsp.distances import euclidean_distance_matrix
from python_tsp.exact import solve_tsp_dynamic_programming

from pathfinding.world.objective import Objective
from pathfinding.world.primitives import Vector
from pathfinding.world.world import Robot, World


def __hamiltonian_path(robot: Robot, objectives: List[Objective]) -> (List[int], float):
    """
    Returns the hamiltonian path of the initial robot and the objectives.
    This is used as a heuristic to determine the optimal visitation order of the objectives.

    :param robot: The robot (initial point).
    :param objectives: The objectives to visit.
    :return:
        The indexes of the robot (0) and objectives (1:N) in the order of visitation.
        The total distance the optimal permutation produces.
    """
    positions = [[robot.south_west.x, robot.south_west.y]]
    positions.extend([[objective.south_west.x, objective.south_west.y] for objective in objectives])
    distance_matrix = euclidean_distance_matrix(np.array(positions))
    permutation, distance = solve_tsp_dynamic_programming(distance_matrix)
    return permutation, distance


def __search(world: World, initial: Vector, objective: Vector):
    frontier = __PriorityQueue()
    source: dict[Vector, Vector | None] = {}
    cost: dict[Vector, int] = {}

    frontier.add(0, initial)
    source[initial] = None
    cost[initial] = 0

    while not frontier.empty():
        current = frontier.pop()

        if current == objective:
            break

        for next in graph.neighbors(current):
            new_cost = cost[current] + graph.cost(current, next)
            if next not in cost or new_cost < cost[next]:
                frontier.add(new_cost + __euclidean_distance(objective, next), next)
                source[next] = current
                cost[next] = new_cost

    return source, cost


class __PriorityQueue:
    elements: List[(int, Vector)] = []

    def empty(self):
        return not self.elements

    def add(self, priority: int, vector: Vector) -> None:
        heapq.heappush(self.elements, (priority, vector))

    def pop(self) -> Vector:
        return heapq.heappop(self.elements)[1]


def __euclidean_distance(a: Vector, b: Vector) -> int:
    return int(math.sqrt((b.x - a.x)**2 + (b.y - a.y)**2))