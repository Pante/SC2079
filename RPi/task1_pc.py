import json
import os
import socket
import sys
import threading
from multiprocessing import Manager, Process
from pathlib import Path
from datetime import datetime as dt
from time import time_ns, sleep
import cv2
import numpy as np

sys.path.insert(1, "/home/raspberrypi/Desktop/MDP Group 14 Repo/SC2079/RPi")
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
        self.host = "192.168.14.14"
        self.port = 5000
        self.client_socket = None

        self.stream_listener = StreamListener("v12_task1.pt")
        self.IMG_BLACKLIST = ["40", "marker"]
        self.prev_image = None
        self.img_time_dict = {}
        self.time_threshold_ns = 2.0e9
        self.img_pending_arr = []
        self.stitching_img_dict = {}
        self.stitching_arr = []  # to store the image_id's of the image to stitch
        self.should_stitch = False
        self.stitch_len = 0 # number of images to stitch.

        self.start_time = time_ns()

    def start(self):
        self.pc_receive_thread = threading.Thread(target=self.pc_receive)
        self.stream_thread = threading.Thread(target=self.stream_start)
        self.pc_receive_thread.start()  # Receive from PC
        self.stream_thread.start()  # Start stream

    def stream_start(self):
        self.stream_listener.start_stream_read(
            self.on_result, self.on_disconnect, conf_threshold=0.65, show_video=True
        )
        
    def on_result(self, result, frame):
        if result is not None:
            names = result.names
            
            for box in result.boxes:
                detected_img_id = names[int(box.cls[0].item())]
                detected_conf_level = box.conf.item()
                if detected_img_id in self.IMG_BLACKLIST:
                    continue
            
                self.prev_image = detected_img_id

                if detected_img_id not in self.stitching_img_dict or (
                    self.stitching_img_dict[detected_img_id][0] < detected_conf_level
                ):
                    # If the newly detected confidence level < current one in the dictionary, replace
                    self.stitching_img_dict[detected_img_id] = (
                        detected_conf_level,
                        frame,
                    )
                    print(f"Saw {detected_img_id} with confidence level {detected_conf_level}.")
                
                # Saving the frames into dictionaries
                cur_time = time_ns()
                old_time = cur_time
                if detected_img_id in self.img_time_dict:
                    old_time = self.img_time_dict[detected_img_id][0]
                
                self.img_time_dict[detected_img_id] = (old_time, cur_time)
                
                rem = len(self.img_pending_arr)
                if rem > 0:
                    max_overlap = 0
                    max_obstacle_id = None
                    for i, (obstacle_id, timestamp) in enumerate(self.img_pending_arr):
                        overlap = self.check_timestamp(detected_img_id, timestamp, old_time, cur_time)
                        if overlap > max_overlap:
                            max_overlap = overlap
                            max_obstacle_id = obstacle_id

                    if max_obstacle_id is not None:
                        self.match_image(max_obstacle_id, detected_img_id)
                        self.img_pending_arr.pop(i)

                        if self.should_stitch and len(self.stitching_arr) >= self.stitch_len:
                            # last image reached.
                            print("Found last image, stitching now...")
                            self.stream_listener.close()
                            self.should_stitch = False
                            stitchImages(self.stitching_arr, self.stitching_img_dict)

        elif self.prev_image != "NONE":
            # No object detected, send "NONE" over
            # Upon capture image, if no object is detected -- "NONE", continue to wait until a object is detected (not "NONE")
            self.prev_image = "NONE"

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

    def interval_overlap(self, int1, int2):
        min1, max1 = int1
        min2, max2 = int2

        return min(max1, max2) - max(min1, min2)

    def check_timestamp(self, img_id, timestamp, old_time, cur_time):
        if img_id in self.stitching_arr:
            return 0
        
        timestamp_int = (timestamp, timestamp + self.time_threshold_ns)
        comp_int = (old_time, cur_time)
        overlap = self.interval_overlap(comp_int, timestamp_int)

        return overlap
    
    def match_image(self, obstacle_id, img_id):
        print(f"Matched obstacle ID {obstacle_id} as image ID {img_id}.")
        self.stitching_arr.append(img_id)
        print(f"Images found for stitching: {len(self.stitching_arr)}")
        message_content = f"{obstacle_id},{self.stitching_img_dict[img_id][0]},{img_id}"
        print("Sending:", message_content)
        self.client_socket.send(message_content.encode("utf-8"))

    def pc_receive(self) -> None:
        print("PC Socket connection started successfully")
        self.connect()
        # print("Went into the receive function")
        while not self.exit:
            try:
                message_rcv = self.client_socket.recv(1024).decode("utf-8")
                print("Message received from PC:", message_rcv)

                if "DETECT" in message_rcv:
                    #last timestamp sent in
                    obstacle_id = message_rcv.split(",")[1]
                    timestamp = time_ns()
                    
                    max_overlap = 0
                    max_img_id = None
                    for img_id, (old_time, cur_time) in self.img_time_dict.items():
                        overlap = self.check_timestamp(img_id, timestamp, old_time, cur_time)
                        print(f"overlap: {overlap}, max overlap: {max_overlap}")
                        if overlap > 0 and overlap >= max_overlap:
                            print(f"replacing max overlap with {overlap}")
                            max_overlap = overlap
                            max_img_id = img_id
                    
                    if max_img_id is not None:
                        self.match_image(obstacle_id, max_img_id)
                        del self.img_time_dict[max_img_id]
                    else:
                        self.img_pending_arr.append((obstacle_id, timestamp))

                elif "PERFORM STITCHING" in message_rcv:
                    self.stitch_len = int(message_rcv.split(",")[1])
                    # perform stitching
                    if len(self.stitching_arr) < self.stitch_len:
                        print("Stitch request received, wait for completion...")
                        self.should_stitch = True
                        sleep(self.time_threshold_ns * 2e-9)
                        if self.should_stitch:
                            stitchImages(self.stitching_arr, self.stitching_img_dict)
                    else:
                        print("All images present, stitching now...")
                        self.stream_listener.close()
                        stitchImages(self.stitching_arr, self.stitching_img_dict)

                if not message_rcv:
                    print("PC connection dropped")
                    break
            except OSError as e:
                print("Error in sending data:", e)
                break

def stitchImages(id_arr, stitching_dict):
    col_count = 0

    blank = np.zeros((320, 320, 3), np.uint8)
    cols = []
    col_cur = []
    for id in id_arr:
        _, img = stitching_dict[id]
        img = cv2.resize(img, (320, 320))
        col_cur.append(img)
        col_count += 1

        if col_count == 2:
            col_count = 0
            cols.append(np.vstack(col_cur))
            col_cur.clear()
        # print("Image appended to list")
    
    rem = len(col_cur)
    if rem > 0 and rem < 2:
        col_cur.append(blank)
        cols.append(np.vstack(col_cur))
    canvas = np.hstack(cols)

    # Save collage and save a copy
    cv2.imwrite(f"collage_{dt.strftime(dt.now(), '%H%M%S')}.jpg", canvas)

    # Display collage
    window_name = "Collage"
    cv2.imshow(window_name, canvas)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    pcMain = Task1PC()
    pcMain.start()
