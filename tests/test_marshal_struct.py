"""
Contains test for the Structure patching classes
"""

import struct
from collections.abc import Sequence
from ctypes import (  # type: ignore[attr-defined]
    Array,
    CField,
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
    FillEndianSwapStructure,
    MarshalStructure,
    MarshalUnion,
    OffsetField,
    StructureDict,
    StructureList,
    eq_compare_and_return_field_failure,
)

if TYPE_CHECKING:
    from ctypes import _CT as CDataBound

SCRIPT_DIR = Path(__file__).parent.resolve()


class TestSimpleStructure(MarshalStructure):
    _fields_ = [
        ("simple_field1", c_int64),
        ("simple_field2", c_uint32),
    ]


class TestUnion(MarshalUnion):
    _fields_ = [
        ("union_uint64", c_uint64),
        ("union_uint32", c_uint32),
    ]


class TestStructure(MarshalStructure):
    _anonymous_ = ["anonymous_union_field"]
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
        ("union_field", TestUnion),
        ("anonymous_union_field", TestUnion),
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


TEST_ARGUMENTS_LIST = [
    (
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
        TestUnion(0x1_0000_0000),
        TestUnion(union_uint32=0x42),
    ),
]


TEST_VALUES_LIST = [
    (*test_arguments[:14], *tuple[int]((bit_value for bit_value, _ in test_arguments[14:27])), *test_arguments[27:])
    for test_arguments in TEST_ARGUMENTS_LIST
]


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
        source_bytes=test_arguments[0].to_bytes(1, signed=True)
        + test_arguments[1].to_bytes(1)
        + test_arguments[2].to_bytes(2, "little", signed=True)
        + test_arguments[3].to_bytes(2, "little")
        + test_arguments[4].to_bytes(4, "little", signed=True)
        + test_arguments[5].to_bytes(4, "little")
        + test_arguments[6].to_bytes(8, "little", signed=True)
        + test_arguments[7].to_bytes(8, "little")
        + struct.pack("<f", test_arguments[8])
        + struct.pack("<d", test_arguments[9])
        + string_to_bytes(test_arguments[10], 32 * sizeof(c_char))
        + string_to_bytes(test_arguments[11], 32 * sizeof(c_wchar))
        + b"".join([i.to_bytes(1) for i in test_arguments[12]])
        + b"".join(
            [
                int(getattr(nested_struct, "simple_field1")).to_bytes(8, "little", signed=True)
                + int(getattr(nested_struct, "simple_field2")).to_bytes(4, "little")
                for nested_struct in test_arguments[13]
            ]
        )
        + bitfields_to_bytes(test_arguments[14:27])
        + b"".join(
            [int(getattr(test_union, "union_uint64")).to_bytes(8, "little") for test_union in test_arguments[27:]]
        ),
        expected_struct=TestStructure(*test_values),
    )
    for test_arguments, test_values in zip(TEST_ARGUMENTS_LIST, TEST_VALUES_LIST)
]

TEST_MARSHAL_STRUCT_TO_BYTES_PARAM_LIST: list[TestMarshalBytesFromStruct] = [
    TestMarshalBytesFromStruct(struct_data, byte_data)
    for byte_data, struct_data in TEST_MARSHAL_BYTES_TO_STRUCT_PARAM_LIST
]


def test_struct_to_array(input_array: Sequence[Any] | Array[CDataBound]) -> StructureList:
    output_array: StructureList = []
    for field_value in input_array:
        if isinstance(field_value, (MarshalStructure, MarshalUnion)):
            if isinstance(field_value, MarshalStructure):
                sub_dict: StructureDict = test_struct_to_dict(field_value)
            else:
                sub_dict = test_union_to_dict(field_value)
            output_array.append(sub_dict)

        elif isinstance(field_value, (Sequence, Array)) and not isinstance(field_value, (str, bytes)):
            sub_array = test_struct_to_array(field_value)
            output_array.append(sub_array)
        else:
            output_array.append(field_value)
    return output_array


def test_struct_to_dict(output_struct: MarshalStructure) -> StructureDict:
    output_dict: StructureDict = {}
    for field_tup in output_struct._fields_:
        field_value = getattr(output_struct, field_tup[0])
        field_desc: CField = getattr(type(output_struct), field_tup[0])
        if isinstance(field_value, (MarshalStructure, MarshalUnion)):
            if isinstance(field_value, MarshalStructure):
                sub_dict: StructureDict = test_struct_to_dict(field_value)
            else:
                sub_dict = test_union_to_dict(field_value)
            if field_desc.is_anonymous:
                output_dict.update(sub_dict)
            else:
                output_dict[field_tup[0]] = sub_dict
        elif isinstance(field_value, (Sequence, Array)) and not isinstance(field_value, (str, bytes)):
            sub_array = test_struct_to_array(field_value)
            output_dict[field_tup[0]] = sub_array
        else:
            output_dict[field_tup[0]] = field_value
    return output_dict


