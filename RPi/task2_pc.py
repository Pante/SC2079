import socket
import sys
import threading
from multiprocessing import Manager
from stitching import stitch_images, add_to_stitching_dict

sys.path.insert(1, "/home/raspberrypi/Desktop/MDP Group 14 Repo/SC2079/RPi")
from TestingScripts.Camera_Streaming_UDP.stream_listener import StreamListener


class Task2PC:
    def __init__(self, config):
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
        print(f"! -- initialising weights file: {config.task2_weights}....")
        self.stream_listener = StreamListener(config.task2_weights)

        self.stitching_arr = []
        self.stitching_dict = {}
        self.filename = "task2"

        self.obstacle_id = 1
        self.obstacle_img_id = None

        # left and right arrow IDs
        self.LEFT_ARROW_ID = "39"
        self.RIGHT_ARROW_ID = "38"

    def start(self):
        self.pc_receive_thread = threading.Thread(target=self.pc_receive)
        self.stream_thread = threading.Thread(target=self.stream_start)
        self.pc_receive_thread.start()  # Receive from PC
        self.stream_thread.start()  # Start stream

    def stream_start(self):
        self.stream_listener.start_stream_read(
            self.on_result, self.on_disconnect, conf_threshold=0.65, show_video=False
        )

    def on_result(self, result, frame):
        message_content = None

        if result is not None:
            conf_level = result.boxes[0].conf.item()
            img_id = result.names[int(result.boxes[0].cls[0].item())]

            if img_id not in [self.LEFT_ARROW_ID, self.RIGHT_ARROW_ID]:
                print(f"Detected invalid image {img_id}, skipping...")
                return
            
            if self.obstacle_img_id is None:
                # Detected a different image, send over.
                message_content = f"{conf_level},{img_id}"
                self.obstacle_img_id = img_id
            
            if img_id == self.obstacle_img_id:
                add_to_stitching_dict(self.stitching_dict, self.obstacle_id, conf_level, frame)

        if message_content is not None:
            print("Sending:", message_content)
            self.client_socket.send(message_content.encode("utf-8"))

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
                message_rcv = self.client_socket.recv(1024).decode("utf-8")
                if not message_rcv:
                    print("PC connection dropped")
                    break
                print("Message received from PC:", message_rcv)

                if "SEEN" in message_rcv:
                    self.obstacle_id += 1
                    self.obstacle_img_id = None

                elif "STITCH" in message_rcv:
                    stitch_images([1, 2], self.stitching_dict, filename=self.filename)
            except OSError as e:
                print("Error in sending data:", e)
                break


def main(config):
    print("# ------------- Running Task 2, PC ---------------- #")
    print(f"You are {'out' if config.is_outdoors else 'in'}doors.")
    pcMain = Task2PC(config)
    pcMain.start()
