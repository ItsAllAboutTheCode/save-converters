"""
Contains classes used patch structures types from a save format
Primarily contains method for endian swapping structure data
when converting from a platform with big-endian save data(PS3/Wii)
to a platform using little-endian (most other platform in existence
i.e PC, PS1, PS3, PS4, PS5, NSW, all Xbox platforms)
"""

import logging
from ctypes import (  # type: ignore[attr-defined]
    Array,
    CField,
    Structure,
    Union,
    c_byte,
    c_char,
    c_double,
    c_float,
    c_int,
    c_int8,
    c_int16,
    c_int32,
    c_int64,
    c_longlong,
    c_ubyte,
    c_uint,
    c_uint8,
    c_uint16,
    c_uint32,
    c_uint64,
    c_ulonglong,
    sizeof,
)
from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    cast,
)

if TYPE_CHECKING:
    from ctypes import _CData as CData

LOGGER = logging.getLogger("marshal_struct_base")
LOGGER.setLevel(logging.INFO)
stdoutHandler = logging.StreamHandler()
LOGGER.addHandler(stdoutHandler)

SCRIPT_NAME = Path(__file__).name


SIGNED_TYPES = [c_byte, c_int8, c_int16, c_int, c_int32, c_longlong, c_int64]
UNSIGNED_TYPES = [c_ubyte, c_uint8, c_uint16, c_uint, c_uint32, c_ulonglong, c_uint64]
BYTE_TYPES = [c_uint8, c_int8]
BYTE_TYPES_PLUS_CHAR = BYTE_TYPES + [c_char]
INT_TYPES = SIGNED_TYPES + UNSIGNED_TYPES
FLOAT_TYPES = [c_float, c_double]

ByteorderLiteral = Literal["little", "big"]
StructureDict = dict[str, Any]
StructureList = list[Any]


#
# Marshal Structure Definition
#
class MarshalStructBase(Structure):
    """
    Base class for C like structure type which can marhsal values
    to/from bytes and to/from a python dictionary
    """

    pass


class MarshalUnionBase(Union):
    """
    Base class for C like structure type which can marhsal values
    to/from bytes and to/from a python dictionary
    """

    pass