def test_union_to_dict(output_union: MarshalUnion) -> StructureDict:
    output_dict: StructureDict = {}
    for field_tup in output_union._fields_:
        field_value = getattr(output_union, field_tup[0])
        field_desc: CField = getattr(type(output_union), field_tup[0])
        if isinstance(field_value, (MarshalStructure, MarshalUnion)):
            if isinstance(field_value, MarshalStructure):
                sub_dict: StructureDict = test_struct_to_dict(field_value)
            else:
                sub_dict = test_union_to_dict(field_value)
            if field_desc.is_anonymous:
                output_dict.update(sub_dict)
            else:
                output_dict[field_tup[0]] = sub_dict
        elif isinstance(field_value, (Sequence, Array)) and not isinstance(field_value, (str, bytes)):
            sub_array = test_struct_to_array(field_value)
            output_dict[field_tup[0]] = sub_array
        else:
            output_dict[field_tup[0]] = field_value
    return output_dict


def arguments_to_dict(struct_type: type[MarshalStructure], test_arguments: tuple[Any, ...]) -> StructureDict:
    output_dict: StructureDict = {}
    for field_tup, value in zip(struct_type._fields_, test_arguments):
        field_desc: CField = getattr(struct_type, field_tup[0])
        if isinstance(value, (MarshalStructure, MarshalUnion)):
            if isinstance(value, MarshalStructure):
                sub_dict: StructureDict = test_struct_to_dict(value)
            else:
                sub_dict = test_union_to_dict(value)

            if field_desc.is_anonymous:
                # Merge the sub dictionary with the parent dictionary if the struct/union field is anonymous
                output_dict.update(sub_dict)
            else:
                output_dict[field_tup[0]] = sub_dict
        elif issubclass(field_tup[1], Array):
            if not isinstance(value, (str, bytes)):
                sub_array = test_struct_to_array(value)
                output_dict[field_tup[0]] = sub_array
            elif isinstance(value, bytes):
                output_dict[field_tup[0]] = value.hex(" ") if field_tup[1]._type_ != c_char else value.decode("utf-8")
            else:  # instance of str
                output_dict[field_tup[0]] = value
        else:
            output_dict[field_tup[0]] = value

    return output_dict


def arguments_to_yaml(struct_type: type[MarshalStructure], test_arguments: tuple[Any, ...]) -> bytes:

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
        arguments_to_dict(TestStructure, test_values),
        expected_struct=TestStructure(*test_values),
    )
    for test_values in TEST_VALUES_LIST
]

TEST_MARSHAL_STRUCT_TO_DICT_PARAM_LIST: list[TestMarshalStructureToDict] = [
    TestMarshalStructureToDict(struct_data, dict_data)
    for dict_data, struct_data in TEST_MARSHAL_STRUCT_FROM_DICT_PARAM_LIST
]

TEST_MARSHAL_STRUCT_FROM_YAML_PARAM_LIST: list[TestMarshalStructureFromYaml] = [
    TestMarshalStructureFromYaml(
        arguments_to_yaml(TestStructure, test_values),
        expected_struct=TestStructure(*test_values),
    )
    for test_values in TEST_VALUES_LIST
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


def test_structure_pretty_compare(left: TestStructure, right: TestStructure, msg: str | None = None):
    compare_result = eq_compare_and_return_field_failure(left, right)
    if not compare_result:
        # find the field that differs
        curr_left, curr_right = left, right
        left_field_value = None
        right_field_value = None
        for field_name in compare_result.field_name_parts:
            left_field_value = (
                getattr(curr_left, str(field_name))
                if isinstance(curr_left, MarshalStructure)
                else curr_left[int(field_name)]
            )
            right_field_value = (
                getattr(curr_right, str(field_name))
                if isinstance(curr_right, MarshalStructure)
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
            with self.subTest(source_bytes):
                from_bytes_result = TestStructure.from_bytes(
                    memoryview(source_bytes), TestStructure, byteorder="little"
                )
                self.assertTrue(from_bytes_result)
                self.assertEqual(expected_struct, from_bytes_result.value)

    def test_convert_struct_to_bytes_success(self):
        for source_struct, expected_bytes in TEST_MARSHAL_STRUCT_TO_BYTES_PARAM_LIST:
            with self.subTest(source_struct):
                to_bytes_result = source_struct.to_bytes(byteorder="little")
                self.assertTrue(to_bytes_result)
                self.assertEqual(expected_bytes, to_bytes_result.value)

    def test_convert_struct_to_dict_success(self):
        for source_struct, expected_dict in TEST_MARSHAL_STRUCT_TO_DICT_PARAM_LIST:
            with self.subTest(source_struct):
                to_dict_result = source_struct.to_dict()
                self.assertTrue(to_dict_result)
                self.assertEqual(expected_dict, to_dict_result.value)

    def test_convert_dict_to_struct_success(self):
        for source_dict, expected_struct in TEST_MARSHAL_STRUCT_FROM_DICT_PARAM_LIST:
            with self.subTest(source_dict):
                from_dict_result = TestStructure.from_dict(source_dict, TestStructure)
                self.assertTrue(from_dict_result)
                self.assertEqual(expected_struct, from_dict_result.value)

    def test_convert_struct_to_yaml_success(self):
        for source_struct, expected_yaml in TEST_MARSHAL_STRUCT_TO_YAML_PARAM_LIST:
            with self.subTest(source_struct):
                to_yaml_result = source_struct.to_yaml()
                self.assertTrue(to_yaml_result)
                self.assertEqual(expected_yaml, to_yaml_result.value)

    def test_convert_yaml_to_struct_success(self):
        for source_yaml, expected_struct in TEST_MARSHAL_STRUCT_FROM_YAML_PARAM_LIST:
            with self.subTest(source_yaml):
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
