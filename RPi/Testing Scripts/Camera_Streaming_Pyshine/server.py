# server.py
import cv2
import torch
from ultralytics import YOLO
import pyshine as ps # pip install pyshine==0.0.9
import json

# Load YOLOv8
# model = torch.hub.load('ultralytics/yolov8', 'custom', path_or_model='v6.pt') # replace 'yolov8.pt' with your model path
model = YOLO('v6.pt')

def main():
    cap = cv2.VideoCapture()
    cap.open("http://192.168.14.14:5000/stream.mjpg")

    while True:
        success, frame = cap.read()
        if success:
            # Perform inference
            # results = model(frame)
            results = model.predict(frame, save=False, imgsz=640, conf=0.7)
            names = results[0].names
            
            
            if len(results[0].boxes.conf) > 0:
                print("CONFIDENCE LEVEL: ", results[0].boxes[0].conf.item())
                print("CLASS: ", names[int(results[0].boxes[0].cls[0].item())])
                
                # TODO: Pass this data to RPI through the PC socket - Flask API
            
            # print(boxes)
            annotated_frame = results[0].plot()
            
            # Display the resulting frame
            # cv2.imshow("YOLOv8 Inference", annotated_frame)
            # cv2.imshow('YOLOv8 Object Detection', frame)

            # Break the loop on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    # cv2.destroyAllWindows()

if __name__=='__main__':
    main()