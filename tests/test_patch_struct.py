"""
Contains test for the Structure patching classes
"""

import struct
from collections.abc import Sequence
from ctypes import (
    Array,
    c_byte,
    c_char,
    c_double,
    c_float,
    c_int8,
    c_int16,
    c_int32,
    c_int64,
    c_ubyte,
    c_uint8,
    c_uint16,
    c_uint32,
    c_uint64,
    c_wchar,
    sizeof,
)
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, Any, NamedTuple
from unittest import TestCase

from ruamel.yaml import YAML
from save_convert.structs.marshal_structure import (
    EndianSwapStructure,
    FillEndianSwapStructure,
    OffsetField,
    StructureDict,
    StructureList,
)

if TYPE_CHECKING:
    from ctypes import _CT as CDataBound

SCRIPT_DIR = Path(__file__).parent.resolve()


class TestSimpleStructure(EndianSwapStructure):
    _fields_ = [
        ("simple_field1", c_int64),
        ("simple_field2", c_uint32),
    ]


class TestStructure(EndianSwapStructure):
    _fields_ = [
        ("int8_field", c_int8),
        ("uint8_field", c_uint8),
        ("int16_field", c_int16),
        ("uint16_field", c_uint16),
        ("int32_field", c_int32),
        ("uint32_field", c_uint32),
        ("int64_field", c_int64),
        ("uint64_field", c_uint64),
        ("float_field", c_float),
        ("double_field", c_double),
        ("ascii_array_field", c_char * 32),
        ("utf8_array_field", c_wchar * 32),
        ("raw_byte_array_field", c_byte * 32),
        ("nested_struct_field", TestSimpleStructure * 2),
        ("bitfield_0", c_byte, 1),
        ("bitfield_1", c_byte, 1),
        ("bitfield_2", c_byte, 1),
        ("bitfield_3", c_byte, 1),
        ("bitfield_4", c_byte, 1),
        ("bitfield_5", c_byte, 1),
        ("bitfield_6", c_byte, 1),
        ("bitfield_7", c_byte, 1),
        ("bitfield_8", c_byte, 1),
        ("bitfield_9", c_byte, 1),
        ("ubitfield_10", c_ubyte, 1),
        ("ubitfield_11", c_ubyte, 1),
        ("ubitfield_12_to_15", c_ubyte, 4),
    ]


class TestMarshalBytesToStruct(NamedTuple):
    source_bytes: bytes
    expected_struct: TestStructure


class TestMarshalBytesFromStruct(NamedTuple):
    source_struct: TestStructure
    expected_bytes: bytes


class TestMarshalStructureFromDict(NamedTuple):
    source_dict: StructureDict
    expected_struct: TestStructure


class TestMarshalStructureToDict(NamedTuple):
    source_struct: TestStructure
    expected_dict: StructureDict


class TestMarshalStructureFromYaml(NamedTuple):
    source_yaml: bytes
    expected_struct: TestStructure


class TestMarshalStructureToYaml(NamedTuple):
    source_struct: TestStructure
    expected_yaml: bytes


TEST_ARGUMENTS = (
    -5,
    127,
    -1024,
    1666,
    -126950,
    4346750,
    -(2**33),
    2**40,
    1.0,
    -2.0,
    b"Hello World",
    "Good Morning World",
    tuple([i for i in range(0, 32)]),
    (TestSimpleStructure(-42, 1337), TestSimpleStructure(-69, 8080)),
    # For signed bitfield type of 1-bit, a value of 1 would represent the value of -1
    # a signed type is by definition negative if the highest bit is 1.
    (-1, 1),
    (0, 1),
    (-1, 1),
    (-1, 1),
    (0, 1),
    (0, 1),
    (-1, 1),
    (0, 1),
    (-1, 1),
    (-1, 1),
    (0, 1),
    (1, 1),
    (0xA, 4),
)


TEST_VALUES = (
    *TEST_ARGUMENTS[:14],
    *tuple[int]((bit_value for bit_value, _ in TEST_ARGUMENTS[14:])),
)


def bitfields_to_bytes(bit_values_with_size: Sequence[tuple[int, int]]) -> bytes:
    output_bytes = bytearray()
    for i in range(0, len(bit_values_with_size)):
        bit_value = bit_values_with_size[i][0]
        bit_size = bit_values_with_size[i][1]
        if i % 8 == 0:
            output_bytes.append(0)
        output_bytes[-1] |= (bit_value & ((1 << bit_size) - 1)) << (i % 8)
    return bytes(output_bytes)


def string_to_bytes(str_val: bytes | str, field_byte_size: int) -> bytes:
    output_bytes = bytearray(str_val if isinstance(str_val, bytes) else str_val.encode("utf-32-le"))
    output_bytes.resize(field_byte_size)
    return bytes(output_bytes)


