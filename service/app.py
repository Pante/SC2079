from __future__ import annotations

import logging

from flask_openapi3 import Info, OpenAPI
from flask_cors import CORS

from pathfinding.pathfinding_controller import api as pathfinding_api


app = OpenAPI(__name__, info=Info(title='MDP API', version='1.0.0'))
app.register_api(pathfinding_api)
CORS(app)

logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    app.run(host='192.168.14.13', port=5001)
