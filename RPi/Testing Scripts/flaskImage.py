import requests

def send_image_to_server(image_path):
    url = 'http://localhost:5000/rpi_image'
    files = {'image': open(image_path, 'rb')}
    response = requests.post(url, files=files)
    return response.json()

image_path = '' # path to the image saved in the system
response = send_image_to_server(image_path)
print(response) 
