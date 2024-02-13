# ErrorContext

an optional object which contains values required to render the error message.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------

## Example

```python
from openapi_client.models.error_context import ErrorContext

# TODO update the JSON string below
json = "{}"
# create an instance of ErrorContext from a JSON string
error_context_instance = ErrorContext.from_json(json)
# print the JSON string representation of the object
print ErrorContext.to_json()

# convert the object into a dict
error_context_dict = error_context_instance.to_dict()
# create an instance of ErrorContext from a dict
error_context_form_dict = error_context.from_dict(error_context_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


