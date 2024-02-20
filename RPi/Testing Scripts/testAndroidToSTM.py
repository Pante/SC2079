import json
import queue
import time
from multiprocessing import Process, Manager
from typing import Optional
import os
#import requests
import sys
from pathlib import Path
from multiprocessing import Process, Manager
sys.path.insert(1, '/home/raspberrypi/Desktop/MDP Group 14 Repo/SC2079/RPi')

from Communication.android import Android, AndroidMessage
from Communication.stm import STM

class AndroidToSTMTest:

	def __init__(self):
		self.android = Android()
		self.stm = STM()
		self.manager = Manager()
		
		self.android_dropped = self.manager.Event()
		self.unpause = self.manager.Event()
		
		self.movement_lock = self.manager.Lock()
		
		self.process_android_receive = None
		
		# ~ self.ack_count = 0
		# ~ self.first_result = "temp"
		# ~ self.second_result = "temp"
		
        
	def start(self):
		# ~ android = Android()

		# Connect to android
		self.android.connect()
		print("Android processess successfully started")
		
		self.stm.connect()
		print("STM processes successfully started")
		
		self.process_android_receive = Process(target=self.android_receive)
		self.process_receive_stm = Process(target=self.receive_stm)


		# Start processes
		self.process_android_receive.start() # Receive from android
		self.process_receive_stm.start() # Receive from stm
		
		user_input = 0;

		while user_input < 3:
			user_input = int(input("1: Send a message, 2: Exit"))
			if user_input == 1:
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
				# ~ try:
					# ~ self.android.receive()
				# ~ except OSError as e:
					# ~ print("Error in receiving data: {e}")

		# End the connection
		self.android.disconnect()

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


if __name__ == '__main__':
	testingAndroidSTM = AndroidToSTMTest() #init
	testingAndroidSTM.start()
	
	# ~ threads = [] # Keeps track of the list of threads
	#thread = threading.Thread(target=testingBluetooth.bt_main)
	#threads.append(thread)
	#thread.start()
	
	# Waiting for all threads to finish
	# ~ for thread in threads:
		# ~ thread.join()
