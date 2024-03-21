from __future__ import annotations

from dataclasses import dataclass

from pathfinding.search.instructions import Turn, TurnInstruction, Move, MoveInstruction, MiscInstruction
from pathfinding.search.segment import segment
from pathfinding.world.primitives import Vector
from pathfinding.world.world import World, Obstacle


def search(world: World, objectives: dict[Obstacle, tuple[Vector, set[Vector]]]) -> list[Segment]:
    segments = []
    current = world.robot.vector
    for _ in world.obstacles:
        seg = segment(world, current, objectives)
        if seg is None:
            for objective in objectives.keys():
                print(f'WARNING: Unable to find path to {objective}. Skipping.')
            return segments

        obstacle, _, path = seg
        segments.append(Segment.compress(world, seg))
        current, _ = path[-1]
        objectives.pop(obstacle)

    return segments


@dataclass
class Segment:
    image_id: int
    cost: int
    instructions: list[TurnInstruction | MoveInstruction | MiscInstruction]
    vectors: list[Vector]

    @classmethod
    def compress(cls, world: World, information: tuple[Obstacle, int, list[tuple[Vector, Turn | Move | None]]]) -> Segment:
        obstacle, cost, parts = information
        instructions: list[TurnInstruction | MoveInstruction | MiscInstruction] = []
        vectors: list[Vector] = []

        for vector, move in parts:
            match move:
                case Turn():
                    instructions.append(move.turn)
                    vectors.extend(move.vectors)

                case Move() if instructions and isinstance(instructions[-1], MoveInstruction) and instructions[-1].move == move.move:
                    instructions[-1].amount += len(move.vectors) * world.cell_size
                    vectors.extend(move.vectors)

                case Move():
                    instructions.append(MoveInstruction(move=move.move, amount=len(move.vectors) * world.cell_size))
                    vectors.extend(move.vectors)

        instructions.append(MiscInstruction.CAPTURE_IMAGE)

        return cls(obstacle.image_id, cost, instructions, vectors)
