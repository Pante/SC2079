import json
import queue
import time
from multiprocessing import Process, Manager
from typing import Optional
import os
#import requests
import sys
from pathlib import Path
from multiprocessing import Process, Manager

sys.path.insert(1, '/home/raspberrypi/Desktop/MDP Group 14 Repo/SC2079/RPi')

# ~ path_root = Path(__file__).parents[2]
# ~ sys.path.append(str(path_root))
from Communication.android import Android, AndroidMessage
from Communication.stm import STM
# ~ from Communication.configuration import API_IP, API_PORT

class RPiAction:
    """
    Class that represents an action that the RPi needs to take.    
    """

    def __init__(self, type, value):
        """
        :param cat: The category of the action. Can be 'info', 'mode', 'path', 'snap', 'obstacle', 'location', 'failed', 'success'
        :param value: The value of the action. Can be a string, a list of coordinates, or a list of obstacles.
        """
        self._type = type
        self._value = value

    @property
    def type(self):
        return self._type

    @property
    def value(self):
        return self._value
    
class RaspberryPi:
    """
    Class that represents the Raspberry Pi.
    """

    def __init__(self):
        """
        Initializes the Raspberry Pi.
        """
        self.stm = STM()

    def start(self):
        """
        Starts the RPi orchestrator
        """
        try:
            ### Start up initialization ###
            self.stm.connect()
            print("STM connected successfully")
            user_input = 0
            while user_input < 3:
                user_input = int(input("1: Send a message, 2: Receive a message, 3: Exit >> "))
                if user_input == 1:
                    try:
                        command_text = input("Enter command >> ")
                        # ~ REFERENCE
                        #define CMD_FORWARD_DIST_TARGET 'T'		//go forward for a target distance.
                        #define CMD_FORWARD_DIST_WITHIN 'W'		//go forward until within a certain distance.
                        #define CMD_BACKWARD_DIST_TARGET 't'	//go backward for a target distance.
                        #define CMD_BACKWARD_DIST_WITHIN 'w'	//go backward until within a certain distance.
                        self.stm.send(command_text + '\n')
                        print("message sent")
                    except OSError as e:
                        print("Error in sending data: {e}")
                else:
                    try:
                        self.stm.receive()
                    except OSError as e:
                        print("Error in receiving data: {e}")
            self.stm.stmTest()
            self.stm.disconnect()
        except KeyboardInterrupt:
            self.stop()


if __name__ == "__main__":
    rpi = RaspberryPi()
    rpi.start()
