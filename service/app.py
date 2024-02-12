from __future__ import annotations

import logging

from flask_openapi3 import Info, OpenAPI

from pathfinding.pathfinding_controller import api as pathfinding_api


app = OpenAPI(__name__, info=Info(title='MDP API', version='1.0.0'))
app.register_api(pathfinding_api)

logging.basicConfig(level=logging.DEBUG)


# @app.post('/image/prediction/task-1')
# def image_prediction_task1():
#     pass
    # file, obstacle_id, signal = __parse(request)
    #
    # ## TODO: Pass into model & return image id
    # image_id = 'Foo'
    #
    # return jsonify({
    #     "obstacle_id": obstacle_id,
    #     "image_id": image_id
    # })


# @app.post('/image/prediction/task-2')
# def image_prediction_task2():
#     pass
    # file, obstacle_id, signal = __parse(request)
    #
    # ## TODO: Pass into model & return image id
    # image_id = 'Foo'
    #
    # return jsonify({
    #     "obstacle_id": obstacle_id,
    #     "image_id": image_id
    # })


# def __parse(request: Request) -> (str, str, str):
#     file = request.files['file']
#     file.save(os.path.join('uploads', file.filename))
#     # filename format: "<timestamp>_<obstacle_id>_<signal>.jpeg"
#     constituents = file.filename.split("_")
#     obstacle_id = constituents[1]
#     signal = constituents[2].strip(".jpg")
#
#     return file.filename, obstacle_id, signal


# @app.get('/image/stitch')
# def image_stitch() -> None:
#     # TODO: stitch images
#     pass


if __name__ == '__main__':
    app.run()
