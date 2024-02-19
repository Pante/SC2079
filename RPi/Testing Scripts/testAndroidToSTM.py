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


from Communication.android import Android, AndroidMessage
from Communication.stmMain import RaspberryPi, RPiAction

