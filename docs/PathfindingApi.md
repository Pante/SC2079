# openapi_client.PathfindingApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**pathfinding_post**](PathfindingApi.md#pathfinding_post) | **POST** /pathfinding/ | 


# **pathfinding_post**
> PathfindingResponse pathfinding_post(pathfinding_request)



### Example


```python
import openapi_client
from openapi_client.models.pathfinding_request import PathfindingRequest
from openapi_client.models.pathfinding_response import PathfindingResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.PathfindingApi(api_client)
    pathfinding_request = openapi_client.PathfindingRequest() # PathfindingRequest | 

    try:
        api_response = api_instance.pathfinding_post(pathfinding_request)
        print("The response of PathfindingApi->pathfinding_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PathfindingApi->pathfinding_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **pathfinding_request** | [**PathfindingRequest**](PathfindingRequest.md)|  | 

### Return type

[**PathfindingResponse**](PathfindingResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**422** | Unprocessable Entity |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