@dataclass
class UpdateFromStructResult:
    """
    Stores the result of the `update_from_other_structure` operation

    It contains a bool representing if the operation has completed successfully
    along with a list of qualified fields name representing the fields that were modified
    """

    result: bool
    updated_field_names: list[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.result


@dataclass
class CompareStructureResults:
    """
    Stores the result of a comparing an EndianSwapStructure
    If the comparison fails, a list of field names is returned that can be used
    to find the first field whose comparison failed.
    ex. Comparison of a structure with a nested structure that fails
    ```
        class Simple(EndianSwapStructure): _fields_ = [('int_field', c_uint64)]
        class Complex(EndianSwapStructure): _fields_ = [('nested', Simple), ('float_field', c_float)]
        ...
        a = Complex(Simple(1), 2.0)
        b = Complex(Simple(2), 2.0)
        a == b
    ```

    The comparison above would set the result field to False and the field name parts list
    to ['nested', 'int_field']

    The caller can then retrieve the value of the field via getattr
    ```
        curr_struct = a
        field_value = None
        for field_name in field_name_parts:
            field_value = getattr(curr_struct, field_name)
            curr_struct = field_value
    ```
    """

    result: bool
    field_name_parts: list[str | int]

    def __bool__(self) -> bool:
        return self.result


#
# Marshal Assert methods
#
def assert_struct_size(struct_type: type[MarshalStructBase], size_in_bytes: int):
    """
    Assert method that can be used to verify that a struct is equal to a byte size
    """
    if __debug__:
        if sizeof(struct_type) != size_in_bytes:
            field_log_list: list[str] = []
            for field in struct_type._fields_:
                field_desc: CField = getattr(struct_type, field[0])
                field_log_list.append(f"{field_desc.name} | 0x{field_desc.byte_offset:X} | 0x{field_desc.byte_size:X}")
            raise AssertionError(
                f"Struct {struct_type.__name__} is not expected size: 0x{size_in_bytes:X}\n"
                f"Actual size: 0x{sizeof(struct_type):X}\n"
                + "Field Name | Field Byte Offset | Field Byte Size\n"
                + "\n".join(field_log_list)
            )


def assert_field_offset(struct_type: type[MarshalStructBase], field_name: str, byte_offset: int):
    """
    Assert method that can be used to verify that a field in a struct is at a specified
    relative byte offset
    """
    if __debug__:
        field_desc: CField | None = getattr(struct_type, field_name)
        if not field_desc:
            raise AssertionError(f"Struct {struct_type.__name__} does not have a field of '{field_name}n")
        if not field_desc.byte_offset == byte_offset:
            raise AssertionError(
                f"Struct {struct_type.__name__} field '{field_name}' byte offset is not expected value:"
                f" 0x{byte_offset:X}\n"
                f"Actual byte offset: 0x{field_desc.byte_offset:X}\n"
            )


def assert_struct_no_padding(struct_type: type[MarshalStructBase]):
    """
    Asserts that the struct has no padding bytes between fields or at the end of the structure

    Rationale of when to use: When a structure has padding, if it gets marshaled to a byte array,
    the size of the byte array will be less than the size of the struct.
    This can cause issues if the user needs to map the marshaled bytes directly to a structure, such
    as when attepting to save or load save data.

    What this method validates is that each field within the struct covers the byte offsets
    of the entire struct range [0, struct_size) with no gaps.
    """

    # Track the previous field offset where its data end
    prev_field: CField | None = None
    padding_errors: list[str] = []

    for field_name, _field_type, *_ in struct_type._fields_:
        field_desc: CField = cast(CField, getattr(struct_type, field_name))
        if prev_field:
            prev_field_range = (
                prev_field.byte_offset,
                prev_field.byte_offset + prev_field.byte_size,
            )
            prev_field_name = prev_field.name
            prev_is_bitfield = prev_field.is_bitfield
        else:
            prev_field_range = (0, 0)
            prev_field_name = ""
            prev_is_bitfield = False
        if prev_field_range[1] < field_desc.byte_offset:
            padding_errors += [
                f"The previous field `{prev_field_name} has padding before the current field {field_desc.name}.\n"
                f"Previous field: offset_range=[0x{prev_field_range[0]:x},"
                f" 0x{prev_field_range[1]:x})\n"
                f"Current field: offset_range=[0x{field_desc.byte_offset:x},"
                f" 0x{field_desc.byte_offset + field_desc.byte_size:x})\n"
                f"There is a padding between offsets [0x{prev_field_range[1]:x},"
                f" 0x{field_desc.byte_offset:x})"
            ]
        elif (
            prev_field_range[1] == field_desc.byte_offset
            or prev_is_bitfield
            and prev_field_range[0] == field_desc.byte_offset
        ):
            # Previous specified field ends at current field start offset
            # or the previous field is a bitfield that has the same byte offset as the current field
            # so proceed to the next field
            pass

        prev_field = field_desc

    # After the last loop verify that the final field goes to the end of the structure
    if prev_field:
        last_field_to_end_struct_range = (
            prev_field.byte_offset + prev_field.byte_size,
            sizeof(struct_type),
        )
        if last_field_to_end_struct_range[0] < last_field_to_end_struct_range[1]:
            padding_errors += [
                f"The final field `{prev_field.name}` has padding before the end of struct {struct_type.__name__}.\n"
                f"Final field: offset_range=[0x{prev_field.byte_offset:x},"
                f" 0x{prev_field.byte_offset + prev_field.byte_size:x})\n"
                f"The struct has size 0x{last_field_to_end_struct_range[1]:x}\n"
                f"There is a padding between offsets [0x{last_field_to_end_struct_range[0]:x},"
                f" 0x{last_field_to_end_struct_range[1]:x})"
            ]

    if padding_errors:
        raise AssertionError("\n".join(padding_errors))


def update_from_other_structure(
    source_struct: MarshalStructBase, target_struct: MarshalStructBase
) -> UpdateFromStructResult:
    """
    Updates the fields of the target struct using the fields of the source struct.
    Any fields that exist in the target struct that does NOT exist in the source struct
    will be left unchanged.

    This method works by iterating each field of the source struct recursively checking if the target struct
    has the name same field name and type. For fields that match, the source struct data is copied over
    to the target struct.

    :return: a list of fields that were updated in the target struct. For descendent fields not at the root
    they will be prefixed with the parent fields separated by a dot(i.e foo.bar)

    ex. Given the following structures
    ```
    class CoorSystem1(MarshalStructBase):
        _fields_ = [
            ("t", c_float),
            ("u", c_float),
            ("v", c_float),
            ("x", c_uint32),
        ]

    class CoorSystem2(MarshalStructBase):
        _fields_ = [
            ("v", c_float),
            ("x", c_float), # Note this type is different from CoorSystem1
            ("y", c_float),
            ("z", c_float),
        ]
    ```

    The operation of copying a source struct to target struct would have the following results
    ```
    source_struct = CoorSystem1(1.0, 2.0, 3.0, 4)
    target_struct = CoorSystem1(5.0, 6.0, 7.0, 8.0)

    if result:= update_from_other_structure(source_struct, target_struct):
        print(target_struct)
    ```

    prints: (3.0, 6.0, 7.0, 8.0)

    The 'v' field from the source struct is copied over as it matches field name AND type.
    However the `x` is not, as the field type does not match (c_uint32 vs c_float)
    """

    updated_field_list: list[str] = []
    for field_tup in source_struct._fields_:
        field_desc: CField = getattr(type(source_struct), field_tup[0])
        field_name: str = field_desc.name
        field_type: type = field_desc.type

        target_field_desc: CField = getattr(target_struct, field_name)

        if field_name != target_field_desc.name or field_type != target_field_desc.type:
            continue

        field_value = getattr(source_struct, field_name)
        setattr(target_struct, field_name, field_value)
        updated_field_list.append(field_name)

    return UpdateFromStructResult(True, updated_field_list)


#
# Marshal Union Definition
#

# Sentinal values representing which union field to marshal
# The field can be selected by either int or string
# String values are used to lookup the union field by name
# Int values are used to lookup the union field by index

MarshalUnionFieldList = list[int | str]


class MarshalUnionFieldEnum(IntEnum):
    First = 0
    Last = -1
    All = 0xFFFF_FFF


UnionFieldsToStore = MarshalUnionFieldEnum | MarshalUnionFieldList
UnionFieldToLoad = Literal[MarshalUnionFieldEnum.First, MarshalUnionFieldEnum.Last] | int | str


#
# MarshalStruct and MarshalUnionBase compare methods
#
def eq_compare_array(left: Array[CData], right: Array[CData]) -> CompareStructureResults:
    if len(left) != len(right):
        return CompareStructureResults(False, [])
    else:
        for index, (left_array_elem, right_array_elem) in enumerate(zip(left, right)):
            if isinstance(left_array_elem, Array):
                compare_result = eq_compare_array(left_array_elem, right_array_elem)
                if not compare_result:
                    compare_result.field_name_parts.insert(0, index)
                    return compare_result
            if isinstance(left_array_elem, (MarshalStructBase, MarshalUnionBase)):
                compare_result = eq_compare_and_return_field_failure(left_array_elem, right_array_elem)
                if not compare_result:
                    compare_result.field_name_parts.insert(0, index)
                    return compare_result
            else:
                if left_array_elem != right_array_elem:
                    return CompareStructureResults(False, [index])

    return CompareStructureResults(True, [])


def eq_compare_and_return_field_failure(
    struct_or_union: MarshalStructBase | MarshalUnionBase, other: object
) -> CompareStructureResults:
    """
    Defines rich comparison equality for struct types that inherit from this class
    """
    if not isinstance(other, type(struct_or_union)):
        return CompareStructureResults(False, [])

    for field_tup in struct_or_union._fields_:
        # The field descriptor is looked up via the field name on the class type
        # The field value is lookup up via the field name on a class instance
        left_value = getattr(struct_or_union, field_tup[0])
        right_value = getattr(other, field_tup[0])
        if isinstance(left_value, Array):
            compare_result = eq_compare_array(left_value, right_value)
            if not compare_result:
                # prepend the current field name to the field name parts
                compare_result.field_name_parts.insert(0, field_tup[0])
                return compare_result
        elif isinstance(left_value, (MarshalStructBase, MarshalUnionBase)):
            compare_result = eq_compare_and_return_field_failure(left_value, right_value)
            if not compare_result:
                # prepend the current field name to the field name parts
                compare_result.field_name_parts.insert(0, field_tup[0])
                return compare_result
        else:
            if left_value != right_value:
                return CompareStructureResults(False, [field_tup[0]])

    return CompareStructureResults(True, [])
