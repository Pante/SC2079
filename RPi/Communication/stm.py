# from Communication.link import Link
# from Communication.configuration import SERIAL_PORT, BAUD_RATE
import sys
from pathlib import Path
from typing import Optional

import serial

sys.path.insert(1, "/home/raspberrypi/Desktop/MDP Group 14 Repo/SC2079/RPi")
from Communication.configuration import BAUD_RATE, SERIAL_PORT


class STM:

    def __init__(self):
        """
        Constructor for STMLink.
        """
        super().__init__()
        self.serial = None
        self.received = []

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
        self.serial.write(bytes(message, "utf-8"))
        print("Sent to STM32:", str(message).rstrip())

    def wait_receive(self, ticks=5000) -> Optional[str]:
        """Receive a message from STM32, utf-8 decoded

        Returns:
            Optional[str]: message received
        """
        while True:
            if self.serial.in_waiting > 0:
                return str(self.serial.read_all(), "utf-8")

    def send_cmd(self, flag, speed, angle, val):
        """Send command and wait for acknowledge."""
        cmd = flag
        if flag not in ["S", "D", "M"]:
            cmd += f"{speed}|{round(angle, 2)}|{round(val, 2)}"
        cmd += "\n"
        self.send(cmd)
