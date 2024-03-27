from ultralytics import YOLO
import cv2
import os
from PIL import Image
import numpy as np

#Holds class names
#names = ['Number 1', 'Number 2', 'Number 3', 'Number 4', 'Number 5', 'Number 6', 'Number 7', 'Number 8', 'Number 9', 'Alphabet A', 
         #'Alphabet B', 'Alphabet C', 'Alphabet D', 'Alphabet E', 'Alphabet F', 'Alphabet G', 'Alphabet H', 'Alphabet S', 'Alphabet T', 
         #'Alphabet U', 'Alphabet V', 'Alphabet W', 'Alphabet X', 'Alphabet Y', 'Alphabet Z', 'Up Arrow', 'Down Arrow', 'Right Arrow', 'Left Arrow', 
         #'Stop sign', 'Bullseye']

model = YOLO('v9_task1.pt')

#Only using for testing
def predictImages():
    #path to folder containing saved frame images from pi camera
    imageFolder = 'picam_images'
    
    for root, dirs, files in os.walk(imageFolder):
        for file in files:
            image_path = os.path.join(root, file)
            with Image.open(image_path) as img:
                # Append the image object to the list
                model.predict(img, save=True, imgsz=640, conf=0.9) #For testing prototyping only, remove when integrating with robot

def archiveImages():
    imageFolder = 'picam_images' #Change to where picam frames are saved.
    archiveFolder = 'picam_archive' #change to folder where you want to archive images.

    for files in os.walk(imageFolder):
        for file in files:
            src_path = os.path.join(imageFolder, file)
            dst_path = os.path.join(archiveFolder, file)
            os.rename(src_path, dst_path)

def stitchImages():
    images = []
    #change path to where pi camera frames are being saved.
    imageFolder = 'runs/segment/Predict'

    for root, dirs, files in os.walk(imageFolder):
        for file in files:
            image_path = os.path.join(root, file)
            img = cv2.imread(image_path)
            if img is not None:
                img = cv2.resize(img, (320,320))
                images.append(img)
                #print("Image appended to list")

    column1, column2, column3, column4, canvas = None
    if (len(images) == 2):
        column1 = np.vstack([images[0],images[1]])
        canvas = np.hstack(column1)
    elif (len(images) == 3):
        column1 = np.vstack([images[0],images[1]])
        column2 = np.vstack([images[2]])
        canvas = np.hstack([column1,column2])
    elif (len(images) == 4):
        column1 = np.vstack([images[0],images[1]])
        column2 = np.vstack([images[2],images[3]])
        canvas = np.hstack([column1,column2])
    elif (len(images) == 5):
        column1 = np.vstack([images[0],images[1]])
        column2 = np.vstack([images[2],images[3]])
        column3 = np.vstack([images[4]])
        canvas = np.hstack([column1,column2,column3])
    elif (len(images) == 6):
        column1 = np.vstack([images[0],images[1]])
        column2 = np.vstack([images[2],images[3]])
        column3 = np.vstack([images[4],images[5]])
        canvas = np.hstack([column1,column2,column3])
    elif (len(images) == 7):
        column1 = np.vstack([images[0],images[1]])
        column2 = np.vstack([images[2],images[3]])
        column3 = np.vstack([images[4],images[5]])
        column4 = np.vstack([images[6]])
        canvas = np.hstack([column1,column2,column3,column4])
    else:
        column1 = np.vstack([images[0],images[1]])
        column2 = np.vstack([images[2],images[3]])
        column3 = np.vstack([images[4],images[5]])
        column4 = np.vstack([images[6],images[7]])
        canvas = np.hstack([column1,column2,column3,column4])
    
    # Display collage
    cv2.imshow("Collage", canvas)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Save collage and save a copy
    cv2.imwrite("collage.jpg", canvas)
    archiveImages()

#predictImages()
stitchImages()
