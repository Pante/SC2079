# ImagePredictionResponse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**image_id** | **int** |  | 
**obstacle_id** | **int** |  | 

## Example

```python
from openapi_client.models.image_prediction_response import ImagePredictionResponse

# TODO update the JSON string below
json = "{}"
# create an instance of ImagePredictionResponse from a JSON string
image_prediction_response_instance = ImagePredictionResponse.from_json(json)
# print the JSON string representation of the object
print ImagePredictionResponse.to_json()

# convert the object into a dict
image_prediction_response_dict = image_prediction_response_instance.to_dict()
# create an instance of ImagePredictionResponse from a dict
image_prediction_response_form_dict = image_prediction_response.from_dict(image_prediction_response_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


