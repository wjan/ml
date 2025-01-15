import cv2
import numpy as np
import time 
import requests

class Quicker:
    def invoke_car_control(self, command):
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7,ru;q=0.6',
            'Connection': 'keep-alive',
            'Referer': 'http://192.168.4.1/',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        }
        requests.get('http://192.168.4.1/control?var=car&val=' + command, headers=headers, verify=False)
    

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
        self.invoke_car_control(command)
        time.sleep(duration / 1000)
        self.invoke_car_control('5')
        self.invoke_car_control('5')


    def main(self, callback):
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
                if frame is not None:
                    cv2.imshow('Video Stream', frame)
                frame = cv2.imencode(".png", frame)[1].tobytes()
                callback(frame)


