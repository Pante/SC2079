import cv2
import torch
from ultralytics import YOLO
import pyshine as ps
import json
import asyncio
import threading
import queue

model = YOLO('v9_task1.pt')

class ImageRecognitionThread(threading.Thread):
    def __init__(self, frame, queue):
        threading.Thread.__init__(self)
        self.frame = frame
        self.queue = queue

    def run(self):
        results = model.predict(self.frame, save=False, imgsz=640, conf=0.7)
        names = results[0].names

        if len(results[0].boxes.conf) > 0:
            print("CONFIDENCE LEVEL: ", results[0].boxes[0].conf.item())
            print("CLASS: ", names[int(results[0].boxes[0].cls[0].item())])

        annotated_frame = results[0].plot()
        self.queue.put(annotated_frame)

async def main():
    cap = cv2.VideoCapture()
    cap.open("http://192.168.14.14:5000/stream.mjpg")

    frame_queue = queue.Queue()

    while True:
        success, frame = cap.read()
        if success:
            thread = ImageRecognitionThread(frame, frame_queue)
            thread.start()

        if not frame_queue.empty():
            annotated_frame = frame_queue.get()
            cv2.imshow("YOLOv8 Inference", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__=='__main__':
    asyncio.run(main())