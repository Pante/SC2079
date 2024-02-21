import sys
import bluetooth as bt
import threading
import socket
import time
from pathlib import Path
from multiprocessing import Process, Manager
import sys
sys.path.insert(1, '/home/raspberrypi/Desktop/MDP Group 14 Repo/SC2079/RPi')
from Communication.android import Android, AndroidMessage

class BluetoothConnectionTest:

	def __init__(self):
		self.android = Android()
		self.manager = Manager()
		
		self.android_dropped = self.manager.Event()
		self.unpause = self.manager.Event()
		
		self.movement_lock = self.manager.Lock()
		
		self.process_android_receive = None
		
		
		# ~ self.ack_count = 0
		# ~ self.first_result = "temp"
		# ~ self.second_result = "temp"
		
        
	def bt_main(self):
		# ~ android = Android()

		# Connect to android
		self.android.connect()
		print("Android processess successfully started")

		self.process_android_receive = Process(target=self.android_receive)

		# Start processes
		self.process_android_receive.start() # Receive from android
		
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
				
				message: dict = json.loads(message_rcv)
				print("Message type: ", message['type'])
				print("Message value: ", message['value'])
			except OSError:
				self.android_dropped.set()
				print("Event set: Bluetooth connection dropped")

			if message_rcv is None:
				continue

if __name__ == '__main__':
	testingBluetooth = BluetoothConnectionTest() #init
	testingBluetooth.bt_main()
	threads = [] # Keeps track of the list of threads
	
	
	
	
	#thread = threading.Thread(target=testingBluetooth.bt_main)
	#threads.append(thread)
	#thread.start()
	
	# Waiting for all threads to finish
	# ~ for thread in threads:
		# ~ thread.join()
