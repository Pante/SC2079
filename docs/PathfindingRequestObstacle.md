# PathfindingRequestObstacle


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**direction** | [**Direction**](Direction.md) | The direction of the image. | 
**image_id** | **int** | The image ID. | 
**north_east** | [**PathfindingPoint**](PathfindingPoint.md) | The north-east corner of the obstacle. | 
**south_west** | [**PathfindingPoint**](PathfindingPoint.md) | The south-west corner of the obstacle. | 

## Example

```python
from openapi_client.models.pathfinding_request_obstacle import PathfindingRequestObstacle

# TODO update the JSON string below
json = "{}"
# create an instance of PathfindingRequestObstacle from a JSON string
pathfinding_request_obstacle_instance = PathfindingRequestObstacle.from_json(json)
# print the JSON string representation of the object
print PathfindingRequestObstacle.to_json()

# convert the object into a dict
pathfinding_request_obstacle_dict = pathfinding_request_obstacle_instance.to_dict()
# create an instance of PathfindingRequestObstacle from a dict
pathfinding_request_obstacle_form_dict = pathfinding_request_obstacle.from_dict(pathfinding_request_obstacle_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


