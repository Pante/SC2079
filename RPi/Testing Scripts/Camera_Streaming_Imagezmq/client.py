import time
import io
import imagezmq
from picamera import PiCamera

camera = PiCamera()
# TODO: Replace the IP Address with the PC's IP Address
image_sender = imagezmq.ImageSender(connect_to='tcp://192.168.14.14')  

camera.start_preview()

try:
    time.sleep(2)  # Give the camera time to warm up
    while True:
        stream = io.BytesIO()
        camera.capture(stream, format='jpeg')
        image_sender.send_image(stream.getvalue())
        time.sleep(0.1)  # Adjust the delay based on your needs
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    stream.close()
    image_sender.close()
    camera.stop_preview()