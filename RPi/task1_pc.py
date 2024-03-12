import json
import os
import socket
import sys
import threading
from multiprocessing import Manager, Process
from pathlib import Path

from time import time_ns
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

        self.stream_listener = StreamListener("v9_task2_tuneup.pt")
        self.IMG_BLACKLIST = ["40", "marker"]
        self.prev_image = None
        self.img_time_dict = {}
        self.time_threshold = -0.5e9
        self.img_pending_arr = []
        self.stitching_img_dict = {}
        self.stitching_arr = []  # to store the image_id's of the image to stitch
        self.should_stitch = False
        self.stitch_len = 0 # number of images to stitch.

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

        message_content = None
        img_id = 1
        if result is not None:
            names = result.names
            detected_img_id = names[int(result.boxes[0].cls[0].item())]
            detected_conf_level = result.boxes[0].conf.item()
            if detected_img_id in self.IMG_BLACKLIST:
                return
        
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
                old_time = self.img_time_dict[detected_img_id]
            else:
                self.img_time_dict[detected_img_id] = old_time
            
            rem = len(self.img_pending_arr)
            if rem > 0:
                for i, (obstacle_id, timestamp) in enumerate(self.img_pending_arr):
                    if self.check_timestamp(obstacle_id, detected_img_id, timestamp, old_time, cur_time):
                        self.img_pending_arr.pop(i)

                        if self.should_stitch and len(self.stitching_arr) >= self.stitch_len:
                            # last image reached.
                            print("Found last image, stitching now...")
                            self.stream_listener.close()
                            stitchImages(self.stitching_arr, self.stitching_img_dict)
                        break

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
            self.client_socket.send(bytes(f"TIME,{time_ns()}", "utf-8"))
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

    def check_timestamp(self, obstacle_id, img_id, timestamp, old_time, cur_time):
        if img_id in self.stitching_arr:
            return False
        
        old_time -= self.time_threshold
        cur_time += self.time_threshold
        print(f"Image ID {img_id}: Checking {old_time} <= {timestamp} <= {cur_time}...")
        if timestamp >= old_time and timestamp <= cur_time:
            print(f"Matched obstacle ID {obstacle_id} as image ID {img_id}.")
            self.stitching_arr.append(img_id)
            print(f"Images found for stitching: {len(self.stitching_arr)}")
            message_content = f"{obstacle_id},{self.stitching_img_dict[img_id][0]},{img_id}"
            print("Sending:", message_content)
            self.client_socket.send(message_content.encode("utf-8"))

            return True
        
        print("Not within range.")
        return False
        
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
                    obstacle_id, timestamp_str = message_rcv.split(",")[1:]
                    timestamp = int(timestamp_str.strip())
                    
                    cur_time = time_ns()
                    has_found = False
                    for img_id, old_time in self.img_time_dict.items():
                        if self.check_timestamp(obstacle_id, img_id, timestamp, old_time, cur_time):
                            has_found = True
                            del self.img_time_dict[img_id]
                            break
                    
                    if not has_found:
                        self.img_pending_arr.append((obstacle_id, timestamp))

                elif "PERFORM STITCHING" in message_rcv:
                    self.stitch_len = int(message_rcv.split(",")[1])
                    # perform stitching
                    if len(self.stitching_arr) < self.stitch_len:
                        print("Stitch request received, wait for completion...")
                        self.should_stitch = True
                    else:
                        self.stream_listener.close()
                        stitchImages(self.stitching_arr, self.stitching_img_dict)

                if not message_rcv:
                    print("PC connection dropped")
                    break
            except OSError as e:
                print("Error in sending data:", e)
                break


def archiveImages():
    imageFolder = "stitching_images"  # Change to where picam frames are saved.
    archiveFolder = (
        "stitching_archive"  # change to folder where you want to archive images.
    )

    for files in os.walk(imageFolder):
        for file in files:
            src_path = os.path.join(imageFolder, file)
            dst_path = os.path.join(archiveFolder, file)
            os.rename(src_path, dst_path)


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

    # Display collage
    cv2.imshow("Collage", canvas)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Save collage and save a copy
    cv2.imwrite("collage_task1.jpg", canvas)


if __name__ == "__main__":
    pcMain = Task1PC()
    pcMain.start()
