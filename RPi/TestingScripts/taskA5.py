import pyshine as ps
# ~ from picamera import PiCamera
import picamera
from pathlib import Path
from multiprocessing import Process, Manager
from threading import Thread
import time
import sys
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

class TaskA5:
	def __init__(self):
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
		# Rin on 192.168.14.13, Port 5000
		self.conf = Configuration(host="http://192.168.14.13:5000")
		self.client = ApiClient(configuration=self.conf)
		self.last_image = None
		self.prev_image = None
		self.STM_Stopped = False
		
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

		
		# Start processes
		self.process_pc_receive.start() # Receive from PC
		self.process_android_receive.start() # Receive from android
		self.process_stm_receive.start() # Receive from PC
		self.normalPathfinding() # Calculate the path
		
		
	def main(self):
		
		userInput = 0
		while userInput < 3:
			try:
				user_input = int(input("1: Send a message, 2: Exit, 3. Send android"))
				if user_input == 1:
					try:
						message_content = input("Enter message content: ")
						self.pc.send(message_content)
						print("message sent")
						# time.sleep(10)
					except OSError as e:
						print("Error in sending data: {e}")
				elif user_input == 3:
					try:
						action_type = input("Type of action:")
						message_content = input("Enter message content: ")
						# ~ self.android.send(AndroidMessage(action_type, message_content))
						print("message sent")
						# time.sleep(10)
					except OSError as e:
						print("Error in sending data: {e}")
				else:
					break
					# Try to send data over
					self.pc.send("Hello from RPI")
				print("RPI Sent message through successfully")

			# ~ except OSError as e:
				# ~ print("Error in sending data: {e}")
			finally:
				self.pc.disconnect()
		
	def get_last_image(self) -> str:
		print(f"Returning last_image as {self.last_image}")
		return self.last_image
	
	def set_last_image(self, img) -> None:
		print(f"Setting last_image as {self.last_image}")
		self.last_image = img

	def pc_receive(self) -> None:
		# ~ print("WENT INTO PC RECEIVE FUNCTION")
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
							# ~ self.android.send(AndroidMessage(action_type, message_content))
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
				print("Message received from Android:", message_rcv)

			except OSError:
				self.android_dropped.set()
				print("Event set: Bluetooth connection dropped")

			if message_rcv is None:
				continue
	
	def set_stm_stop(self, val) -> None:
		self.STM_Stopped = val
			
	def get_stm_stop(self) -> bool:
		return self.STM_Stopped
		
	def stm_receive(self) -> None:
		# ~ print("Went into STM receive function")
		while True:
			message_rcv = None
			try:
				message_rcv = self.stm.wait_receive()
				# ~ print("Message received from STM:", message_rcv)
				if "fS" in message_rcv:
					self.set_stm_stop(True) # Finished stopping, can start delay to recognise image
					print("Setting STM Stopped to true")
			except OSError as e:
				print(f"Error in receiving STM data: {e}")

			if message_rcv is None:
				continue
				
	def normalPathfinding(self):
		obstacleArr = []
		
		for dir_str in ["SOUTH", "EAST", "NORTH", "WEST"]:		
			direction_one = Direction(dir_str)
			image_id_1 = 1
			south_west =  PathfindingPoint(x=20,y=20)
			north_east = PathfindingPoint(x=20,y=20)
			pathObstacle =  PathfindingRequestObstacle(direction=direction_one, image_id = image_id_1, north_east = north_east, south_west = south_west)
			obstacleArr.append(pathObstacle)
		
		robot_direction = Direction("NORTH")
		robot_south_west =  PathfindingPoint(x=19,y=0)
		robot_north_east =  PathfindingPoint(x=22,y=3)
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
		
		for i, segment in enumerate(segments):
			print(f"On segment {i+1} of {len(segments)}:")
			self.set_stm_stop(False) # Reset to false upon starting the new segment
			
			# ~ print("PATH ", i, ": ", segment.path.actual_instance[0])
			print("PATH ", i, ": ", segment.path.actual_instance)
			print("Segment ", i , ": " , segment.instructions)
			# ~ print(segment.instructions[0])
			print("SEGMENT NUMBER ", i)
			i = i + 1
			
			for instruction in segment.instructions:
				# TODO 26/2/2024: Only send the instructions after receiving acknowledgements from STM
				
				actual_instance = instruction.actual_instance
				inst = ""
				flag = ''
				angle = 0
				val = 0
				
				if hasattr(actual_instance, 'move'):
					# If have move attribute, it is a PathfindingResponseMoveInstruction
					inst = PathfindingResponseMoveInstruction(amount = actual_instance.amount, move = actual_instance.move)
					move_direction = inst.move.value
					angle = 0
					val = inst.amount
					# ~ print("IS MOVE: ", inst)
					print("AMOUNT TO MOVE: ", val)
					print("MOVE DIRECTION: ", move_direction)
					# Send instructions to stm
					if move_direction == "FORWARD":
						flag = 'T'
					elif move_direction == "BACKWARD":
						flag = 't'
						
				else:
					try:
						inst = TurnInstruction(actual_instance)
					except:
						inst = MiscInstruction(actual_instance)
					
					print("Final Instruction ", inst)
					if isinstance(inst, MiscInstruction) and str(inst.value) == "CAPTURE_IMAGE":
						flag = 'S'
						# ~ time.sleep(3) # When the CAPTURE_IMAGE command is triggered, wait for 3 seconds first to detect the image
						# ~ print("LATEST IMAGE: ", self.last_image)
						# ~ while self.last_image is "None":
							# ~ pass

						# ~ if self.last_image != 'marker':
							# ~ self.android.send(AndroidMessage('TARGET', self.last_image))
							# ~ # Image found, break out of this and don't send anymore instructions to the STM
							# ~ break

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
				# ~ self.android.send(AndroidMessage('TARGET,', segment.image_id, ",", self.last_image))
				msg_str = f"TARGET,{segment.image_id},{last_image}"
				self.android.send(msg_str)
				# ~ self.android.send('TARGET: ' + self.last_image)
				# Image found, break out of this and don't send anymore instructions to the STM
				break


if __name__ == '__main__':
	pc = TaskA5() #init
	pc.main()
	threads = [] # Keeps track of the list of threads
