# import pyshine as ps
import picamera
from pathlib import Path
from multiprocessing import Process, Manager
from threading import Thread
import time
import sys
import threading
import socket
import time
from multiprocessing import Process, Manager
sys.path.insert(1, '/home/raspberrypi/Desktop/MDP Group 14 Repo/SC2079/RPi')
from Communication.pc import PC
from Communication.android import Android, AndroidMessage
from Communication.stm import STM
from TestingScripts.Camera_Streaming_UDP.stream_server import StreamServer

# Pathfinding
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


class Task1RPI:
    def __init__(self):
        # Obstacle Array
	self.obstacleArr = []
        
        # Robot 
        self.robot = None
     
        self.prev_image = None
	self.stm = STM()
	self.android = Android()
	self.pc = PC()
	self.manager = Manager()
	self.process_stm_receive = None
	self.process_pc_receive = None
	self.process_pc_stream = None
	self.process_android_receive = None
	self.android_dropped = self.manager.Event()
	self.host = "192.168.14.14"
	self.port = 5000
	self.HTML ="""
					<html>
					<head>
					<title>PyShine Live Streaming</title>
					</head>

					<body>
					<center><h1> PyShine Live Streaming using PiCamera </h1></center>
					<center><img src="stream.mjpg" width='640' height='480' autoplay playsinline></center>
					</body>
					</html>
					"""
	self.conf = Configuration(host="http://192.168.14.13:5000")
	self.client = ApiClient(configuration=self.conf)
	self.last_image = None
	self.prev_image = None
	self.STM_Stopped = False

    def initialize(self):
        try:
            # let stream server start before calling other sockets.
            self.process_pc_stream = Thread(target=self.stream_start)
            self.process_pc_stream.start()  # Start the Stream
            time.sleep(0.1)

            self.android.connect()
            self.stm.connect()
            self.pc.connect()

            print("PC Successfully connected through socket")
            self.process_android_receive = Thread(target=self.android_receive)
            self.process_stm_receive = Thread(target=self.stm_receive)
            self.process_pc_receive = Thread(target=self.pc_receive)

            
            # Start Threads
            self.process_pc_receive.start() # Receive from PC
            self.process_android_receive.start() # Receive from android
            self.process_stm_receive.start() # Receive from PC
            
        except OSError as e:
            print("Initialization failed: ", e)
		

    def pc_receive(self) -> None:
	while True:
	    try:
		message_rcv = self.pc.receive()
		print(message_rcv)
		
		if "NONE" in message_rcv:
		    self.set_last_image("NONE")
		else:
		    split_results = message_rcv.split(",")
		    confidence_level = None
		    
		    try:
			confidence_level = float(split_results[0])
		    except ValueError:
			confidence_level = None
						
		    object_id = "NONE"
		    if len(split_results) > 1:
			    object_id = split_results[1]
		    
		    print("OBJECT ID:" , object_id)
		    
		    if confidence_level is not None:
			    if object_id == "marker":
				    print("MARKER")
				    action_type = "TARGET"
				    message_content = object_id
				    self.prev_image = object_id
				    self.set_last_image(object_id)
			    elif object_id == "NONE":
				    self.set_last_image("NONE")
			    else:
				# Not a marker, can just send back to relevant parties (android)
				print("OBJECT ID IS: ", object_id)
				try:
				    if self.prev_image == None:
					# New image detected, send to Android
					action_type = "TARGET"
					message_content = object_id
					# ~ self.android.send(AndroidMessage(action_type, message_content))
					self.prev_image = object_id
					self.set_last_image(object_id)
				    elif self.prev_image == object_id:
					# Do nothing, no need to send since the prev image is the same as current image
					self.set_last_image(object_id)
					pass
				    else:
					# The current image is new, so can send to Android
					action_type = "TARGET"
					message_content = object_id
					# ~ self.android.send(AndroidMessage(action_type, message_content))
					self.prev_image = object_id
					self.set_last_image(object_id)
				except OSError:
					self.android_dropped.set()
					print("Event set: Bluetooth connection dropped")
		    else:
			self.set_last_image("NONE")
		    # Depending on the message type and value, pass to other processes
		    # e.g. self.stm.send()
			
	    except OSError as e:
		    print(f"Error in receiving data: {e}")
		    break

	def stream_start(self):
	    StreamServer().start()

	def android_receive(self) -> None:
	    print("Went into android receive function")
	    while True:
		message_rcv = None
		try:
		    message_rcv = self.android.receive()

		    if "BEGIN" in message_rcv:
			# TODO: Begin Task 1
			self.callPathfinding() # Calculate the path

			
		    elif "OBSTACLE" in message_rcv:
			message_split = message_rcv.split(",")
			obstacle_id = message_split[1] #OBSTACLE ID
			x_axis = message_split[2] # X AXIS OF OBSTACLE
			y_axis = message_split[3] # Y AXIS OF OBSTACLE
			direction = Direction(message_split[4]) # DIRECTION OF OBSTACLE

			obstacle_south_west = PathfindingPoint(x=x_axis,y=y_axis)
			obstacle_north_east = PathfindingPoint(x=x_axis + 4,y=y_axis + 4) # TODO: Need to change +x value to new grid size
			# Need to add 4 to x and y from the south_west to get the north_east coords
			newObstacle =  PathfindingRequestObstacle(direction=direction, image_id = obstacle_id, south_west = obstacle_south_west, north_east = obstacle_north_east)
			
			if len(self.obstacleArr) == 0:
			    # Obstacle array is empty, add the new obstacle inside
			    self.obstacleArr.append(newObstacle)
			else:
			    # self.obstacleArr is not empty, check if the new Obstacle already exists. If yes, update. If no, insert.
			    for i, obstacle in enumerate(self.obstacleArr):
				if obstacle_id == self.obstacleArr[i].image_id:
				    # Obstacle exists, update values
				    self.obstacleArr[i] = newObstacle
				    break
			    else:
				# Obstacle ID does not exist in ObstacleArr, append new Obstacle inside. 
				self.obstacleArr.append(newObstacle)
				
			print("Obstacle set successfully: ", newObstacle)
			print("Number of obstacles: ", len(self.obstacleArr))
			
		    elif "ROBOT" in message_rcv:
			message_split = message_rcv.split(",")
			x_axis = message_split[1] # X AXIS OF ROBOT
			y_axis = message_split[2] # Y AXIS OF ROBOT
			robot_direction = Direction(message_split[3]) # DIRECTION OF ROBOT
			robot_south_west =  PathfindingPoint(x=x_axis,y=y_axis)
			robot_north_east =  PathfindingPoint(x=x_axis + 4,y=y_axis + 4) # TODO: Need to change +x value to new grid size
			self.robot =  PathfindingRequestRobot(direction = robot_direction, north_east = robot_north_east, south_west = robot_south_west)
			print("Robot set successfully: ", self.robot)
		    else:
			# Catch for messages with no keywords (OBSTACLE/ROBOT/BEGIN)
			print("Not a keyword, message received: ", message_rcv)
		    print("Message received from Android:", message_rcv)

	    except OSError:
		    self.android_dropped.set()
		    print("Event set: Bluetooth connection dropped")

	    if message_rcv is None:
		    continue

	def stm_receive(self) -> None:
	    msg = ""
	    while True:
		message_rcv = None
		try:
		    message_rcv = self.stm.wait_receive()
		    print("Message received from STM: ", message_rcv)
		    if "fS" in message_rcv:
			self.set_stm_stop(True) # Finished stopping, can start delay to recognise image
			print("Setting STM Stopped to true")
		    elif message_rcv[0] == "f":
			# Finished command, send to android
			message_split = message_rcv[1:].split("|") # Ignore the 'f' at the start
			cmd_speed = message_split[0]
			turning_degree = message_split[1]
			distance = message_split[2]
			
			cmd = cmd_speed[0] # Command (t/T)
			speed = cmd_speed[1:]
                    
			if turning_degree == -25:
			    # Turn left
			    if cmd == "t":
				# Backward left
				msg = "TURN,BACKWARD_LEFT"
			    elif cmd == "T":
				# Forward left
				msg = "TURN,FORWARD_LEFT"
			elif turning_degree == 25:
			    # Turn right
			     if cmd == "t":
				# Backward right
				msg = "TURN,BACKWARD_RIGHT"
			    elif cmd == "T":
				# Forward right
				msg = "TURN,FORWARD_RIGHT"
			elif turning_degree == 0:
			    if cmd == "t":
				# Backward
				msg = "MOVE," + distance + ",BACKWARD"
			    elif cmd == "T":
				# Forward
				msg = "MOVE," + distance + ",FORWARD"
			else:
			    # Unknown turning degre
			    print("Unknown turning degree")
			    msg = "No instruction"
			    continue
                    
			print("Msg: ", msg)
			try:
			    self.android.send(msg)
			    print("SENT TO ANDROID SUCCESSFULLY: ", msg)
			except OSError:
			    self.android_dropped.set()
			    print("Event set: Android dropped")

		    self.android_dropped.clear() # Clear previously set event
                    
		except OSError as e:
			print(f"Error in receiving STM data: {e}")

		if message_rcv is None:
			contiSnue


	def stop(self):
            """Stops all processes on the RPi and disconnects from Android, STM and PC"""
            self.android.disconnect()
            self.stm.disconnect()
            self.pc.disconnect()
            # TODO: Add Stream disconnect
            print("Program Ended\n")

    def reconnect_android(self):
        """
        Handles the reconnection to Android in the event of a lost connection. 
        If connection establised will wait until disconnected before taking action
        """

        print("Reconnection handler is watching\n")
        while True:
            self.android_dropped.wait() # Wait for bluetooth connection to drop with Android.
            print("Android link is down, initiating reconnect\n")

            # Kill child processes
            print("Killing Child Processes\n")
            self.process_android_receive.kill()

            # Wait for the child processes to finish
            self.process_android_receive.join()
            assert self.process_android_receive.is_alive() is False
            print("Child Processes Killed Successfully\n")

            # Clean up old sockets
            self.android.disconnect()

            # Reconnect
            self.android.connect()

            # Reinitialise Android processes
            self.process_android_receive = Process(target=self.android_receive)

            # Start previously killed processes
            self.process_android_receive.start()

            print("Android processess successfully restarted")

            message: AndroidMessage = AndroidMessage("general", "Link successfully reconnected!")
            try:
                self.android.send(message)
            except OSError:
                self.android_dropped.set()
                print("Event set: Android dropped")

            self.android_dropped.clear() # Clear previously set event

    def callPathfinding(self):
	pathfindingRequest =  PathfindingRequest(obstacles=self.obstacleArr, robot=self.robot)
	pathfinding_api =  PathfindingApi(api_client=self.client)
	response = pathfinding_api.pathfinding_post(pathfindingRequest)
	segments = response.segments
	i = 1
	j = 1
	counter = 0
		
	for i, segment in enumerate(segments):
	    print(f"On segment {i+1} of {len(segments)}:")
	    self.set_stm_stop(False) # Reset to false upon starting the new segment
	    
	    print("PATH ", i, ": ", segment.path.actual_instance)
	    print("Segment ", i , ": " , segment.instructions)
	    print("SEGMENT NUMBER ", i)
	    i = i + 1
			
	    for instruction in segment.instructions:				
		actual_instance = instruction.actual_instance
		inst = ""
		flag = ''
		angle = 0
		val = 0
			
		if hasattr(actual_instance, 'move'): # MOVE Instruction
		    inst = PathfindingResponseMoveInstruction(amount = actual_instance.amount, move = actual_instance.move)
		    move_direction = inst.move.value
		    angle = 0
		    val = inst.amount
		    print("AMOUNT TO MOVE: ", val)
		    print("MOVE DIRECTION: ", move_direction)

		    # Send instructions to stm
		    if move_direction == "FORWARD":
			    flag = 'T'
		    elif move_direction == "BACKWARD":
			    flag = 't'
			    
		else:
		    try:
			inst = TurnInstruction(actual_instance) # TURN Instruction
		    except:
			inst = MiscInstruction(actual_instance) # MISC Instruction
		    
		    # print("Final Instruction ", inst)
		    if isinstance(inst, MiscInstruction) and str(inst.value) == "CAPTURE_IMAGE":
			    flag = 'S' # STM to stop before recognising image and sending results to RPi

		    elif isinstance(inst, TurnInstruction):
			    val = 90
			    # TODO: Send instruction to the STM to turn
			    inst_send = inst.value
			    if inst.value == "FORWARD_LEFT":
				    flag = 'T'
				    angle = '-25'
			    elif inst.value == "FORWARD_RIGHT":
				    flag = 'T'
				    angle = '25'
			    elif inst.value == "BACKWARD_LEFT":
				    flag = 't'
				    angle = '-25'
			    else:
				    # BACKWARD_RIGHT
				    flag = 't'
				    angle = '25'
			
			    self.stm.send_cmd(flag, 60, angle, val)
			    time.sleep(0.2)
			
		while not self.get_stm_stop():
		    # Wait until the STM has execute all the commands and stopped (True), then wait x seconds to recognise image
		    pass
		
		print("STM stopped, recognising image...")
		# STM has stopped, recognise image - x seconds to recognise
		time.sleep(2)
		print("Image recognition delay done.")
		last_image = self.get_last_image()
		print("Last image:" , last_image)
		if last_image == 'marker':
		    msg_str = f"TARGET,{last_image},{last_image}"
		    self.android.send(msg_str)
		    print("Going next, it's MARKER")
		    continue # Perform next segment
		elif last_image == 'NONE':
		    print("Last image is NONE")
		    continue
		else:
		    # Image found, send to android.
		    msg_str = f"TARGET,{segment.image_id},{last_image}"
		    self.android.send(msg_str)
		    # Image found, break out of this and don't send anymore instructions to the STM
		    break

	def get_last_image(self) -> str:
	    print(f"Returning last_image as {self.last_image}")
	    return self.last_image
	
	def set_last_image(self, img) -> None:
	    print(f"Setting last_image as {self.last_image}")
	    self.last_image = img

	def set_stm_stop(self, val) -> None:
	    self.STM_Stopped = val
			
	def get_stm_stop(self) -> bool:
	    return self.STM_Stopped

if __name__ == '__main__':
    task1 = Task1RPI() #init
    task1.initialize()
