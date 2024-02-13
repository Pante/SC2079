# PathfindingResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**segments** | [**List[PathfindingResponseSegment]**](PathfindingResponseSegment.md) | The data for moving the robot from the start/objective to another objective. | 

## Example

```python
from openapi_client.models.pathfinding_response import PathfindingResponse

# TODO update the JSON string below
json = "{}"
# create an instance of PathfindingResponse from a JSON string
pathfinding_response_instance = PathfindingResponse.from_json(json)
# print the JSON string representation of the object
print PathfindingResponse.to_json()

# convert the object into a dict
pathfinding_response_dict = pathfinding_response_instance.to_dict()
# create an instance of PathfindingResponse from a dict
pathfinding_response_form_dict = pathfinding_response.from_dict(pathfinding_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


