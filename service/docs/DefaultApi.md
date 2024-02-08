# openapi_client.DefaultApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**pathfinding_post**](DefaultApi.md#pathfinding_post) | **POST** /pathfinding | 


# **pathfinding_post**
> ResponseBody pathfinding_post(body)



### Example


```python
import time
import os
import openapi_client
from openapi_client.models.obstacle import Obstacle
from openapi_client.models.response_body import ResponseBody
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
    api_instance = openapi_client.DefaultApi(api_client)
    body = openapi_client.Obstacle() # Obstacle | 

    try:
        api_response = api_instance.pathfinding_post(body)
        print("The response of DefaultApi->pathfinding_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->pathfinding_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | [**Obstacle**](Obstacle.md)|  | 

### Return type

[**ResponseBody**](ResponseBody.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: */*

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful operation |  -  |
**400** | Invalid input |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

