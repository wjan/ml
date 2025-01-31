
import torch
import matplotlib.pyplot as plt 
import cv2

import numpy as np
import sys
from quicker import Quicker
import threading
import time
plt.switch_backend('qtagg')
# cap = cv2.VideoCapture('rtsp://192.168.0.48:8554/stream0')
# plotData = None
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)


class YoloCar:
    last_direction = 'left'
    person_found = False
    prev_person_found = False

    def processFrame(self, frame):
        self.person_found = False
        if frame is not None:
            result = model(frame)
            cv2.imshow('YOLO', np.squeeze(result.render())),
            cv2.waitKey(1)
            items = result.xyxy[0]
            for index in range(len(items)):
                
                item = items[index].cpu().numpy()
                # if item[5] == 0 and item[4] > 0.3:
                if item[5] in [2, 3, 5, 6, 7, 8]:
                    quicker.light_on(255)
                    
                    xcenter = int((item[0] + item[2]) / 2)
                    width = frame.shape[1]
                    # height = frame.shape[0]
                    center = width / 2
                    offset = (xcenter - center) / width

                    if item[2] - item[0] > width / 3:
                        quicker.light_on(0)
                        quicker.car_control('stop', 300)
                        quicker.car_control("backward", 300)
                        time.sleep(0.1)
                        quicker.car_control('stop', 300)
                        quicker.car_control(self.last_direction, 300)
                        time.sleep(0.5)
                        quicker.car_control('stop', 300)
                        quicker.light_on(1)
                    else:
                        self.person_found = True

                        if not self.prev_person_found:
                            # stop from spinning
                            quicker.car_control('stop', 100)

                        if offset < 0:
                            self.last_direction = 'left'
                        else:
                            self.last_direction = 'right'

                        print(offset)

                        if offset < -0.2:
                            quicker.light_on(255)
                            quicker.car_control('stop', 300)
                            quicker.car_control('left', 300)
                            time.sleep(0.1)
                            quicker.light_on(0)
                            quicker.car_control('stop', 300)
                            time.sleep(0.2)
                            quicker.light_on(255)

                            print(f"Go left")
                        elif offset > 0.2:
                            quicker.light_on(255)
                            quicker.car_control('stop', 300)
                            quicker.car_control('right', 300)
                            time.sleep(0.1)
                            quicker.light_on(0)
                            quicker.car_control('stop', 300)
                            time.sleep(0.2)
                            quicker.light_on(255)

                        else:
                            quicker.car_control('ahead', 100)
                            print(f"Go ahead")
                            time.sleep(0.3)
                            quicker.car_control('stop', 100)

            if self.person_found == False:
                quicker.light_on(1)

                # if self.prev_person_found:
                #     quicker.car_control('stop', 300)
                
                quicker.car_control('stop', 300)
                quicker.car_control(self.last_direction, 300)
                time.sleep(0.1)
                quicker.car_control('stop', 300)
                time.sleep(0.2)

                print(f"Spin")

            self.prev_person_found = self.person_found

        


quicker = Quicker()
yoloCar = YoloCar()

quicker.main(yoloCar.processFrame)
# t1 = threading.Thread(target=quicker.main)
# t1.start()
# while True:
    # processFrame(quicker.frame)
# cv2.destroyAllWindows()

