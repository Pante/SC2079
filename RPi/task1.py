import pyshine as ps
# ~ from picamera import PiCamera
import picamera
from pathlib import Path
import bluetooth as bt
import threading
import socket
import time
from multiprocessing import Process, Manager
import sys
sys.path.insert(1, '/home/raspberrypi/Desktop/MDP Group 14 Repo/SC2079/RPi')
from Communication.pc import PC
from Communication.android import Android, AndroidMessage
from Communication.stm import STM


class Task1Main:
	def __init__(self):
		self.stm = STM()
		self.android = Android()
		self.pc = PC()
		self.manager = Manager()
		self.process_pc_receive = None
		self.process_pc_stream = None
		self.process_android_receive = None
		
		self.android_dropped = self.manager.Event()
        self.unpause = self.manager.Event()

        # Locks
        self.movement_lock = self.manager.Lock()
		
		
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
	
	def initial(self):
		
		try:
            self.android.connect()
            message: AndroidMessage = AndroidMessage('GEN', 'Android successfully connected to the RPi')
            try:
                self.android.send(message)
            except OSError:
                self.android_dropped.set()
                print("Event set: Android dropped")
            # Connecting to the STM 
			self.stm.connect()
			print("STM connected successfully")
			
			# Connecting to the PC
			self.pc.connect()
			print("PC Successfully connected through socket")
			self.pc.send("PC connected successfully")
			
			# Starting processes - Multiprocessing:
			# Receiving messages from Android (Sockets)
			self.process_android_receive = Process(target=self.android_receive)
			# Receiving messages from PC (Sockets)
			self.process_pc_receive = Process(target=self.pc_receive)
			# Receicing stream from PC (Stream)
			self.process_pc_stream = Process(target=self.stream_start)
			# Receiving messages from STM (Serial - for Acknowledgements)
			self.process_receive_stm = Process(target=self.receive_stm)
			
			# Start processes - Multiprocessing 
			self.process_pc_receive.start() # Receive from PC
			self.process_android_receive.start() # Receive from android
			self.process_receive_stm.start() # Receive from STM
			self.process_pc_stream.start() # Start the Stream
			
			message: AndroidMessage = AndroidMessage('GEN', 'Everything is set up, ready to run!')
            try:
                self.android.send(message)
            except OSError:
                self.android_dropped.set()
                print("Event set: Android dropped")
			
		except KeyboardInterrupt:
			self.stop()
		
		
		
		
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
				
				if confidence_level > 0.7:
					if object_id == "marker":
						# TODO: Confirm is marker, send pathfindingresponse with the obstacle facing the other direction
						print("MARKER")
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

	def android_receive(self) -> None:
		while True:
			message_rcv: Optional[str] = None
			try:
				message_rcv = self.android.receive()
				print("Message received:", message_rcv)
				
				# Depending on the message type and value, pass to other processes
				# e.g. self.stm.send()
				# TODO: GET OUTPUTS TO SEND TO EACH OTHER
				# Sample
				# ~ self.stm.send("AF000")
				# ~ self.stm.send("T50|0|30\n")
				
				if message_rcv == "f":
					self.stm.send("T50|0|30\n")
				elif message_rcv == "b":
					self.stm.send("t50|0|30\n")
				elif message_rcv == "fr":
					self.stm.send("T50|25|30\n")
				elif message_rcv == "fl":
					self.stm.send("T50|-25|30\n")
				elif message_rcv == "bl":
					self.stm.send("t50|-25|30\n")
				elif message_rcv == "br":
					self.stm.send("t50|25|30\n")
				
				# ~ command_send = message_rcv + "\n"
				
				# ~ self.stm.send(command_send)
				
				# ~ message: dict = json.loads(message_rcv)
				# ~ print("Message type: ", message['type'])
				# ~ print("Message value: ", message['value'])
			except OSError:
				self.android_dropped.set()
				print("Event set: Bluetooth connection dropped")

			if message_rcv is None:
				continue


	def receive_stm(self) -> None:
			"""
			[Child Process] Receive acknowledgement messages from STM, and release the movement lock to allow next movement
			"""
			while True:
				message: str = self.stm.receive()
				# TODO: Perform actions based on STM's responses
				
				# ~ if message.startswith("ACK"):
					# ~ self.ack_count+=1
					# ~ try:
						# ~ self.movement_lock.release()
						# ~ print("ACK from STM received, movement lock released")
					# ~ except Exception:
						# ~ print("Tried to release a released lock")

					# ~ if(self.ack_count == 1):
						# ~ self.movement_lock.acquire()
						# ~ self.first_result = self.cap_and_rec("first_image")
						# ~ if(self.first_result == "38"): #right
							# ~ self.stm.send("RF000") # Increase ack to 6
						# ~ elif(self.first_result == "39"): #left
							# ~ self.stm.send("LF000")
						# ~ else: # go left by default
							 # ~ self.stm.send("LF000")

					# ~ if (self.ack_count == 2): # Ready to scan second obstacle
						# ~ self.movement_lock.acquire()
						# ~ self.second_result = self.cap_and_rec("second_image")
						# ~ print(f"Second result is: {self.second_result}") 
						# ~ if(self.second_result == "3838"): #right, right
							# ~ self.stm.send("OF000") 
						# ~ elif(self.second_result == "3939"): #left, left
							# ~ self.stm.send("MF000")
						# ~ elif(self.second_result == "3839"): #right, left
							# ~ self.stm.send("PF000")
						# ~ elif(self.second_result == "3938"): #left, right
							# ~ self.stm.send("NF000")
						# ~ else: # go left by default
							 # ~ self.stm.send("MF000")
						# ~ self.pc.send("Stitch")

					# ~ if (self.ack_count == 3):
						# ~ #self.pc.send("Stitch")
						# ~ self.ack_count = 0
						# ~ self.unpause.clear()
						# ~ message: AndroidMessage = AndroidMessage("general", "Finished run")
						# ~ try:
							# ~ self.android.send(message)
						# ~ except OSError:
							# ~ self.android_dropped.set()
							# ~ print("Event set: Android dropped")
						# ~ #self.stop()   
				# ~ else:
					# ~ print(f"Ignore unknown message from STM: {message}")


	def stop(self):
            """Stops all processes on the RPi and disconnects from Android, STM and PC"""
            self.android.disconnect()
            self.stm.disconnect()
            self.pc.disconnect()
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

if __name__ == '__main__':
	task1 = Task1Main() #init
	task1.initial()
	# ~ threads = [] # Keeps track of the list of threads
