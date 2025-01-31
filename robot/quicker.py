import cv2
import numpy as np
import sys
import time 
import requests

class Quicker:

    frame = None

    def __init__(self):
        
        self.invoke_car_control("car", '5')
        self.invoke_car_control('flash', 255)
        # self.invoke_car_control('speed', 4)
        self.invoke_car_control('speed', 5)
        # self.invoke_car_control('quality', 37)
        self.invoke_car_control('quality', 20)
        self.invoke_car_control('framesize', 6)
        
        for i in range(0, 255):
            if i % 5 == 0:
                self.invoke_car_control('flash', 255 - i)

    def light_on(self, value):
        self.invoke_car_control('flash', value)
        
    def invoke_car_control(self, command, value):
        headers = {
            'Accept': '*/*'
        }
        requests.get(f"http://192.168.4.1/control?var={command}&val={value}", headers=headers, verify=False)
    

    def car_control(self, direction, duration):
        command = 5

        direction = direction.lower().strip()

        if direction == "ahead":
            command = '1'
            duration = 100
        elif direction == "backward":
            command = '2'
        elif direction == "left":
            command = '3'
            duration = 100
        elif direction == "right":
            command = '4'
            duration = 100
        elif direction == "stop":
            command = '5'
        self.invoke_car_control("car", command)
        # time.sleep(duration / 1000)
        # self.invoke_car_control("car", '5')
        #self.invoke_car_control('5')
        # time.sleep(0.5)


    def main(self, callback):
        url = 'http://192.168.4.1/capture'

        # Fetch the image using requests
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:134.0) Gecko/20100101 Firefox/134.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            # 'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Priority': 'u=0, i'
        }
        while True:
            response = requests.get(url, headers=headers)
            image_data = response.content

            # Convert the image data into a numpy array
            image_array = np.frombuffer(image_data, np.uint8)

            # Decode the image array into an OpenCV image
            self.frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            # self.frame = cv2.flip(self.frame, 0)
            # self.frame = cv2.flip(self.frame, 1)
            callback(self.frame)
            # time.sleep(0.1)




    def main2(self):
        stream_url = 'http://192.168.4.1:81/stream'
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7,ru;q=0.6',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        }

        # Open a connection to the stream
        response = requests.get(stream_url, headers=headers, stream=True)

        if response.status_code != 200:
            print("Error: Unable to open video stream")
            exit()

        bytes_data = b''
        for chunk in response.iter_content(chunk_size=1024):
            bytes_data += chunk
            a = bytes_data.find(b'\xff\xd8')
            b = bytes_data.find(b'\xff\xd9')

            if a != -1 and b != -1:
                jpg = bytes_data[a:b+2]
                bytes_data = bytes_data[b+2:]
                # Decode the image
                img_array = np.frombuffer(jpg, dtype=np.uint8)
                frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                frame = cv2.flip(frame, 0)
                frame = cv2.flip(frame, 1)

                self.frame = frame
                
        
        


