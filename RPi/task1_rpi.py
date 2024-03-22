# import pyshine as ps
import socket
import sys
import time
from multiprocessing import Manager, Process
from pathlib import Path
from threading import Thread

sys.path.insert(1, "/home/raspberrypi/Desktop/MDP Group 14 Repo/SC2079/RPi")
from Communication.android import Android, AndroidDummy
from Communication.pc import PC
from Communication.stm import STM
from openapi_client.api.image_recognition_api import ImageRecognitionApi
from openapi_client.api.pathfinding_api import PathfindingApi
from openapi_client.api_client import ApiClient

# Pathfinding
from openapi_client.configuration import Configuration
from openapi_client.models.direction import Direction
from openapi_client.models.error_context import ErrorContext
from openapi_client.models.error_type import ErrorType
from openapi_client.models.image_prediction_response import ImagePredictionResponse
from openapi_client.models.location import Location
from openapi_client.models.message import Message
from openapi_client.models.misc_instruction import MiscInstruction
from openapi_client.models.move import Move
from openapi_client.models.path import Path
from openapi_client.models.pathfinding_point import PathfindingPoint
from openapi_client.models.pathfinding_request import PathfindingRequest
from openapi_client.models.pathfinding_request_obstacle import (
    PathfindingRequestObstacle,
)
from openapi_client.models.pathfinding_request_robot import PathfindingRequestRobot
from openapi_client.models.pathfinding_response import PathfindingResponse
from openapi_client.models.pathfinding_response_move_instruction import (
    PathfindingResponseMoveInstruction,
)
from openapi_client.models.pathfinding_response_segment import (
    PathfindingResponseSegment,
)
from openapi_client.models.pathfinding_response_segment_instructions_inner import (
    PathfindingResponseSegmentInstructionsInner,
)
from openapi_client.models.pathfinding_vector import PathfindingVector
from openapi_client.models.turn_instruction import TurnInstruction
from openapi_client.models.validation_error_model import ValidationErrorModel
from TestingScripts.Camera_Streaming_UDP.stream_server import StreamServer


