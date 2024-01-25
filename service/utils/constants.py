from dataclasses import dataclass
from enum import Enum
from marshmallow import Schema, fields
from marshmallow_enum import EnumField

class Direction(Enum):
    NORTH = 1
    EAST = 2
    SOUTH = 3
    WEST = 4

class ConstantInstruction(Enum):
    RESET_GYROSCOPE = 1
    STOP = 2
    CAPTURE_IMAGE = 3

class Move(Enum):
    FORWARD = 1
    FORWARD_LEFT = 2
    FORWARD_RIGHT = 3
    BACKWARD = 4
    BACKWARD_LEFT = 5
    BACKWARD_RIGHT = 6

@dataclass
class MoveInstruction:
    move: Move
    amount: int

class ConstantInstructionSchema(Schema):
    instruction = EnumField(ConstantInstruction)


class MoveInstructionSchema(Schema):
    move = EnumField(Move)
    amount = fields.Int()

# Angle constants
NORTH = 0
SOUTH = 180
EAST = -90
WEST = 90

# Robot dimensions
ROBOT_W = 30
ROBOT_H = 30

# Colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (192, 192, 192)
BLUE = (50, 100, 150)
LIGHT_BLUE = (100, 255, 255)
LIGHT_RED = (255, 144, 144)
LIGHT_GREEN = (154, 247, 182)
SIMULATOR_BG = (93, 177, 222)