import cv2
import numpy as np
import requests
from ollama import chat
import time 
import requests

def invoke_car_control(command):
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7,ru;q=0.6',
        'Connection': 'keep-alive',
        'Referer': 'http://192.168.4.1/',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    }

    # Make the request
    response = requests.get('http://192.168.4.1/control?var=car&val=' + command, headers=headers, verify=False)
    
    # if response.status_code == 200:
    #     print("Request successful!")
    #     print("Response:", response.text)
    # else:
    #     print("Error:", response.status_code)

def car_control(direction, duration):
    command = 5

    direction = direction.lower().strip()

    if direction == "ahead":
        command = '1'
        duration = 500
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
    invoke_car_control(command)
    time.sleep(duration / 1000)
    invoke_car_control('5')
    invoke_car_control('5')


# Example usage




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
# car_control('left', 100)
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
        msg = {
            'role': 'user',
            # 'content': 'Imagine your task is to explore the scene and surrondings further to remember how many rooms you have found. What is the direction you want to take from here? Your answer should contain of two parts: a numeric value stating of number of rooms you have found and a single word from the given list to suggest new direction: left, right, forward or backward. Also give a total count of rooms you have found.',
            # 'content': 'Your task is to explore the scene and surrondings further to remember how many rooms you have found.' +
            # 'What is the direction you want me to move camera from here? Your answer should contain of two words: a numeric value stating number of unique rooms you have detected so far (including the history of previous messages) and a single word from the given list to suggest new direction: left, right, forward or backward. For example, the answer format should be: 1 left',
            # 'content': 'What do you see? Max 10 words answer',
            # 'content': 'You are a robot trying to explore the area. What is the furthest place you could go while avoiding obstacles on the floor? Please answer with just one word: forwad, backward, left, right.',
            'content': 'What is the furthest place you could go while avoiding obstacles on the floor? Answer with just one word: ahead, left, right.',
            # 'content': 'Where is the furthest place you could go while avoiding obstacles? Choose only one direction: left, right or ahead,',
            # 'content': 'What do you see?',
            'images': [frame],
        }
        response = chat(
        model='llava',
        messages=[msg],
        )

        

        print(response.message.content)
        car_control(response.message.content, 300)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()
