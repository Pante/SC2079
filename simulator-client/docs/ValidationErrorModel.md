# ValidationErrorModel


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**ctx** | [**ErrorContext**](ErrorContext.md) |  | [optional] 
**loc** | [**Location**](Location.md) |  | [optional] 
**msg** | [**Message**](Message.md) |  | [optional] 
**type_** | [**ErrorType**](ErrorType.md) |  | [optional] 

## Example

```python
from openapi_client.models.validation_error_model import ValidationErrorModel

# TODO update the JSON string below
json = "{}"
# create an instance of ValidationErrorModel from a JSON string
validation_error_model_instance = ValidationErrorModel.from_json(json)
# print the JSON string representation of the object
print ValidationErrorModel.to_json()

# convert the object into a dict
validation_error_model_dict = validation_error_model_instance.to_dict()
# create an instance of ValidationErrorModel from a dict
validation_error_model_form_dict = validation_error_model.from_dict(validation_error_model_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


