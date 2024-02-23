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
		
		# Added in
		# Last location of robot
		self.last_robot_x = 0
		self.last_robot_y = 0
		self.last_robot_direction = None
		self.latest_image = None
		self.directions = ["NORTH", "EAST", "SOUTH", "WEST"]
		self.current_direction_index = 0
		self.normalPathfinding()
		# ~ self.API_PATH = "127.0.0.1"
		# ~ self.port = 5000
		# ~ self.connected = False
	
	# Get the data from android side
	
	# Android receive side will call the populatePathFinding with it's details
	
	
	# ~ def populatePathFinding(self, populateDetails):
		
		# ~ # TODO: Receive from android side then populate all of this - initialization
		
		
		# ~ return obstacleArr, pathRobot
		
	
	def normalPathfinding(self):
		obstacleArr = []
		direction_one = Direction("SOUTH")
		image_id_1 = 1
		north_east = PathfindingPoint(x=1, y=7)
		south_west =  PathfindingPoint(x=0,y=6)
		pathObstacle =  PathfindingRequestObstacle(direction=direction_one, image_id = image_id_1, north_east = north_east, south_west = south_west)
		# Replace with path_finding_obstacle_1 and path_finding_obstacle_2 when ready
		obstacleArr.append(pathObstacle)
		
		image_id_2 = 1
		direction_two = Direction("EAST")
		north_east = PathfindingPoint(x=1, y=7)
		south_west =  PathfindingPoint(x=0,y=6)
		pathObstacle =  PathfindingRequestObstacle(direction=direction_two, image_id = image_id_2, north_east = north_east, south_west = south_west)
		obstacleArr.append(pathObstacle)
		
		robot_direction = Direction("NORTH")
		robot_north_east =  PathfindingPoint(x=1,y=1)
		robot_south_west =  PathfindingPoint(x=0,y=0)
		# Replace with current_robot_position when ready
		pathRobot =  PathfindingRequestRobot(direction = robot_direction, north_east = robot_north_east, south_west = robot_south_west)
		
		pathfindingRequest =  PathfindingRequest(obstacles=obstacleArr, robot=pathRobot)
		pathfinding_api =  PathfindingApi(api_client=self.client)
		
		response = pathfinding_api.pathfinding_post(pathfindingRequest)
		segments = response.segments
		# ~ print(segments)
		j = 1
		i = 1
		counter = 0
		for segment in segments:
			
			# ~ print("PATH ", i, ": ", segment.path.actual_instance[0])
			print("PATH ", i, ": ", segment.path.actual_instance)
			print("Segment ", i , ": " , segment.instructions)
			# ~ print(segment.instructions[0])
			print("SEGMENT NUMBER ", i)
			i = i + 1
			
			for instruction in segment.instructions:
				actual_instance = instruction.actual_instance
				inst = ""
				if hasattr(actual_instance, 'move'):
					# If have move attribute, it is a PathfindingResponseMoveInstruction
					inst = PathfindingResponseMoveInstruction(amount = actual_instance.amount, move = actual_instance.move)
					amt_to_move = inst.amount
					move_direction = inst.move.value
					# ~ print("IS MOVE: ", inst)
					print("AMOUNT TO MOVE: ", amt_to_move)
					print("MOVE DIRECTION: ", move_direction)
					# NOTE
					# Counter is to keep track the number of moves the STM32 took, used to index the path.actual_instance[counter]
					# Last coordinates for south-west is the x and y of segment.path.actual_instance[counter]
					# ~ self.last_robot_x = segment.path.actual_instance[counter].x
					# ~ self.last_robot_y = segment.path.actual_instance[counter].y
					# ~ self.last_robot_direction = segment.path.actual_instance[counter].direction
					
					counter = counter + 1
				else:
					try:
						inst = TurnInstruction(actual_instance)
					except:
						inst = MiscInstruction(actual_instance)
					
					print("Final Instruction ", inst)
					if isinstance(inst, MiscInstruction) and str(inst.value) == "CAPTURE_IMAGE":
						print("LATEST IMAGE: ", self.latest_image)
						
						if self.latest_image == "NONE":
							# No image detected, so need to wait until it's detected
						# ~ if self.latest_image == "marker":
							
							
							
							
							# ~ self.haveMarker()
							
							
						# TODO: Take in the image recognised and send it to the android
						# Since got image recognised, then no need to traverse the next segment already, so break
						# ~ if self.latest_image == "marker":
							# ~ # TODO: Have marker, need to go to the next side
							# ~ # Need to get the id of the one with the marker
							
							
							# ~ index = self.directions.index(self.last_direction)
							# ~ new_direction = (index+ 1) % len(self.directions)
							
							# ~ # CONTINUE 23/2/2024: CREATE OBJECTS TO POPULATE haveMarker()
							# ~ self.haveMarker()
						# ~ elif self.latest_image == "NONE":
							# ~ pass
						# ~ else:
							# ~ # Normal image detected, send the image_id to android and calculate new path to take based on latest x, y and direction
							# ~ self.android.send()
							
						
						
						break
					elif isinstance(inst, TurnInstruction):
						# TODO: Send instruction to the STM to turn
						inst_send = inst.value
						
						print("Sending turning instruction to stm: ", inst_send)
					else:
						# IS A MOVE INSTRUCTION
						inst_send = inst.value
						# TODO: Send instruction to the STM to move
						print("Sending move instruction to stm: ", inst_send)
						# ~ self.stm.send("MOVE")
				
			
		

	
	# Takes in 2 PathfindingRequestObstacle and one PathfindingRequestRobot objects
	def haveMarker(self, path_finding_obstacle_1, path_finding_obstacle_2, current_robot_position):
		
		# ~ instructionsArr = []
		# ~ obstacleArr = []
		# ~ counter = 0
		
		# ~ direction_one = Direction("SOUTH")
		# ~ image_id_1 = 1
		# ~ north_east = PathfindingPoint(x=1, y=7)
		# ~ south_west =  PathfindingPoint(x=0,y=6)
		# ~ pathObstacle =  PathfindingRequestObstacle(direction=direction_one, image_id = image_id_1, north_east = north_east, south_west = south_west)
		# ~ # Replace with path_finding_obstacle_1 and path_finding_obstacle_2 when ready
		# ~ obstacleArr.append(pathObstacle)
		
		# ~ image_id_2 = 1
		# ~ direction_two = Direction("EAST")
		# ~ north_east = PathfindingPoint(x=1, y=7)
		# ~ south_west =  PathfindingPoint(x=0,y=6)
		# ~ pathObstacle =  PathfindingRequestObstacle(direction=direction_two, image_id = image_id_2, north_east = north_east, south_west = south_west)
		# ~ obstacleArr.append(pathObstacle)
		
		# ~ robot_direction = Direction("NORTH")
		# ~ robot_north_east =  PathfindingPoint(x=1,y=1)
		# ~ robot_south_west =  PathfindingPoint(x=0,y=0)
		# ~ # Replace with current_robot_position when ready
		# ~ pathRobot =  PathfindingRequestRobot(direction = robot_direction, north_east = robot_north_east, south_west = robot_south_west)
		
		
		# ~ print(obstacleArr)
		
		# ~ pathfindingRequest =  PathfindingRequest(obstacles=obstacleArr, robot=pathRobot)
		# ~ pathfinding_api =  PathfindingApi(api_client=self.client)
		
		# ~ response = pathfinding_api.pathfinding_post(pathfindingRequest)
		
							

		
	def receive(self):
		pass
		
	def send(self, data):
		pass
		
		
if __name__ == '__main__':
	pcFlask = PCFlask() #init
	
	

