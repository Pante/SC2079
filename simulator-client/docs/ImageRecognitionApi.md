# MdpApi.ImageRecognitionApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**imagePredictionTask1Post**](ImageRecognitionApi.md#imagePredictionTask1Post) | **POST** /image/prediction/task-1 | 
[**imagePredictionTask2Post**](ImageRecognitionApi.md#imagePredictionTask2Post) | **POST** /image/prediction/task-2 | 
[**imageStitchPost**](ImageRecognitionApi.md#imageStitchPost) | **POST** /image/stitch | 



## imagePredictionTask1Post

> ImagePredictionResponse imagePredictionTask1Post(file)



### Example

```javascript
import MdpApi from 'mdp_api';

let apiInstance = new MdpApi.ImageRecognitionApi();
let file = "/path/to/file"; // File | 
apiInstance.imagePredictionTask1Post(file, (error, data, response) => {
  if (error) {
    console.error(error);
  } else {
    console.log('API called successfully. Returned data: ' + data);
  }
});
```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file** | **File**|  | 

### Return type

[**ImagePredictionResponse**](ImagePredictionResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: multipart/form-data
- **Accept**: application/json


## imagePredictionTask2Post

> ImagePredictionResponse imagePredictionTask2Post(file)



### Example

```javascript
import MdpApi from 'mdp_api';

let apiInstance = new MdpApi.ImageRecognitionApi();
let file = "/path/to/file"; // File | 
apiInstance.imagePredictionTask2Post(file, (error, data, response) => {
  if (error) {
    console.error(error);
  } else {
    console.log('API called successfully. Returned data: ' + data);
  }
});
```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file** | **File**|  | 

### Return type

[**ImagePredictionResponse**](ImagePredictionResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: multipart/form-data
- **Accept**: application/json


## imageStitchPost

> imageStitchPost()



### Example

```javascript
import MdpApi from 'mdp_api';

let apiInstance = new MdpApi.ImageRecognitionApi();
apiInstance.imageStitchPost((error, data, response) => {
  if (error) {
    console.error(error);
  } else {
    console.log('API called successfully.');
  }
});
```

### Parameters

This endpoint does not need any parameter.

### Return type

null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: Not defined

