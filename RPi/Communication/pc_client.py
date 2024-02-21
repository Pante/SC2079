import socket
import threading
from multiprocessing import Process, Manager

class PCClient:
    def __init__(self):
        # self.manager = Manager()
        self.process_PC_receive = None
        # self.pc_dropped = self.manager.Event()
        self.host = '192.168.14.14'
        self.port = 5000
        self.client_socket = None
        
    def main(self):
       
        print("PC Socket connection started successfully")
        self.process_PC_receive = Process(target=self.pc_receive)
        self.connect()
        self.process_PC_receive.start() # Receive from PC
        user_input = 0
        while user_input < 3:
            user_input = int(input("1: Send a message, 2: Exit"))
            if user_input == 1:
                try:
                    # action_type = input("Type of action:")
                    message_content = input("Enter message content: ")
                    self.client_socket.send(message_content.encode('utf-8'))
                    print("message received from PC: ", message_content)
                    # time.sleep(10)
                except OSError as e:
                    print("Error in sending data: {e}")
            else:
                break
        
        # End connection
        self.disconnect()
        
    def connect(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
        except OSError as e:
            print("Error in connecting to PC: {e}")
            
    def disconnect(self):
        try:
            self.client_socket.shutdown(socket.SHUT_RDWR)
            self.client_socket.close()
            self.client_socket = None
            print("Disconnected from PC successfully")
        except Exception as e:
            print("Failed to disconnected from PC: %s", str(e))
        
        
    def pc_receive(self) -> None:
        print("Went into the receive function")
        while True:
            try:
                message_rcv = self.client_socket.recv(1024).decode('utf-8')
                if not message_rcv:
                    print("PC connection dropped")
                    break
                print("Message received from PC:", message_rcv)
            except OSError as e:
                    print("Error in sending data: {e}")
                    break
        
if __name__ == '__main__':
    pcClient = PCClient()
    pcClient.main()
    
        



# HOST = '192.168.14.14'  # The server's hostname or IP address
# PORT = 5000    # The port used by the server




# def receive():
#     while True:
#         text = s.recv(1024)
#         print(text.decode())

# def send():
#     while True:
#         text = input()
#         s.send(text.encode())

# def main():
#     s = socket.socket()
#     s.connect((HOST, PORT)) 

#     while True:
#         userInput = input("1. Send message, 2. Receive message, 3. Exit")
#         if userInput == 1:
#             message = input("Enter message: ")
#             send(message)
#         elif userInput == 2:
#             receive()
#         else:
#             break

# threading.Thread(target=receive).start()
# threading.Thread(target=send).start()