class Task1RPI:
    def __init__(self, config):
        self.config = config

        self.obstacle_dict = {}  # Obstacle Dict
        self.robot = None  # Robot
        self.prev_image = None
        self.stm = STM()
        self.android = Android()
        # self.android = AndroidDummy()
        self.pc = PC()
        self.manager = Manager()
        self.process_stm_receive = None
        self.process_pc_receive = None
        self.process_pc_stream = None
        self.process_android_receive = None
        self.android_dropped = self.manager.Event()
        self.host = "192.168.14.14"
        self.port = 5000
        self.conf = Configuration(host="http://192.168.14.13:5001")
        self.pathfinding_api = PathfindingApi(api_client=ApiClient(configuration=self.conf))
        self.last_image = None
        self.prev_image = None
        self.STM_Stopped = False

        self.start_time = 0
        self.drive_speed = 40 if config.is_outdoors else 55
        self.drive_angle = 25
    def initialize(self):
        try:
            # let stream server start before calling other sockets.
            self.process_pc_stream = Thread(target=self.stream_start)
            self.process_pc_stream.start()  # Start the Stream
            time.sleep(0.1)

            self.stm.connect()
            self.pc.connect()
            self.android.connect()

            print("PC Successfully connected through socket")
            self.process_android_receive = Thread(target=self.android_receive)
            self.process_stm_receive = Thread(target=self.stm_receive)
            self.process_pc_receive = Thread(target=self.pc_receive)

            # Start Threads
            self.process_pc_receive.start()  # Receive from PC
            self.process_android_receive.start()  # Receive from android
            self.process_stm_receive.start()  # Receive from PC

            # Manual init
            # self.manual_init()

        except OSError as e:
            print("Initialization failed: ", e)

    def manual_init(self) -> None:
        self.robot = self.get_api_object(
                PathfindingRequestRobot, "NORTH", (0, 0), (11, 11)
            )
        N, S, E, W = "NORTH", "SOUTH", "EAST", "WEST"
        self.obstacle_dict = {
            1: self.get_api_object(
                PathfindingRequestObstacle,
                W,
                (160, 0),
                (10, 10),
                id=1,
            ),
            2: self.get_api_object(
                PathfindingRequestObstacle,
                S,
                (63, 160),
                (10, 10),
                id=2,
            ),
            3: self.get_api_object(
                PathfindingRequestObstacle,
                S,
                (127, 147),
                (10, 10),
                id=3,
            ),
            4: self.get_api_object(
                PathfindingRequestObstacle,
                N,
                (88, 74),
                (10, 10),
                id=4,
            ),
            5: self.get_api_object(
                PathfindingRequestObstacle,
                W,
                (190, 38),
                (10, 10),
                id=5,
            ),
            6: self.get_api_object(
                PathfindingRequestObstacle,
                N,
                (49, 10),
                (10, 10),
                id=6,
            ),
            # 7: self.get_api_object(
            #     PathfindingRequestObstacle,
            #     S,
            #     (80, 95),
            #     (10, 10),
            #     id=7,
            # ),
            # 8: self.get_api_object(
            #     PathfindingRequestObstacle,
            #     W,
            #     (85, 55),
            #     (10, 10),
            #     id=8,
            # ),
        }
        self.start()
    
    def pc_receive(self) -> None:
        while True:
            try:
                message_rcv = self.pc.receive()
                print(f"Received from PC: {message_rcv}")
                if "NONE" in message_rcv:
                    self.set_last_image("NONE")
                else:
                    msg_split = message_rcv.split(",")
                    if len(msg_split) != 3:
                        continue

                    obstacle_id, conf_str, object_id = msg_split
                    confidence_level = None

                    try:
                        confidence_level = float(conf_str)
                    except ValueError:
                        confidence_level = None

                    print("OBJECT ID:", object_id)

                    if confidence_level is not None:
                        self.android.send(f"TARGET,{obstacle_id},{object_id}")

            except OSError as e:
                print(f"Error in receiving data: {e}")
                break

    def stream_start(self):
        StreamServer().start(framerate=15, quality=45, is_outdoors=self.config.is_outdoors)

    def get_api_object(self, Object, dir, sw, size, id=None):
        # TODO: test 200x200
        x, y = sw
        w, h = size
    
        direction = Direction(dir)
        south_west = PathfindingPoint(x=x, y=y)
        north_east = PathfindingPoint(x=(x + w) - 1, y=(y + h) - 1)

        if id is not None:
            return Object(
                direction=direction,
                south_west=south_west,
                north_east=north_east,
                image_id=id,
            )

        return Object(direction=direction, south_west=south_west, north_east=north_east)

    def android_receive(self) -> None:
        print("Went into android receive function")
        while True:
            message_rcv = None
            try:
                message_rcv = self.android.receive()
                messages = message_rcv.split('\n')
                for message_rcv in messages:
                    if len(message_rcv) == 0:
                        continue

                    print("Message received from Android:", message_rcv)
                    if "BEGIN" in message_rcv:
                        print("BEGINNNN!")
                        # TODO: Begin Task 1
                        self.start()  # Calculate the path
                    elif "CLEAR" in message_rcv:
                        print(" --------------- CLEARING OBSTACLES LIST. ---------------- ")
                        self.obstacle_dict.clear()
                    elif "OBSTACLE" in message_rcv:
                        print("OBSTACLE!!!!")
                        id, x, y, dir = message_rcv.split(",")[1:]
                        id = int(id)

                        if dir == "-1":
                            if id in self.obstacle_dict:
                                del self.obstacle_dict[id]
                                print("Deleted obstacle", id)
                        elif dir not in ["NORTH", "SOUTH", "EAST", "WEST"]:
                            print("Invalid direction provided:", dir + ", ignoring...")
                            continue
                        else:
                            newObstacle = self.get_api_object(
                                PathfindingRequestObstacle,
                                dir,
                                (int(x), int(y)),
                                (10, 10),
                                id=id,
                            )
                            self.obstacle_dict[id] = newObstacle

                            print("Obstacle set successfully: ", newObstacle)
                        print(f"--------------- Current list {len(self.obstacle_dict)}: -------------")
                        obs_items = self.obstacle_dict.items()
                        if len(obs_items) == 0:
                            print("! no obstacles.")
                        else:
                            for id, obstacle in obs_items:
                                print(f"{id}: {obstacle}")

                    elif "ROBOT" in message_rcv:
                        print("NEW ROBOT LOCATION!!!")
                        x, y, dir = message_rcv.split(",")[1:]
                        x, y = int(x), int(y)

                        if x < 0 or y < 0:
                            print("Illegal robot coordinate, ignoring...")
                            continue

                        self.robot = self.get_api_object(
                            PathfindingRequestRobot, dir, (int(x), int(y)), (21, 21)
                        )
                        print("Robot set successfully: ", self.robot)
                    else:
                        # Catch for messages with no keywords (OBSTACLE/ROBOT/BEGIN)
                        print("Not a keyword, message received: ", message_rcv)
                
            except OSError:
                self.android_dropped.set()
                print("Event set: Bluetooth connection dropped")

            if message_rcv is None:
                continue

    def stm_receive(self) -> None:
        msg = ""
        while True:
            message_rcv = None
            try:
                message_rcv = self.stm.wait_receive()
                print("Message received from STM: ", message_rcv)
                if "fS" in message_rcv:
                    self.set_stm_stop(
                        True
                    )  # Finished stopping, can start delay to recognise image
                    print("Setting STM Stopped to true")
                elif message_rcv[0] == "f":
                    # Finished command, send to android
                    message_split = message_rcv[1:].split(
                        "|"
                    )  # Ignore the 'f' at the start
                    cmd_speed = message_split[0]
                    turning_degree = message_split[1]
                    distance = message_split[2].strip()

                    cmd = cmd_speed[0]  # Command (t/T)
                    speed = cmd_speed[1:]

                    send_count = 1

                    if turning_degree == f"-{self.drive_angle}":
                        # Turn left
                        if cmd == "t":
                            # Backward left
                            msg = "TURN,BACKWARD_LEFT,0"
                        elif cmd == "T":
                            # Forward left
                            msg = "TURN,FORWARD_LEFT,0"
                    elif turning_degree == f"{self.drive_angle}":
                        # Turn right
                        if cmd == "t":
                            # Backward right
                            msg = "TURN,BACKWARD_RIGHT,0"
                        elif cmd == "T":
                            # Forward right
                            msg = "TURN,FORWARD_RIGHT,0"
                    elif turning_degree == "0":
                        if cmd == "t":
                            # Backward
                            msg = "MOVE,BACKWARD," + distance
                        elif cmd == "T":
                            # Forward
                            msg = "MOVE,FORWARD," + distance
                    else:
                        # Unknown turning degree
                        print("Unknown turning degree")
                        msg = "No instruction"
                        continue

                    print("Msg: ", msg)
                    try:
                        self.android.send(msg)
                        print("SENT TO ANDROID SUCCESSFULLY: ", msg)
                    except OSError:
                        self.android_dropped.set()
                        print("Event set: Android dropped")

                    self.android_dropped.clear()  # Clear previously set event

            except OSError as e:
                print(f"Error in receiving STM data: {e}")

            if message_rcv is None:
                continue

    def stop(self):
        """Stops all processes on the RPi and disconnects from Android, STM and PC"""
        time.sleep(0.2)
        self.android.send("STOP")
        # self.android.disconnect()
        # self.stm.disconnect()
        # self.pc.disconnect()
        # TODO: Add Stream disconnect/end
        print("Program Ended\n")

    def start(self):
        pathfindingRequest = PathfindingRequest(
            obstacles=self.obstacle_dict.values(), robot=self.robot, verbose=False
        )
        response = None

        self.start_time = time.time_ns()
        print("! Sending request to API...")
        try:
            response = self.pathfinding_api.pathfinding_post(pathfindingRequest)
        except:
            print("Server failed, try again.")
            return
        
        print(f"! Request completed in {(time.time_ns() - self.start_time) / 1e9:.3f}s.")
        segments = response.segments
        for i, segment in enumerate(segments):
            print(f"On segment {i+1} of {len(segments)}:")
            self.set_stm_stop(False)  # Reset to false upon starting the new segment

            # print("PATH ", i, ": ", segment.path.actual_instance)
            # print("Segment ", i, ": ", segment.instructions)
            print("SEGMENT NUMBER ", i)
            i = i + 1

            for instruction in segment.instructions:
                actual_instance = instruction.actual_instance
                inst = ""
                flag = ""
                angle = 0
                val = 0

                if hasattr(actual_instance, "move"):  # MOVE Instruction
                    inst = PathfindingResponseMoveInstruction(
                        amount=actual_instance.amount, move=actual_instance.move
                    )
                    move_direction = inst.move.value
                    angle = 0
                    val = inst.amount
                    print("AMOUNT TO MOVE: ", val)
                    print("MOVE DIRECTION: ", move_direction)

                    # Send instructions to stm
                    if move_direction == "FORWARD":
                        flag = "T"
                    elif move_direction == "BACKWARD":
                        flag = "t"

                else:
                    try:
                        inst = TurnInstruction(actual_instance)  # TURN Instruction
                    except:
                        inst = MiscInstruction(actual_instance)  # MISC Instruction

                    # print("Final Instruction ", inst)
                    if (
                        isinstance(inst, MiscInstruction)
                        and str(inst.value) == "CAPTURE_IMAGE"
                    ):
                        flag = "S"  # STM to stop before recognising image and sending results to RPi

                    elif isinstance(inst, TurnInstruction):
                        val = 90
                        inst_send = inst.value
                        if inst.value == "FORWARD_LEFT":
                            flag = "T"
                            angle = -self.drive_angle
                        elif inst.value == "FORWARD_RIGHT":
                            flag = "T"
                            angle = self.drive_angle
                        elif inst.value == "BACKWARD_LEFT":
                            flag = "t"
                            angle = -self.drive_angle
                        else:
                            # BACKWARD_RIGHT
                            flag = "t"
                            angle = self.drive_angle

                self.stm.send_cmd(flag, self.drive_speed, angle, val)
            print("STM Command sent successfully...")
            while not self.get_stm_stop():
                # Wait until the STM has execute all the commands and stopped (True), then wait x seconds to recognise image
                pass

            time.sleep(0.75)
            print("STM stopped, sending time of capture...")
            self.pc.send(
                f"DETECT,{segment.image_id}"
            )

        print(f">>>>>>>>>>>> Completed in {(time.time_ns() - self.start_time) / 1e9:.2f} seconds.")
        try:
            print("request stitch")
            self.pc.send(f"PERFORM STITCHING,{len(segments)}")
        except OSError as e:
            print("Error in sending stitching command to PC: " + e)

        self.stop()

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


def main(config):
    print("# ------------- Running Task 1, RPi ---------------- #")
    print(f"You are {'out' if config.is_outdoors else 'in'}doors.")
    task1 = Task1RPI(config)  # init
    task1.initialize()