TEST_MARSHAL_BYTES_TO_STRUCT_PARAM_LIST: list[TestMarshalBytesToStruct] = [
    TestMarshalBytesToStruct(
        source_bytes=TEST_ARGUMENTS[0].to_bytes(1, signed=True)
        + TEST_ARGUMENTS[1].to_bytes(1)
        + TEST_ARGUMENTS[2].to_bytes(2, "little", signed=True)
        + TEST_ARGUMENTS[3].to_bytes(2, "little")
        + TEST_ARGUMENTS[4].to_bytes(4, "little", signed=True)
        + TEST_ARGUMENTS[5].to_bytes(4, "little")
        + TEST_ARGUMENTS[6].to_bytes(8, "little", signed=True)
        + TEST_ARGUMENTS[7].to_bytes(8, "little")
        + struct.pack("<f", TEST_ARGUMENTS[8])
        + struct.pack("<d", TEST_ARGUMENTS[9])
        + string_to_bytes(TEST_ARGUMENTS[10], 32 * sizeof(c_char))
        + string_to_bytes(TEST_ARGUMENTS[11], 32 * sizeof(c_wchar))
        + b"".join([i.to_bytes(1) for i in TEST_ARGUMENTS[12]])
        + b"".join(
            [
                int(getattr(nested_struct, "simple_field1")).to_bytes(8, "little", signed=True)
                + int(getattr(nested_struct, "simple_field2")).to_bytes(4, "little")
                for nested_struct in TEST_ARGUMENTS[13]
            ]
        )
        + bitfields_to_bytes(TEST_ARGUMENTS[14:]),
        expected_struct=TestStructure(*TEST_VALUES),
    )
]

TEST_MARSHAL_STRUCT_TO_BYTES_PARAM_LIST: list[TestMarshalBytesFromStruct] = [
    TestMarshalBytesFromStruct(struct_data, byte_data)
    for byte_data, struct_data in TEST_MARSHAL_BYTES_TO_STRUCT_PARAM_LIST
]


def test_struct_to_array(input_array: Sequence[Any] | Array[CDataBound]) -> StructureList:
    output_array: StructureList = []
    for field_value in input_array:
        if isinstance(field_value, EndianSwapStructure):
            sub_dict: StructureDict = test_struct_to_dict(field_value)
            output_array.append(sub_dict)
        elif isinstance(field_value, (Sequence, Array)) and not isinstance(field_value, (str, bytes)):
            sub_array = test_struct_to_array(field_value)
            output_array.append(sub_array)
        else:
            output_array.append(field_value)
    return output_array


def test_struct_to_dict(output_struct: EndianSwapStructure) -> StructureDict:
    output_dict: StructureDict = {}
    for field in output_struct._fields_:
        field_value = getattr(output_struct, field[0])
        if isinstance(field_value, EndianSwapStructure):
            sub_dict: StructureDict = test_struct_to_dict(field_value)
            output_dict[field[0]] = sub_dict
        elif isinstance(field_value, (Sequence, Array)) and not isinstance(field_value, (str, bytes)):
            sub_array = test_struct_to_array(field_value)
            output_dict[field[0]] = sub_array
        else:
            output_dict[field[0]] = field_value
    return output_dict


def arguments_to_dict(struct_type: type[EndianSwapStructure], test_arguments: tuple[Any, ...]) -> StructureDict:
    output_dict: StructureDict = {}
    for field_tup, value in zip(struct_type._fields_, test_arguments):
        if isinstance(value, EndianSwapStructure):
            sub_dict: StructureDict = test_struct_to_dict(value)
            output_dict[field_tup[0]] = sub_dict
        elif issubclass(field_tup[1], Array) and not isinstance(value, (str, bytes)):
            if field_tup[1]._type_ in [c_int8, c_uint8]:
                output_dict[field_tup[0]] = bytes(value).hex(" ")
            else:
                sub_array = test_struct_to_array(value)
                output_dict[field_tup[0]] = sub_array
        elif isinstance(value, bytes):
            output_dict[field_tup[0]] = value.hex(" ")
        else:
            output_dict[field_tup[0]] = value

    return output_dict


def arguments_to_yaml(struct_type: type[EndianSwapStructure], test_arguments: tuple[Any, ...]) -> bytes:

    output_dict: StructureDict = arguments_to_dict(struct_type, test_arguments)
    yaml = YAML()
    yaml_byte_stream = BytesIO()
    try:
        yaml.dump(output_dict, yaml_byte_stream)
    except AttributeError:
        return b""
    return yaml_byte_stream.getvalue()


TEST_MARSHAL_STRUCT_FROM_DICT_PARAM_LIST: list[TestMarshalStructureFromDict] = [
    TestMarshalStructureFromDict(
        arguments_to_dict(TestStructure, TEST_VALUES),
        expected_struct=TestStructure(*TEST_VALUES),
    )
]

TEST_MARSHAL_STRUCT_TO_DICT_PARAM_LIST: list[TestMarshalStructureToDict] = [
    TestMarshalStructureToDict(struct_data, dict_data)
    for dict_data, struct_data in TEST_MARSHAL_STRUCT_FROM_DICT_PARAM_LIST
]

