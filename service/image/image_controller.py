from __future__ import annotations

import os
from http import HTTPStatus

from flask import make_response
from flask_openapi3 import APIBlueprint, Tag, FileStorage
from pydantic import BaseModel

api = APIBlueprint(
    '/image',
    __name__,
    url_prefix='/image',
    abp_tags=[Tag(name='Image Recognition')],
)


class ImagePredictionRequest(BaseModel):
    file: FileStorage


class ImagePredictionResponse(BaseModel):
    obstacle_id: int
    image_id: int


@api.post('/prediction/task-1', responses={200: ImagePredictionResponse})
def image_prediction_task1(form: ImagePredictionRequest):
    file, obstacle_id, signal = __parse(form)

    # TODO: Pass into model & return image id
    prediction_response = ImagePredictionResponse(obstacle_id=1, image_id=2)

    response = make_response(prediction_response.model_dump(mode='json'), HTTPStatus.OK)
    response.mimetype = "application/json"
    return response


@api.post('/prediction/task-2', responses={200: ImagePredictionResponse})
def image_prediction_task2(form: ImagePredictionRequest):
    file, obstacle_id, signal = __parse(form)

    # TODO: Pass into model & return image id
    prediction_response = ImagePredictionResponse(obstacle_id=1, image_id=2)

    response = make_response(prediction_response.model_dump(mode='json'), HTTPStatus.OK)
    response.mimetype = "application/json"
    return response


def __parse(form: ImagePredictionRequest) -> tuple[str, str, str]:
    file = form.file
    file.save(os.path.join('uploads', form.file.filename))
    # filename format: "<timestamp>_<obstacle_id>_<signal>.jpeg"
    constituents = file.filename.split("_")
    obstacle_id = constituents[1]
    signal = constituents[2].strip(".jpg")

    return file.filename, obstacle_id, signal


@api.post('/stitch')
def image_stitch() -> None:
    # TODO: stitch images
    pass
