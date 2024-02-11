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
