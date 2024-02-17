# import cv2
# from imagezmq import ImageHub
from ultralytics import YOLO
import cv2
import glob
import os
# import sys
# from pathlib import Path
# path_root = Path(__file__).parents[2]
# sys.path.append(str(path_root))


# # Initialize YOLO model
# # TODO: Need to change this. The model should be loaded from the PC
# yolo = YOLO(model='v6.pt')

# # Initialize ImageHub to receive video stream
# image_hub = ImageHub()

# while True:
#     # Receive the frame from the client
#     client_name, frame = image_hub.recv_image()

#     # Perform YOLO object detection on the frame
#     results = yolo(frame)

#     # Draw bounding boxes on the frame
#     annotated_frame = results.render()[0]

#     # Display the annotated frame
#     cv2.imshow('YOLO Object Detection', annotated_frame)

#     # Break the loop if 'q' key is pressed
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # Release resources
# cv2.destroyAllWindows()
# image_hub.close()

# def predict():
#     # model = YOLO('yolov8n.pt')
#     model = YOLO(model='v6.pt')
#     img0 = 'photo2.jpeg'
#     img1 = 'photo1.jpeg'
#     img2 = 'photo.jpeg'
#     img3 = 'photo3.jpeg'
#     # result = model.predict(img, save=True, imgsz=640, conf=0.5)
#     result = model([img0, img1, img2,img3], save=True, imgsz=640, conf=0.5, show_labels=True, show_boxes=True, line_width=4)
#     # result = model('bus.jpg')  # list of 1 Results object
#     # result.plot()
#     # result.show()
#     print(result)

   
# predict()
