from __future__ import annotations

from datetime import datetime
from http import HTTPStatus

import numpy as np
from flask import make_response
from flask_openapi3 import APIBlueprint, Tag
from pathfinding.search.instructions import (
    MiscInstruction,
    Move,
    MoveInstruction,
    TurnInstruction,
)
from pathfinding.search.search import Segment, search
from pathfinding.world.objective import generate_objectives
from pathfinding.world.primitives import Direction, Point, Vector
from pathfinding.world.world import Obstacle, Robot, World
from pydantic import BaseModel, Field

api = APIBlueprint(
    "/pathfinding",
    __name__,
    url_prefix="/pathfinding",
    abp_tags=[Tag(name="Pathfinding")],
)


class PathfindingRequest(BaseModel):
    verbose: bool = Field(
        default=True,
        description="Whether to attach the path and cost alongside the movement "
        "instructions in the response.",
    )

    size: int | None = Field(
        default=40, description="The width & height in number of cells."
    )
    robot: PathfindingRequestRobot = Field(
        description="The initial position of the robot."
    )
    obstacles: list[PathfindingRequestObstacle] = Field(min_length=1)


class PathfindingRequestRobot(BaseModel):
    direction: Direction = Field(description="The direction of the robot.")
    south_west: PathfindingPoint = Field(
        description="The south-west corner of the robot."
    )
    north_east: PathfindingPoint = Field(
        description="The north-east corner of the robot."
    )

    def to_robot(self):
        south_west = self.south_west.to_point()
        north_east = self.north_east.to_point()

        # This is a workaround to ensure that the centre point isn't off-centre. It is to workaround incorrect turning
        # calculation.
        if (north_east.x - south_west.x) % 2 != 0 and (
            north_east.y - south_west.y
        ) % 2 != 0:
            north_east = Point(north_east.x + 1, north_east.y + 1)

        return Robot(self.direction, south_west, north_east)


class PathfindingRequestObstacle(BaseModel):
    image_id: int = Field(ge=1, description="The image ID.")
    direction: Direction = Field(description="The direction of the image.")
    south_west: PathfindingPoint = Field(
        description="The south-west corner of the obstacle."
    )
    north_east: PathfindingPoint = Field(
        description="The north-east corner of the obstacle."
    )

    def to_obstacle(self):
        south_west = self.south_west.to_point()
        north_east = self.north_east.to_point()
        return Obstacle(self.direction, south_west, north_east, self.image_id)


class PathfindingResponse(BaseModel):
    segments: list[PathfindingResponseSegment] = Field(
        description="The data for moving the robot from the "
        "start/objective to another objective."
    )


class PathfindingResponseSegment(BaseModel):
    image_id: int
    cost: int | None = Field(description="The cost, included only if verbose is true.")
    instructions: list[
        MiscInstruction | TurnInstruction | PathfindingResponseMoveInstruction
    ]
    path: list[PathfindingVector] | None = Field(
        description="The path (unordered), included only if verbose is true."
    )

    @classmethod
    def from_segment(cls, verbose: bool, segment: Segment):
        cost = segment.cost if verbose else 0
        instructions = [
            (
                PathfindingResponseMoveInstruction.from_move_instruction(i)
                if isinstance(i, MoveInstruction)
                else i
            )
            for i in segment.instructions
        ]
        vectors = (
            [PathfindingVector.from_vector(vector) for vector in segment.vectors]
            if verbose
            else []
        )
        return cls(
            image_id=segment.image_id,
            cost=cost,
            instructions=instructions,
            path=vectors,
        )


class PathfindingResponseMoveInstruction(BaseModel):
    move: Move
    amount: int = Field(
        ge=1, description="The amount to move the robot in centimetres."
    )

    @classmethod
    def from_move_instruction(cls, move_instruction: MoveInstruction):
        return cls(move=move_instruction.move, amount=move_instruction.amount)


class PathfindingVector(BaseModel):
    direction: Direction = Field(description="The direction")
    x: int = Field(ge=0)
    y: int = Field(ge=0)

    @classmethod
    def from_vector(cls, vector: Vector):
        return cls(direction=vector.direction, x=vector.x, y=vector.y)

    def to_vector(self):
        return Vector(self.direction, self.x, self.y)


class PathfindingPoint(BaseModel):
    x: int = Field(ge=0)
    y: int = Field(ge=0)

    @classmethod
    def from_point(cls, point: Point):
        return cls(x=point.x, y=point.y)

    def to_point(self):
        return Point(self.x, self.y)


@api.post("/", responses={200: PathfindingResponse})
def pathfinding(body: PathfindingRequest):
    print(datetime.now())
    robot = body.robot.to_robot()
    obstacles = [obstacle.to_obstacle() for obstacle in body.obstacles]
    world = World(100, robot, obstacles)

    objectives = generate_objectives(world)
    segments = search(world, objectives)

    pathfinding_response = PathfindingResponse(
        segments=[
            PathfindingResponseSegment.from_segment(
                verbose=body.verbose, segment=segment
            )
            for segment in segments
        ]
    )

    # dump(world, segments)
    print(datetime.now())

    response = make_response(
        pathfinding_response.model_dump(mode="json"), HTTPStatus.OK
    )
    response.mimetype = "application/json"
    return response


def dump(world: World, segments: list[Segment]):
    """
    Dumps the path to a txt file for visualization.

    :param world:
    :param segments:
    :return:
    """
    map = np.array(world.grid, dtype=int)
    for obstacle in world.obstacles:
        west_x = max(obstacle.south_west.x, 0)
        east_x = min(obstacle.north_east.x + 1, world.size)
        south_y = max(obstacle.south_west.y, 0)
        north_y = min(obstacle.north_east.y + 1, world.size)

        map[west_x:east_x, south_y:north_y] = 9

    for i, s in enumerate(segments):
        for v in s.vectors:
            map[v.x, v.y] = i + 2

    a = np.rot90(map)
    np.savetxt("dump.txt", a, fmt="%d")

# 10 cells