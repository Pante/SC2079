import socket
import sys
import threading
from multiprocessing import Manager
from time import time_ns, sleep
from stitching import stitch_images, add_to_stitching_dict

sys.path.insert(1, "/home/raspberrypi/Desktop/MDP Group 14 Repo/SC2079/RPi")
from TestingScripts.Camera_Streaming_UDP.stream_listener import StreamListener


class Task1PC:
    def __init__(self, config):
        self.config = config
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

        self.stream_listener = StreamListener(config.task1_weights)
        self.IMG_BLACKLIST = ["marker"]
        self.prev_image = None
        self.img_time_dict = {}
        self.time_advance_ns = 0.75e9
        self.time_threshold_ns = 1.5e9
        self.img_pending_arr = []
        self.stitching_img_dict = {}
        self.stitching_arr = []  # to store the image_id's of the image to stitch
        self.should_stitch = False
        self.stitch_len = 0 # number of images to stitch.

        self.filename = "task1" # filename of collage.
        self.start_time = time_ns()

    def start(self):
        self.pc_receive_thread = threading.Thread(target=self.pc_receive)
        self.stream_thread = threading.Thread(target=self.stream_start)
        self.pc_receive_thread.start()  # Receive from PC
        self.stream_thread.start()  # Start stream

    def stream_start(self):
        self.stream_listener.start_stream_read(
            self.on_result, self.on_disconnect, conf_threshold=self.config.conf_threshold, show_video=False
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
                add_to_stitching_dict(self.stitching_img_dict, detected_img_id, detected_conf_level, frame)
                
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
                            stitch_images(self.filename, self.stitching_arr, self.stitching_img_dict)

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
        
        timestamp_int = (timestamp - self.time_advance_ns, timestamp + self.time_threshold_ns)
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
                            stitch_images(self.filename, self.stitching_arr, self.stitching_img_dict)
                    else:
                        print("All images present, stitching now...")
                        self.stream_listener.close()
                        stitch_images(self.filename, self.stitching_arr, self.stitching_img_dict)

                if not message_rcv:
                    print("PC connection dropped")
                    break
            except OSError as e:
                print("Error in sending data:", e)
                break

def main(config):
    print("# ------------- Running Task 1, PC ---------------- #")
    print(f"You are {'out' if config.is_outdoors else 'in'}doors.")
    pcMain = Task1PC(config)
    pcMain.start()
