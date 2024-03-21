import base64
import socket

import cv2
import numpy as np
from ultralytics import YOLO


# Used to connect to RPi streaming.
class StreamListener:
    # define constants.
    def define_constants(self):
        self.BUFF_SIZE = 65536
        self.HOST_ADDR = ("192.168.14.14", 5005)
        self.REQ_STREAM = b"stream_request"

    # pass in the weights file for use with YOLO.
    def __init__(self, weights):
        # define constants.
        self.define_constants()

        # initialise model.
        self.model = YOLO(weights)

        # intialise socket.
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.BUFF_SIZE)

        # timeout of 3 seconds to signal disconnect.
        self.sock.settimeout(3)

    # send stream request to socket.
    def req_stream(self):
        print("Sending request to HOST.")
        self.sock.sendto(self.REQ_STREAM, self.HOST_ADDR)

    # start streaming.
    # on_result(result) will be called with the result image if conf_threshold is met.
    # on_disconnect() is called when the stream is ended.
    # pass show_video=False to avoid a live window.
    def start_stream_read(
        self, on_result, on_disconnect, conf_threshold=0.7, show_video=True
    ):
        # request for stream to be sent to this client.
        self.req_stream()

        while True:
            packet = None
            try:
                packet, _ = self.sock.recvfrom(self.BUFF_SIZE)
            except:
                print("Timeout, ending stream")
                break

            # decode received packet and run prediction model.
            frame = base64.b64decode(packet)
            npdata = np.frombuffer(frame, dtype=np.uint8)
            frame = cv2.imdecode(npdata, cv2.IMREAD_COLOR)
            res = self.model.predict(
                frame,
                save=False,
                imgsz=frame.shape[1],
                conf=conf_threshold,
                verbose=False,
            )[0]

            # perform actions based on results.
            annotated_frame = frame
            if len(res.boxes) > 0:
                annotated_frame = res.plot()
                on_result(res, annotated_frame)
            else:
                on_result(None, None)

            if show_video:
                cv2.imshow("Stream", annotated_frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break

        # call final disconnect handler.
        on_disconnect()

    # release all resources and close.
    def close(self):
        self.sock.close()
