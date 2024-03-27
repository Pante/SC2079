from multiprocessing import freeze_support
from ultralytics import YOLO


model = YOLO('v9_task1.pt') #load custom model

if __name__ == '__main__':
    freeze_support()
    model.tune(data='data.yaml', epochs=24, optimizer='AdamW', name="v10_model", flipud=0.0, fliplr=0.0, scale=0.7, save=False, val=False, plots=False)