TEST_MARSHAL_STRUCT_FROM_YAML_PARAM_LIST: list[TestMarshalStructureFromYaml] = [
    TestMarshalStructureFromYaml(
        arguments_to_yaml(TestStructure, TEST_VALUES),
        expected_struct=TestStructure(*TEST_VALUES),
    )
]

TEST_MARSHAL_STRUCT_TO_YAML_PARAM_LIST: list[TestMarshalStructureToYaml] = [
    TestMarshalStructureToYaml(struct_data, yaml_data)
    for yaml_data, struct_data in TEST_MARSHAL_STRUCT_FROM_YAML_PARAM_LIST
]


# Filled Structure metadata
TEST_FILLED_STRUCTURE_SIZE = 512


class TestFillStructure(FillEndianSwapStructure):  #  type: ignore[metaclass]
    _size_ = TEST_FILLED_STRUCTURE_SIZE
    _offset_fields_ = [
        OffsetField(4, ("int8_field", c_int8)),
        OffsetField(16, ("uint64_field", c_uint64)),
        OffsetField(28, ("float_field", c_float)),
        OffsetField(32, ("double_field", c_double)),
        OffsetField(400, ("bitfield_2", c_byte, 1)),
    ]


def test_structure_pretty_compare(left: TestStructure, right: TestStructure, msg=None):
    compare_result = left.eq_compare_and_return_field_failure(right)
    if not compare_result:
        # find the field that differs
        curr_left, curr_right = left, right
        left_field_value = None
        right_field_value = None
        for field_name in compare_result.field_name_parts:
            left_field_value = (
                getattr(curr_left, str(field_name))
                if isinstance(curr_left, EndianSwapStructure)
                else curr_left[int(field_name)]
            )
            right_field_value = (
                getattr(curr_right, str(field_name))
                if isinstance(curr_right, EndianSwapStructure)
                else curr_right[int(field_name)]
            )
            curr_left, curr_right = left_field_value, right_field_value
        msg = (
            f"TestStructure field {compare_result.field_name_parts} differs: {left_field_value} != {right_field_value}"
        )
        raise AssertionError(msg)


class TestEndianSwapStructure(TestCase):
    def setUp(self):
        self.addTypeEqualityFunc(TestStructure, test_structure_pretty_compare)

    def test_convert_bytes_to_struct_success(self):
        for source_bytes, expected_struct in TEST_MARSHAL_BYTES_TO_STRUCT_PARAM_LIST:
            output_struct = TestStructure()
            self.assertTrue(TestStructure.from_bytes(memoryview(source_bytes), output_struct, byteorder="little"))
            self.assertEqual(expected_struct, output_struct)

    def test_convert_struct_to_bytes_success(self):
        for source_struct, expected_bytes in TEST_MARSHAL_STRUCT_TO_BYTES_PARAM_LIST:
            output_buffer = bytearray()
            self.assertTrue(source_struct.to_bytes(output_buffer, byteorder="little"))
            self.assertEqual(expected_bytes, bytes(output_buffer))

    def test_convert_struct_to_dict_success(self):
        for source_struct, expected_dict in TEST_MARSHAL_STRUCT_TO_DICT_PARAM_LIST:
            output_dict = StructureDict()
            self.assertTrue(source_struct.to_dict(output_dict))
            self.assertEqual(expected_dict, output_dict)

    def test_convert_dict_to_struct_success(self):
        for source_dict, expected_struct in TEST_MARSHAL_STRUCT_FROM_DICT_PARAM_LIST:
            from_dict_result = TestStructure.from_dict(source_dict, TestStructure)
            self.assertTrue(from_dict_result)
            self.assertEqual(expected_struct, from_dict_result.value)

    def test_convert_struct_to_yaml_success(self):
        for source_struct, expected_yaml in TEST_MARSHAL_STRUCT_TO_YAML_PARAM_LIST:
            to_yaml_result = source_struct.to_yaml()
            self.assertTrue(to_yaml_result)
            self.assertEqual(expected_yaml, to_yaml_result.value)

    def test_convert_yaml_to_struct_success(self):
        for source_yaml, expected_struct in TEST_MARSHAL_STRUCT_FROM_YAML_PARAM_LIST:
            from_yaml_result = TestStructure.from_yaml(source_yaml, TestStructure)
            self.assertTrue(from_yaml_result)
            self.assertEqual(expected_struct, from_yaml_result.value)


class TestFilledEndianSwapStructure(TestCase):
    def setUp(self):
        self.addTypeEqualityFunc(TestStructure, test_structure_pretty_compare)

    def test_fill_struct_is_specified_struct_size(self):
        self.assertEqual(sizeof(TestFillStructure), TEST_FILLED_STRUCTURE_SIZE)

    def test_fill_struct_instance_can_be_created(self):
        test_struct = TestFillStructure()
        self.assertHasAttr(test_struct, "__generated_field_1__")


class TestPatchStructEndianSwap(TestCase):
    def setUp(self):
        self.addTypeEqualityFunc(TestStructure, test_structure_pretty_compare)
