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


class Task2RPI:
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
                    # TODO: Begin Task 2 - Send W command to STM?
                    

              
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
                         
			except OSError as e:
				print(f"Error in receiving STM data: {e}")

			if message_rcv is None:
				continue


	def stop(self):
            """Stops all processes on the RPi and disconnects from Android, STM and PC"""
            self.android.disconnect()
            self.stm.disconnect()
            self.pc.disconnect()
            # TODO: Add Stream disconnect
            print("Program Ended\n")
        
        
if __name__ == '__main__':
	task2 = Task2RPI() #init
	task2.initialize()