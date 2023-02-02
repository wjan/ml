
import torch
import matplotlib.pyplot as plt 
import cv2
import threading

import numpy as np
from PIL import Image
import sys
from tkinter import Tk, Canvas
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)


plt.switch_backend('qtagg')
#cap = cv2.VideoCapture('rtsp://tapoadmin:tapoadmin@192.168.0.207/stream1')
cap = cv2.VideoCapture(42)

midas = torch.hub.load('intel-isl/MiDaS', 'MiDaS_small')
midasDevice = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
midas.to(midasDevice)
print("Using device for MiDaS:", midasDevice)
#midas.to('cpu')
midas.eval()
# Input transformation pipeline
transforms = torch.hub.load('intel-isl/MiDaS', 'transforms')
transform = transforms.small_transform 

plotData = None

model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

plt.switch_backend('qtagg')

def computeVision(window, canvas):
    global plotData
    prevDict = {}


    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.axis('off')
    canvas2 = FigureCanvasTkAgg(fig, master=window)  # A tk.DrawingArea.
    canvas2.get_tk_widget().pack(expand=1)

    while cap.isOpened():
        ret, frame = cap.read()
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        imgbatch = transform(img).to(midasDevice)

        with torch.no_grad(): 
            prediction = midas(imgbatch)
            prediction = torch.nn.functional.interpolate(
                prediction.unsqueeze(1),
                size = img.shape[:2], 
                mode='bicubic', 
                align_corners=False
            ).squeeze()

            output = prediction.cpu().numpy()
        # plt.imshow(output)
        # plt.pause(0.00001)

        frame = frame[:, :, [2,1,0]]
        frame = Image.fromarray(frame) 
        frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
        result = model(frame)
        items = result.xyxy[0]

        currDict = {}
        tol = 40

        cv2.imshow('YOLO', np.squeeze(result.render()))
        canvas.delete("all")
        for index in range(len(items)):
            added = False
            item = items[index].cpu().numpy()

            xcenter = int((item[0] + item[2]) / 2)
            ycenter = int((item[1] + item[3]) / 2)
            depth = int(output[ycenter][xcenter] * 1.6)
            scaleFactor = 0.5 - output[ycenter][xcenter] / 650 #0-1
            #scale = int(item[2] - item[0]) * scaleFactor
            scale = 50

            if item[5] in prevDict:
                prev = prevDict[item[5]]
                for i in range(len(prev)):
                    if (abs(prev[i]['x'] - xcenter) < tol) and (abs(prev[i]['y'] - depth) < tol):
                        if item[5] in currDict:
                            currDict[item[5]].append(prev[i])
                        else:
                            currDict[item[5]] = [prev[i]]
                        added = True
                        #print("added", item[5])
                        break
            else:
                currDict[item[5]] = [{ 'x': xcenter, 'y': depth, 's': scale, 'c': item[5]}]
                added = True

            if not added:
                if item[5] in currDict:
                    currDict[item[5]].append({ 'x': xcenter, 'y': depth, 's': scale, 'c': item[5]})
                else:
                    currDict[item[5]] = [{ 'x': xcenter, 'y': depth, 's': scale, 'c': item[5]}]

        prevDict = currDict

        canvas.delete("all")
        for key in currDict:
            itemName = model.names[key]
            for i in range(len(currDict[key])):
                obj = currDict[key][i]
                color = f"#{'{0:03X}'.format(int(key) * 40)}"
                # canvas.create_oval(
                #         obj['x'], obj['y'],
                #         obj['x'] + obj['s'], obj['y'] + obj['s'],
                #         outline=color
                #         #fill=color
                # )
                canvas.create_rectangle(obj['x'], obj['y'], obj['x'] + obj['s'], obj['y'] + obj['s'], outline=color, width=3)
                canvas.create_text(obj['x'] + 20, obj['y'] - 10, text=itemName)
        
        ax.imshow(output)
        canvas2.draw()
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            sys.exit()



plt.show()
window = Tk()
canvas = Canvas(window, width = 1920, height = 1080)
canvas.pack()


t = threading.Thread(target=computeVision, args=(window, canvas))
t.start()
window.mainloop()
            