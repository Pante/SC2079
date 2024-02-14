import io
import time
import requests
from picamera import PiCamera

def send_frame(frame):
    """Send a frame to the server."""
    url = 'http://192.168.14.14/stream'
    headers = {'Content-Type': 'image/jpeg'}
    response = requests.post(url, data=frame, headers=headers)
    return response

with PiCamera() as camera:
    camera.resolution = (640, 480)
    stream = io.BytesIO()

    for _ in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
        # send current frame to server
        stream.seek(0)
        frame = stream.read()
        response = send_frame(frame)

        # check response
        if response.status_code != 200:
            print('Failed to send frame:', response.status_code, response.text)

        # reset stream for next frame
        stream.seek(0)
        stream.truncate()