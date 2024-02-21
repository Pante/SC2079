import pyshine as ps
# ~ from picamera import PiCamera
import picamera
from pathlib import Path
from multiprocessing import Process, Manager
import sys
sys.path.insert(1, '/home/raspberrypi/Desktop/MDP Group 14 Repo/SC2079/RPi')
from Communication.pc import PC
from Communication.android import Android, AndroidMessage
from Communication.stm import STM


class PCSocketTest:
	def __init__(self):
		self.stm = STM()
		self.android = Android()
		self.pc = PC()
		self.manager = Manager()
		self.process_pc_receive = None
		self.process_pc_stream = None
		self.process_android_receive = None
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
	
	def main(self):
		# ~ self.android.connect()
		# ~ self.stm.connect()
		self.pc.connect()
		print("PC Successfully connected through socket")
		self.process_pc_receive = Process(target=self.pc_receive)
		self.process_pc_stream = Process(target=self.stream_start)
		# ~ self.process_android_receive = Process(target=self.android_receive)
		# Start processes
		self.process_pc_receive.start() # Receive from PC
		self.process_pc_stream.start() # Start the Stream
		# ~ self.process_android_receive.start() # Receive from android
		
		userInput = 0
		while userInput < 3:
			try:
				user_input = int(input("1: Send a message, 2: Exit"))
				if user_input == 1:
					try:
						message_content = input("Enter message content: ")
						self.pc.send(message_content)
						print("message sent")
						# time.sleep(10)
					except OSError as e:
						print("Error in sending data: {e}")
				else:
					break
					# Try to send data over
					# ~ self.pc.send("Hello from RPI")
				# ~ print("RPI Sent message through successfully")

			except OSError as e:
				print("Error in sending data: {e}")
			# ~ finally:
				# ~ self.pc.disconnect()
		
	def pc_receive(self) -> None:
		print("WENT INTO RECEIVE FUNCTION")
		while True:
			# ~ message_rcv: Optional[str] = None
			try:
				message_rcv = self.pc.receive()
				print(message_rcv)
				
				split_results = message_rcv.split(",")
				confidence_level = float(split_results[0])
				object_id = split_results[1]
				
				print("OBJECT ID:" , object_id)
				
				if confidence_level > 0.75:
					if object_id == "marker":
						# TODO: Confirm is marker, send pathfindingresponse with the obstacle facing the other direction
						print("MARKER")
						# TODO: IF MARKER, CALL PATHFINDINGRESPONSE WITH OBSTACLE FACE
					else:
						# Not a marker, can just send back to relevant parties (android) - NEED TO TEST
						action_type = "TARGET_ID"
						message_content = object_id
						# TODO: Add in android when testing - UNCOMMENT IN FINAL INTEGRATION
						# ~ self.android.send(AndroidMessage(action_type, message_content))
				
				# Depending on the message type and value, pass to other processes
				# e.g. self.stm.send()
				
			except OSError as e:
				print("Error in receiving data: {e}")
				break

				
	def stream_start(self):
		StreamProps = ps.StreamProps
		StreamProps.set_Page(StreamProps,self.HTML)
		address = ('192.168.14.14',5005) # Enter your IP address 
		StreamProps.set_Mode(StreamProps,'picamera')    
		with picamera.PiCamera(resolution='640x480', framerate=30) as camera:
			output = ps.StreamOut()
			StreamProps.set_Output(StreamProps,output)
			camera.rotation = 0
			camera.start_recording(output, format='mjpeg')
			try:
				server = ps.Streamer(address, StreamProps)
				print('Server started at','http://'+address[0]+':'+str(address[1]))
				server.serve_forever()
			finally:
				camera.stop_recording()

if __name__ == '__main__':
	pc = PCSocketTest() #init
	pc.main()
	threads = [] # Keeps track of the list of threads
