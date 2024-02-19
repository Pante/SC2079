from typing import Optional
from multiprocessing import Manager
import threading
import socket
import sys
import time
import pathlib as Path
# Install pyshine
import pyshine as ps
from picamera import PiCamera
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))
from RPi.Communication.link import Link

class PC(Link):
	def __init__(self):
		self.host = "192.168.14.14"
		self.port = 12345
		self.connected = False
		self.server_socket = None
		self.client_socket = None
		# Stream on or off
		# self.streamOn = False

		# self.manager = Manager()
		# self.switchStream = self.manager.Event()
		# # For image rec
		# self.StreamProps = ps.StreamProps

		# self.HTML="""
		# <html>
		# <head>
		# <title>Pyshine Live Streaming </title>
		# </head>
		
		# <body>
		# <center><h1>  Live Image Recognition </h1></center>
		# <center><img src="stream.mjpg" width='1280' height='720' autoplay playsinline></center>
		# </body>
		# </html>
		# """

	
	def connect(self):
		self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		print("Socket established successfully")
		
		# Binding the socket
		try:
			self.server_socket.bind((self.host, self.port))
			print("Socket binded successfully")
		except socket.error as e:
			print("Socket inding failed: %s" , str(e))
			self.server_socket.close()
			sys.exit()
		
		# Establish connection to the PC
		print("Waiting for PC Connection...")
		try:
			self.server_socket.listen(128)
			self.client_socket, client_address = self.server_socket.accept()
			print("PC connected successfully from client address of %s", str(client_address))
		except socket.error as e:
			print("Error in getting server/client socket: %s", str(e))
		
		self.connect = True
		# Connect to rpi camera - TODO
		
	# Disconnect RPi from PC
	def disconnect(self):
		try:
			self.server_socket.shutdown(socket.SHUT_RDWR)
			self.client_socket.shutdown(socket.SHUT_RDWR)
			self.server_socket.close()
			self.client_socket.close()
			self.server_socket = None
			self.client_socket = None
			self.connected = False
			print("Disconnected from PC successfully")
		except Exception as e:
			print("Failed to disconnected from PC: %s", str(e))
			
	# send data to PC
	def send(self, message: str) -> None:
		try:
			message_bytes = message.encode('utf-8')
			self.client_socket.send(message.bytes)
			print("Sent: %s", str(message))
		except Exception as e:
			print("Failed to send message: %s", str(e))
			
	# receive data from PC
	def receive(self) -> Optional[str]:
		try:
			unclean_message = self.client_socket.recv(1024)
			message = unclean_message.strip().decode("utf-8")
			print("Message received from pc: %s" , str(e))
			return message
		except OSError as e:
			print("Message failed to be received: %s ", str(e))
			raise e

# TODO: TRY PYSHINE FOR STREAMING
# def camera_stream(self):
# 	while True:
# 		if(self.streamOn == False):
# 			self.streamOn = True
# 			try:
# 				with picamera.PiCamera(resolution='1280x720', framerate=5) as self.camera:
# 					self.output = ps.StreamOut()
# 					self.StreamProps.set_Output(self.StreamProps, self.output)
# 					self.camera.rotation = 0
# 					self.camera.start_recording(self.output, format='mjpeg')
# 					try:
# 						self.server = ps.Streamer(self.address, self.StreamProps)
# 						print('Server started at','http://' + self.address[0] + ':' + str(self.address[1]))
# 						self.server.serve_forever()
# 						print("Put stream to sleep")
# 						self.switchStream.wait()
# 						print("Recording Stopped")

# 					finally:
# 						self.streamOn = False       
# 						self.camera.stop_recording()
# 			except Exception as e:
# 				print("Error: %s\n", str(e))


# def camera_cap(self) -> str:
			
# 	while True:
# 		message: Optional[str] = None
# 		try:
# 			message = self.receive()
# 			if message != None:
# 				return message
# 		except Exception as e:
# 			#print("Waiting for image capture instruction")
# 			continue

# 		# if message.startswith("Result"):
# 		#     return message
            
            
# def old_camera_cap(self) -> str:
	
# 	with picamera.PiCamera(resolution='1280x720', framerate=5) as self.camera:
# 		self.output = ps.StreamOut()
# 		self.StreamProps.set_Output(self.StreamProps, self.output)
# 		self.camera.rotation = 0
# 		self.camera.start_recording(self.output, format='mjpeg')
# 		output = None
# 		try:
# 			self.server = ps.Streamer(self.address, self.StreamProps)
# 			print('Server started at','http://' + self.address[0] + ':' + str(self.address[1]))
# 			self.server.serve_forever()
# 			self.send("Capture")
# 			print("Capture")
# 			while True:
# 				message: Optional[str] = None
# 				message = self.receive()

# 				if message is None:
# 					continue
# 				output = message
# 		finally:
# 			self.camera.stop_recording()
# 			return output
