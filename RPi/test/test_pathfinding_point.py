# coding: utf-8

"""
    MDP API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)

    The version of the OpenAPI document: 1.0.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest

from openapi_client.models.pathfinding_point import PathfindingPoint

class TestPathfindingPoint(unittest.TestCase):
    """PathfindingPoint unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> PathfindingPoint:
        """Test PathfindingPoint
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `PathfindingPoint`
        """
        model = PathfindingPoint()
        if include_optional:
            return PathfindingPoint(
                x = 0.0,
                y = 0.0
            )
        else:
            return PathfindingPoint(
                x = 0.0,
                y = 0.0,
        )
        """

    def testPathfindingPoint(self):
        """Test PathfindingPoint"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
