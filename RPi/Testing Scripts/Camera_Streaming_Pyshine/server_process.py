# server.py
import cv2
import torch
from ultralytics import YOLO
import pyshine as ps # pip install pyshine==0.0.9
import json
import multiprocessing
import time

# Load YOLOv8
model = YOLO('v6.pt')

def process_frame(frame, queue):
    # Perform inference
    results = model.predict(frame, save=False, imgsz=640, conf=0.7)
    names = results[0].names

    if len(results[0].boxes.conf) > 0:
        print("CONFIDENCE LEVEL: ", results[0].boxes[0].conf.item())
        print("CLASS: ", names[int(results[0].boxes[0].cls[0].item())])

    # TODO: Pass this data to RPI through the PC socket - Flask API

    # print(boxes)
    annotated_frame = results[0].plot()

    # Put the frame in the queue
    queue.put(annotated_frame)

def main():
    cap = cv2.VideoCapture()
    cap.open("http://192.168.14.14:5000/stream.mjpg")

    # Create a Queue for the frames
    frame_queue = multiprocessing.Queue()

    while True:
        success, frame = cap.read()
        if success:
            # Start a new process for each frame
            p = multiprocessing.Process(target=process_frame, args=(frame, frame_queue))
            p.start()

        # Display the resulting frame
        if not frame_queue.empty():
            annotated_frame = frame_queue.get()
            cv2.imshow("YOLOv8 Inference", annotated_frame)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__=='__main__':
    main()