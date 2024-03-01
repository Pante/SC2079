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
from Others.const import SYMBOL_MAPPING
#from logger import prepare_logger
from Others.configuration import API_IP, API_PORT

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
        # Initializations
        #self.logger = prepare_logger()
        self.android = Android()
        self.stm = STM()
        self.pc = PC()
        self.manager = Manager()

        # Events
        self.android_dropped = self.manager.Event()
        self.unpause = self.manager.Event()

        # Locks
        self.movement_lock = self.manager.Lock()

        # Queues
        self.android_queue = self.manager.Queue()  # Messages to send to Android
        self.rpi_action_queue = self.manager.Queue() # Actions to be performed by RPI
        self.command_queue = self.manager.Queue() # Commands from algorithm to be processed by STM
        self.path_queue = self.manager.Queue() # X,Y,d Coordinates of the robot after execution of the command

        # Create processes
        self.process_android_receive = None
        self.process_receive_stm = None
        self.process_android_sender = None
        self.process_command_execute = None
        self.process_rpi_action = None
        self.ack_flag = False

        # Lists
        self.obstacles = self.manager.dict() # Dictionary of obstacles
        self.current_location = self.manager.dict() # Current location coordinates

     
    def start(self):
        """
        Starts the RPi orchestrator
        """
        try:
            ### Start up initialization ###
            self.android.connect() # Connect via bluetooth
            self.android_queue.put(AndroidMessage('general', 'You are connected to the RPi!'))
            self.stm.connect() # Connect via serial
            self.pc.connect() # Connect via socket, rpi ip address
            self.check_api() # Checks if api of algo server is running

            # Initializing child processes
            self.process_android_receive = Process(target=self.android_receive)
            self.process_receive_stm = Process(target=self.receive_stm)
            self.process_android_sender = Process(target=self.android_sender)
            self.process_command_execute = Process(target=self.command_execute)
            self.process_rpi_action = Process(target=self.rpi_action)

            # Start processes
            self.process_android_receive.start() # Receive from android
            self.process_receive_stm.start() # Receive from STM (ACK)
            self.process_android_sender.start() # Send out information to be displayed on Android
            self.process_command_execute.start() # Commands to Send Out To STM
            self.process_rpi_action.start() # Different RPI Actions (1. Receive obstacles and send to algo)

            # self.logger.info("Child Processes started")
            print("Child processes started!\n")

            ## Start up Complete ##

            # Send success messages to Android to let you know ready to start
            self.android_queue.put(AndroidMessage('general', 'Ready to run!'))
            self.android_queue.put(AndroidMessage('mode', 'path'))
            self.reconnect_android()
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
            """Stops all processes on the RPi and disconnects from Android, STM and PC"""
            self.android.disconnect()
            self.stm.disconnect()
            self.pc.disconnect()
            print("Program Ended\n")
            #self.logger.info("Program exited!")

    def check_api(self) -> bool:
        """Check whether image recognition and algorithm API server is up and running

        Returns:
            bool: True if running, False if not.
        """
        # Check image recognition API
        url = f"http://{API_IP}:{API_PORT}/status"
        try:
            response = requests.get(url, timeout=1)
            if response.status_code == 200:
                print("API is up!\n")
                #self.logger.debug("API is up!")
                return True
            return False
        # If error, then log, and return False
        except ConnectionError:
            print("API Connection Error\n")
            #self.logger.warning("API Connection Error")
            return False
        except requests.Timeout:
            print("API Timeout\n")
            #self.logger.warning("API Timeout")
            return False
        except Exception as e:
            print("Error in api: %s\n", str(e))
            #self.logger.warning(f"API Exception: {e}")
            return False

    def reconnect_android(self):
        """
        Handles the reconnection to Android in the event of a lost connection. 
        If connection establised will wait until disconnected before taking action
        """

        print("Reconnection handler is watching\n")
        #self.logger.info("Reconnection handler is watching...")

        while True:
            
            self.android_dropped.wait() # Wait for bluetooth connection to drop with Android.
            print("Android link is down, initiating reconnect\n")

            # Kill child processes
            print("Killing Child Processes\n")
            self.process_android_sender.kill()
            self.process_android_receive.kill()

            # Wait for the child processes to finish
            self.process_android_sender.join()
            self.process_android_receive.join()
            assert self.process_android_sender.is_alive() is False
            assert self.process_android_receive.is_alive() is False
            print("Child Processes Killed Successfully\n")

            # Clean up old sockets
            self.android.disconnect()

            # Reconnect
            self.android.connect()

            # Reinitialise Android processes
            self.process_android_sender = Process(target=self.android_sender)
            self.process_android_receive = Process(target=self.android_receive)

            # Start previously killed processes
            self.process_android_sender.start()
            self.process_android_receive.start()

            print("Android processess successfully restarted")
            self.android_queue.put(AndroidMessage("general", "Link successfully reconnected!"))
            self.android_queue.put(AndroidMessage('mode', 'path'))

            self.android_dropped.clear() # Clear previously set event

    def android_receive(self) -> None:
        """
        [Child Process] Processes the messages received from Android Tablet
        """
        while True:
            message_rcv: Optional[str] = None
            try:
                message_rcv = self.android.receive()
            except OSError:
                self.android_dropped.set()
                print("Event set: Bluetooth connection dropped")
                #self.logger.debug("Event set: Android connection dropped")

            if message_rcv is None:
                continue

            # Loads message received from json string into a dictionary
            message: dict = json.loads(message_rcv)

            ## Command: Set obstacles ##
            if message['type'] == "obstacles":
                self.rpi_action_queue.put(RPiAction(**message))
                print("Rpi Action To Set Obstacles Added")
                #self.logger.debug(f"Set obstacles PiAction added to queue: {message}")

            ## Command: Start Moving ##
            elif message['type'] == "action":
                if message['value'] == "start":
                    # Check if APIs are up and running
                    if not self.check_api():
                        print("API for Algo is not up")
                        #self.logger.error("API is down! Start command aborted.")
                        self.android_queue.put(AndroidMessage('error', "API is down, start command aborted."))

                    # Commencing path following if command queue has been populated from algo
                    if not self.command_queue.empty():
                        #self.logger.info("Gryo reset!")
                        print("Gyro Reset")
                        self.stm.send("RS00")
                        
                        # Main trigger to start movement #
                        self.unpause.set() # Set event unpause
                        print("Start command received, robot will now move on path")
                        #self.logger.info("Start command received, starting robot on path!")
                        self.android_queue.put(AndroidMessage('general', 'Starting robot on path!'))
                        self.android_queue.put(AndroidMessage('status', 'running'))
                    else:
                        print("Command Queue is empty, please set obstacles")
                        #self.logger.warning("The command queue is empty, please set obstacles.")
                        self.android_queue.put(AndroidMessage("error", "Command queue is empty, did you set obstacles?"))
    
    def android_sender(self) -> None:
        """
        [Child process] Responsible for retrieving messages from android_queue and sending them over the Android link. 
        """
        while True:
            # Retrieve message from queue
            try:
                message: AndroidMessage = self.android_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            try:
                self.android.send(message)
            except OSError:
                self.android_dropped.set()
                print("Event set: Android dropped")
                #self.logger.debug("Event set: Android dropped")

    def receive_stm(self) -> None:
        """
        [Child Process] Receive acknowledgement messages from STM, and release the movement lock to allow next movement
        """
        while True:

            message: str = self.stm.receive()

            if message.startswith("ACK"):
                if self.ack_flag == False:
                    self.ack_flag = True
                    print("ACK for reset command for STM received")
                    #self.logger.debug("ACK for RS00 from STM32 received.")
                    continue
                try:
                    self.movement_lock.release()
                    print("ACK from STM received, movement lock released")
                    #self.logger.debug("ACK from STM32 received, movement lock released.")

                    cur_location = self.path_queue.get_nowait()

                    self.current_location['x'] = cur_location['x']
                    self.current_location['y'] = cur_location['y']
                    self.current_location['d'] = cur_location['d']
                    print(f"Current location: {self.current_location}")
                    #self.logger.info(f"self.current_location = {self.current_location}")
                    self.android_queue.put(AndroidMessage('location', {
                        "x": cur_location['x'],
                        "y": cur_location['y'],
                        "d": cur_location['d'],
                    }))

                except Exception:
                    print("Tried to release a released lock")
                    #self.logger.warning("Tried to release a released lock!")
            else:
                print(f"Ignore unknown message from STM: {message}")
                #self.logger.warning(f"Ignored unknown message from STM: {message}")

    def command_execute(self) -> None:
        """
        [Child Process] 
        """
        while True:
            # Retrieve next movement command
            command: str = self.command_queue.get()
            print("Wait for unpause")
            #self.logger.debug("wait for unpause")
            # Wait for unpause event to set [Main Trigger]
            try:
                print("wait for retrylock")
                #self.logger.debug("wait for retrylock")
                self.retrylock.acquire()
                self.retrylock.release()
            except: # Will go here since retrylock not instantiated yet
                print("Wait for unpause event to be set")
                #self.logger.debug("wait for unpause")
                self.unpause.wait()
            print("Wait for movelock")
            #self.logger.debug("wait for movelock")
            self.movement_lock.acquire() # Acquire lock first (needed for both moving, and capturing pictures)

            # STM32 Commands - Send straight to STM32
            stm_prefix = ("FS", "BS", "FW", "BW", "FL", "FR", "BL",
                            "BR", "TL", "TR", "A", "C", "DT", "STOP", "ZZ", "RS")
            if command.startswith(stm_prefix):
                self.stm.send(command)
                print(f"Sending to stm: {command}")
                #self.logger.debug(f"Sending to STM32: {command}")

            # Snap command
            elif command.startswith("CAP"):
                obstacle_id_with_signal = command.replace("CAP", "")

                self.rpi_action_queue.put(RPiAction(type="cap", value=obstacle_id_with_signal))

            # End of path
            elif command == "FIN":
                print(f"Currect location: {self.current_location}")
               
                self.unpause.clear()
                self.movement_lock.release()
                print("Commands queue finished, all photos completed.\n")
                #self.logger.info("Commands queue finished.")
                self.android_queue.put(AndroidMessage("general", "Commands queue finished."))
                self.android_queue.put(AndroidMessage("status", "finished"))
                self.rpi_action_queue.put(RPiAction(type="stitch", value=""))
            else:
                raise Exception(f"Unknown command: {command}")
            
    def rpi_action(self):
        """
        [Child Process] for actions to be taken by RPI
        """
        while True:
            action: RPiAction = self.rpi_action_queue.get()
            print(f"RPI action retreived from queue: {action.type} : {action.value}")
            #self.logger.debug(f"PiAction retrieved from queue: {action.type} {action.value}")

            if action.type == "obstacles":
                for obs in action.value['obstacles']:
                    self.obstacles[obs['id']] = obs
                    print(f"Obstacle {obs['id']}: {obs}")
                #self.request_algo(action.value) # Send the whole dict into request_algo, including mode
            elif action.type == "cap":
                print("capture image")
                #self.cap_and_rec(obstacle_id_with_signal=action.value)
            elif action.type == "stitch":
                print("finish")
                #self.request_stitch()

    def request_algo(self, data, car_x=1, car_y=1, car_d=0, retrying=False):
        """
        Requests for a series of commands and the path from the Algo API.
        The received commands and path are then placed in their respective queues
        """
        print("Requesting path and commands from algo server.")
        #self.logger.info("Requesting path from algo...")
        self.android_queue.put(AndroidMessage("general", "Requesting path and commands from algo server..."))
        print(f"data: {data}")
        #self.logger.info(f"data: {data}")
        body = {**data, "big_turn": "0", "robot_x": car_x,
                "robot_y": car_y, "robot_dir": car_d, "retrying": retrying}
        url = f"http://{API_IP}:{API_PORT}/path"
        response = requests.post(url, json=body)

        # Error encountered at the server, return early
        if response.status_code != 200:
            self.android_queue.put(AndroidMessage("error", "Something went wrong when requesting path and commands from Algo API."))
            print("Something went wrong when requesting path and commands from Algo API.")
            #self.logger.error("Something went wrong when requesting path from Algo API.")
            return

        # Parse response
        result = json.loads(response.content)['data']
        commands = result['commands']
        path = result['path']

        # Print commands received
        print(f"Commands received from API: {commands}")
        #self.logger.debug(f"Commands received from API: {commands}")

        # Put commands and paths into respective queues
        self.clear_queues() # clear queues first to ensure all starts empty
        for c in commands:
            self.command_queue.put(c)
        for p in path[1:]:  # ignore first element as it is the starting position of the robot
            self.path_queue.put(p)

        self.android_queue.put(AndroidMessage("general", "Commands and path received Algo API. Robot is ready to move."))
        print("Commands and path received Algo API. Robot is ready to move.")
        #self.logger.info("Commands and path received Algo API. Robot is ready to move.")
    
    def clear_queues(self):
        """Clear both command and path queues"""
        while not self.command_queue.empty():
            self.command_queue.get()
        while not self.path_queue.empty():
            self.path_queue.get()

if __name__ == "__main__":
    rpi = RaspberryPi()
    rpi.start()