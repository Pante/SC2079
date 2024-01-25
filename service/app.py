from __future__ import annotations

from flasgger import Swagger
from flask import Flask

from pathfinding.pathfinding_controller import pathfinding_blueprint

app = Flask(__name__)
swagger = Swagger(app)

app.register_blueprint(pathfinding_blueprint)


@app.route('/image/prediction', methods=['POST'])
def image_prediction():
    return 'Hello World!'


@app.route('/image/stitch', methods=['GET'])
def image_stitch():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
