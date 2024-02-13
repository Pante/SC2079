# coding: utf-8

"""
    MDP API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)

    The version of the OpenAPI document: 1.0.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest

from openapi_client.models.pathfinding_request_robot import PathfindingRequestRobot

class TestPathfindingRequestRobot(unittest.TestCase):
    """PathfindingRequestRobot unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> PathfindingRequestRobot:
        """Test PathfindingRequestRobot
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `PathfindingRequestRobot`
        """
        model = PathfindingRequestRobot()
        if include_optional:
            return PathfindingRequestRobot(
                direction = 'NORTH',
                north_east = openapi_client.models.pathfinding_point.PathfindingPoint(
                    x = 0.0, 
                    y = 0.0, ),
                south_west = openapi_client.models.pathfinding_point.PathfindingPoint(
                    x = 0.0, 
                    y = 0.0, )
            )
        else:
            return PathfindingRequestRobot(
                direction = 'NORTH',
                north_east = openapi_client.models.pathfinding_point.PathfindingPoint(
                    x = 0.0, 
                    y = 0.0, ),
                south_west = openapi_client.models.pathfinding_point.PathfindingPoint(
                    x = 0.0, 
                    y = 0.0, ),
        )
        """

    def testPathfindingRequestRobot(self):
        """Test PathfindingRequestRobot"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()