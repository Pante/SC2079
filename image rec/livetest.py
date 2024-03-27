from ultralytics import YOLO
import cv2

#model = YOLO('best copy.pt')
model = YOLO('v12_task1.pt')

def predict():
    #live stream predict
    model.predict(source="0", show = True)

predict()