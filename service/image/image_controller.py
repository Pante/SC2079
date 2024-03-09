from __future__ import annotations

from flask_openapi3 import APIBlueprint, Tag

api = APIBlueprint(
    '/image',
    __name__,
    url_prefix='/image',
    abp_tags=[Tag(name='Image Recognition')],
)


@api.post('/stitch')
def image_stitch() -> None:
    # TODO: stitch images
    pass
