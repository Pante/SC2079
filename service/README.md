# Service

This module contains a REST API microservice that is responsible for the car's pathfinding and image recognition/stitching.
It exports 

## Building/Running

The module is created using Python 3.12 and Flask. It uses `pipenv` to manage dependencies. The following instructions
assume you're in the service directory.

To install dependencies:
```shell
pipenv install
```

To run the server:
```shell
python -m flask run
```

The Swagger documentation can be found at `/apidocs`. The corresponding OpenAPI **2** definitions is mentioned in the 
Swagger UI's hot bar. Flasgger doesn't seem to properly support OpenAPI 3 and I'm too lazy to switch to another
library/framework.