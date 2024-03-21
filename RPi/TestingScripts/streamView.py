# import pyshine as ps
import socket
import sys
import time
from multiprocessing import Manager, Process
from pathlib import Path
from threading import Thread

sys.path.insert(1, "/home/raspberrypi/Desktop/MDP Group 14 Repo/SC2079/RPi")


from TestingScripts.Camera_Streaming_UDP.stream_server import StreamServer


class Task1RPI:
    def __init__(self):
        self.obstacle_dict = {}  # Obstacle Dict
        self.robot = None  # Robot
        self.prev_image = None
        # self.stm = STM()
        # self.android = Android()
        # self.android = AndroidDummy()
        # self.pc = PC()
        # self.manager = Manager()
        # self.process_stm_receive = None
        # self.process_pc_receive = None
        self.process_pc_stream = None
        # self.process_android_receive = None
        # self.android_dropped = self.manager.Event()
        self.host = "192.168.14.14"
        self.port = 5000
        self.host_time_offset = 0
        # self.conf = Configuration(host="http://192.168.14.15:5000")
        # self.client = ApiClient(configuration=self.conf)
        self.last_image = None
        self.prev_image = None
        self.STM_Stopped = False

        self.drive_speed = 90
        self.drive_angle = 25
    def initialize(self):
        try:
            # let stream server start before calling other sockets.
            self.process_pc_stream = Thread(target=self.stream_start)
            self.process_pc_stream.start()  # Start the Stream
            time.sleep(0.1)

          


           
            

        except OSError as e:
            print("Initialization failed: ", e)

    def pc_receive(self) -> None:
        while True:
            try:
                message_rcv = self.pc.receive()
                print(f"Received from PC: {message_rcv}")
                

            except OSError as e:
                print(f"Error in receiving data: {e}")
                break

    def stream_start(self):
        StreamServer().start()

   

   


if __name__ == "__main__":
    task1 = Task1RPI()  # init
    task1.initialize()
