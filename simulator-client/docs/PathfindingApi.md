# MdpApi.PathfindingApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**pathfindingPost**](PathfindingApi.md#pathfindingPost) | **POST** /pathfinding/ | 



## pathfindingPost

> PathfindingResponse pathfindingPost(pathfindingRequest)



### Example

```javascript
import MdpApi from 'mdp_api';

let apiInstance = new MdpApi.PathfindingApi();
let pathfindingRequest = new MdpApi.PathfindingRequest(); // PathfindingRequest | 
apiInstance.pathfindingPost(pathfindingRequest, (error, data, response) => {
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
 **pathfindingRequest** | [**PathfindingRequest**](PathfindingRequest.md)|  | 

### Return type

[**PathfindingResponse**](PathfindingResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

