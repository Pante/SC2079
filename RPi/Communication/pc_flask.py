from typing import Optional
from multiprocessing import Manager
import threading
import socket
import time
# Install pyshine
# ~ import pyshine as ps
# ~ from picamera import PiCamera
from pathlib import Path
import sys
# ~ path_root = Path(__file__).parents[2]
# ~ sys.path.append(str(path_root))
sys.path.insert(1, '/home/raspberrypi/Desktop/MDP Group 14 Repo/SC2079/RPi')
from openapi_client.configuration import Configuration
from openapi_client.api_client import ApiClient
from openapi_client.api.image_recognition_api import ImageRecognitionApi
from openapi_client.api.pathfinding_api import PathfindingApi
from openapi_client.models.direction import Direction
from openapi_client.models.error_context import ErrorContext
from openapi_client.models.error_type import ErrorType
from openapi_client.models.image_prediction_response import ImagePredictionResponse
from openapi_client.models.location import Location
from openapi_client.models.message import Message
from openapi_client.models.misc_instruction import MiscInstruction
from openapi_client.models.move import Move
from openapi_client.models.path import Path
from openapi_client.models.pathfinding_point import PathfindingPoint
from openapi_client.models.pathfinding_request import PathfindingRequest
from openapi_client.models.pathfinding_request_obstacle import PathfindingRequestObstacle
from openapi_client.models.pathfinding_request_robot import PathfindingRequestRobot
from openapi_client.models.pathfinding_response import PathfindingResponse
from openapi_client.models.pathfinding_response_move_instruction import PathfindingResponseMoveInstruction
from openapi_client.models.pathfinding_response_segment import PathfindingResponseSegment
from openapi_client.models.pathfinding_response_segment_instructions_inner import PathfindingResponseSegmentInstructionsInner
from openapi_client.models.pathfinding_vector import PathfindingVector
from openapi_client.models.turn_instruction import TurnInstruction
from openapi_client.models.validation_error_model import ValidationErrorModel

from Communication.link import Link
# ~ from openapi_client.models import PathfindingResponse, PathfindingResponseMoveInstruction, PathfindingResponseSegment, PathfindingResponseSegmentInstructionsInner, PathfindingVector

class PCFlask(Link):
	
	def __init__(self):
		self.conf = Configuration(host="http://192.168.14.13:5000")
		self.client = ApiClient(configuration=self.conf)
		
		self.testAPI()
		# ~ self.API_PATH = "127.0.0.1"
		# ~ self.port = 5000
		# ~ self.connected = False
		
	def testAPI(self):
		print("Hello")
		direction = Direction("NORTH")
		image_id = 1
		north_east = PathfindingPoint(x=1, y=1)
		south_west =  PathfindingPoint(x=4,y=4)
		pathObstacle =  PathfindingRequestObstacle(direction=direction, image_id = image_id, north_east = north_east, south_west = south_west)
		
		robot_direction = Direction("NORTH")
		robot_north_east =  PathfindingPoint(x=0,y=0)
		robot_south_west =  PathfindingPoint(x=0,y=0)
		pathRobot =  PathfindingRequestRobot(direction = robot_direction, north_east = robot_north_east, south_west = robot_south_west)
		
		obstacleArr = []
		obstacleArr.append(pathObstacle)


		
		print(obstacleArr)
		
		pathfindingRequest =  PathfindingRequest(obstacles=obstacleArr, robot=pathRobot)
		pathfinding_api =  PathfindingApi(api_client=self.client)
		
		response = pathfinding_api.pathfinding_post(pathfindingRequest)
		
		segments = response.segments
		
		print("SEGMENTS:" ,segments[0])
		
		# ~ print("RESPONSE: ", response)
		
	def receive(self):
		pass
		
	def send(self, data):
		pass
		
		
if __name__ == '__main__':
	pcFlask = PCFlask() #init
	
	

