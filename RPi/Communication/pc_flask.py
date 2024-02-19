from typing import Optional
from multiprocessing import Manager
import threading
import socket
import time
# Install pyshine
import pyshine as ps
from picamera import PiCamera


from pathlib import Path
import sys
# ~ path_root = Path(__file__).parents[2]
# ~ sys.path.append(str(path_root))
sys.path.insert(1, '/home/raspberrypi/Desktop/MDP Group 14 Repo/SC2079/RPi')

from Communication.link import Link
from openapi_client.models import PathfindingResponse, PathfindingResponseMoveInstruction, PathfindingResponseSegment, PathfindingResponseSegmentInstructionsInner, PathfindingVector



class PC(Link):
	def __init__(self):
		self.API_PATH = "127.0.0.1"
		self.port = 5000
		self.connected = False
		
	# ~ def connect(self):
		# ~ # Send some sample data and expect a response (200)
		
		
		
	# ~ def disconnect(self):
		# Do we need this?

	def send(self, message: str) -> None:
		print("Hello")
	
	def receive(self, message: str) -> None:
		print("Hello")
