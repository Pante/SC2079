from __future__ import annotations

import logging

from flask_openapi3 import Info, OpenAPI
from flask_cors import CORS

from pathfinding.pathfinding_controller import api as pathfinding_api
from image.image_controller import api as image_api


app = OpenAPI(__name__, info=Info(title='MDP API', version='1.0.0'))
app.register_api(pathfinding_api)
app.register_api(image_api)
CORS(app)

logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    app.run(host='localhost', port=5001)
