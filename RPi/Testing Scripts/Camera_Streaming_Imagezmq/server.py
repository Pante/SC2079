import cv2
import sys
import random
import numpy as np
import imagezmq
import torch


# from pathlib import Path
# path_root = Path(__file__).parents[3]
# sys.path.append(str(path_root))

# from yolov5.models.experimental import attempt_load
# # from utils.datasets import letterbox
# from yolov5.utils.general import check_img_size, non_max_suppression, scale_coords
# from yolov5.utils.plots import plot_one_box
# from yolov5.utils.torch_utils import select_device
from PIL import Image

# Alternative to YoloV's letterbox function
def resize_image(image, size=(640, 640)):
    return cv2.resize(image, size, interpolation = cv2.INTER_AREA)

# Load the model
device = select_device('')
model = attempt_load('../yolov_model/v6.pt', map_location=device)  # replace with your model path
imgsz = check_img_size(640, s=model.stride.max())  # check img_size

# Get names and colors
names = model.module.names if hasattr(model, 'module') else model.names
colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(len(names))]

# Create an image receiver
image_hub = imagezmq.ImageHub()

try:
    while True:
        # Receive an image
        _, img = image_hub.recv_image()

        # Acknowledge that we received the image
        image_hub.send_reply(b'OK')

        # Preprocess the image for the model
       # img = letterbox(img, imgsz, stride=model.stride.max())[0]
        img = resize_image(img, (imgsz, imgsz))
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
        img = np.ascontiguousarray(img)
        img = torch.from_numpy(img).to(device)
        img = img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0

        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        # Run the image through the model
        pred = model(img, augment=False)[0]

        # TODO: REPLACE THIS WITH THE NEW .predict FUNCTION - Bohui
        


        # START EDITS - Bohui
        # Apply NMS
        pred = non_max_suppression(pred, 0.25, 0.45, classes=None, agnostic=False)

        # Process detections
        for i, det in enumerate(pred):  # detections per image
            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], img.shape).round()

                # Convert img to a PIL Image
                img_pil = Image.fromarray(img)

                # Write results
                for *xyxy, conf, cls in reversed(det):
                    label = f'{names[int(cls)]} {conf:.2f}'
                    plot_one_box(xyxy, img, label=label, color=colors[int(cls)], line_thickness=3)

                # Convert img_pil back to a numpy array
                img = np.array(img_pil)
    
        # END EDITS - Bohui
        # Display the image
        cv2.imshow('Live Camera Feed', img)
        if cv2.waitKey(1) == ord('q'):  # Exit if Q is pressed
            break

except KeyboardInterrupt:
    # Exit the loop if Ctrl+C is pressed
    pass
finally:
    cv2.destroyAllWindows()  # Close the display window
    
    
