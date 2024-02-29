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


class PCSocketTest:
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
		self.latest_image = None
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
									self.latest_image = prev_image
								elif prev_image == object_id:
									# Do nothing, no need to send since the prev image is the same as current image
									self.latest_image = prev_image
									pass
								else:
									# The current image is new, so can send to Android
									action_type = "TARGET"
									message_content = object_id
									self.android.send(AndroidMessage(action_type, message_content))
									prev_image = object_id
									self.latest_image = prev_image
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
		address = ('192.168.14.14',5005) # Enter your IP address 
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
				
	# ~ def reconnect_android(self):
		# ~ """
		# ~ Handles the reconnection to Android in the event of a lost connection. 
		# ~ If connection establised will wait until disconnected before taking action
		# ~ """
		# ~ print("Reconnection handler is watching\n")
		# ~ while True:
			
			# ~ self.android_dropped.wait() # Wait for bluetooth connection to drop with Android.
			# ~ print("Android link is down, initiating reconnect\n")

			# ~ # Kill child processes
			# ~ print("Killing Child Processes\n")
			# ~ self.process_android_receive.kill()

			# ~ # Wait for the child processes to finish
			# ~ self.process_android_receive.join()
			# ~ assert self.process_android_receive.is_alive() is False
			# ~ print("Child Processes Killed Successfully\n")

			# ~ # Clean up old sockets
			# ~ self.android.disconnect()

			# ~ # Reconnect
			# ~ self.android.connect()

			# ~ # Reinitialise Android processes
			# ~ self.process_android_receive = Thread(target=self.android_receive)

			# ~ # Start previously killed processes
			# ~ self.process_android_receive.start()

			# ~ print("Android processess successfully restarted")

			# ~ message: AndroidMessage = AndroidMessage("general", "Link successfully reconnected!")
			# ~ try:
				# ~ self.android.send(message)
			# ~ except OSError:
				# ~ self.android_dropped.set()
				# ~ print("Event set: Android dropped")

			# ~ self.android_dropped.clear() # Clear previously set event



if __name__ == '__main__':
	pc = PCSocketTest() #init
	pc.main()
	threads = [] # Keeps track of the list of threads
