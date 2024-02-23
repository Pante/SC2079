"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = void 0;
var _ApiClient = _interopRequireDefault(require("../ApiClient"));
var _ImagePredictionResponse = _interopRequireDefault(require("../model/ImagePredictionResponse"));
var _ValidationErrorModel = _interopRequireDefault(require("../model/ValidationErrorModel"));
function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { "default": obj }; }
function _typeof(o) { "@babel/helpers - typeof"; return _typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o; }, _typeof(o); }
function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }
function _defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, _toPropertyKey(descriptor.key), descriptor); } }
function _createClass(Constructor, protoProps, staticProps) { if (protoProps) _defineProperties(Constructor.prototype, protoProps); if (staticProps) _defineProperties(Constructor, staticProps); Object.defineProperty(Constructor, "prototype", { writable: false }); return Constructor; }
function _toPropertyKey(t) { var i = _toPrimitive(t, "string"); return "symbol" == _typeof(i) ? i : String(i); }
function _toPrimitive(t, r) { if ("object" != _typeof(t) || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r || "default"); if ("object" != _typeof(i)) return i; throw new TypeError("@@toPrimitive must return a primitive value."); } return ("string" === r ? String : Number)(t); } /**
 * MDP API
 * No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)
 *
 * The version of the OpenAPI document: 1.0.0
 * 
 *
 * NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).
 * https://openapi-generator.tech
 * Do not edit the class manually.
 *
 */
/**
* ImageRecognition service.
* @module api/ImageRecognitionApi
* @version 1.0.0
*/
var ImageRecognitionApi = exports["default"] = /*#__PURE__*/function () {
  /**
  * Constructs a new ImageRecognitionApi. 
  * @alias module:api/ImageRecognitionApi
  * @class
  * @param {module:ApiClient} [apiClient] Optional API client implementation to use,
  * default to {@link module:ApiClient#instance} if unspecified.
  */
  function ImageRecognitionApi(apiClient) {
    _classCallCheck(this, ImageRecognitionApi);
    this.apiClient = apiClient || _ApiClient["default"].instance;
  }

  /**
   * Callback function to receive the result of the imagePredictionTask1Post operation.
   * @callback module:api/ImageRecognitionApi~imagePredictionTask1PostCallback
   * @param {String} error Error message, if any.
   * @param {module:model/ImagePredictionResponse} data The data returned by the service call.
   * @param {String} response The complete HTTP response.
   */

  /**
   * @param {File} file 
   * @param {module:api/ImageRecognitionApi~imagePredictionTask1PostCallback} callback The callback function, accepting three arguments: error, data, response
   * data is of type: {@link module:model/ImagePredictionResponse}
   */
  _createClass(ImageRecognitionApi, [{
    key: "imagePredictionTask1Post",
    value: function imagePredictionTask1Post(file, callback) {
      var postBody = null;
      // verify the required parameter 'file' is set
      if (file === undefined || file === null) {
        throw new Error("Missing the required parameter 'file' when calling imagePredictionTask1Post");
      }
      var pathParams = {};
      var queryParams = {};
      var headerParams = {};
      var formParams = {
        'file': file
      };
      var authNames = [];
      var contentTypes = ['multipart/form-data'];
      var accepts = ['application/json'];
      var returnType = _ImagePredictionResponse["default"];
      return this.apiClient.callApi('/image/prediction/task-1', 'POST', pathParams, queryParams, headerParams, formParams, postBody, authNames, contentTypes, accepts, returnType, null, callback);
    }

    /**
     * Callback function to receive the result of the imagePredictionTask2Post operation.
     * @callback module:api/ImageRecognitionApi~imagePredictionTask2PostCallback
     * @param {String} error Error message, if any.
     * @param {module:model/ImagePredictionResponse} data The data returned by the service call.
     * @param {String} response The complete HTTP response.
     */

    /**
     * @param {File} file 
     * @param {module:api/ImageRecognitionApi~imagePredictionTask2PostCallback} callback The callback function, accepting three arguments: error, data, response
     * data is of type: {@link module:model/ImagePredictionResponse}
     */
  }, {
    key: "imagePredictionTask2Post",
    value: function imagePredictionTask2Post(file, callback) {
      var postBody = null;
      // verify the required parameter 'file' is set
      if (file === undefined || file === null) {
        throw new Error("Missing the required parameter 'file' when calling imagePredictionTask2Post");
      }
      var pathParams = {};
      var queryParams = {};
      var headerParams = {};
      var formParams = {
        'file': file
      };
      var authNames = [];
      var contentTypes = ['multipart/form-data'];
      var accepts = ['application/json'];
      var returnType = _ImagePredictionResponse["default"];
      return this.apiClient.callApi('/image/prediction/task-2', 'POST', pathParams, queryParams, headerParams, formParams, postBody, authNames, contentTypes, accepts, returnType, null, callback);
    }

    /**
     * Callback function to receive the result of the imageStitchPost operation.
     * @callback module:api/ImageRecognitionApi~imageStitchPostCallback
     * @param {String} error Error message, if any.
     * @param data This operation does not return a value.
     * @param {String} response The complete HTTP response.
     */

    /**
     * @param {module:api/ImageRecognitionApi~imageStitchPostCallback} callback The callback function, accepting three arguments: error, data, response
     */
  }, {
    key: "imageStitchPost",
    value: function imageStitchPost(callback) {
      var postBody = null;
      var pathParams = {};
      var queryParams = {};
      var headerParams = {};
      var formParams = {};
      var authNames = [];
      var contentTypes = [];
      var accepts = [];
      var returnType = null;
      return this.apiClient.callApi('/image/stitch', 'POST', pathParams, queryParams, headerParams, formParams, postBody, authNames, contentTypes, accepts, returnType, null, callback);
    }
  }]);
  return ImageRecognitionApi;
}();