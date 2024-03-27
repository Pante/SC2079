from multiprocessing import freeze_support
from ultralytics import YOLO

model = YOLO('yolov8n-seg.pt') #load pre-trained model


if __name__ == '__main__':
    freeze_support()
    results = model.train(data='data.yaml', name="v13_trial_3", epochs=24, imgsz=640, flipud=0.0, fliplr=0.0)
    results = model.val() #Evaluate model with validation dataset
