# Service

This module contains a REST API microservice that is responsible for the car's pathfinding and image recognition/stitching.
It exports 

## Building/Running

The module is created using Python 3.12 and `flask-openapi3`. It uses `pipenv` to manage dependencies. The following 
instructions assumes you're already in the service directory.

Else, change to service directory:
```shell
cd service
```

To install dependencies:
```shell
pipenv install
```

To run the server:
```shell
python -m flask run
```

The Swagger documentation can be found at `http://localhost:5000/openapi/swagger`. Alternatively, the OpenAPI definitions 
can be downloaded directly at http://localhost:5000/openapi/openapi.json (useful if you're planning to generate an OpenAPI client).