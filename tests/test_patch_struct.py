"""
Contains test for the Structure patching classes
"""

from unittest import TestCase

from save_convert.save_converter_base import UNKNOWN_CONVERT_FORMAT
from save_convert.structs.patch_struct import PatchStructEndianSwap

from tests.test_marshal_struct import (
    TEST_MARSHAL_BYTES_TO_STRUCT_PARAM_LIST,
    TestStructure,
    test_structure_pretty_compare,
)


class TestPatchStructEndianSwap(TestCase):
    def setUp(self):
        self.addTypeEqualityFunc(TestStructure, test_structure_pretty_compare)

    def test_endian_swap_round_trip(self):
        for source_bytes, _ in TEST_MARSHAL_BYTES_TO_STRUCT_PARAM_LIST:
            with self.subTest(source_bytes):
                patcher = PatchStructEndianSwap(0, 0, TestStructure, byteorder="little")
                patch_result = patcher(source_bytes, 0, UNKNOWN_CONVERT_FORMAT)

                self.assertTrue(patch_result)
                # patch result should contain Big Endian data
                self.assertNotEqual(source_bytes, patch_result.target_data)

                # Patch the Big Endian data and the result should be the source data
                patcher = PatchStructEndianSwap(0, 0, TestStructure, byteorder="big")
                patch_result = patcher(patch_result.target_data, 0, UNKNOWN_CONVERT_FORMAT)

                self.assertTrue(patch_result)
                self.assertEqual(source_bytes, patch_result.target_data)
