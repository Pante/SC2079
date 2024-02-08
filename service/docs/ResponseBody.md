# ResponseBody


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**distance** | **float** |  | [optional] 
**instructions** | **List[object]** |  | [optional] 

## Example

```python
from openapi_client.models.response_body import ResponseBody

# TODO update the JSON string below
json = "{}"
# create an instance of ResponseBody from a JSON string
response_body_instance = ResponseBody.from_json(json)
# print the JSON string representation of the object
print ResponseBody.to_json()

# convert the object into a dict
response_body_dict = response_body_instance.to_dict()
# create an instance of ResponseBody from a dict
response_body_form_dict = response_body.from_dict(response_body_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


