import sys
import bluetooth as bt
import threading
import socket
from multiprocessing import Process, Manager
from pathlib import Path
path_root = Path(__file__).parents[2]
sys.path.append(str(path_root))
from RPi.Communication.android import Android, AndroidMessage

# ~ def receive_data(client_socket):
	# ~ try:
		# ~ while True:
			# ~ # Receive data from the Android device.
			# ~ received_data = client_socket.recv(1024)
			# ~ if not received_data:
				# ~ break;
			# ~ print("Received data: {received_data.decode('utf-8')}")
			
			# ~ # Sending a example response back to the Android Device after receiving data
			# ~ response_data = "Hello and good morning from RPI"
			# ~ client_socket.send(response_data.encode('utf-8'))
			
	# ~ except Exception as e:
		# ~ print("Error in receive_data: {e}")
	
	# ~ finally:
		# ~ # After receiving data, close the connection and sockets.
		# ~ try:
			# ~ client_socket.shutdown(socket.SHUT_RDWR)
			# ~ client_socket.close()
			# ~ print("Client socket closed")
		# ~ except Exception as e:
			# ~ print("Error in closing client socket: {e}")

# SCRIPT RUNS FROM HERE UPON EXECUTION
android = Android()

# Establish connection.
android.connect()

# Try to send data over
# Deciding whether to send or receive data

# Initializing variables
user_input = 0
while user_input < 2:
	user_input = input("1: Send a message, 2: Receive a message, 3: Break out of loop")
	if user_input == 1:
		try:
			action_type = input("Type of action:")
			message_content = input("Enter message content: ")
			android.send(AndroidMessage(action_type, message_content))
			print("message sent")
			time.sleep(20)
			break
		except OSError as e:
			print("Error in sending data: {e}")
			# ~ print("Disconnected")
			# ~ reconnect_android()
			# ~ android.send(AndroidMessage('general', "Reconnected."))
	else:
		try:
			android.receive()
			break
		except OSError as e:
			print("Error in receiving data: {e}")

# End connection.
android.disconnect()
