import requests

def send_image_to_server(image_path):
    url = 'http://localhost:5000/rpi_image'
    files = {'image': open(image_path, 'rb')}
    response = requests.post(url, files=files)
    return response.text
    

image_path = 'Flask_Image_Testing/dog_input.jpg' # path to the image saved in the system
response = send_image_to_server(image_path)
print(response) 
