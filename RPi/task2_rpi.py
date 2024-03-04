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
        self.HTML = """
            <html>
            <head>
            <title>PyShine Live Streaming</title>
            </head>

            <body>
            <center><h1> PyShine Live Streaming using PiCamera </h1></center>
            <center><img src="stream.mjpg" width='640' height='480' autoplay playsinline></center>
            </body>
            </html>
        """
        self.last_image = None
        self.prev_image = None
        self.STM_Stopped = False
        self.num_obstacle = 1

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
                        if self.get_last_image() == "38":  # RIGHT ARROW
                            # TODO: Perform set of commands to turn right
                            print("Right arrow detected")
                            # Perform Right Arc
                            self.stm.send_cmd("T", 95, 25, 45)
                            self.stm.send_cmd("T", 95, 0, 10)
                            self.stm.send_cmd("T", 95, -25, 105)
                            self.stm.send_cmd("T", 95, 0, 26.8)
                            self.stm.send_cmd("t", 95, -25, 60)
                            self.stm.send_cmd("t", 95, -25, 60)  # End of Rigt Arc

                        elif self.get_last_image() == "39":  # LEFT ARROW
                            # TODO: Perform set of commands to turn left
                            print("Left arrow detected")
                            # Perform Left Arc

                            # End of Left Arc

                        self.stm.send_cmd("W", 95, 0, 50)  # Move towards next obstacle
                        self.stm.send_cmd("W", 95, 0, 30)
                        self.stm.send_cmd(
                            "S", 95, 0, 0
                        )  # Stopped in front of next obstacle

                    elif self.num_obstacle == 2:  # Second Obstacle
                        if self.get_last_image() == "38":  # RIGHT ARROW
                            # TODO: Perform set of commands to turn right
                            print("Right arrow detected")
                        elif self.get_last_image() == "39":  # LEFT ARROW
                            # TODO: Perform set of commands to turn left
                            print("Left arrow detected")

                        # self.stm.send_cmd("W", 95, 0, 50)  # Move towards next obstacle
                        # self.stm.send_cmd("W", 95, 0, 30)
                        # self.stm.send_cmd(
                        #     "S", 95, 0, 0
                        # )  # Stopped in front of next obstacle

                    elif (
                        self.num_obstacle == 3
                    ):  # Finished obstacle 2, go back to carpark
                        print("Going back to carpark...")
                        # TODO: Perform set of commands to go back to the carpark

                    self.num_obstacle += 1

            except OSError as e:
                print(f"Error in receiving STM data: {e}")

            if message_rcv is None:
                continue

    def start(self):
        print("Starting program...")
        print("Sending initial commands to the STM32...")
        self.stm.send_cmd("W", 95, 0, 50)
        self.stm.send_cmd("W", 95, 0, 30)
        self.stm.send_cmd("S", 95, 0, 0)

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
        print(f"Setting last_image as {self.last_image}")
        self.last_image = img

    def set_stm_stop(self, val) -> None:
        self.STM_Stopped = val

    def get_stm_stop(self) -> bool:
        return self.STM_Stopped


if __name__ == "__main__":
    task2 = Task2RPI()  # init
    task2.initialize()
