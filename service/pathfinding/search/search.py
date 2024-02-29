from __future__ import annotations

from dataclasses import dataclass
from itertools import pairwise
from typing import List

import numpy as np
from python_tsp.distances import euclidean_distance_matrix
from python_tsp.exact import solve_tsp_dynamic_programming

from pathfinding.search.instructions import Turn, TurnInstruction, Move, MoveInstruction, MiscInstruction
from pathfinding.search.segment import segment
from pathfinding.world.primitives import Vector
from pathfinding.world.world import Robot, World, Obstacle


def search(world: World, objectives: dict[Obstacle, set[Vector]]) -> List[Segment]:
    entities = [world.robot] + world.obstacles
    permutation, _ = __hamiltonian_path(entities, objectives)
    return __segments(world, [entities[i] for i in permutation], objectives)


# TODO: We should replace this function path with better search heuristics to prevent edge cases.
def __hamiltonian_path(entities: List[Robot | Obstacle], objectives: dict[Obstacle, set[Vector]]) -> tuple[
    List[int], float]:
    """
    Returns the hamiltonian path of the initial robot and the objectives.
    This is used as a heuristic to determine the optimal visitation order of the objectives.

    :param entities: The robot and objectives to visit.
    :return:
        The indexes of the robot (0) and objectives (1:N) in the order of visitation.
        The total distance the optimal permutation produces.

    11, 29, 9, 13
    """

    positions: list[list[int]] = []
    for entity in entities:
        match entity:
            case r if isinstance(r, Robot):
                positions.append([entity.south_west.x, entity.south_west.y])

            case o if isinstance(o, Obstacle):
                # Getting an element from a set is non-deterministic
                objective = next(iter(objectives[o]))
                positions.append([objective.x, objective.y])

    positions = [[entity.south_west.x, entity.south_west.y] for entity in entities]
    distance_matrix = euclidean_distance_matrix(np.array(positions))
    distance_matrix[:, 0] = 0
    permutation, distance = solve_tsp_dynamic_programming(distance_matrix)
    return permutation, distance


def __segments(world: World, entities: List[Robot | Obstacle], objectives: dict[Obstacle, set[Vector]]) -> List[Segment]:
    segments = []
    for a, b in pairwise(entities):
        tuple = segment(world, a.vector, objectives[b])
        segments.append(Segment.compress(world, b.image_id if isinstance(b, Obstacle) else None, tuple))

    return segments


@dataclass
class Segment:
    image_id: int
    cost: int
    instructions: List[TurnInstruction | MoveInstruction | MiscInstruction]
    vectors: list[Vector]

    @classmethod
    def compress(cls, world: World, image_id: int | None, information: tuple[int, list[tuple[Vector, Turn | Move]]]) -> Segment:
        cost, parts = information
        instructions: List[TurnInstruction | MoveInstruction | MiscInstruction] = []
        vectors: list[Vector] = []

        for vector, movement in parts:
            match movement:
                case Turn():
                    instructions.append(movement.turn)
                    vectors.extend(movement.vectors)

                case Move() if instructions and isinstance(instructions[-1], MoveInstruction) and instructions[-1].move == movement:
                    vectors.append(vector)
                    instructions[-1].amount += world.cell_size

                case Move():
                    vectors.append(vector)
                    instructions.append(MoveInstruction(movement, world.cell_size))

        instructions.append(MiscInstruction.CAPTURE_IMAGE)

        return cls(image_id, cost, instructions, vectors)
