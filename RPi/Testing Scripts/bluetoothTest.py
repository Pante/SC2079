import sys
import bluetooth as bt
import threading
import socket
import time
from pathlib import Path
from multiprocessing import Process, Manager
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))
from RPi.Communication.android import Android, AndroidMessage

class BluetoothConnectionTest:

	def __init__(self):
		#self.android = Android()
		#self.android.connect()
		print("Android processess successfully started yayay")
		
	def bt_main(self):
		android = Android()

		# Connect to android
		android.connect()
		print("Android processess successfully started")

		user_input = 0;

		while user_input < 3:
			user_input = int(input("1: Send a message, 2: Receive a message, 3: Exit"))
			if user_input == 1:
				print("HELLO")
				try:
					action_type = input("Type of action:")
					message_content = input("Enter message content: ")
					android.send(AndroidMessage(action_type, message_content))
					print("message sent")
					# time.sleep(10)
				except OSError as e:
					print("Error in sending data: {e}")
			else:
				try:
					android.receive()
				except OSError as e:
					print("Error in receiving data: {e}")

		# End the connection
		android.disconnect()

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
