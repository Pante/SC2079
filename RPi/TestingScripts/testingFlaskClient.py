import requests
from flasgger import Swagger, swag_from
from flask import Flask, request

url = "http://localhost:5000/rpi"  # Replace 'localhost:5000' with the actual server address

# Your request payload
payload = {
    # Add your request parameters here
    "action": "move",
    "description": "Move the robot forward by 1 meter",
}

# Send the POST request
response = requests.post(url, json=payload)

# Check the response status code
if response.status_code == 200:
    print(response.text)
    print("Request successful")
else:
    print("Request failed")
