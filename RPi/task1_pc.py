import json
import os
import socket
import sys
import threading
from multiprocessing import Manager, Process
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(1, "/home/raspberrypi/Desktop/MDP Group 14 Repo/SC2079/RPi")
from TestingScripts.Camera_Streaming_UDP.stream_listener import StreamListener


class Task1PC:
    def __init__(self):
        # self.manager = Manager()
        self.process_PC_receive = None
        self.process_PC_stream = None

        self.exit = False
        self.pc_receive_thread = None
        self.stream_thread = None

        # self.pc_dropped = self.manager.Event()
        self.host = "192.168.14.14"
        self.port = 5000
        self.client_socket = None

        self.stream_listener = StreamListener("TestingScripts/v9_task1.pt")
        self.prev_image = None
        self.stitching_img_dict = {}
        self.stitching_arr = []  # to store the image_id's of the image to stitch

    def start(self):
        self.pc_receive_thread = threading.Thread(target=self.pc_receive)
        self.stream_thread = threading.Thread(target=self.stream_start)
        self.pc_receive_thread.start()  # Receive from PC
        self.stream_thread.start()  # Start stream

    def stream_start(self):
        self.stream_listener.start_stream_read(
            self.on_result, self.on_disconnect, conf_threshold=0.65, show_video=True
        )

    def on_result(self, result, frame):

        message_content = None
        img_id = 1
        if result is not None:
            names = result.names
            detected_img_id = names[int(result.boxes[0].cls[0].item())]
            detected_conf_level = result.boxes[0].conf.item()
            if self.prev_image is None:
                # New image, can send over
                # Only if the confidence is over threshold then pass to the PC
                # TODO: Pass this data to RPI through the PC socket - Flask API
                message_content = str(detected_conf_level) + "," + detected_img_id
                self.prev_image = detected_img_id
                # self.prev_image = names[int(result.boxes[0].cls[0].item())]
                # print("FIRST: ", self.prev_image)
            elif detected_img_id != self.prev_image:
                # New image, can send over
                message_content = str(detected_conf_level) + "," + detected_img_id
                self.prev_image = detected_img_id

                # Saving the frames into the dictionary first

                if detected_img_id not in self.stitching_img_dict:
                    self.stitching_img_dict[detected_img_id] = (
                        detected_conf_level,
                        frame,
                    )
                elif (
                    detected_img_id in self.stitching_img_dict
                    and self.stitching_img_dict[detected_img_id][0]
                    < detected_conf_level
                ):
                    # If the newly detected confidence level < current one in the dictionary, replace
                    self.stitching_img_dict[detected_img_id] = (
                        detected_conf_level,
                        frame,
                    )

                # stitching_img_dict[names[int(result.boxes[0].cls[0].item())]] = (result.boxes[0].conf.item(), frame)

                # stitching_img_dict[1] = (conf, frame)
                # stitching_img_dict[1][0]

                # directory = "stitching_images/"
                # files = os.listdir(directory)

                # # If the folder is empty, there won't be any iterations for this for loop
                # for file in files:
                #     image_id, confidence = file.split(",")[0], float(
                #         file.split(",")[1].split(".jpg")[0]
                #     )
                #     # If the image_id matches and the confidnce of the current frame is more than the one in the folder
                #     if (
                #         image_id == names[int(result.boxes[0].cls[0].item())]
                #         and confidence > result.boxes[0].conf.item()
                #     ):
                #         os.remove(directory + "/" + file)
                #         cv2.imwrite(directory, frame)
                #         break
                #     else:
                #         # Do nothing, the folder image's confidence level is higher than the current image
                #         pass
                # else:
                #     # If the image_id does not exist in the folder, create new image in the folder
                #     cv2.imwrite(
                #         directory
                #         + "/"
                #         + names[int(result.boxes[0].cls[0].item())]
                #         + ","
                #         + str(result.boxes[0].conf.item())
                #         + ".jpg",
                #         frame,
                #     )

                # if int(result.boxes[0].conf.item()) > 0.7:
                #     directory = (
                #         "stitching_images/" + names[int(result.boxes[0].cls[0].item())]
                #     )
                #     if not os.path.exists(directory):
                #         os.makedirs(directory)
                #     img_path = (
                #         directory + "/" + str(result.boxes[0].conf.item()) + ".jpg"
                #     )
                #     cv2.imwrite(img_path, frame)

        elif self.prev_image != "NONE":
            # No object detected, send "NONE" over
            # Upon capture image, if no object is detected -- "NONE", continue to wait until a object is detected (not "NONE")
            message_content = "NONE"
            self.prev_image = "NONE"

        if message_content is not None:
            print("Sending:", message_content)
            self.client_socket.send(message_content.encode("utf-8"))

    def on_disconnect(self):
        print("Stream disconnected, disconnect.")
        self.disconnect()

    def connect(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
        except OSError as e:
            print("Error in connecting to PC:", e)

    def disconnect(self):
        try:
            self.exit = True
            self.client_socket.shutdown(socket.SHUT_RDWR)
            self.client_socket.close()
            self.client_socket = None
            print("Disconnected from PC successfully")

        except Exception as e:
            print("Failed to disconnected from PC:", e)

    def pc_receive(self) -> None:
        print("PC Socket connection started successfully")
        self.connect()
        # print("Went into the receive function")
        while not self.exit:
            try:
                message_rcv = self.client_socket.recv(1024).decode("utf-8")

                # STITCHING
                if "STITCH_IMG" in message_rcv:
                    self.stitching_arr.append(
                        message_rcv
                    )  # Append the image_id of the image to stitch

                elif "PERFORM STITCHING" in message_rcv:
                    # perform stitching
                    # Save images into folder
                    for image_id in self.stitching_arr:
                        if image_id in self.stitching_img_dict:
                            confidence, frame = self.stitching_img_dict[image_id]
                            filename = f"stitching_images/{image_id},{confidence}.jpg"
                            cv2.imwrite(filename, frame)
                    stitchImages()

                if not message_rcv:
                    print("PC connection dropped")
                    break
                print("Message received from PC:", message_rcv)
            except OSError as e:
                print("Error in sending data:", e)
                break


def archiveImages():
    imageFolder = "stitching_images"  # Change to where picam frames are saved.
    archiveFolder = (
        "stitching_archive"  # change to folder where you want to archive images.
    )

    for files in os.walk(imageFolder):
        for file in files:
            src_path = os.path.join(imageFolder, file)
            dst_path = os.path.join(archiveFolder, file)
            os.rename(src_path, dst_path)


def stitchImages():

    images = []
    # change path to where pi camera frames are being saved.
    imageFolder = "stitching_images/"

    for root, dirs, files in os.walk(imageFolder):
        for file in files:
            image_path = os.path.join(root, file)
            img = cv2.imread(image_path)
            if img is not None:
                img = cv2.resize(img, (320, 320))
                images.append(img)
                # print("Image appended to list")

    column1, column2, column3, column4, canvas = None
    if len(images) == 2:
        column1 = np.vstack([images[0], images[1]])
        canvas = np.hstack(column1)
    elif len(images) == 3:
        column1 = np.vstack([images[0], images[1]])
        column2 = np.vstack([images[2]])
        canvas = np.hstack([column1, column2])
    elif len(images) == 4:
        column1 = np.vstack([images[0], images[1]])
        column2 = np.vstack([images[2], images[3]])
        canvas = np.hstack([column1, column2])
    elif len(images) == 5:
        column1 = np.vstack([images[0], images[1]])
        column2 = np.vstack([images[2], images[3]])
        column3 = np.vstack([images[4]])
        canvas = np.hstack([column1, column2, column3])
    elif len(images) == 6:
        column1 = np.vstack([images[0], images[1]])
        column2 = np.vstack([images[2], images[3]])
        column3 = np.vstack([images[4], images[5]])
        canvas = np.hstack([column1, column2, column3])
    elif len(images) == 7:
        column1 = np.vstack([images[0], images[1]])
        column2 = np.vstack([images[2], images[3]])
        column3 = np.vstack([images[4], images[5]])
        column4 = np.vstack([images[6]])
        canvas = np.hstack([column1, column2, column3, column4])
    else:
        column1 = np.vstack([images[0], images[1]])
        column2 = np.vstack([images[2], images[3]])
        column3 = np.vstack([images[4], images[5]])
        column4 = np.vstack([images[6], images[7]])
        canvas = np.hstack([column1, column2, column3, column4])

    # Display collage
    cv2.imshow("Collage", canvas)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Save collage and save a copy
    cv2.imwrite("collage.jpg", canvas)
    archiveImages()


if __name__ == "__main__":
    pcMain = Task1PC()
    pcMain.start()
