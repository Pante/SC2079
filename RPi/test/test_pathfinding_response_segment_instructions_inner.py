# coding: utf-8

"""
    MDP API

    No description provided (generated by Openapi Generator https://github.com/openapitools/openapi-generator)

    The version of the OpenAPI document: 1.0.0
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest

from openapi_client.models.pathfinding_response_segment_instructions_inner import PathfindingResponseSegmentInstructionsInner

class TestPathfindingResponseSegmentInstructionsInner(unittest.TestCase):
    """PathfindingResponseSegmentInstructionsInner unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> PathfindingResponseSegmentInstructionsInner:
        """Test PathfindingResponseSegmentInstructionsInner
            include_option is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `PathfindingResponseSegmentInstructionsInner`
        """
        model = PathfindingResponseSegmentInstructionsInner()
        if include_optional:
            return PathfindingResponseSegmentInstructionsInner(
                amount = None,
                move = 'FORWARD'
            )
        else:
            return PathfindingResponseSegmentInstructionsInner(
                amount = None,
                move = 'FORWARD',
        )
        """

    def testPathfindingResponseSegmentInstructionsInner(self):
        """Test PathfindingResponseSegmentInstructionsInner"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
