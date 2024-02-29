import json
import os
import socket
from typing import Optional
import time
import bluetooth as bt
from pathlib import Path
import sys
# ~ path_root = Path(__file__).parents[2]
# ~ sys.path.append(str(path_root))

sys.path.insert(1, '/home/raspberrypi/Desktop/MDP Group 14 Repo/SC2079/RPi')


from Communication.link import Link

class AndroidMessage:
    """
    Class for communicating with Android tablet over Bluetooth.
    """

    def __init__(self, type: str, value: str):
        """
        Constructor for AndroidMessage.
        :param type: Type Of Message.
        :param value: Message sent.
        """
        self._type = type
        self._value = value

    @property
    def type(self):
        """
        Returns the message type.
        :return: String representation of the message type.
        """
        return self._type

    @property
    def value(self):
        """
        Returns the message as a string.
        :return: String representation of the message.
        """
        return self._value

    @property
    def jsonify(self) -> str:
        """
        Returns the message as a JSON string.
        :return: JSON string representation of the message.
        """
        return json.dumps({'type': self._type, 'value': self._value})


class Android(Link):
    """Class for communicating with Android tablet over Bluetooth connection. 

    ## General Format
    Messages between the Android app and Raspi will be in the following format:
    ```json
    {"type": "xxx", "value": "xxx"}
    ```

    The `type` field will have the following possible values:
    - `general`: general messages
    - `error`: error messages, usually in response of an invalid action
    - `location`: the current location of the robot (in Path mode)
    - `imageRec`: image recognition results
    - `mode`: the current mode of the robot (`manual` or `path`)
    - `status`: status updates of the robot (`running` or `finished`)
    - `obstacles`: list of obstacles 
    - `action`: movement-related, like starting the run

    ## Android to RPi

    #### Set Obstacles
    The contents of `obstacles` together with the configured turning radius (`configuration.py`) will be passed to the Algorithm API.
    ```json
    {
    "type": "obstacles",
    "value": {
        "obstacles": [{"x": 5, "y": 10, "id": 1, "d": 2}],
        "mode": "0"
    }
    }
    ```
    RPi will store the received commands and path and make a call to the Algorithm API

    ### Start
    Signals to the robot to start dispatching the commands (when obstacles were set).
    ```json
    {"type": "action", "value": "start"}
    ```

    If there are no commands in the queue, the RPi will respond with an error:
    ```json
    {"type": "error", "value": "Command queue is empty, did you set obstacles?"}
    ```

    ### Image Recognition 

    #### RPi to Android
    ```json
    {"type": "imageRec", "value": {"image_id": "A", "obstacle_id":  "1"}}
    ```

    ### Location Updates (RPi to Android)
    In Path mode, the robot will periodically notify Android with the updated location of the robot.
    ```json
    {"type": "location", "value": {"x": 1, "y": 1, "d": 0}}
    ```
    where `x`, `y` is the location of the robot, and `d` is its direction.



    """

    def __init__(self):
        """
        Initialize the Bluetooth connection.
        """
        # Initialize super class's init.
        super().__init__()
        self.hostId = "192.168.14.14"
        # UUID to be generated, but can just use the default one - Bryan
        self.uuid = "00001101-0000-1000-8000-00805f9b34fb" #Default but should try generated
        self.connected = False
        self.client_socket = None
        self.server_socket = None

    def connect(self):
        """
        Connect to Andriod by Bluetooth
        """
        print("Bluetooth Connection Started")
        try:
            # Make RPi discoverable by the Android tablet to complete pairing
            os.system("sudo hciconfig hci0 piscan")
            
            # START: Bluetooth socket codes
            # Initialize server socket
            #port = 1 # port 1 is commonly used, but we already specified port 1 as default when setting up RFCOMM.
            self.server_socket = bt.BluetoothSocket(bt.RFCOMM)
            self.server_socket.bind((self.hostId, bt.PORT_ANY))
            self.server_socket.listen(1)

            # Parameters
            port = self.server_socket.getsockname()[1]

            # Advertise
            bt.advertise_service(self.server_socket, "MDPGroup14 RPi", service_id=self.uuid, service_classes=[self.uuid, bt.SERIAL_PORT_CLASS], profiles=[bt.SERIAL_PORT_PROFILE])

            print("Awaiting bluetooth connection on port: %d", port)
            self.client_socket, client_address = self.server_socket.accept()
            print("Accepted connection from client address of: %s", str(client_address))
            self.connected = True
            
            # Start new thread to handle the receiving of data from Android
            #client_thread = threading.Thread(target=receive, args=(client_socket,))
            #client_thread.start()
            
			# END: Bluetooth socket codes
			
        except Exception as e:
			# Prints out the error if socket connection failed.
            print("Android socket connection failed: %s", str(e))
            self.server_socket.close()
            self.client_socket.close()

    def disconnect(self):
        """Disconnect from Android Bluetooth connection and shutdown all the sockets established"""
        try:
            print("Disconnecting bluetooth")
            # socket.shutdown is not necessary to close the connection, but is beneficial when dealing with multithreading processes. - Bryan
            self.server_socket.shutdown(socket.SHUT_RDWR)
            self.client_socket.shutdown(socket.SHUT_RDWR)
            self.client_socket.close()
            self.server_socket.close()
            self.client_socket = None
            self.server_socket = None
            self.connected = False
            print("Bluetooth has been disconnected")
        except Exception as e:
            print("Failed to disconnect bluetooth: %s", str(e))

    def send(self, message: AndroidMessage):
        """Send message to Android"""
        try:
			# Default code to send a message to Android. - Bryan
            # ~ self.client_socket.send(f"{message.jsonify}\n".encode("utf-8"))
            self.client_socket.send(f"{message}\n".encode("utf-8"))
            print("Sent to Android: %s", str(message))
            # ~ print("Sent to Android: %s", str(message.jsonify))
        except OSError as e:
            print("Message sending failed: %s", str(e))
            raise e

    def receive(self) -> Optional[str]:
        """Receive message from Android"""
        try:
            # ~ while True:
            # Default code to receive data from Android in JSON format. - Bryan
            unclean_message = self.client_socket.recv(1024)
            message = unclean_message.strip().decode("utf-8")
            # ~ print("Message received from Android: %s", str(message))
            # ~ response_data = "Message received successfully!"
            # ~ self.client_socket.send(response_data.encode('utf-8'))
            # ~ print(message)
            return message
        except OSError as e:  # connection broken, try to reconnect
            print("Message failed to be received: %s", str(e))
            raise e
        
    def repeatMessageTest(self):
        message = AndroidMessage("general", "Testing, hi from rpi")
        while True:
            time.sleep(2)
            if(self.connected):
                self.send(message)
            else:
                print("no connection")
                break
