import base64
import socket
import time
from threading import Thread

import cv2
import picamera
from picamera.array import PiRGBArray


class StreamServer:
    # define constants.
    def define_constants(self):
        self.BUFF_SIZE = 65536
        self.HOST_ADDR = ("192.168.14.14", 5005)
        self.REQ_STREAM = b"stream_request"

    def __init__(self):
        # define constants.
        self.define_constants()

        # initialise socket.
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, self.BUFF_SIZE)
        self.sock.bind(self.HOST_ADDR)
        print(f"Bound stream server to {self.HOST_ADDR}.")
        self.sock.settimeout(1)

        # define client address (used to send stream to).
        self.client_addr = None

        # start receiving thread (and exit flag).
        self.exit = False
        Thread(target=self.receive_proc).start()

    # thread processto listen to incoming requests, and set client address accordingly.
    def receive_proc(self):
        while not self.exit:
            try:
                msg, client_addr = self.sock.recvfrom(self.BUFF_SIZE)
                print(f"received {msg} from {client_addr}.")
                if msg == self.REQ_STREAM:
                    print(f"Redirecting stream to {client_addr}.")
                    self.client_addr = client_addr
            except:
                pass

    # main server thread.
    def start(self, resolution=(640, 480), framerate=20, quality=45, is_outdoors=False):
        equalizeHist = False
        # start main camera.
        with picamera.PiCamera(
            resolution=resolution,
            framerate=framerate,
        ) as cam:
            time.sleep(0.1)
            if is_outdoors:
                cam.exposure_compensation = 25
                cam.exposure_mode = 'backlight'
                cam.awb_mode = 'shade'
                equalizeHist = True
            
            cam.hflip = True
            cam.vflip = True

            raw = PiRGBArray(cam, cam.resolution)
            for frame in cam.capture_continuous(raw, format="bgr", use_video_port=True):
                img = frame.array
                if equalizeHist:
                    tmp = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    img = cv2.equalizeHist(tmp)

                # get encoding.
                buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, quality])[1]
                # encode in base64 for further compression.
                buffer = base64.b64encode(buffer)
                # send to client address.
                if not self.client_addr is None:
                    self.sock.sendto(buffer, self.client_addr)
                # reset camera frame.
                raw.truncate(0)

                if self.exit:
                    break

    # close the server.
    def close(self):
        self.exit = True
