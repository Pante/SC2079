from typing import Optional
import serial
# from Communication.link import Link
# from Communication.configuration import SERIAL_PORT, BAUD_RATE
import sys
from pathlib import Path
sys.path.insert(1, '/home/raspberrypi/Desktop/MDP Group 14 Repo/SC2079/RPi')
from Communication.configuration import SERIAL_PORT, BAUD_RATE
from Communication.link import Link

class STM(Link):
    """Class for communicating with STM32 microcontroller over UART serial connection.

    ### RPi to STM32
    RPi sends the following commands to the STM32.

    #### Path mode commands
    High speed forward/backward, with turning radius of `3x1`
    - `SFx`: Move forward `x` units
    - `SBx`: Move backward `x` units
    - `LF00`: Move to the forward-left location
    - `RF00`: Move to the forward-right location
    - `LB00`: Move to the backward-left location
    - `RB00`: Move to the backward-right location

    ### STM32 to RPi
    After every command received on the STM32, an acknowledgement (string: `ACK`) must be sent back to the RPi.
    This signals to the RPi that the STM32 has completed the command, and is ready for the next command.

    """

    def __init__(self):
        """
        Constructor for STMLink.
        """
        super().__init__()
        self.serial = None

    def connect(self):
        """Connect to STM32 using serial UART connection, given the serial port and the baud rate"""
        self.serial = serial.Serial(SERIAL_PORT, BAUD_RATE)
        print("Connected to STM32")
    def disconnect(self):
        """Disconnect from STM32 by closing the serial link that was opened during connect()"""
        self.serial.close()
        self.serial = None
        print("Disconnected from STM32")

    def send(self, message: str) -> None:
        """Send a message to STM32, utf-8 encoded 

        Args:
            message (str): message to send
        """
        self.serial.write(f"{message}".encode("utf-8"))
        print("Sent to STM32: %s", str(message))

    def receive(self) -> Optional[str]:
        """Receive a message from STM32, utf-8 decoded

        Returns:
            Optional[str]: message received
        """
        print(self.serial)
        message = str(self.serial.read(10).decode("utf-8", errors="ignore"))
        print("Message received from stm: %s", str(message))
        return message
    
    def stmTest(self):
        self.send("SF010")
        while True:
            message: str = self.receive()
            if message != None:
                print(message)
                break
		
