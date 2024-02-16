import json
import queue
import time
from multiprocessing import Process, Manager
from typing import Optional
import os
import requests
from Communication.android import Android, AndroidMessage
from Communication.stm import STM
from Communication.pc import PC
from Others.configuration import API_IP, API_PORT


class RaspberryPi:
    """
    Class that represents the Raspberry Pi.
    """

    def __init__(self):
        """
        Initializes the Raspberry Pi.
        """
        # Initializations
        self.stm = STM()
        self.pc = PC()
        self.manager = Manager()

        # Locks
        self.movement_lock = self.manager.Lock()

        # Event set
        self.unpause = self.manager.Event()

        # Queues
        self.command_queue = self.manager.Queue() # Commands from algorithm to be processed by STM
        self.path_queue = self.manager.Queue() # X,Y,d Coordinates of the robot after execution of the command

        # Create processes
        self.process_start_stream = None
        self.process_receive_stm = None
        self.process_command_execute = None

        # Lists
        self.obstacles = self.manager.dict() # Dictionary of obstacles
        self.current_location = self.manager.dict() # Current location coordinates

     
    def start(self):
        """
        Starts the RPi orchestrator
        """
        try:
            ### Start up initialization ###
            self.stm.connect() # Connect via serial
            self.pc.connect() # Connect via socket, rpi ip address
            #self.check_api() # Checks if api of algo server is running
            # self.request_algo({
            #     "obstacles": [{"x": 1, "y": 7, "id": 1, "d": 2}],
            #     "mode": "0"
            # })
            # self.request_algo({
            #     "obstacles": [{"x": 1, "y": 7, "id": 1, "d": 2}],
            #     "mode": "0"
            # })
            self.command_queue.put("CAP")

            # Initializing child processes
            self.process_start_stream = Process(target=self.pc.camera_stream)
            self.process_receive_stm = Process(target=self.receive_stm)
            self.process_command_execute = Process(target=self.command_execute)

            # Start processes
            self.process_start_stream.start()
            self.process_receive_stm.start() # Receive from STM (ACK)
            self.process_command_execute.start() # Commands to Send Out To STM

            print("Child processes started!\n")

        except KeyboardInterrupt:
            self.stop()

    def stop(self):
            """Stops all processes on the RPi and disconnects from Android, STM and PC"""
            self.stm.disconnect()
            self.pc.disconnect()
            print("Program Ended\n")
            
    def receive_stm(self) -> None:
        while True:
            message: str = self.stm.receive()

            if message.startswith("ACK"):
                try:
                    self.movement_lock.release()

                    print("ACK from STM received, movement lock released")

                except Exception:
                    print("Tried to release a released lock")
            else:
                print(f"Ignore unknown message from STM: {message}")

    def command_execute(self) -> None:
        """
        [Child Process] 
        """
        while True:
            # Retrieve next movement command
            if self.command_queue.empty():
                #print("queue empty!")
                continue
            command: str = self.command_queue.get()

            self.movement_lock.acquire() # Acquire lock first (needed for both moving, and capturing pictures)

            # STM32 Commands - Send straight to STM32
            stm_prefix = ("SF", "SB", "RF", "RB", "LF", "LB", "JF", "JB", "KF", "KB")

            if command.startswith(stm_prefix):
                #time.sleep(2)
                self.stm.send(command)
                print(f"Sending to stm: {command}")
            elif command.startswith("CAP"):
                self.cap_and_rec()
            elif command == "FIN":
                print("Finished all commands.")
                self.stop()
            else:
                raise Exception(f"Unknown command: {command}")
            

    def clear_queues(self):
        """Clear both command and path queues"""
        while not self.command_queue.empty():
            self.command_queue.get()
        while not self.path_queue.empty():
            self.path_queue.get()

    def cap_and_rec(self) -> None:
        # Capture image
    
        print(f"Get Ready To Capture Image")
       
        try:
            self.pc.send("Image Rec Start")
            results = self.pc.camera_cap() 
            print(results)
            if results == "bullseye":
                self.command_queue.put("RF090")
                self.command_queue.put("SF020")
                self.command_queue.put("LF090")
                self.command_queue.put("SB030")
                self.command_queue.put("LF090")
                self.command_queue.put("CAP")
            else:
                self.command_queue.put("FIN")
        except Exception as e:
            print("Error in sending/receiving message: %s\n", str(e))

        # release lock so that bot can continue moving
        self.movement_lock.release()

if __name__ == "__main__":
    rpi = RaspberryPi()
    rpi.start()
    rpi.unpause.wait()