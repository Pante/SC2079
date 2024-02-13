# PathfindingRequestRobot


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**direction** | [**Direction**](Direction.md) | The direction of the robot. | 
**north_east** | [**PathfindingPoint**](PathfindingPoint.md) | The north-east corner of the robot. | 
**south_west** | [**PathfindingPoint**](PathfindingPoint.md) | The south-west corner of the robot. | 

## Example

```python
from openapi_client.models.pathfinding_request_robot import PathfindingRequestRobot

# TODO update the JSON string below
json = "{}"
# create an instance of PathfindingRequestRobot from a JSON string
pathfinding_request_robot_instance = PathfindingRequestRobot.from_json(json)
# print the JSON string representation of the object
print PathfindingRequestRobot.to_json()

# convert the object into a dict
pathfinding_request_robot_dict = pathfinding_request_robot_instance.to_dict()
# create an instance of PathfindingRequestRobot from a dict
pathfinding_request_robot_form_dict = pathfinding_request_robot.from_dict(pathfinding_request_robot_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


