from __future__ import annotations

from dataclasses import dataclass
from itertools import pairwise
from typing import List

import numpy as np
from python_tsp.distances import euclidean_distance_matrix
from python_tsp.exact import solve_tsp_dynamic_programming

from pathfinding.search.instructions import Turn, TurnInstruction, Move, MoveInstruction, MiscInstruction
from pathfinding.search.segment import segment
from pathfinding.world.objective import Objective
from pathfinding.world.primitives import Vector, Point
from pathfinding.world.world import Robot, World, GRID_CELL_SIZE


def search(world: World, objectives: List[Objective]) -> List[Segment]:
    entities = [world.robot] + objectives
    permutation, _ = __hamiltonian_path(entities)
    return __segments(world, [entities[i] for i in permutation])


def __hamiltonian_path(entities: List[Robot | Objective]) -> tuple[List[int], float]:
    """
    Returns the hamiltonian path of the initial robot and the objectives.
    This is used as a heuristic to determine the optimal visitation order of the objectives.

    :param robot: The robot (initial point).
    :param entities: The objectives to visit.
    :return:
        The indexes of the robot (0) and objectives (1:N) in the order of visitation.
        The total distance the optimal permutation produces.
    """
    # TODO: Clarify whether we need to return back to starting position.
    #       Can be switched to use open TSP algorithm otherwise.
    positions = [[entity.south_west.x, entity.south_west.y] for entity in entities]
    distance_matrix = euclidean_distance_matrix(np.array(positions))
    permutation, distance = solve_tsp_dynamic_programming(distance_matrix)
    return permutation, distance


def __segments(world: World, entities: List[Robot | Objective]) -> List[Segment]:
    segments = []
    for a, b in pairwise(entities):
        tuple = segment(world, a.vector, b.vector)
        segments.append(Segment.compress(b.image_id if isinstance(b, Objective) else None, tuple))

    return segments


@dataclass
class Segment:
    image_id: int
    cost: int
    instructions: List[TurnInstruction | MoveInstruction | MiscInstruction]
    vectors: list[Vector]

    @classmethod
    def compress(cls, image_id: int | None, information: tuple[int, list[tuple[Vector, Turn | Move]]]) -> Segment:
        cost, parts = information
        instructions: List[TurnInstruction | MoveInstruction | MiscInstruction] = []
        vectors: list[Vector] = []

        for vector, movement in parts:
            match movement:
                case Turn():
                    instructions.append(movement.turn)
                    vectors.extend(movement.vectors)

                case Move() if instructions and instructions[-1] is MoveInstruction and instructions[
                    -1].move == movement:
                    vectors.append(vector)
                    instructions[-1].amount += GRID_CELL_SIZE

                case Move():
                    vectors.append(vector)
                    instructions.append(MoveInstruction(movement, GRID_CELL_SIZE))

        # TODO: This might need to be tweaked if we need to move back to starting point
        instructions.append(MiscInstruction.CAPTURE_IMAGE)

        return cls(image_id, cost, instructions, vectors)
