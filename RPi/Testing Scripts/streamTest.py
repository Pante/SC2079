from typing import Optional
from multiprocessing import Manager
import socket
import sys

import cv2
import numpy as np
import socket
import time
from threading import Thread

# Initialize the socket connection
# server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_socket.bind(('0.0.0.0', 8000))
# server_socket.listen(0)
# client_socket, addr = server_socket.accept()

class StreamTest:
    # START: Adapted from pc.py
    def __init__(self):
            self.host = ""
            self.port = 0
            self.connected = False
            self.server_socket = None
            self.client_socket = None
            
            self.model = None
            self.classes = []
            self.camera = None
        
    def connect(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print("Socket established successfully")
        
        # Binding the socket
        try:
            self.server_socket.bind((self.host, self.port))
            print("Socket binded successfully")
        except socket.error as e:
            print("Socket binding failed: %s" , str(e))
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
    # END: Adapted from pc.py

    # Function to process the PiCamera feed
    def process_camera_feed(self):
        # camera.start_preview() # Opens up the preview screen
        # camera.stop_preview() # Closes the preview screen
        while True:
            ret, frame = self.camera.read()
            if not ret:
                break

            # Preprocess the frame
            blob = cv2.dnn.blobFromImage(frame, 1/255, (416, 416), (0, 0, 0), swapRB=True, crop=False)

            # Forward pass through the YOLOv5 model
            self.model.setInput(blob)
            outputs = self.model.forward(self.model.getUnconnectedOutLayersNames())

            # Process the outputs
            boxes = []
            confidences = []
            class_ids = []
            for output in outputs:
                for detection in output:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    if confidence > 0.5:
                        center_x = int(detection[0] * frame.shape[1])
                        center_y = int(detection[1] * frame.shape[0])
                        width = int(detection[2] * frame.shape[1])
                        height = int(detection[3] * frame.shape[0])
                        left = int(center_x - width / 2)
                        top = int(center_y - height / 2)
                        boxes.append([left, top, width, height])
                        confidences.append(float(confidence))
                        class_ids.append(class_id)

            # Apply non-maximum suppression to remove overlapping bounding boxes
            indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

            # Draw the bounding boxes and labels on the frame
            for i in indices:
                i = i[0]
                box = boxes[i]
                left, top, width, height = box
                label = f'{self.classes[class_ids[i]]}: {confidences[i]:.2f}'
                cv2.rectangle(frame, (left, top), (left + width, top + height), (0, 255, 0), 2)
                cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Convert the frame to JPEG format
            _, buffer = cv2.imencode('.jpg', frame)
            frame_data = buffer.tobytes()

            # Send the frame data to the PC via the socket connection
            self.client_socket.sendall(frame_data)

        def start(self):
            # Define the YOLOv5 model and classes
            self.model = cv2.dnn.readNet('yolov5.weights', 'yolov5.cfg')
            self.classes = []
            with open('coco.names', 'r') as f:
                self.classes = [line.strip() for line in f.readlines()]

            # Initialize the PiCamera
            self.camera = cv2.VideoCapture(0)
            # Start the camera feed processing in a separate thread
            camera_thread = Thread(target=StreamTest.process_camera_feed)
            camera_thread.start()

            # Main loop to receive commands from the PC
            while True:
                command = self.client_socket.recv(1024).decode('utf-8')
                if command == 'quit':
                    break

            # Clean up the resources
            self.camera.release()
            cv2.destroyAllWindows()
            streamTest.disconnect()
            # client_socket.close()
            # server_socket.close()
    
if __name__ == '__main__':
    streamTest = StreamTest() #init
    streamTest.connect()
    streamTest.start()

# Server side (PC):
# import cv2
# import numpy as np
# import socket
# import struct

# # Create a socket
# server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_socket.bind(('localhost', 8485))  # Replace with your host and port
# server_socket.listen()

# while True:
#     client_socket, addr = server_socket.accept()
#     data = b''
#     payload_size = struct.calcsize(">L")
#     while True:
#         while len(data) < payload_size:
#             data += client_socket.recv(4096)
#         packed_msg_size = data[:payload_size]
#         data = data[payload_size:]
#         msg_size = struct.unpack(">L", packed_msg_size)[0]
#         while len(data) < msg_size:
#             data += client_socket.recv(4096)
#         frame_data = data[:msg_size]
#         data = data[msg_size:]

#         # Deserialize frame
#         frame = cv2.imdecode(np.frombuffer(frame_data, dtype='uint8'), cv2.IMREAD_COLOR)

#         # Display the resulting frame
#         cv2.imshow('Frame', frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break