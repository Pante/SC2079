from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Tuple, Union

from flasgger import swag_from
from flask import Blueprint, request, jsonify
from marshmallow import Schema, fields, ValidationError
from marshmallow_enum import EnumField

from pathfinding.instruction_parser import MiscInstruction, TurnInstruction, Move, MoveInstruction
from pathfinding.world.world import Obstacle, Direction

# Blueprint for pathfinding routes
pathfinding_blueprint = Blueprint('pathfinding', __name__)


@pathfinding_blueprint.route('/pathfinding', methods=['POST'])
@swag_from({
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': 'true',
            'schema': {
                'id': 'Obstacle',
                'required': ['direction', 'south_west', 'north_east'],
                'properties': {
                    'direction': {
                        'type': 'string',
                        'enum': ['NORTH', 'EAST', 'SOUTH', 'WEST']
                    },
                    'south_west': {
                        'type': 'array',
                        'items': {
                            'type': 'integer'
                        },
                        'minItems': 2,
                        'maxItems': 2
                    },
                    'north_east': {
                        'type': 'array',
                        'items': {
                            'type': 'integer'
                        },
                        'minItems': 2,
                        'maxItems': 2
                    }
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Successful operation',
            'schema': {
                'id': 'ResponseBody',
                'properties': {
                    'distance': {
                        'type': 'number',
                        'format': 'float'
                    },
                    'instructions': {
                        'type': 'array',
                        'items': {
                            'oneOf': [
                                {
                                    'type': 'object',
                                    'properties': {
                                        'instruction': {
                                            'type': 'string',
                                            'enum': ['RESET_GYROSCOPE', 'STOP', 'CAPTURE_IMAGE']
                                        }
                                    },
                                    'required': ['instruction']
                                },
                                {
                                    'type': 'object',
                                    'properties': {
                                        'move': {
                                            'type': 'string',
                                            'enum': ['FORWARD', 'FORWARD_LEFT', 'FORWARD_RIGHT', 'BACKWARD',
                                                     'BACKWARD_LEFT', 'BACKWARD_RIGHT']
                                        },
                                        'amount': {
                                            'type': 'integer'
                                        }
                                    },
                                    'required': ['move', 'amount']
                                }
                            ]
                        }
                    }
                }
            }
        },
        '400': {
            'description': 'Invalid input',
        }
    }
})
def pathfinding():
    try:
        data: RequestBody = RequestBodySchema().load(request.json)
        # TODO: add actual pathfinding algorithm

    except ValidationError as err:
        return jsonify(err.messages), 400


@dataclass
class RequestBody:
    """
    Represents a pathfinding request.

    Attributes:
        obstacles (List[PathfindingRequestObstacle]): The obstacles that the pathfinding algorithm needs to avoid.
                                                      Ordering does not matter.
    """
    obstacles: [Obstacle]


@dataclass
class ObstacleSchema(Schema):
    direction = EnumField(Direction)
    south_west = fields.Tuple((fields.Int(), fields.Int()))
    north_east = fields.Tuple((fields.Int(), fields.Int()))


@dataclass
class RequestBodySchema(Schema):
    obstacles = fields.List(fields.Nested(ObstacleSchema()))


@dataclass
class ResponseBody:
    """
    Represents the response body for a pathfinding request.

    Attributes:
        distance (float): The total distance of the calculated path.
        instructions (List[Union[ConstantInstruction, MoveInstruction]]): The instructions for traversing the obstacles
            in the given request.
    """
    distance: float
    instructions: [Union[ConstantInstruction, MoveInstruction]]


class ConstantInstructionSchema(Schema):
    instruction = EnumField(ConstantInstruction)


class MoveInstructionSchema(Schema):
    move = EnumField(Move)
    amount = fields.Int()

