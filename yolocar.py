
import torch
import matplotlib.pyplot as plt 
import cv2

import numpy as np
import sys
from quicker import Quicker

plt.switch_backend('qtagg')
cap = cv2.VideoCapture('rtsp://192.168.0.48:8554/stream0')
plotData = None
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
    # cv2.imshow('YOLO', np.squeeze(result.render())),
    items = result.xyxy[0]
    for index in range(len(items)):
        if item[5] == 0:
            item = items[index].cpu().numpy()

            xcenter = int((item[0] + item[2]) / 2)

            width = frame.shape[1]
            center = width / 2
            
            offset = (xcenter - center) / width

            print(offset)
            if offset < -0.1:
                quicker.car_control('right', 100)
            elif offset > 0.1:
                quicker.car_control('left', 100)
            else:
                quicker.car_control('ahead', 100)

        



quicker.main(processFrame)
# computeVision()

