import cv2
import imagezmq

image_receiver = imagezmq.ImageHub()

try:
    while True:
        _, image = image_receiver.recv_image()
        cv2.imshow("Image Stream", image)
        cv2.waitKey(1)
        image_receiver.send_reply(b'OK')
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    cv2.destroyAllWindows()
    image_receiver.close()
