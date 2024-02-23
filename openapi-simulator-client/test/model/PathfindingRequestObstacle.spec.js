/**
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

(function(root, factory) {
  if (typeof define === 'function' && define.amd) {
    // AMD.
    define(['expect.js', process.cwd()+'/src/index'], factory);
  } else if (typeof module === 'object' && module.exports) {
    // CommonJS-like environments that support module.exports, like Node.
    factory(require('expect.js'), require(process.cwd()+'/src/index'));
  } else {
    // Browser globals (root is window)
    factory(root.expect, root.MdpApi);
  }
}(this, function(expect, MdpApi) {
  'use strict';

  var instance;

  beforeEach(function() {
    instance = new MdpApi.PathfindingRequestObstacle();
  });

  var getProperty = function(object, getter, property) {
    // Use getter method if present; otherwise, get the property directly.
    if (typeof object[getter] === 'function')
      return object[getter]();
    else
      return object[property];
  }

  var setProperty = function(object, setter, property, value) {
    // Use setter method if present; otherwise, set the property directly.
    if (typeof object[setter] === 'function')
      object[setter](value);
    else
      object[property] = value;
  }

  describe('PathfindingRequestObstacle', function() {
    it('should create an instance of PathfindingRequestObstacle', function() {
      // uncomment below and update the code to test PathfindingRequestObstacle
      //var instance = new MdpApi.PathfindingRequestObstacle();
      //expect(instance).to.be.a(MdpApi.PathfindingRequestObstacle);
    });

    it('should have the property direction (base name: "direction")', function() {
      // uncomment below and update the code to test the property direction
      //var instance = new MdpApi.PathfindingRequestObstacle();
      //expect(instance).to.be();
    });

    it('should have the property imageId (base name: "image_id")', function() {
      // uncomment below and update the code to test the property imageId
      //var instance = new MdpApi.PathfindingRequestObstacle();
      //expect(instance).to.be();
    });

    it('should have the property northEast (base name: "north_east")', function() {
      // uncomment below and update the code to test the property northEast
      //var instance = new MdpApi.PathfindingRequestObstacle();
      //expect(instance).to.be();
    });

    it('should have the property southWest (base name: "south_west")', function() {
      // uncomment below and update the code to test the property southWest
      //var instance = new MdpApi.PathfindingRequestObstacle();
      //expect(instance).to.be();
    });

  });

}));