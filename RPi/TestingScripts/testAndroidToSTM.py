import json
import os
import queue
import sys
import time
from multiprocessing import Manager, Process
from pathlib import Path
from typing import Optional

sys.path.insert(1, "/home/raspberrypi/Desktop/MDP Group 14 Repo/SC2079/RPi")

from Communication.android import Android, AndroidMessage
from Communication.stm import STM


class AndroidToSTMTest:
    def __init__(self):
        self.android = Android()
        self.stm = STM()
        self.manager = Manager()

        self.android_dropped = self.manager.Event()
        self.unpause = self.manager.Event()

        self.movement_lock = self.manager.Lock()

        self.process_android_receive = None

    def start(self):
        self.android.connect()
        print("Android processes successfully started")

        self.stm.connect()
        print("STM processes successfully started")

        self.process_android_receive = Process(target=self.android_receive)
        self.process_receive_stm = Process(target=self.receive_stm)

        self.process_android_receive.start()  # Receive from android
        self.process_receive_stm.start()  # Receive from stm

        user_input = 0

        while user_input < 3:
            user_input = int(input("1: Send a message, 2: Exit"))
            if user_input == 1:
                try:
                    action_type = input("Type of action:")
                    message_content = input("Enter message content: ")
                    self.android.send(AndroidMessage(action_type, message_content))
                    print("message sent")
                except OSError as e:
                    print(f"Error in sending data: {e}")
            else:
                break

        self.android.disconnect()

    def android_receive(self) -> None:
        while True:
            message_rcv: Optional[str] = None
            try:
                message_rcv = self.android.receive()
                print("Message received:", message_rcv)

                if message_rcv == "f":
                    self.stm.send_cmd("T", 60, 0, 20)
                elif message_rcv == "b":
                    self.stm.send_cmd("t", 60, 0, 20)
                elif message_rcv == "fr":
                    self.stm.send_cmd("T", 60, 25, 90)
                elif message_rcv == "fl":
                    self.stm.send_cmd("T", 60, -25, 90)
                elif message_rcv == "bl":
                    self.stm.send_cmd("t", 60, -25, 90)
                elif message_rcv == "br":
                    self.stm.send_cmd("t", 60, 25, 90)

            except OSError:
                self.android_dropped.set()
                print("Event set: Bluetooth connection dropped")

            if message_rcv is None:
                continue

    def receive_stm(self) -> None:
        while True:
            message_rcv = self.stm.wait_receive()
            print(message_rcv)
            if message_rcv[0] == "f":
                print("message received:", message_rcv)
                # Finished command, send to android
                message_split = message_rcv[1:].split(
                    "|"
                )  # Ignore the 'f' at the start

                for m in message_split:
                    print(m)

                cmd_speed = message_split[0]
                turning_degree = message_split[1]
                distance = message_split[2].strip()

                cmd = cmd_speed[0]  # Command (t/T)
                speed = cmd_speed[1:]

                print("Cmd = " + cmd)
                print("Turning degree = " + turning_degree)
                print("Distance = " + distance)

                if turning_degree == "-25":
                    # Turn left
                    if "t" in cmd:
                        # Backward left
                        msg = "TURN,BACKWARD_LEFT,0"
                    elif "T" in cmd:
                        # Forward left
                        msg = "TURN,FORWARD_LEFT,0"
                elif turning_degree == "25":
                    # Turn right
                    if "t" in cmd:
                        # Backward right
                        msg = "TURN,BACKWARD_RIGHT,0"
                    elif "T" in cmd:
                        # Forward right
                        msg = "TURN,FORWARD_RIGHT,0"
                elif turning_degree == "0":
                    if "t" in cmd:
                        # Backward
                        msg = "MOVE,BACKWARD," + distance
                    elif "T" in cmd:
                        # Forward
                        msg = "MOVE,FORWARD," + distance
                else:
                    # Unknown turning degree
                    print("Unknown turning degree")
                    msg = "No instruction"

                print("Msg: ", msg)
                try:
                    self.android.send(msg)
                    print("SENT TO ANDROID SUCCESSFULLY: ", msg)
                except OSError:
                    self.android_dropped.set()
                    print("Event set: Android dropped")

                self.android_dropped.clear()  # Clear previously set event


if __name__ == "__main__":
    testingAndroidSTM = AndroidToSTMTest()  # init
    testingAndroidSTM.start()
