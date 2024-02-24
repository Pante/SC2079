import pyshine as ps
# ~ from picamera import PiCamera
import picamera
from pathlib import Path
from multiprocessing import Process, Manager
from threading import Thread
import sys
sys.path.insert(1, '/home/raspberrypi/Desktop/MDP Group 14 Repo/SC2079/RPi')
from Communication.pc import PC
from Communication.android import Android, AndroidMessage
from Communication.stm import STM

class TaskA5:
	def __init__(self):
		self.prev_image = None
		self.stm = STM()
		self.android = Android()
		self.pc = PC()
		self.manager = Manager()
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
		self.android.connect()
		# ~ self.stm.connect()
		self.pc.connect()
		print("PC Successfully connected through socket")
		self.process_android_receive = Process(target=self.android_receive)
		self.process_pc_receive = Process(target=self.pc_receive)
		self.process_pc_stream = Process(target=self.stream_start)

		
		# Start processes
		self.process_pc_receive.start() # Receive from PC
		self.process_android_receive.start() # Receive from android
		
		self.process_pc_stream.start() # Start the Stream
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
						self.android.send(AndroidMessage(action_type, message_content))
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
		
	def pc_receive(self) -> None:
		print("WENT INTO PC RECEIVE FUNCTION")
		while True:
			# ~ message_rcv: Optional[str] = None
			try:
				message_rcv = self.pc.receive()
				print(message_rcv)
				
				if "NONE" in message_rcv:
					print("No image detected")
				else:
					split_results = message_rcv.split(",")
					confidence_level = float(split_results[0])
					object_id = split_results[1]
					
					print("OBJECT ID:" , object_id)
					
					if confidence_level > 0.7 and confidence_level is not None:
						if object_id == "marker":
							print("MARKER")
							action_type = "TARGET"
							message_content = object_id
							self.android.send(AndroidMessage(action_type, message_content))
							prev_image = object_id
							self.last_image = object_id
						elif object_id == "None":
							self.last_image = "None"
						else:
							print("Yes")
							# Not a marker, can just send back to relevant parties (android)
							print("OBJECT ID IS: ", object_id)
							try:
								if prev_image == None:
									# New image detected, send to Android
									action_type = "TARGET"
									message_content = object_id
									self.android.send(AndroidMessage(action_type, message_content))
									prev_image = object_id
									elf.last_image = object_id
								elif prev_image == object_id:
									# Do nothing, no need to send since the prev image is the same as current image
									elf.last_image = object_id
									pass
								else:
									# The current image is new, so can send to Android
									action_type = "TARGET"
									message_content = object_id
									self.android.send(AndroidMessage(action_type, message_content))
									prev_image = object_id
									elf.last_image = object_id
							except OSError:
								self.android_dropped.set()
								print("Event set: Bluetooth connection dropped")
							
					# Depending on the message type and value, pass to other processes
					# e.g. self.stm.send()
				
			except OSError as e:
				print("Error in receiving data: {e}")
				break

				
	def stream_start(self):
		StreamProps = ps.StreamProps
		StreamProps.set_Page(StreamProps,self.HTML)
		address = ('192.168.14.14',5005) # IP Address of RPi
		# NOTE: Port 5000 is for PC socket, 5005 is for live stream
		StreamProps.set_Mode(StreamProps,'picamera')    
		with picamera.PiCamera(resolution='640x480', framerate=30) as camera:
			output = ps.StreamOut()
			StreamProps.set_Output(StreamProps,output)
			camera.rotation = 180
			# ~ camera.color_effects = (128,128)
			camera.start_recording(output, format='mjpeg')
			try:
				server = ps.Streamer(address, StreamProps)
				print('Server started at','http://'+address[0]+':'+str(address[1]))
				server.serve_forever()
			finally:
				camera.stop_recording()

	def android_receive(self) -> None:
		print("Went into android receive function")
		while True:
			message_rcv: Optional[str] = None
			try:
				message_rcv = self.android.receive()
				print("Message received from Android:", message_rcv)
				
				# Depending on the message type and value, pass to other processes
				# e.g. self.stm.send()
				
				# ~ message: dict = json.loads(message_rcv)
				# ~ print("Message type: ", message['type'])
				# ~ print("Message value: ", message['value'])

			except OSError:
				self.android_dropped.set()
				print("Event set: Bluetooth connection dropped")

			if message_rcv is None:
				continue
				
	def normalPathfinding(self):
		obstacleArr = []
		direction_one = Direction("SOUTH")
		image_id_1 = 1
		north_east = PathfindingPoint(x=20, y=20)
		south_west =  PathfindingPoint(x=21,y=21)
		pathObstacle =  PathfindingRequestObstacle(direction=direction_one, image_id = image_id_1, north_east = north_east, south_west = south_west)
		obstacleArr.append(pathObstacle)
		
		direction_one = Direction("EAST")
		image_id_2 = 1
		north_east = PathfindingPoint(x=20, y=20)
		south_west =  PathfindingPoint(x=21,y=21)
		pathObstacle =  PathfindingRequestObstacle(direction=direction_one, image_id = image_id_2, north_east = north_east, south_west = south_west)
		obstacleArr.append(pathObstacle)
		
		direction_one = Direction("NORTH")
		image_id_3 = 1
		north_east = PathfindingPoint(x=20, y=20)
		south_west =  PathfindingPoint(x=21,y=21)
		pathObstacle =  PathfindingRequestObstacle(direction=direction_one, image_id = image_id_3, north_east = north_east, south_west = south_west)
		obstacleArr.append(pathObstacle)
		
		direction_one = Direction("WEST")
		image_id_4 = 1
		north_east = PathfindingPoint(x=20, y=20)
		south_west =  PathfindingPoint(x=21,y=21)
		pathObstacle =  PathfindingRequestObstacle(direction=direction_one, image_id = image_id_4, north_east = north_east, south_west = south_west)
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
					print("AMOUNT TO MOVE: ", amt_to_move)
					print("MOVE DIRECTION: ", move_direction)
					
					# Send instructions to stm
					if move_direction == "FORWARD":
						self.stm.send("T60|0|" + str(amt_to_move) + "\n")
					elif move_direction == "BACKWARD":
						self.stm.send("t60|0|" + str(amt_to_move) + "\n")

				else:
					try:
						inst = TurnInstruction(actual_instance)
					except:
						inst = MiscInstruction(actual_instance)
					
					print("Final Instruction ", inst)
					if isinstance(inst, MiscInstruction) and str(inst.value) == "CAPTURE_IMAGE":
						# latest.image stores the last image recognised by the image rec algo 
						# if the image rec algo doesn't detect anything, latest.image = "NONE", else, latest_image = image_id of the recognised image
						print("LATEST IMAGE: ", self.latest_image)
						while self.latest_image is None:
							pass
						
						if self.latest_image != 'marker':
							self.android.send(AndroidMessage('TARGET', self.latest_image))

					elif isinstance(inst, TurnInstruction):
						# TODO: Send instruction to the STM to turn
						if inst.value == "FORWARD_LEFT":
							self.stm.send("T60|-25|90\n")
						elif inst.value == "FORWARD_RIGHT":
							self.stm.send("T60|25|90\n")
						elif inst.value == "BACKWARD_LEFT":
							self.stm.send("t60|-25|90\n")
						else:
							# BACKWARD_RIGHT
							self.stm.send("t60|25|90\n")
						
						print("Sent turning instruction to stm: ", inst.value)
					else:
						# A MOVE instruction, pass
						pass



if __name__ == '__main__':
	pc = TaskA5() #init
	pc.main()
	threads = [] # Keeps track of the list of threads
