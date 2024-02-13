# openapi_client.ImageRecognitionApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**image_prediction_task1_post**](ImageRecognitionApi.md#image_prediction_task1_post) | **POST** /image/prediction/task-1 | 
[**image_prediction_task2_post**](ImageRecognitionApi.md#image_prediction_task2_post) | **POST** /image/prediction/task-2 | 
[**image_stitch_post**](ImageRecognitionApi.md#image_stitch_post) | **POST** /image/stitch | 


# **image_prediction_task1_post**
> ImagePredictionResponse image_prediction_task1_post(file)



### Example


```python
import openapi_client
from openapi_client.models.image_prediction_response import ImagePredictionResponse
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
    api_instance = openapi_client.ImageRecognitionApi(api_client)
    file = None # bytearray | 

    try:
        api_response = api_instance.image_prediction_task1_post(file)
        print("The response of ImageRecognitionApi->image_prediction_task1_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ImageRecognitionApi->image_prediction_task1_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file** | **bytearray**|  | 

### Return type

[**ImagePredictionResponse**](ImagePredictionResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**422** | Unprocessable Entity |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **image_prediction_task2_post**
> ImagePredictionResponse image_prediction_task2_post(file)



### Example


```python
import openapi_client
from openapi_client.models.image_prediction_response import ImagePredictionResponse
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
    api_instance = openapi_client.ImageRecognitionApi(api_client)
    file = None # bytearray | 

    try:
        api_response = api_instance.image_prediction_task2_post(file)
        print("The response of ImageRecognitionApi->image_prediction_task2_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ImageRecognitionApi->image_prediction_task2_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file** | **bytearray**|  | 

### Return type

[**ImagePredictionResponse**](ImagePredictionResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**422** | Unprocessable Entity |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **image_stitch_post**
> image_stitch_post()



### Example


```python
import openapi_client
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
    api_instance = openapi_client.ImageRecognitionApi(api_client)

    try:
        api_instance.image_stitch_post()
    except Exception as e:
        print("Exception when calling ImageRecognitionApi->image_stitch_post: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined


[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

