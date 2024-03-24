# import pyshine as ps
import socket
import math
import sys
import time
from multiprocessing import Manager, Process
from pathlib import Path
from threading import Thread, Lock
from random import randint

sys.path.insert(1, "/home/raspberrypi/Desktop/MDP Group 14 Repo/SC2079/RPi")
from Communication.android import Android, AndroidDummy
from Communication.pc import PC
from Communication.stm import STM
from TestingScripts.Camera_Streaming_UDP.stream_server import StreamServer

def sin_deg(angle):
    return math.sin(angle * math.pi / 180)
def cos_deg(angle):
    return math.cos(angle * math.pi / 180)

class Task2RPI:
    def __init__(self):
        self.prev_image = None
        self.stm = STM()
        self.pc = PC()
        # self.android = Android()
        self.android = AndroidDummy()
        self.manager = Manager()
        self.process_stm_receive = None
        self.process_pc_receive = None
        self.process_pc_stream = None
        self.process_android_receive = None
        self.android_dropped = self.manager.Event()
        self.host = "192.168.14.14"
        self.port = 5000

        self.lock = Lock()
        self.last_image = None
        self.prev_image = None

        self.num_obstacle = 1
        self.is_right1 = False # track whether first obstacle was a left or right turn
        self.is_right2 = False # track whether second obstacle was a left or right turn
        self.done_obstacle2 = False # track whether second arrow was seen

        self.on_arrow_callback = None  # callback that takes in a single argument, boolean is_right

        self.capture_dist1 = 30 # distance between first arrow and where car will stop.
        self.capture_dist2 = 25 # distance between second arrow and where car will stop.
        self.theta2 = 10 # angle to face second obstacle after first arc.
        self.obstacle_dist1 = None # distance between carpark and first obstacle.
        self.obstacle_dist2 = None # distance between carpark and second obstacle.
        self.wall_dist = None # distance driven to face wall after second obstacle.
        self.wall_complete = False # signal wall has been tracked.
        self.obstacle2_length_half = None # length of obstacle.

        self.turning_r = 40 # turning radius
        self.r0 = 21 # absolute distance from center line after passing obstacle 1
        self.chassis_cm = 15 # length from axle to axle
        self.wheelbase_cm = 16.5 # length between front wheels
        self.drive_speed = 85  # tune to balance speed with precision. kachow!
        # left and right arrow IDs
        self.LEFT_ARROW_ID = "39"
        self.RIGHT_ARROW_ID = "38"

    def initialize(self):
        try:
            # let stream server start before calling other sockets.
            print("starting stream")
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

        # start after init.
        self.start()

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

                    # print("OBJECT ID:", object_id)

                    if confidence_level is not None:
                        if object_id not in ["marker", "NONE"]:
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
                    print("Beginning run.")
                    self.start()

            except OSError:
                self.android_dropped.set()
                print("Event set: Bluetooth connection dropped")
            if message_rcv is None:
                continue

    def stm_receive(self) -> None:
        while True:
            try:
                messages = self.stm.wait_receive()

                for message_rcv in messages.split('\n'):
                    print("Message received from STM: ", message_rcv)
                    if "fD" in message_rcv:
                        dist_val_str = message_rcv.replace("fD", "").replace('\0', '').strip()
                        if len(dist_val_str) == 0:
                            # Robot is beginning drive towards obstacle, take in latest_image then decide what to do

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

                            # elif self.num_obstacle == 3: 
                            #     # Finished obstacle 2, go back to carpark
                            #     print("Going back to carpark...")
                            #     # TODO: Perform set of commands to go back to the carpark
                            #     self.perform_carpark()

                            self.num_obstacle += 1
                        else:
                            # Robot has finished tracking distance; save accordingly
                            dist_val = float(dist_val_str)

                            # set distances in order.
                            with self.lock:
                                if self.obstacle_dist1 is None:
                                    self.obstacle_dist1 = dist_val + self.capture_dist1
                                elif self.obstacle_dist2 is None:
                                    self.obstacle_dist2 = dist_val
                                elif self.wall_dist is None:
                                    self.wall_dist = dist_val
                                    self.wall_complete = True
                                else:
                                    self.stop()
                                # else:
                                #     self.wall_dist += dist_val
                                #     self.wall_complete = True
            except OSError as e:
                print(f"Error in receiving STM data: {e}")

    def send_D(self):
        self.stm.send_cmd("D", 0, 0, 0)
    
    def drive(self, angle, val, is_forward=True, speed=None):
        if speed is None:
            speed = self.drive_speed
        
        if val < 0:
            val = -val
            is_forward = not is_forward
        
        self.stm.send_cmd("T" if is_forward else "t", speed, angle, val)
    
    def drive_until(self, angle, val, is_forward=True, speed=None):
        if speed is None:
            speed = self.drive_speed
        
        self.stm.send_cmd("W" if is_forward else "w", speed, angle, val)
    
    def wall_ride(self, angle, is_right, threshold=30, is_forward=True, speed=None):
        if speed is None:
            speed = self.drive_speed
        
        char = 'R' if is_right else 'L'
        if not is_forward:
            char = char.lower()

        self.stm.send_cmd(char, speed, angle, threshold)

    # translate x and y. (+x to the left)
    def translate(self, x, y):
        print(f"Translating {x}, {y}.")
        is_right = x >= 0
        if not is_right:
            x = -x
        
        x /= 2
        y /= 2
        r =  (x**2 + y**2) / (2*x) # turning radius to execute.
        angle = math.atan(self.chassis_cm / (r - self.wheelbase_cm/2)) * 180 / math.pi # calculate steering angle.
        theta = math.asin(y/r) * 180 / math.pi # resultant facing angle after turn.
        if angle > 25:
            angle = 25
        if self.is_right2:
            angle = -angle
        
        self.drive(angle, theta)
        self.drive(-angle, theta)
        

    # drive towards obstacle (and insert 'D' to signal distance tracking).
    def perform_toward_obstacle(self, capture_dist=30) -> None:
        # self.stm.send_cmd("W", self.drive_speed, 0, 50)
        self.send_D()
        self.drive_until(0, capture_dist)
        self.send_D()

    # drive until IR sensor is above threshold (and insert 'D' for distance tracking).
    def perform_wall_track(self, is_right, is_forward=True, threshold=30, should_track=False) -> None:
        if should_track:
            self.send_D()
        self.wall_ride(0, is_right, is_forward=is_forward, threshold=threshold, speed=65)
        if should_track:
            self.send_D()
    
    # drive arc for first 10x10 obstacle.
    def perform_arc1(self, is_right) -> None:
        # get initial turning angle.
        angle = 25 if is_right else -25

        turn_theta = 33
        self.drive(angle, turn_theta)
        self.drive(0, 18)
        self.drive(-angle, turn_theta + self.theta2)

    # drive arc for second 60x10 obstacle.
    def perform_arc2(self, is_right1, is_right2) -> None:
        is_cross = is_right1 != is_right2
        angle = 25 if is_right2 else -25
        
        # while self.obstacle_dist2 is None:
        #     pass
        
        # turn to be parallel to the second obstacle.
        if is_cross:
            gamma = 25
            self.drive(0, 10)
            self.drive(-angle, gamma, False)
            self.drive(angle, 90 - gamma - self.theta2)
        else:
            gamma = 46
            delta = self.theta2 * 1.7
            self.drive(angle, self.theta2 + delta)
            self.drive(-angle, gamma, False)
            self.drive(angle *0.8, 90 - gamma - delta)

        # use wall tracking to find wall.
        wall_is_right = not is_right2
        self.perform_wall_track(wall_is_right, is_forward=False, threshold=-50)
        self.perform_wall_track(wall_is_right, is_forward=True, threshold=50)

        self.drive(-angle, 180)
        self.perform_wall_track(wall_is_right, is_forward=True, threshold=50, should_track=True)
        # wait for wall distance to be calculated.
        while not self.wall_complete:
            pass

        print(f"----------------- Wall distance: {self.wall_dist:.3f}cm --------------")
        self.drive(-angle, 90)

    # set this callback it is time to detect an arrow for obstacle 1.
    def callback_obstacle1(self, is_right) -> None:
        with self.lock:
            self.is_right1 = is_right

        self.perform_arc1(is_right)
        self.perform_toward_obstacle()
        # time.sleep(3)
        # if not self.done_obstacle2:
        #     # haven't seen; guess
        #     self.callback_obstacle2(randint(0, 1) == 1)

        self.on_arrow_callback = None  # clear callback.

    # set this callback it is time to detect an arrow for obstacle 2.
    def callback_obstacle2(self, is_right) -> None:
        with self.lock:
            self.done_obstacle2 = True
            self.is_right2 = is_right

        self.perform_arc2(self.is_right1, is_right)
        self.on_arrow_callback = None  # clear callback.

        self.perform_carpark()

    # drive back to the carpark.
    def perform_carpark(self) -> None:
        while self.obstacle_dist1 is None or self.obstacle_dist2 is None:
            pass
        
        side1 = self.wall_dist
        if self.is_right2:
            side1 = -side1

        y1 = (self.obstacle_dist2 + self.chassis_cm + self.capture_dist2) * math.cos(self.theta2 * math.pi / 180) + 10
        side2 = self.r0 + 15
        if self.is_right1:
            side2 = -side2

        y2 = self.obstacle_dist1
        # self.drive(0, y1)
        self.translate(side1, y1)
        self.translate(side2, y2)
        self.drive_until(0, 20, speed=70) # slowly advance into carpark.
        self.send_D() # signal stop.
        self.send_D()


    def start(self):
        print("Starting program...")
        print("Sending initial commands to the STM32...")
        self.start_time = time.time_ns()
        self.perform_toward_obstacle(self.capture_dist1)

    def stop(self):
        """Stops all processes on the RPi and disconnects from Android, STM and PC"""
        self.stm.disconnect()
        self.pc.disconnect()
        self.android.send("STOP")
        self.android.disconnect()
        # TODO: Add Stream disconnect
        print(f">>>>>>>>>> Ended: {(time.time_ns() - self.start_time) / 1e9:.3f}s. -------------- !")

    def get_last_image(self) -> str:
        # print(f"Returning last_image as {self.last_image}")
        return self.last_image

    def set_last_image(self, img) -> None:
        # print(f"Setting last_image as {img}")
        with self.lock:
            self.last_image = img

        if self.on_arrow_callback is not None and (
            img == self.RIGHT_ARROW_ID or img == self.LEFT_ARROW_ID
        ):
            self.on_arrow_callback(img == self.RIGHT_ARROW_ID)


def main():
    task2 = Task2RPI()  # init
    task2.initialize()

def test():
    print("in testing")
    task2 = Task2RPI()
    task2.stm.connect()
    Thread(target=task2.stm_receive).start()
    task2.drive_speed = 80
    task2.is_right1 = False
    task2.is_right2 = True

    task2.perform_toward_obstacle(task2.capture_dist1)
    task2.perform_arc1(task2.is_right1)
    # task2.perform_toward_obstacle(task2.capture_dist2)
    # task2.perform_arc2(task2.is_right1, task2.is_right2)
    
    # task2.perform_carpark()

if __name__ == "__main__":
    main()
    # test()
    # pass
