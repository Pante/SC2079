# PathfindingRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**obstacles** | [**List[PathfindingRequestObstacle]**](PathfindingRequestObstacle.md) |  | 
**robot** | [**PathfindingRequestRobot**](PathfindingRequestRobot.md) | The initial position of the robot. | 
**verbose** | **bool** | Whether to attach the path and cost alongside the movement instructions in the response. | [optional] [default to True]

## Example

```python
from openapi_client.models.pathfinding_request import PathfindingRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PathfindingRequest from a JSON string
pathfinding_request_instance = PathfindingRequest.from_json(json)
# print the JSON string representation of the object
print PathfindingRequest.to_json()

# convert the object into a dict
pathfinding_request_dict = pathfinding_request_instance.to_dict()
# create an instance of PathfindingRequest from a dict
pathfinding_request_form_dict = pathfinding_request.from_dict(pathfinding_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


