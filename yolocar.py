
import torch
import matplotlib.pyplot as plt 
import cv2

import numpy as np
import sys
from quicker import Quicker

plt.switch_backend('qtagg')
# cap = cv2.VideoCapture('rtsp://192.168.0.48:8554/stream0')
# plotData = None
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

quicker = Quicker()

def computeVision():

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.axis('off')
    
    while cap.isOpened():
        ret, frame = cap.read()
        
        processFrame(frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            sys.exit()

def processFrame(frame):
    # print(frame.shape)
    result = model(frame)
    cv2.imshow('YOLO', np.squeeze(result.render())),
    cv2.waitKey(1)
    items = result.xyxy[0]
    person_found = False
    for index in range(len(items)):
        person_found = True
        item = items[index].cpu().numpy()
        if item[5] == 0:
            xcenter = int((item[0] + item[2]) / 2)

            width = frame.shape[1]
            center = width / 2
            
            offset = (xcenter - center) / width

            print(f"Width: {width}")
            print(f"Offset: {offset}")

            print(offset)
            if offset < -0.2:
                quicker.car_control('right', 100)
                print(f"Go left")
            elif offset > 0.2:
                quicker.car_control('left', 100)
                print(f"Go right")
            else:
                quicker.car_control('ahead', 100)
                print(f"Go ahead")
        if person_found == False:
            quicker.car_control('left', 100)
            print(f"Spin")

        



quicker.main(processFrame)
# computeVision()
cv2.destroyAllWindows()

