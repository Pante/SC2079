import socket
import threading
from multiprocessing import Process, Manager
import json
from pathlib import Path
import sys
sys.path.insert(1, '/home/raspberrypi/Desktop/MDP Group 14 Repo/SC2079/RPi')
from TestingScripts.Camera_Streaming_UDP.stream_listener import StreamListener

class Task1PC:
    def __init__(self):
        # self.manager = Manager()
        self.process_PC_receive = None
        self.process_PC_stream = None
        
        self.exit = False
        self.pc_receive_thread = None
        self.stream_thread = None
        
        # self.pc_dropped = self.manager.Event()
        self.host = '192.168.14.14'
        self.port = 5000
        self.client_socket = None

        self.stream_listener = StreamListener('TestingScripts/v9_task1.pt')
        self.prev_image = None
    
    def start(self):
        try:
            self.pc_receive_thread = threading.Thread(target=self.pc_receive)
            self.stream_thread = threading.Thread(target=self.stream_start)
            self.pc_receive_thread.start()  # Receive from PC
            self.stream_thread.start()  # Start stream
        except KeyboardInterrupt:
            print("Exiting program")
        finally:
            self.disconnect()
            
        
    def stream_start(self):
        self.stream_listener.start_stream_read(
            self.on_result, self.on_disconnect,
            conf_threshold=0.65, 
            show_video=True
        )

    def on_result(self, result):
        message_content = None

        if result is not None:
            names = result.names

            if self.prev_image is None:
                # New image, can send over
                # Only if the confidence is over threshold then pass to the PC
                # TODO: Pass this data to RPI through the PC socket - Flask API
                message_content = str(result.boxes[0].conf.item()) + "," + names[int(result.boxes[0].cls[0].item())]
                self.prev_image = names[int(result.boxes[0].cls[0].item())]
                # print("FIRST: ", self.prev_image)
            elif names[int(result.boxes[0].cls[0].item())] != self.prev_image:
                # New image, can send over
                message_content = str(result.boxes[0].conf.item()) + "," + names[int(result.boxes[0].cls[0].item())]
                self.prev_image = names[int(result.boxes[0].cls[0].item())]
                # print("SECOND: ", self.prev_image)
        
        elif self.prev_image != "NONE":
            # No object detected, send "NONE" over
            # Upon capture image, if no object is detected -- "NONE", continue to wait until a object is detected (not "NONE")
            message_content = "NONE"
            self.prev_image = "NONE"

        if message_content is not None:
            print("Sending:", message_content)
            self.client_socket.send(message_content.encode('utf-8'))
    
    def on_disconnect(self):
        print("Stream disconnected, disconnect.")
        self.disconnect()
    
    def connect(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
        except OSError as e:
            print("Error in connecting to PC:", e)
            
    def disconnect(self):
        try:
            self.exit = True
            self.client_socket.shutdown(socket.SHUT_RDWR)
            self.client_socket.close()
            self.client_socket = None
            print("Disconnected from PC successfully")

        except Exception as e:
            print("Failed to disconnected from PC:", e)
        
    def pc_receive(self) -> None:
        print("PC Socket connection started successfully")
        self.connect()
        # print("Went into the receive function")
        while not self.exit:
            try:
                message_rcv = self.client_socket.recv(1024).decode('utf-8')
                if not message_rcv:
                    print("PC connection dropped")
                    break
                print("Message received from PC:", message_rcv)
            except OSError as e:
                    print("Error in sending data:", e)
                    break
        
if __name__ == '__main__':
    pcMain = Task1PC()
    pcMain.start()
    
        


