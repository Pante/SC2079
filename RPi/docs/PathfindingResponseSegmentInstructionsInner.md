# PathfindingResponseSegmentInstructionsInner


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **object** | The amount to move the robot in centimetres. | 
**move** | [**Move**](Move.md) |  | 

## Example

```python
from openapi_client.models.pathfinding_response_segment_instructions_inner import PathfindingResponseSegmentInstructionsInner

# TODO update the JSON string below
json = "{}"
# create an instance of PathfindingResponseSegmentInstructionsInner from a JSON string
pathfinding_response_segment_instructions_inner_instance = PathfindingResponseSegmentInstructionsInner.from_json(json)
# print the JSON string representation of the object
print PathfindingResponseSegmentInstructionsInner.to_json()

# convert the object into a dict
pathfinding_response_segment_instructions_inner_dict = pathfinding_response_segment_instructions_inner_instance.to_dict()
# create an instance of PathfindingResponseSegmentInstructionsInner from a dict
pathfinding_response_segment_instructions_inner_form_dict = pathfinding_response_segment_instructions_inner.from_dict(pathfinding_response_segment_instructions_inner_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


