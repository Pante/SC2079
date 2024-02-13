# PathfindingResponseSegment


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**cost** | [**Cost**](Cost.md) |  | 
**image_id** | **int** |  | 
**instructions** | [**List[PathfindingResponseSegmentInstructionsInner]**](PathfindingResponseSegmentInstructionsInner.md) |  | 
**path** | [**Path**](Path.md) |  | 

## Example

```python
from openapi_client.models.pathfinding_response_segment import PathfindingResponseSegment

# TODO update the JSON string below
json = "{}"
# create an instance of PathfindingResponseSegment from a JSON string
pathfinding_response_segment_instance = PathfindingResponseSegment.from_json(json)
# print the JSON string representation of the object
print PathfindingResponseSegment.to_json()

# convert the object into a dict
pathfinding_response_segment_dict = pathfinding_response_segment_instance.to_dict()
# create an instance of PathfindingResponseSegment from a dict
pathfinding_response_segment_form_dict = pathfinding_response_segment.from_dict(pathfinding_response_segment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


