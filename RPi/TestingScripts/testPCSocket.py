from pathlib import Path
from multiprocessing import Process, Manager
import sys
sys.path.insert(1, '/home/raspberrypi/Desktop/MDP Group 14 Repo/SC2079/RPi')
from Communication.pc import PC


class PCSocketTest:
	def __init__(self):
		self.pc = PC()
		self.manager = Manager()
		self.process_pc_receive = None
		host = "192.168.14.14"
		port = 5000
		self.pc = PC()
	
	def main(self):
		self.pc.connect()
		print("PC Successfully connected through socket")
		self.process_pc_receive = Process(target=self.pc_receive)

		# Start processes
		self.process_pc_receive.start() # Receive from PC
		
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
				# Depending on the message type and value, pass to other processes
				# e.g. self.stm.send()
				
				# ~ message: dict = json.loads(message_rcv)
				# ~ print("Message type: ", message['type'])
				# ~ print("Message value: ", message['value'])
			except OSError as e:
				print("Error in receiving data: {e}")
				break
				# ~ self.pc_dropped.set()
				# ~ print("Event set: Bluetooth connection dropped")

			# ~ if message_rcv is None:
				# ~ continue

if __name__ == '__main__':
	pc = PCSocketTest() #init
	pc.main()
	threads = [] # Keeps track of the list of threads
