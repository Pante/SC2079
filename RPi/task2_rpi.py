# import pyshine as ps
import socket
import sys
import threading
import time
from multiprocessing import Manager, Process
from pathlib import Path
from threading import Thread

import picamera

sys.path.insert(1, "/home/raspberrypi/Desktop/MDP Group 14 Repo/SC2079/RPi")
from Communication.android import Android, AndroidMessage
from Communication.pc import PC
from Communication.stm import STM
from TestingScripts.Camera_Streaming_UDP.stream_server import StreamServer


class Task2RPI:
    def __init__(self):
        self.prev_image = None
        self.stm = STM()
        self.pc = PC()
        self.android = Android()
        self.manager = Manager()
        self.process_stm_receive = None
        self.process_pc_receive = None
        self.process_pc_stream = None
        self.process_android_receive = None
        self.android_dropped = self.manager.Event()
        self.host = "192.168.14.14"
        self.port = 5000
        self.last_image = None
        self.prev_image = None
        self.STM_Stopped = False
        
        self.num_obstacle = 1
        self.on_arrow_callback = None # callback that takes in a single argument, boolean is_right

        self.drive_speed = 95 # tune to balance speed with precision. kachow!
        # left and right arrow IDs
        self.LEFT_ARROW_ID = "39"
        self.RIGHT_ARROW_ID = "38"

    def initialize(self):
        try:
            # let stream server start before calling other sockets.
            self.process_pc_stream = Thread(target=self.stream_start)
            self.process_pc_stream.start()  # Start the Stream
            time.sleep(0.1)

            self.stm.connect()
            self.pc.connect()
            self.android.connect()

            self.process_android_receive = Thread(target=self.android_receive)
            self.process_stm_receive = Thread(target=self.stm_receive)
            self.process_pc_receive = Thread(target=self.pc_receive)

            # Start Threads
            self.process_pc_receive.start()  # Receive from PC
            self.process_android_receive.start()  # Receive from android
            self.process_stm_receive.start()  # Receive from PC
        except OSError as e:
            print("Initialization failed: ", e)

    def pc_receive(self) -> None:
        while True:
            try:
                message_rcv = self.pc.receive()
                print(message_rcv)

                if "NONE" in message_rcv:
                    self.set_last_image("NONE")
                else:
                    split_results = message_rcv.split(",")
                    confidence_level = None

                    try:
                        confidence_level = float(split_results[0])
                    except ValueError:
                        confidence_level = None

                    object_id = "NONE"
                    if len(split_results) > 1:
                        object_id = split_results[1]

                    print("OBJECT ID:", object_id)

                    if confidence_level is not None:
                        if object_id == "marker":
                            print(
                                "MARKER"
                            )  # When it's a marker, don't update the last_image
                            # self.prev_image = object_id
                            # self.set_last_image(object_id)
                        elif object_id == "NONE":
                            self.set_last_image("NONE")
                        else:
                            # Not a marker, can just send back to relevant parties (android)
                            print("OBJECT ID IS: ", object_id)
                            try:
                                if self.prev_image == None:
                                    # New image detected, send to Android
                                    self.prev_image = object_id
                                    self.set_last_image(object_id)
                                elif self.prev_image == object_id:
                                    # Do nothing, no need to send since the prev image is the same as current image
                                    self.set_last_image(object_id)
                                    pass
                                else:
                                    # The current image is new, so can send to Android
                                    self.prev_image = object_id
                                    self.set_last_image(object_id)
                            except OSError:
                                self.android_dropped.set()
                                print("Event set: Bluetooth connection dropped")
                    else:
                        self.set_last_image("NONE")
                    # Depending on the message type and value, pass to other processes
                    # e.g. self.stm.send()

            except OSError as e:
                print(f"Error in receiving data: {e}")
                break

    def stream_start(self):
        StreamServer().start()

    def android_receive(self) -> None:
        print("Went into android receive function")
        while True:
            message_rcv = None
            try:
                message_rcv = self.android.receive()

                if "BEGIN" in message_rcv:
                    # Begin Task 2
                    print("Message received from Android:", message_rcv)
                    self.start()

            except OSError:
                self.android_dropped.set()
                print("Event set: Bluetooth connection dropped")
            if message_rcv is None:
                continue

    def stm_receive(self) -> None:
        msg = ""
        cmd_send = ""
        while True:
            message_rcv = None
            try:
                message_rcv = self.stm.wait_receive()
                print("Message received from STM: ", message_rcv)
                # TODO: Logic for task 2

                if "fS" in message_rcv:
                    # Robot has stopped, take in latest_image then decide what to do
                    self.set_stm_stop(True)
                    if self.num_obstacle == 1:  # First Obstacle
                        if self.get_last_image() == self.RIGHT_ARROW_ID:  # RIGHT ARROW
                            print("Right arrow detected")
                            self.callback_obstacle1(True)

                        elif self.get_last_image() == self.LEFT_ARROW_ID:  # LEFT ARROW
                            print("Left arrow detected")
                            self.callback_obstacle1(False)
                        
                        else:
                            # set to trigger on next arrow found.
                            self.on_arrow_callback = self.callback_obstacle1

                    elif self.num_obstacle == 2:  # Second Obstacle
                        if self.get_last_image() == self.RIGHT_ARROW_ID:  # RIGHT ARROW
                            print("Right arrow detected")
                            self.callback_obstacle2(True)
                            
                        elif self.get_last_image() == self.LEFT_ARROW_ID:  # LEFT ARROW
                            print("Left arrow detected")
                            self.callback_obstacle2(False)
                        
                        else:
                            # set to trigger on next arrow found.
                            self.on_arrow_callback = self.callback_obstacle2

                    elif (
                        self.num_obstacle == 3
                    ):  # Finished obstacle 2, go back to carpark
                        print("Going back to carpark...")
                        # TODO: Perform set of commands to go back to the carpark
                        self.perform_carpark()

                    self.num_obstacle += 1

            except OSError as e:
                print(f"Error in receiving STM data: {e}")

            if message_rcv is None:
                continue

    # drive towards obstacle (and insert 'S' to signal camera tracking).
    def perform_toward_obstacle(self) -> None:
        self.stm.send_cmd("W", self.drive_speed, 0, 50)
        self.stm.send_cmd("S", self.drive_speed, 0, 0)
        self.stm.send_cmd("W", self.drive_speed, 0, 30)

    # drive arc for first 10x10 obstacle.
    def perform_arc1(self, is_right) -> None:
        #get initial turning angle.
        angle = 25 if is_right else -25

        self.stm.send_cmd("T", self.drive_speed, angle, 45)
        self.stm.send_cmd("T", self.drive_speed, 0, 10)
        self.stm.send_cmd("T", self.drive_speed, -angle, 105)
        self.stm.send_cmd("T", self.drive_speed, 0, 26.8)
        self.stm.send_cmd("t", self.drive_speed, -angle, 60)

    # drive arc for second 60x10 obstacle.
    def perform_arc2(self, is_right) -> None:
        #get initial turning angle.
        angle = 25 if is_right else -25

        self.stm.send_cmd("T", self.drive_speed, angle, 45)
        self.stm.send_cmd("T", self.drive_speed, 0, 10)
        self.stm.send_cmd("T", self.drive_speed, -angle, 105)
        self.stm.send_cmd("T", self.drive_speed, 0, 26.8)
        self.stm.send_cmd("t", self.drive_speed, -angle, 60)

    # set this callback it is time to detect an arrow for obstacle 1.
    def callback_obstacle1(self, is_right) -> None:
        self.perform_arc1(is_right)
        self.perform_toward_obstacle()

        self.on_arrow_callback = None # clear callback.

    # set this callback it is time to detect an arrow for obstacle 2.
    def callback_obstacle2(self, is_right) -> None:
        self.perform_arc2(is_right)

        self.on_arrow_callback = None # clear callback.
    
    # drive back to the carpark.
    def perform_carpark(self) -> None:
        pass

    def start(self):
        print("Starting program...")
        print("Sending initial commands to the STM32...")
        self.perform_toward_obstacle()

    def stop(self):
        """Stops all processes on the RPi and disconnects from Android, STM and PC"""
        self.stm.disconnect()
        self.pc.disconnect()
        self.android.disconnect()
        # TODO: Add Stream disconnect
        print("Program Ended\n")

    def get_last_image(self) -> str:
        print(f"Returning last_image as {self.last_image}")
        return self.last_image

    def set_last_image(self, img) -> None:
        print(f"Setting last_image as {img}")

        if (img == self.RIGHT_ARROW_ID or img == self.LEFT_ARROW_ID) and self.on_arrow_callback is not None:
            self.on_arrow_callback(img == self.RIGHT_ARROW_ID)

        self.last_image = img

    def set_stm_stop(self, val) -> None:
        self.STM_Stopped = val

    def get_stm_stop(self) -> bool:
        return self.STM_Stopped


if __name__ == "__main__":
    task2 = Task2RPI()  # init
    task2.initialize()
