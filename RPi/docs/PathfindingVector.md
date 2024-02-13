# PathfindingVector


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**direction** | [**Direction**](Direction.md) | The direction | 
**x** | **int** |  | 
**y** | **int** |  | 

## Example

```python
from openapi_client.models.pathfinding_vector import PathfindingVector

# TODO update the JSON string below
json = "{}"
# create an instance of PathfindingVector from a JSON string
pathfinding_vector_instance = PathfindingVector.from_json(json)
# print the JSON string representation of the object
print PathfindingVector.to_json()

# convert the object into a dict
pathfinding_vector_dict = pathfinding_vector_instance.to_dict()
# create an instance of PathfindingVector from a dict
pathfinding_vector_form_dict = pathfinding_vector.from_dict(pathfinding_vector_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


