# PathfindingResponseMoveInstruction


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**amount** | **int** | The amount to move the robot in centimetres. | 
**move** | [**Move**](Move.md) |  | 

## Example

```python
from openapi_client.models.pathfinding_response_move_instruction import PathfindingResponseMoveInstruction

# TODO update the JSON string below
json = "{}"
# create an instance of PathfindingResponseMoveInstruction from a JSON string
pathfinding_response_move_instruction_instance = PathfindingResponseMoveInstruction.from_json(json)
# print the JSON string representation of the object
print PathfindingResponseMoveInstruction.to_json()

# convert the object into a dict
pathfinding_response_move_instruction_dict = pathfinding_response_move_instruction_instance.to_dict()
# create an instance of PathfindingResponseMoveInstruction from a dict
pathfinding_response_move_instruction_form_dict = pathfinding_response_move_instruction.from_dict(pathfinding_response_move_instruction_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


