import torch
import cv2
import numpy as np
from PIL import Image
import sys
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

#cap = cv2.VideoCapture('rtsp://tapoadmin:tapoadmin@192.168.0.207/stream1')
cap = cv2.VideoCapture(0)
while cap.isOpened():
    ret, frame = cap.read()
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    frame = frame[:, :, [2,1,0]]
    frame = Image.fromarray(frame) 
    frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
    result = model(frame)

    # Results
    result.print()
    # results.show()  # or .show()
    cv2.imshow('YOLO', np.squeeze(result.render()))

    result.xyxy[0]  # img1 predictions (tensor)
    result.pandas().xyxy[0]
    if cv2.waitKey(1) & 0xFF == ord('q'):
        sys.exit()

cv2.destroyAllWindows()