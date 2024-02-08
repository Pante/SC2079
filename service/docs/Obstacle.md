# Obstacle


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**direction** | **str** |  | 
**north_east** | **List[int]** |  | 
**south_west** | **List[int]** |  | 

## Example

```python
from openapi_client.models.obstacle import Obstacle

# TODO update the JSON string below
json = "{}"
# create an instance of Obstacle from a JSON string
obstacle_instance = Obstacle.from_json(json)
# print the JSON string representation of the object
print Obstacle.to_json()

# convert the object into a dict
obstacle_dict = obstacle_instance.to_dict()
# create an instance of Obstacle from a dict
obstacle_form_dict = obstacle.from_dict(obstacle_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


