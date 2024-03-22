from time import sleep

from picamera import PiCamera

camera = PiCamera()
camera.resolution = (640, 480)
camera.hflip = True
camera.vflip = True
camera.exposure_compensation = 25
camera.exposure_mode = 'backlight'
camera.awb_mode = 'shade'
camera.start_preview()

user_input = ""
burst = 12

id = 27
while len(user_input) == 0:
    user_input = input(f"Burst {burst} pictures; enter anything to Exit >> ")
    if len(user_input) > 0:
        print("Stopping preview...")
        camera.stop_preview()
        break

    for i in range(burst):
        # sleep(2)
        camera.capture(f"/home/raspberrypi/Desktop/saved_images/{id}-{i}.jpg")
    
    print("Done capturing")
    id += 1