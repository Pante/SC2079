import socket
import threading
from multiprocessing import Process, Manager
import cv2
import torch
from ultralytics import YOLO
import pyshine as ps # pip install pyshine==0.0.9
import json

class PCMainIntegrated:
    def __init__(self):
        # self.manager = Manager()
        self.process_PC_receive = None
        self.process_PC_stream = None
        
        self.pc_receive_thread = None
        self.stream_thread = None
        
        # self.pc_dropped = self.manager.Event()
        self.host = '192.168.14.14'
        self.port = 5000
        self.client_socket = None
        self.model = YOLO('v9_task1.pt')
    
    def start(self):
        # self.process_PC_receive = Process(target=self.pc_receive)
        # self.process_PC_stream = Process(target=self.stream_start)
        
        # self.process_PC_receive.start() # Receive from PC
        # self.process_PC_stream.start() # Receive from PC
        # print("PC receiving started successfully")
        # print("Stream started successfully")
        
        self.pc_receive_thread = threading.Thread(target=self.pc_receive)
        self.stream_thread = threading.Thread(target=self.stream_start)
        self.pc_receive_thread.start()  # Receive from PC
        self.stream_thread.start()  # Start stream
        
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
        
    def stream_start(self):
        cap = cv2.VideoCapture()
        cap.open("http://192.168.14.14:5005/stream.mjpg")
        prev_image = None
        while True:
            success, frame = cap.read()
            if success:
                # Perform inference
                # results = model(frame)
                results = self.model.predict(frame, save=False, imgsz=640, conf=0.1)
                names = results[0].names
                
                if len(results[0].boxes.conf) > 0:
                    print("CONFIDENCE LEVEL: ", results[0].boxes[0].conf.item())
                    print("CLASS: ", names[int(results[0].boxes[0].cls[0].item())])
                    
                    if results[0].boxes[0].conf.item() > 0.7:
                        if prev_image is None:
                            # New image, can send over
                            # Only if the confidence is > 0.7 then pass to the PC
                            # TODO: Pass this data to RPI through the PC socket - Flask API
                            message_content = str(results[0].boxes[0].conf.item()) + "," + names[int(results[0].boxes[0].cls[0].item())]
                            # self.client_socket.send(message_content.encode('utf-8'))
                            self.client_socket.send(message_content.encode('utf-8'))
                            prev_image = names[int(results[0].boxes[0].cls[0].item())]
                            print("FIRST: ", prev_image)
                        else:
                            # There is a previous image, compare the new image with the previous one
                            if names[int(results[0].boxes[0].cls[0].item())] == prev_image:
                                # Do nothing
                                pass
                            else:
                                # New image, can send over
                                message_content = str(results[0].boxes[0].conf.item()) + "," + names[int(results[0].boxes[0].cls[0].item())]
                                # self.client_socket.send(message_content.encode('utf-8'))
                                self.client_socket.send(message_content.encode('utf-8'))
                                prev_image = names[int(results[0].boxes[0].cls[0].item())]
                                print("SECOND: ", prev_image)
                else:
                    if prev_image == "NONE":
                        # Dont sent over, it's already NONE
                        pass
                    else:
                        # No obejct detected, send "NONE" over
                        # Upon capture image, if no object is detected -- "NONE", continue to wait until a object is detected (not "NONE")
                        message_content = "NONE"
                        self.client_socket.send(message_content.encode('utf-8'))
                        prev_image = "NONE"
                
                # print(boxes)
                annotated_frame = results[0].plot()
                
                # Display the resulting frame
                cv2.imshow("YOLOv8 Inference", annotated_frame)
                # cv2.imshow('YOLOv8 Object Detection', frame)

                # Break the loop on 'q' key press
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        cap.release()    
    
    
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
        print("PC Socket connection started successfully")
        self.connect()
        # print("Went into the receive function")
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
    pcMain = PCMainIntegrated()
    pcMain.start()
    
        


