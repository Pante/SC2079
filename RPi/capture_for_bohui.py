from time import sleep

from picamera import PiCamera

camera = PiCamera()
camera.resolution = (640, 480)
camera.start_preview()

user_input = 0

while user_input < 3:
    user_input = input("1. Take 10 pictures, 2. Exit")
    if int(user_input) == 1:
        for i in range(10):
            sleep(2)
            camera.capture(f"/home/raspberrypi/Desktop/saved_images/image{i}.jpg")
        print("Done capturing")
    else:
        print("Stopping preview...")
        camera.stop_preview()
else:
    camera.stop_preview()
