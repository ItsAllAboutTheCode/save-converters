"""
Contains classes used patch structures types from a save format
Primarily contains method for endian swapping structure data
when converting from a platform with big-endian save data(PS3/Wii)
to a platform using little-endian (most other platform in existence
i.e PC, PS1, PS3, PS4, PS5, NSW, all Xbox platforms)
"""

import logging
import struct
from collections import deque
from collections.abc import Callable, MutableMapping, Sequence
from ctypes import (  # type: ignore[attr-defined]
    Array,
    CField,
    Structure,
    Union,
    c_bool,
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
    c_wchar,
    sizeof,
)
from dataclasses import dataclass, field
from enum import IntEnum
from io import BytesIO
from itertools import islice, zip_longest
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Literal,
    NamedTuple,
    TypeIs,
    cast,
    overload,
    override,
)

from ruamel.yaml import YAML

if TYPE_CHECKING:
    from ctypes import _CData as CData
    from ctypes import _CDataType

LOGGER = logging.getLogger("marshal_structure")
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
class FromBytesResult[T]:
    """
    Dataclass that encodes the results of the methods `from_bytes/array_from_bytes`

    The next_memoryview member is a memoryview that references the data
    after the input processed by the from_bytes/array_from_bytes calls
    """

    result: bool
    next_memoryview: memoryview | None
    value: T | None = None

    @overload
    def __init__(self, result: Literal[True], next_memoryview: memoryview | None, struct_value: T) -> None:
        pass

    @overload
    def __init__(self, result: Literal[False], next_memoryview: memoryview | None) -> None:
        pass

    def __init__(self, result, next_memoryview=None, struct_value=None):
        self.result = result
        self.next_memoryview = next_memoryview
        self.value = struct_value

    def __bool__(self) -> bool:
        return self.result


@dataclass
class ToBytesResult:
    """
    Dataclass that encodes the results of the methods `to_bytes/array_to_bytes`

    """

    result: bool
    value: bytes = b""

    def __bool__(self) -> bool:
        return self.result


class ToDictResult:
    """
    Dataclass that encodes the results of the method `to_dict`
    """

    result: bool
    value: StructureDict | None

    def __init__(self, result, dict_value=None):
        self.result = result
        self.value = dict_value

    def __bool__(self) -> bool:
        return self.result


class FromDictResult[T]:
    """
    Dataclass that encodes the results of the method `from_dict`
    """

    result: bool
    value: T | None = None

    @overload
    def __init__(self, result: Literal[True], struct_value: T) -> None:
        pass

    @overload
    def __init__(self, result: Literal[False]) -> None:
        pass

    def __init__(self, result, struct_value=None):
        self.result = result
        self.value = struct_value

    def __bool__(self) -> bool:
        return self.result


@dataclass
class ToYamlResult:
    """
    Data that encodes the results of the method `to_yaml`

    It returns the yaml data as as string
    """

    result: bool
    value: bytes = b""

    def __bool__(self) -> bool:
        return self.result


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


FieldSetter = Callable[[str | int, Any], None]

DictFieldSetter = Callable[[Any], None]


@dataclass
class _FieldToBytesResult:
    result: bool

    def __bool__(self) -> bool:
        return self.result


@dataclass
class _BytesConvertResult:
    """
    Dataclass that encodes the results of the interal methods `from_bytes/array_from_bytes`

    The next_memoryview member is a memoryview that references the data
    after the input processed by the from_bytes/array_from_bytes calls
    """

    result: bool
    next_memoryview: memoryview[int]

    def __bool__(self) -> bool:
        return self.result


FieldConvertTypes = (
    MarshalStructBase
    | MarshalUnionBase
    | Array[Any]
    | MutableMapping[str, Any]
    | StructureList
    | bool
    | int
    | float
    | str
    | bytes
)


class _ToFieldResult:
    """
    Internal dataclass for storing the result
    of dictionary or bytearray to a struct field
    """

    result: bool
    value: FieldConvertTypes | None

    @overload
    def __init__(
        self,
        result: Literal[True],
        value: FieldConvertTypes,
    ) -> None:
        pass

    @overload
    def __init__(self, result: Literal[False]) -> None:
        pass

    def __init__(self, result, value=None):
        self.result = result
        self.value = value

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


def should_skip_field(field_name: str) -> bool:
    """
    Determines if a field should be skipped based on the field name
    This is used to prevent propagating __<name>__ fields
    to and from dictionaries
    """
    return field_name.startswith("__")


class MarshalStructure(MarshalStructBase):
    """ctype Structure which can marshal its data to/from bytes
    using the to_bytes/from_bytes method
    """

    def to_bytes(self, byteorder: ByteorderLiteral = "big") -> ToBytesResult:
        output_data = bytearray()
        result = self._struct_to_bytes(output_data, byteorder)
        if not result:
            return ToBytesResult(False)
        return ToBytesResult(True, bytes(output_data))

    def _struct_to_bytes(self, output_data: bytearray, byteorder: ByteorderLiteral = "big") -> _FieldToBytesResult:
        """
        Marshal the structure into the byte array using the specified byte order
        """

        prev_field_desc: CField | None = None
        for field_tup in self._fields_:
            if not field_tup:
                break
            # The field descriptor is looked up via the field name on the class type
            # The field value is lookuped via the field name on a class instance
            field_desc: CField = getattr(type(self), field_tup[0])
            field_value = getattr(self, field_tup[0])
            field_name = field_desc.name
            field_type: type[Any] = cast(type[Any], field_desc.type)
            field_size = field_desc.byte_size

            result = self._field_to_bytes(
                output_data=output_data,
                byteorder=byteorder,
                field_name_or_index=field_name,
                field_type=field_type,
                field_byte_size=field_size,
                field_value=field_value,
                field_desc=field_desc,
                prev_field_desc=prev_field_desc,
            )
            if not result:
                return result

            prev_field_desc = field_desc

        return _FieldToBytesResult(True)

    @staticmethod
    def _array_to_bytes(
        input_array: bytes | str | Array[CData],
        output_data: bytearray,
        field_array_type: type[Array[CData]],
        byteorder: ByteorderLiteral = "big",
    ) -> _FieldToBytesResult:
        """
        Marshals the array of fields into the byte array using the specified byte order

        NOTE: The ctypes has a special case when a c_char array or c_wchar is used
        Instead of the field value being CArray[c_char] or CArray[c_wchar]
        It stores the field as a `bytes` and `str` type respectively.
        """
        max_array_size = sizeof(field_array_type)
        if isinstance(input_array, bytes):
            output_data += input_array
            # Fill byte buffer values with 0 the max array size is reached
            free_byte_count: int = max_array_size - len(input_array)
            if free_byte_count > 0:
                output_data += bytes(free_byte_count)
            return _FieldToBytesResult(True)
        elif isinstance(input_array, str):
            byte_input_array = input_array.encode("utf-32-le" if byteorder == "little" else "utf-32-be")
            output_data += byte_input_array
            free_byte_count = max_array_size - len(byte_input_array)
            if free_byte_count > 0:
                output_data += bytes(free_byte_count)
            return _FieldToBytesResult(True)

        field_type = input_array._type_
        field_size = sizeof(field_type)

        # Parse each field of the array
        for arr_index in range(input_array._length_):
            # The field descriptor is looked up via the field name on the class type
            # The field value is lookuped via the field name on a class instance
            field_value = input_array[arr_index]

            result = MarshalStructure._field_to_bytes(
                output_data=output_data,
                byteorder=byteorder,
                field_name_or_index=arr_index,
                field_type=field_type,
                field_byte_size=field_size,
                field_value=field_value,
                field_desc=None,
                prev_field_desc=None,
            )
            if not result:
                return result

        return _FieldToBytesResult(True)

    @staticmethod
    def _field_to_bytes(
        output_data: bytearray,
        byteorder: ByteorderLiteral,
        field_name_or_index: str | int,
        field_type: type[CData],
        field_byte_size: int,
        field_value: Any,
        field_desc: CField | None,
        prev_field_desc: CField | None,
    ) -> _FieldToBytesResult:
        marshal_buffer = bytearray()
        if issubclass(field_type, MarshalStructure) or issubclass(field_type, MarshalUnion):
            if not isinstance(field_value, (MarshalStructure, MarshalUnion)):
                return _FieldToBytesResult(False)

            if isinstance(field_value, MarshalStructure):
                if not field_value._struct_to_bytes(marshal_buffer, byteorder):
                    LOGGER.error(f"Failed to load structure '{field_name_or_index}' from byte buffer")
                    return _FieldToBytesResult(False)
            else:
                if not field_value._union_to_bytes(marshal_buffer, byteorder):
                    LOGGER.error(f"Failed to load union '{field_name_or_index}' from byte buffer")
                    return _FieldToBytesResult(False)
            output_data += marshal_buffer
        elif issubclass(field_type, Array):
            array_field: bytes | str | Array[Any] | None = None
            if isinstance(field_value, (bytes, str, Array)):
                array_field = field_value
            else:
                LOGGER.error(f"Array field value with type {(type(field_value))} is unsupported for marshalling")
                return _FieldToBytesResult(False)

            if not MarshalStructure._array_to_bytes(array_field, marshal_buffer, field_type, byteorder):
                LOGGER.error(f"Failed to load array '{field_name_or_index}' from byte buffer")
                return _FieldToBytesResult(False)
            output_data += marshal_buffer
        elif field_type == c_bool:
            marshal_buffer += bool(field_value).to_bytes(1)
            output_data += marshal_buffer
        elif field_type == c_char or field_type == c_wchar:
            marshal_buffer += bytes(field_value) if field_type == c_char else str(field_value).encode("utf-8")
            output_data += marshal_buffer
        elif field_type in INT_TYPES:
            bit_value = (
                (int(field_value) & ((1 << field_desc.bit_size) - 1)) << field_desc.bit_offset
                if field_desc and field_desc.is_bitfield
                else field_value
            )

            # Verify that the previous field and the current field do not share the same byte offset
            # Otherwise the fields are bitfields of the same integer
            if (
                not field_desc
                or not field_desc.is_bitfield
                or not prev_field_desc
                or prev_field_desc.byte_offset != field_desc.byte_offset
            ):
                # Insert a 0 integer that is the length of the field byte size
                output_data += (0).to_bytes(field_byte_size)

            # Get a byte view to the integer bytes being processed in the output bytearray
            write_view = memoryview(output_data)[-field_byte_size:]
            # Value of the current integer.
            # The value is 0 unless a bitfield is being processed
            curr_int_value = int.from_bytes(write_view, byteorder=byteorder, signed=field_type in SIGNED_TYPES)

            # bitwise-or the current value of the integer bytes with update bits
            write_view[0:field_byte_size] = (curr_int_value | bit_value).to_bytes(
                field_byte_size, byteorder=byteorder, signed=field_type in SIGNED_TYPES
            )
        elif field_type in FLOAT_TYPES:
            if field_type == c_float:
                pack_fmt = "<f" if byteorder == "little" else ">f"
            else:
                pack_fmt = "<d" if byteorder == "little" else ">d"
            try:
                marshal_buffer += struct.pack(pack_fmt, float(field_value))
            except struct.error as err:
                LOGGER.warning(f"Could not to field {field_value} to float bytes: {err}")
                return _FieldToBytesResult(False)
            output_data += marshal_buffer
        else:
            LOGGER.warning(
                "Unsupported type when marshaling struct:" + f" Type '{field_type}' is not supported. Skipping..."
            )
            return _FieldToBytesResult(False)

        return _FieldToBytesResult(True)

    def to_yaml(self, *, add_field_comments: bool = False, skip_double_underscore_fields: bool = False) -> ToYamlResult:
        """
        Marshal the structure into a python dictionary

        :param: add_field_comments Add comments to yaml file indicating byte offset of each struct field
        :param: skip_double_underscore_fields Whether to skip fields that start with '__'.
                Default is False when storing to yaml (i.e do NOT skip)
                NOTE: This is different from the to_dict method method where '__' fields are skipped by default
        """

        to_dict_result = self.to_dict(skip_double_underscore_fields=skip_double_underscore_fields)
        if not to_dict_result:
            return ToYamlResult(False)

        output_dict = to_dict_result.value

        # Add comments on successful conversion to a dictionary
        yaml = YAML()
        yaml_byte_stream = BytesIO()
        try:
            yaml.dump(output_dict, yaml_byte_stream)
            yaml_byte_stream.seek(0)
            yaml_data = yaml.load(yaml_byte_stream)
        except AttributeError as err:
            LOGGER.error(f"Converting dict to YAML has failed: {err}")
            return ToYamlResult(False)

        # Add comments to yaml specifying the field offsets and sizes
        if add_field_comments:

            class CommentTraverseMetadata(NamedTuple):
                """
                Holds metadata used for commenting Yaml data from a ctype Structure tree
                used for binding a struct/array to its field_name/index list for breath first traversal
                of a structure field without recursion
                """

                yaml_node: Any
                cdata_node: tuple[Structure, list[str]] | tuple[Array[CData], range]
                # Absolute offset where structure fields will be calculated from
                # when outputting
                cdata_offset_base: int

                def is_struct(
                    self, cdata_node: tuple[Structure, list[str]] | tuple[Array[CData], range]
                ) -> TypeIs[tuple[Structure, list[str]]]:
                    return isinstance(cdata_node[0], Structure)

                def is_array(
                    self, cdata_node: tuple[Structure, list[str]] | tuple[Array[CData], range]
                ) -> TypeIs[tuple[Array[CData], range]]:
                    return isinstance(cdata_node[0], Array)

            # Breath first search queue for processing fields in top down order
            field_bfs_queue: deque[CommentTraverseMetadata] = deque(
                [CommentTraverseMetadata(yaml_data, (self, [field_tup[0] for field_tup in self._fields_]), 0)]
            )
            while field_bfs_queue:
                comment_metadata = field_bfs_queue.popleft()
                yaml_field = comment_metadata.yaml_node
                if comment_metadata.is_struct(comment_metadata.cdata_node):
                    struct_or_array_inst: Structure | Array[CData] = comment_metadata.cdata_node[0]
                    field_names_or_indexes: list[str] | range = comment_metadata.cdata_node[1]
                elif comment_metadata.is_array(comment_metadata.cdata_node):
                    struct_or_array_inst = comment_metadata.cdata_node[0]
                    field_names_or_indexes = comment_metadata.cdata_node[1]
                else:
                    continue
                field_abs_offset = comment_metadata.cdata_offset_base

                for field_name_or_index in field_names_or_indexes:
                    if isinstance(struct_or_array_inst, Structure):
                        field_name_or_index = cast(str, field_name_or_index)
                        field_desc: CField = getattr(type(struct_or_array_inst), field_name_or_index)
                        field_value = getattr(struct_or_array_inst, field_name_or_index)
                        field_size = field_desc.byte_size
                    else:
                        field_name_or_index = cast(int, field_name_or_index)
                        field_value = struct_or_array_inst[field_name_or_index]
                        field_size = sizeof(struct_or_array_inst._type_)

                    comment = f"size={field_size}, abs_offset=0x{field_abs_offset:x}"
                    yaml_field.yaml_add_eol_comment(comment, key=field_name_or_index)

                    child_field = yaml_field[field_name_or_index]

                    if isinstance(field_value, MarshalStructure) and isinstance(child_field, dict):
                        field_bfs_queue.append(
                            CommentTraverseMetadata(
                                child_field,
                                (field_value, [field_tup[0] for field_tup in field_value._fields_]),
                                field_abs_offset,
                            )
                        )
                    elif isinstance(field_value, Array) and isinstance(child_field, list):
                        field_bfs_queue.append(
                            CommentTraverseMetadata(
                                yaml_field[field_name_or_index],
                                (field_value, range(len(field_value))),
                                field_abs_offset,
                            )
                        )

                    # Update the field absolute offset
                    field_abs_offset += field_size

        dump_output = BytesIO()
        try:
            yaml.dump(yaml_data, dump_output)
        except AttributeError as err:
            LOGGER.error(f"Dumping struct {self.__name__} to YAML failed: {err}")
            return ToYamlResult(False)

        return ToYamlResult(True, dump_output.getvalue())

    def to_dict(self, skip_double_underscore_fields: bool = True) -> ToDictResult:
        """
        Marshal the structure into a python dictionary

        :param: skip_double_underscore_fields Skip any fields that start with a double underscore
        """

        output_dict: dict[str, Any] = {}

        result: _ToFieldResult = self._struct_to_dict(
            output_dict, skip_double_underscore_fields=skip_double_underscore_fields
        )
        if not result:
            return ToDictResult(False)

        return ToDictResult(True, output_dict)

    def _struct_to_dict(
        self, output_dict: MutableMapping[str, Any], skip_double_underscore_fields: bool
    ) -> _ToFieldResult:
        """
        Marshal the structure into a python dictionary
        """

        for field_tup in self._fields_:
            if not field_tup:
                break
            # The field descriptor is looked up via the field name on the class type
            # The field value is lookup up via the field name on a class instance
            field_desc: CField = getattr(type(self), field_tup[0])
            field_value = getattr(self, field_tup[0])
            field_name = field_desc.name
            field_type: type[Any] = cast(type[Any], field_desc.type)

            if skip_double_underscore_fields and should_skip_field(field_name):
                continue

            def dict_value_setter(value: Any) -> None:
                if field_desc.is_anonymous:
                    # For an anonymous struct or union merge its fields with the parent object
                    output_dict.update(value)
                else:
                    output_dict[field_name] = value

            result: _ToFieldResult = self._field_to_dict(
                dict_value_setter=dict_value_setter,
                field_name_or_index=field_name,
                field_type=field_type,
                field_value=field_value,
                skip_double_underscore_fields=skip_double_underscore_fields,
            )
            if not result:
                return _ToFieldResult(False)

        return _ToFieldResult(True, output_dict)

    @staticmethod
    def _array_to_dict(
        input_array: Array[CData] | str | bytes, array_type: type[Array[CData]], skip_double_underscore_fields: bool
    ) -> _ToFieldResult:
        """Marshal the array into a python dictionary"""

        # For input that is a str or bytes object, copy it directly to the dict
        if isinstance(input_array, bytes):
            return _ToFieldResult(
                True, input_array.hex(" ") if array_type._type_ != c_char else input_array.decode("utf-8")
            )
        elif isinstance(input_array, str):
            return _ToFieldResult(True, input_array)

        field_type = input_array._type_
        field_size = sizeof(field_type)

        output_array: StructureList = []
        field_offset = 0
        # Parse each field of the array
        for arr_index in range(input_array._length_):
            # The field descriptor is looked up via the field name on the class type
            # The field value is lookuped via the field name on a class instance
            field_value = input_array[arr_index]

            def array_value_setter(value: Any) -> None:
                output_array.append(value)

            result: _ToFieldResult = MarshalStructure._field_to_dict(
                dict_value_setter=array_value_setter,
                field_name_or_index=arr_index,
                field_type=field_type,
                field_value=field_value,
                skip_double_underscore_fields=skip_double_underscore_fields,
            )
            if not result:
                return result

            field_offset += field_size

        return _ToFieldResult(True, output_array)

    @staticmethod
    def _field_to_dict(
        dict_value_setter: DictFieldSetter,
        field_name_or_index: str | int,
        field_type: type[CData],
        field_value: Any,
        skip_double_underscore_fields: bool,
    ) -> _ToFieldResult:
        result_value: FieldConvertTypes | None = None
        if issubclass(field_type, MarshalStructure) or issubclass(field_type, MarshalUnion):
            if not isinstance(field_value, (MarshalStructure, MarshalUnion)):
                return _ToFieldResult(False)

            sub_dict = StructureDict()
            if isinstance(field_value, MarshalStructure):
                if not field_value._struct_to_dict(
                    sub_dict, skip_double_underscore_fields=skip_double_underscore_fields
                ):
                    LOGGER.error(f"Failed to load structure '{field_name_or_index}' from byte buffer")
                    return _ToFieldResult(False)
            else:
                if not field_value._union_to_dict(sub_dict, skip_double_underscore_fields):
                    LOGGER.error(f"Failed to load union '{field_name_or_index}' from byte buffer")
                    return _ToFieldResult(False)
            result_value = sub_dict
            dict_value_setter(result_value)
        elif issubclass(field_type, Array):
            to_array_result = MarshalStructure._array_to_dict(
                field_value, field_type, skip_double_underscore_fields=skip_double_underscore_fields
            )
            if not to_array_result or to_array_result.value is None:
                LOGGER.error(f"Failure converting struct array {field_name_or_index} to dictionary field")
                return to_array_result
            result_value = to_array_result.value
            dict_value_setter(result_value)
        elif field_type == c_bool:
            result_value = bool(field_value)
            dict_value_setter(result_value)
        elif field_type == c_char or field_type == c_wchar:
            result_value = bytes(field_value).hex(" ") if field_type == c_char else str(field_value).encode("utf-8")
            dict_value_setter(result_value)
        elif field_type in INT_TYPES:
            result_value = int(field_value)
            dict_value_setter(result_value)
        elif field_type in FLOAT_TYPES:
            result_value = float(field_value)
            dict_value_setter(result_value)
        else:
            LOGGER.warning(
                "Unsupported type when marshaling struct:" + f" Type '{field_type}' is not supported. Skipping..."
            )
            return _ToFieldResult(False)

        return _ToFieldResult(True, result_value)

    # Make sure the output_struct is a subclass of the MarshalStructure (i.e supports to_bytes and from_bytes method)
    @staticmethod
    def from_bytes[T: MarshalStructure](
        input_data: memoryview, struct_type: type[T], byteorder: ByteorderLiteral = "big"
    ) -> FromBytesResult[T]:
        """
        Marshals the bytes from the input byte buffer into the output structure using the specified byte order
        """
        output_struct: T = struct_type()

        result = MarshalStructure._struct_from_bytes(input_data, output_struct, byteorder)
        if not result:
            return FromBytesResult[T](False, result.next_memoryview)

        return FromBytesResult[T](True, result.next_memoryview, output_struct)

    @staticmethod
    def _struct_from_bytes(
        input_data: memoryview, output_struct: MarshalStructure, byteorder: ByteorderLiteral = "big"
    ) -> _BytesConvertResult:
        """
        Marshals the bytes from the input byte buffer into the output structure using the specified byte order
        """
        curr_data_view: memoryview[int] = memoryview(input_data)

        def struct_field_setter(name_or_index: str | int, value: Any) -> None:
            name = cast(str, name_or_index)
            setattr(output_struct, name, value)

        # Iterate over the fields of the struct and checking for sub structures and arrays and fundamental types
        for field_tup, next_field in zip_longest(
            output_struct._fields_, islice(output_struct._fields_, 1, None), fillvalue=None
        ):
            if not field_tup:
                break
            # The field descriptor is looked up via the field name on the class type
            # The field value is lookup up via the field name on a class instance
            field_desc: CField = getattr(type(output_struct), field_tup[0])
            field_value = getattr(output_struct, field_tup[0])
            field_name = field_desc.name
            field_type: type[Any] = cast(type[Any], field_desc.type)
            field_size: int = field_desc.byte_size

            # Grab the next field descriptor if available
            next_field_desc: CField | None = getattr(type(output_struct), next_field[0]) if next_field else None
            result = MarshalStructure._field_from_bytes(
                curr_data_view=curr_data_view,
                byteorder=byteorder,
                field_name_or_index=field_name,
                field_type=field_type,
                field_byte_size=field_size,
                field_value=field_value,
                field_setter=struct_field_setter,
                field_desc=field_desc,
                next_field_desc=next_field_desc,
            )
            if not result:
                return result

            # Update the memory view afte the processed bytes
            curr_data_view = result.next_memoryview

        return _BytesConvertResult(True, curr_data_view)

    @staticmethod
    def _array_from_bytes(
        input_data: memoryview,
        output_array: Array[CData] | bytearray,
        output_array_type: type[Array[CData]],
        byteorder: ByteorderLiteral = "big",
    ) -> _BytesConvertResult:
        """
        Marshals the bytes from the input byte buffer into the output field array using the specified byte order
        for each element

        NOTE: ctypes has a special case for c_char and c_wchar arrays, where it treats the types as the
        builtin bytes and str types respectively
        Therefore when a bytearray is passed into this method, it just copies the bytes from the input data
        """
        if isinstance(output_array, bytearray):
            max_array_size = sizeof(output_array_type)

            # Move the view to only examine the string/bytes data
            input_bytearray_view = input_data[:max_array_size]
            output_array += input_bytearray_view
            return _BytesConvertResult(True, input_data[max_array_size:])

        curr_data_view: memoryview[int] = input_data
        # Get Query the field type and field byte size
        field_type = output_array._type_
        field_size = sizeof(field_type)

        for arr_index in range(output_array._length_):
            field_value = output_array[arr_index]

            def array_field_setter(name_or_index: str | int, value: Any) -> None:
                index = cast(int, name_or_index)
                output_array[index] = value

            result = MarshalStructure._field_from_bytes(
                curr_data_view=curr_data_view,
                byteorder=byteorder,
                field_name_or_index=arr_index,
                field_type=field_type,
                field_byte_size=field_size,
                field_value=field_value,
                field_setter=array_field_setter,
                field_desc=None,
                next_field_desc=None,
            )
            if not result:
                return result

            # Update the memory view afte the processed bytes
            curr_data_view = result.next_memoryview

        return _BytesConvertResult(True, curr_data_view)

    @staticmethod
    def _field_from_bytes(
        curr_data_view: memoryview,
        byteorder: ByteorderLiteral,
        field_name_or_index: str | int,
        field_type: type[CData],
        field_byte_size: int,
        field_value: Any,
        field_setter: FieldSetter,
        field_desc: CField | None,
        next_field_desc: CField | None,
    ) -> _BytesConvertResult:

        if issubclass(field_type, MarshalStructure) or issubclass(field_type, MarshalUnion):
            if is_struct := issubclass(field_type, MarshalStructure):
                result = field_type._struct_from_bytes(curr_data_view, field_value, byteorder)
            else:
                result = field_type._union_from_bytes(curr_data_view, field_value, byteorder)
            if not result:
                LOGGER.error(
                    f"Failed to load {'structure' if is_struct else 'union'} {field_name_or_index} from byte buffer"
                )
                return _BytesConvertResult(False, curr_data_view)

            # advance current memory view after struct bytes
            curr_data_view = result.next_memoryview

        elif issubclass(field_type, Array):
            output_buffer: bytearray | Array[Any] | None = None
            if isinstance(field_value, (bytes, str)):
                output_buffer = bytearray()
            elif isinstance(field_value, Array):
                output_buffer = field_value
            else:
                LOGGER.error(f"Array field value with type {(type(field_value))} is unsupported for marshalling")
                return _BytesConvertResult(False, curr_data_view)

            result = MarshalStructure._array_from_bytes(curr_data_view, output_buffer, field_type, byteorder)
            if not result:
                LOGGER.error(f"Failed to load field {field_name_or_index} from byte buffer")
                return result

            if isinstance(output_buffer, Array):
                field_setter(field_name_or_index, output_buffer)
            else:
                # bytes or str field
                field_setter(
                    field_name_or_index,
                    bytes(output_buffer)
                    if isinstance(field_value, bytes)
                    else output_buffer.decode("utf-32-le" if byteorder == "little" else "utf-32-be"),
                )
            # advance current memory view after array bytes
            curr_data_view = result.next_memoryview

        elif field_type == c_bool:
            field_setter(field_name_or_index, bool(curr_data_view[0]))
            # advance current memory view
            curr_data_view = curr_data_view[field_byte_size:]
        elif field_type == c_char or field_type == c_wchar:
            bytes_value = curr_data_view[0].to_bytes(1)
            field_setter(field_name_or_index, bytes_value if field_type == c_char else bytes_value.decode("utf-8"))
            # advance current memory view
            curr_data_view = curr_data_view[field_byte_size:]
        elif field_type in INT_TYPES:
            int_value = int.from_bytes(
                curr_data_view[0:field_byte_size], byteorder=byteorder, signed=field_type in SIGNED_TYPES
            )
            if field_desc and field_desc.is_bitfield:
                bit_value = (int_value >> field_desc.bit_offset) & ((1 << field_desc.bit_size) - 1)
                field_setter(field_name_or_index, bit_value)
                # If the next field byte offset is the greater than the current bitfield byte offset
                # or the current field is the last one being examined, then advance the memory view
                if not next_field_desc or field_desc.byte_offset < next_field_desc.byte_offset:
                    curr_data_view = curr_data_view[field_byte_size:]
            else:
                field_setter(field_name_or_index, int_value)
                # advance current memory view
                curr_data_view = curr_data_view[field_byte_size:]
        elif field_type in FLOAT_TYPES:
            if field_type == c_float:
                unpack_fmt = "<f" if byteorder == "little" else ">f"
            else:
                unpack_fmt = "<d" if byteorder == "little" else ">d"
            try:
                float_value_tuple = struct.unpack(unpack_fmt, curr_data_view[0:field_byte_size])
            except struct.error as err:
                LOGGER.error(f"Failed to convert bytes {curr_data_view[0:field_byte_size].hex(' ')} to float: {err}")
                return _BytesConvertResult(False, curr_data_view)
            field_setter(field_name_or_index, float_value_tuple[0])
            # advance current memory view
            curr_data_view = curr_data_view[field_byte_size:]
        else:
            LOGGER.error(
                "Failed marshaling structure"
                + f" due to parsing unsupported type {field_type}\n"
                + "Types without fixed size such as 'long' and 'unsigned long' are not supported.\n"
                + "Furthermore types such as pointers aren't supported since save data does not"
                + " contain memory addresses, but may contain relative offsets which are treated as int"
            )
            return _BytesConvertResult(False, curr_data_view)
        return _BytesConvertResult(True, curr_data_view)

    @staticmethod
    def from_yaml(
        input_yaml: bytes, struct_type: type[MarshalStructure], skip_double_underscore_fields: bool = False
    ) -> FromDictResult[MarshalStructure]:
        """
        Marshal a bytearray of yaml into a struct that is derived from this class
        :param: skip_double_underscore_fields Whether to skip fields that start with '__'.
                Default is False when loading YAML or dict(i.e do NOT skip)
        """

        # Convert yaml bytes into dictionary
        yaml = YAML()
        try:
            yaml_data = yaml.load(BytesIO(input_yaml))
        except AttributeError as err:
            LOGGER.error(f"Failed loading yaml from bytes data: {err}")
            return FromDictResult[MarshalStructure](False)

        # Load struct from dictionary
        from_dict_result: FromDictResult[MarshalStructure] = struct_type.from_dict(
            yaml_data, struct_type, skip_double_underscore_fields=skip_double_underscore_fields
        )

        return from_dict_result

    @staticmethod
    def from_dict(
        input_dict: dict[str, Any], struct_type: type[MarshalStructure], skip_double_underscore_fields: bool = True
    ) -> FromDictResult[MarshalStructure]:
        """
        Marshal the structure into a dictionary optionally skipping fields that start with
        double underscore

        :param: skip_double_underscore_fields Whether to skip fields that start with '__'.
                Default is False when loading YAML or dict(i.e do NOT skip)
        """

        return struct_type._struct_from_dict(
            input_dict, struct_type, skip_double_underscore_fields=skip_double_underscore_fields
        )

    @staticmethod
    def _struct_from_dict(
        input_dict: dict[str, Any], struct_type: type[MarshalStructure], skip_double_underscore_fields: bool
    ) -> FromDictResult[MarshalStructure]:
        """
        Marshal the structure into a python dictionary
        """

        output_struct = struct_type()

        def struct_field_setter(name_or_index: str | int, value: Any) -> None:
            name = cast(str, name_or_index)
            setattr(output_struct, name, value)

        # Iterate over the fields of the struct and checking for sub structures and arrays and fundamental types
        for field_tup in output_struct._fields_:
            if not field_tup:
                break
            # The field descriptor is looked up via the field name on the class type
            field_desc: CField = getattr(type(output_struct), field_tup[0])
            field_name = field_desc.name
            field_type: type[Any] = cast(type[Any], field_desc.type)

            if field_desc.is_anonymous:
                # For an anonymous struct or union use the first field that exist in the dictionary to load data into it
                for sub_field_tup in field_desc.type._fields_:
                    if sub_field_tup[0] in input_dict:
                        field_name = sub_field_tup[0]
                        field_type = sub_field_tup[1]

            if skip_double_underscore_fields and should_skip_field(field_name):
                continue

            if field_name not in input_dict:
                LOGGER.error(f"Input dictionary is missing field '{field_name}'")
                return FromDictResult[MarshalStructure](False)

            # Grab the next field descriptor if available
            result = MarshalStructure._field_from_dict(
                field_setter=struct_field_setter,
                dict_value=input_dict[field_name],
                field_name_or_index=field_name,
                field_type=field_type,
                skip_double_underscore_fields=skip_double_underscore_fields,
            )
            if not result:
                return FromDictResult[MarshalStructure](False)

        return FromDictResult[MarshalStructure](True, output_struct)

    @staticmethod
    def _array_from_dict(
        input_array: StructureList | bytes | str, array_type: type[Array[CData]], skip_double_underscore_fields: bool
    ) -> _ToFieldResult:
        """
        Marshal the array into a python dictionary
        """
        field_type = cast("type[CData]", array_type._type_)

        # Convert any stringified hex dumps to a byte array for the bytes types
        # The character types are stored as plain strings
        if field_type in BYTE_TYPES_PLUS_CHAR:
            if isinstance(input_array, str):
                input_array = bytes.fromhex(input_array) if field_type != c_char else input_array.encode("utf-8")

        if field_type == c_char:
            # Arrays of c_char are treated as bytes by the ctypes module
            try:
                return _ToFieldResult(True, input_array)
            except ValueError as err:
                LOGGER.error(f"Could not convert input_array to bytes for field type {field_type}: {err}")
                return _ToFieldResult(False)
        elif field_type == c_wchar:
            # Arrays of c_wchar are treated as str by the ctypes module
            try:
                return _ToFieldResult(True, input_array)
            except ValueError as err:
                LOGGER.error(f"Could not convert input_array to string for field type {field_type}: {err}")
                return _ToFieldResult(False)

        output_array = array_type()
        # Parse each field of the array
        # Truncate to the length of the ctypes Array
        for arr_index in range(output_array._length_):
            # The field descriptor is looked up via the field name on the class type
            # The field value is lookuped via the field name on a class instance
            elem_value = input_array[arr_index]

            def array_field_setter(name_or_index: str | int, value: Any) -> None:
                index = cast(int, name_or_index)
                output_array[index] = value

            result: _ToFieldResult = MarshalStructure._field_from_dict(
                field_setter=array_field_setter,
                dict_value=elem_value,
                field_name_or_index=arr_index,
                field_type=field_type,
                skip_double_underscore_fields=skip_double_underscore_fields,
            )
            if not result:
                return result

        # Return the output array in the result structure
        return _ToFieldResult(True, output_array)

    @staticmethod
    def _field_from_dict(
        field_setter: FieldSetter,
        dict_value: Any,
        field_name_or_index: str | int,
        field_type: type[CData],
        skip_double_underscore_fields: bool,
    ) -> _ToFieldResult:
        if issubclass(field_type, MarshalStructure) or issubclass(field_type, MarshalUnion):
            if is_struct := issubclass(field_type, MarshalStructure):
                from_dict_result: FromDictResult[MarshalStructure] | FromDictResult[MarshalUnion] = (
                    field_type._struct_from_dict(
                        dict_value, field_type, skip_double_underscore_fields=skip_double_underscore_fields
                    )
                )
            else:
                from_dict_result = field_type._union_from_dict(
                    dict_value, field_type, skip_double_underscore_fields=skip_double_underscore_fields
                )

            if not from_dict_result or not from_dict_result.value:
                LOGGER.error(
                    f"Failed to load {'structure' if is_struct else 'union'} {field_name_or_index} from dictionary"
                )
                return _ToFieldResult(False)

            field_setter(field_name_or_index, from_dict_result.value)
            return _ToFieldResult(True, from_dict_result.value)
        elif issubclass(field_type, Array):
            result: _ToFieldResult = MarshalStructure._array_from_dict(
                dict_value, field_type, skip_double_underscore_fields
            )
            if not result:
                LOGGER.error(f"Failed to load field {field_name_or_index} from array")
                return result
            field_setter(field_name_or_index, result.value)
            return result
        elif field_type == c_bool:
            try:
                output_value: Any = bool(dict_value)
            except ValueError as err:
                LOGGER.error(f"field {field_name_or_index} must be convertible to bool: {err}")
                return _ToFieldResult(False)
            field_setter(field_name_or_index, output_value)
            return _ToFieldResult(True, dict_value)
        elif field_type == c_char or field_type == c_wchar:
            if not isinstance(dict_value, str):
                LOGGER.error(f"field {field_name_or_index} must be a string")
                return _ToFieldResult(False)

            try:
                output_value = bytes.fromhex(dict_value)
            except ValueError as err:
                LOGGER.error(f"field {field_name_or_index} must be a string of 2-digit hex number: {err}")
                return _ToFieldResult(False)
            field_setter(field_name_or_index, output_value)
            return _ToFieldResult(True, output_value)
        elif field_type in INT_TYPES:
            try:
                output_value = int(dict_value)
            except ValueError as err:
                LOGGER.error(f"field {field_name_or_index} must be convertible to int: {err}")
                return _ToFieldResult(False)
            field_setter(field_name_or_index, output_value)
            return _ToFieldResult(True, output_value)
        elif field_type in FLOAT_TYPES:
            try:
                output_value = float(dict_value)
            except ValueError as err:
                LOGGER.error(f"field {field_name_or_index} must be convertible to float: {err}")
                return _ToFieldResult(False)
            field_setter(field_name_or_index, output_value)
            return _ToFieldResult(True, output_value)
        else:
            LOGGER.error(
                "Failed marshaling structure"
                + f" due to parsing unsupported type {field_type}\n"
                + "Types without fixed size such as 'long' and 'unsigned long' are not supported.\n"
                + "Furthermore types such as pointers aren't supported since save data cannot"
                + " contain memory addresses, but may contain relative offsets which are treated as int"
            )
            return _ToFieldResult(False)

    @override
    def __eq__(self, other: object) -> bool:
        """
        Defines rich comparison equality for struct types that inherit from this class
        """

        return bool(eq_compare_and_return_field_failure(self, other))


def assert_struct_size(struct_type: type[MarshalStructure], size_in_bytes: int):
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


def assert_field_offset(struct_type: type[MarshalStructure], field_name: str, byte_offset: int):
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


def update_from_other_structure(
    source_struct: MarshalStructure, target_struct: MarshalStructure
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
    class CoorSystem1(MarshalStructure):
        _fields_ = [
            ("t", c_float),
            ("u", c_float),
            ("v", c_float),
            ("x", c_uint32),
        ]

    class CoorSystem2(MarshalStructure):
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
# Marshal Structure Definition
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


class MarshalUnion(MarshalUnionBase):
    """ctype Union which can marshal its data to/from bytes
    using the to_bytes/from_bytes method
    """

    def to_bytes(
        self,
        byteorder: ByteorderLiteral = "big",
        fields_to_marshal: UnionFieldsToStore = MarshalUnionFieldEnum.First,
    ) -> ToBytesResult:
        """
        Marshal the specified field or fields with the union to bytes.
        Defaults to marshalling the FIRST field of a union to bytes object

        :param: fields_to_marshal Selects which union fields to marshal to bytes
                Can be a mixed list of field names and strings
                or an enum indicating whether to marshal all fields
        """
        output_data = bytearray()
        result = self._union_to_bytes(output_data, byteorder, fields_to_marshal)
        if not result:
            return ToBytesResult(False)
        return ToBytesResult(True, bytes(output_data))

    def _union_to_bytes(
        self,
        output_data: bytearray,
        byteorder: ByteorderLiteral = "big",
        fields_to_marshal: UnionFieldsToStore = MarshalUnionFieldEnum.First,
    ) -> _FieldToBytesResult:
        """
        Marshal the union into the byte array using the specified byte order
        :param: fields_to_marshal Selects which union fields to marshal to bytes
                Can be a mixed list of field names and strings
                or an enum indicating whether to marshal all fields
        """
        if not self._fields_:
            return _FieldToBytesResult(False)

        field_indices: list[int] | range = []
        if isinstance(fields_to_marshal, MarshalUnionFieldEnum):
            if fields_to_marshal == MarshalUnionFieldEnum.First:
                field_indices = [0]
            elif fields_to_marshal == MarshalUnionFieldEnum.Last:
                field_indices = [-1]
            else:
                field_indices = range(len(self._fields_))
        else:
            field_indices = cast(list[int], field_indices)
            for index, field in enumerate(self._fields_):
                if index in fields_to_marshal or field[0] in fields_to_marshal:
                    field_indices.append(index)

        if not field_indices:
            LOGGER.error(
                "No matching fields can be found in union to marshal:"
                " The function did not find any matching indices or field names using the provided"
                f" {fields_to_marshal} list"
            )
            return _FieldToBytesResult(False)

        for index in field_indices:
            field = self._fields_[index]
            # The field descriptor is looked up via the field name on the class type
            # The field value is lookuped via the field name on a class instance
            field_desc: CField = getattr(type(self), field[0])
            field_value = getattr(self, field[0])
            field_name = field_desc.name
            field_type: type[Any] = cast(type[Any], field_desc.type)
            field_size = field_desc.byte_size

            result = MarshalStructure._field_to_bytes(
                output_data=output_data,
                byteorder=byteorder,
                field_name_or_index=field_name,
                field_type=field_type,
                field_byte_size=field_size,
                field_value=field_value,
                field_desc=field_desc,
                prev_field_desc=None,
            )
            if not result:
                return result

        return _FieldToBytesResult(True)

    def to_dict(
        self,
        skip_double_underscore_fields: bool = True,
        fields_to_marshal: UnionFieldsToStore = MarshalUnionFieldEnum.All,
    ) -> ToDictResult:
        """
        Marshal the specified field or fields with the union to dictionary.
        Defaults to marshalling the ALL fields of a union to a bytes object

        :param: skip_double_underscore_fields Whether to skip fields that start with '__'.
                Default is True when storing a dict(i.e Do skip)
                NOTE: This is different from the to_yaml method

        :param: fields_to_marshal Selects which union fields to marshal to dictionary
                Can be a mixed list of field names and strings
                or an enum indicating whether to marshal all fields
        """

        output_dict: dict[str, Any] = {}

        result: _ToFieldResult = self._union_to_dict(
            output_dict,
            skip_double_underscore_fields=skip_double_underscore_fields,
            fields_to_marshal=fields_to_marshal,
        )
        if not result:
            return ToDictResult(False)

        return ToDictResult(True, output_dict)

    def _union_to_dict(
        self,
        output_dict: MutableMapping[str, Any],
        skip_double_underscore_fields: bool,
        fields_to_marshal: UnionFieldsToStore = MarshalUnionFieldEnum.All,
    ) -> _ToFieldResult:
        """
        Marshal the union into a python dictionary

        Defaults to marshalling the ALL fields of a union to a bytes object

        :param: fields_to_marshal Selects which union fields to marshal to dictionary
                Can be a mixed list of field names and strings
                or an enum indicating whether to marshal all fields
        """
        if not self._fields_:
            return _ToFieldResult(False)

        field_indices: list[int] | range = []
        if isinstance(fields_to_marshal, MarshalUnionFieldEnum):
            if fields_to_marshal == MarshalUnionFieldEnum.First:
                field_indices = [0]
            elif fields_to_marshal == MarshalUnionFieldEnum.Last:
                field_indices = [-1]
            else:
                field_indices = range(len(self._fields_))
        else:
            field_indices = cast(list[int], field_indices)
            for index, field in enumerate(self._fields_):
                if index in fields_to_marshal or field[0] in fields_to_marshal:
                    field_indices.append(index)

        if not field_indices:
            LOGGER.error(
                "No matching fields can be found in union to marshal:"
                " The function did not find any matching indices or field names using the provided"
                f" {fields_to_marshal} list"
            )
            return _ToFieldResult(False)

        for index in field_indices:
            field = self._fields_[index]
            # The field descriptor is looked up via the field name on the class type
            # The field value is lookuped via the field name on a class instance
            field_desc: CField = getattr(type(self), field[0])
            field_value = getattr(self, field[0])
            field_name = field_desc.name
            field_type: type[Any] = cast(type[Any], field_desc.type)

            if skip_double_underscore_fields and should_skip_field(field_name):
                continue

            def dict_value_setter(value: Any) -> None:
                output_dict[field_name] = value

            result = MarshalStructure._field_to_dict(
                dict_value_setter=dict_value_setter,
                field_name_or_index=field_name,
                field_type=field_type,
                field_value=field_value,
                skip_double_underscore_fields=skip_double_underscore_fields,
            )

            if not result:
                return result

        return _ToFieldResult(True, output_dict)

    @staticmethod
    def from_bytes[T: MarshalUnion](
        input_data: memoryview,
        union_type: type[T],
        byteorder: ByteorderLiteral = "big",
        field_to_load: UnionFieldToLoad = MarshalUnionFieldEnum.First,
    ) -> FromBytesResult[T]:
        """
        Marshals the bytes from the input byte buffer into the output union using the specified byte order

        :param: field_to_load Selects which union field to use to determine how to load the bytes
                data into the union instance
                Valid Values are
                MarshalUnionFieldEnum.First,
                MarshalUnionFieldEnum.Last,
                the index of a field in the union or
                the name of a field in the union
        """
        output_union: T = union_type()

        result = MarshalUnion._union_from_bytes(input_data, output_union, byteorder, field_to_load)
        if not result:
            return FromBytesResult[T](False, result.next_memoryview)

        return FromBytesResult[T](True, result.next_memoryview, output_union)

    @staticmethod
    def _union_from_bytes(
        input_data: memoryview,
        output_union: MarshalUnion,
        byteorder: ByteorderLiteral = "big",
        field_to_load: UnionFieldToLoad = MarshalUnionFieldEnum.First,
    ) -> _BytesConvertResult:
        """
        Marshals the bytes from the input byte buffer into the output union using the specified byte order

        :param: field_to_load Selects which union field to use to determine how to load the bytes
                data into the union instance
                Valid Values are
                MarshalUnionFieldEnum.First,
                MarshalUnionFieldEnum.Last,
                the index of a field in the union or
                the name of a field in the union
        """
        if not output_union._fields_:
            return _BytesConvertResult(False, input_data)

        field_index: int | None = None
        if isinstance(field_to_load, MarshalUnionFieldEnum):
            field_index = 0 if field_to_load == MarshalUnionFieldEnum.First else 1
        elif isinstance(field_to_load, int):
            field_index = field_to_load if field_to_load < len(output_union._fields_) else None
        else:
            for index, field in enumerate(output_union._fields_):
                if field[0] in field_to_load:
                    field_index = index
                    break

        if field_index is None:
            LOGGER.error(
                "No field from union can be used to load data from bytes."
                f" The function did not find any matching indexusing the provided {field_to_load} value"
            )
            return _BytesConvertResult(False, input_data)

        curr_data_view: memoryview[int] = memoryview(input_data)

        def union_field_setter(name_or_index: str | int, value: Any) -> None:
            name = cast(str, name_or_index)
            setattr(output_union, name, value)

        class_field_name = output_union._fields_[field_index][0]
        field_desc: CField = getattr(type(output_union), class_field_name)
        field_value = getattr(output_union, class_field_name)
        field_name = field_desc.name
        field_type: type[Any] = cast(type[Any], field_desc.type)
        field_size: int = field_desc.byte_size

        result = MarshalStructure._field_from_bytes(
            curr_data_view=curr_data_view,
            byteorder=byteorder,
            field_name_or_index=field_name,
            field_type=field_type,
            field_byte_size=field_size,
            field_value=field_value,
            field_setter=union_field_setter,
            field_desc=field_desc,
            next_field_desc=None,
        )
        if not result:
            return result

        # Update the memory view afte the processed bytes
        curr_data_view = result.next_memoryview

        return _BytesConvertResult(True, curr_data_view)

    @staticmethod
    def from_dict(
        input_dict: dict[str, Any],
        union_type: type[MarshalUnion],
        skip_double_underscore_fields: bool = False,
        field_to_load: UnionFieldToLoad = MarshalUnionFieldEnum.First,
    ) -> FromDictResult[MarshalUnion]:
        """
        Marshal the union into a python dictionary
        Defaults to marshaling the first field from the dictionary into the union

        :param: skip_double_underscore_fields Skip loading a field that starts with '__'
        :param: field_to_load Selects which union field to use to determine how to load the bytes
                data into the union instance
                Valid Values are
                MarshalUnionFieldEnum.First,
                MarshalUnionFieldEnum.Last,
                the index of a field in the union or
                the name of a field in the union
        """

        return union_type._union_from_dict(
            input_dict,
            union_type,
            skip_double_underscore_fields=skip_double_underscore_fields,
            field_to_load=field_to_load,
        )

    @staticmethod
    def _union_from_dict(
        input_dict: dict[str, Any],
        union_type: type[MarshalUnion],
        skip_double_underscore_fields: bool,
        field_to_load: UnionFieldToLoad = MarshalUnionFieldEnum.First,
    ) -> FromDictResult[MarshalUnion]:
        """
        Marshal the union into a python dictionary
        Defaults to marshaling the first field from the dictionary into the union

        :param: field_to_load Selects which union field to use to determine how to load the bytes
                data into the union instance
                Valid Values are
                MarshalUnionFieldEnum.First,
                MarshalUnionFieldEnum.Last,
                the index of a field in the union or
                the name of a field in the union
        """

        output_union = union_type()

        if not output_union._fields_:
            return FromDictResult[MarshalUnion](False)

        field_index: int | None = None
        if isinstance(field_to_load, MarshalUnionFieldEnum):
            field_index = 0 if field_to_load == MarshalUnionFieldEnum.First else 1
        elif isinstance(field_to_load, int):
            field_index = field_to_load if field_to_load < len(output_union._fields_) else None
        else:
            for index, field in enumerate(output_union._fields_):
                if field[0] in field_to_load:
                    field_index = index
                    break

        if field_index is None:
            LOGGER.error(
                "No field from union can be used to load data from dictionary."
                f" The function did not find any matching indexusing the provided {field_to_load} value"
            )
            return FromDictResult[MarshalUnion](False)

        def union_field_setter(name_or_index: str | int, value: Any) -> None:
            name = cast(str, name_or_index)
            setattr(output_union, name, value)

        class_field_name = output_union._fields_[field_index][0]
        field_desc: CField = getattr(type(output_union), class_field_name)
        field_name = field_desc.name
        field_type: type[Any] = cast(type[Any], field_desc.type)

        if skip_double_underscore_fields and should_skip_field(field_name):
            return FromDictResult[MarshalUnion](True, output_union)

        if field_name not in input_dict:
            LOGGER.error(f"Input dictionary is missing field '{field_name}'")
            return FromDictResult[MarshalUnion](False)

        # Grab the next field descriptor if available
        result = MarshalStructure._field_from_dict(
            field_setter=union_field_setter,
            dict_value=input_dict[field_name],
            field_name_or_index=field_name,
            field_type=field_type,
            skip_double_underscore_fields=skip_double_underscore_fields,
        )
        if not result:
            return FromDictResult[MarshalUnion](False)

        return FromDictResult[MarshalUnion](True, output_union)


#
# MarshalStruct and MarshalUnion compare methods
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
            if isinstance(left_array_elem, (MarshalStructure, MarshalUnion)):
                compare_result = eq_compare_and_return_field_failure(left_array_elem, right_array_elem)
                if not compare_result:
                    compare_result.field_name_parts.insert(0, index)
                    return compare_result
            else:
                if left_array_elem != right_array_elem:
                    return CompareStructureResults(False, [index])

    return CompareStructureResults(True, [])


def eq_compare_and_return_field_failure(
    struct_or_union: MarshalStructure | MarshalUnion, other: object
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
        elif isinstance(left_value, (MarshalStructure, MarshalUnion)):
            compare_result = eq_compare_and_return_field_failure(left_value, right_value)
            if not compare_result:
                # prepend the current field name to the field name parts
                compare_result.field_name_parts.insert(0, field_tup[0])
                return compare_result
        else:
            if left_value != right_value:
                return CompareStructureResults(False, [field_tup[0]])

    return CompareStructureResults(True, [])


#
# Fill Structure Type section
# defines classes needed to create a structure with user provided offsets for its members
#
class OffsetField(NamedTuple):
    """
    CType field that is tagged with the offset of where it should be placed with the struct
    """

    offset: int
    field_desc: tuple[str, type[_CDataType]] | tuple[str, type[_CDataType], int]


OffsetFields = list[OffsetField]


OFFSET_FIELDS_ATTR_KEY = "_offset_fields_"
SIZE_FIELDS_ATTR_KEY = "_size_"
GENERATED_FIELD_KEY_FMT = "__generated_field_{}__"


class FillStructureType(type(Structure)):  # type: ignore
    """Metaclass used to fill in a ctype structure with class _fields_ data descriptor
    with generic byte array fields until a specific structure length is reached.

    This can be used to make a structure with particular sub-structures and data fields
    at specific offsets while having the other offsets be filled with untagged bytes
    """

    def __new__(cls, name, bases, attrs):
        if "_fields_" in attrs:
            if OFFSET_FIELDS_ATTR_KEY in attrs:
                raise TypeError(
                    f"Class {name} cannot have both `{OFFSET_FIELDS_ATTR_KEY}` and `_fields_`.\n"
                    f"Use {OFFSET_FIELDS_ATTR_KEY} if wanting to set a offset based structure"
                )
            return super().__new__(name, bases, attrs)

        # If the _offset_fields_ key exist, then fill any gaps set the _fields_ key
        # to all the CType fields and generate fields to fill any missing gaps between offsets
        offset_fields: Sequence[OffsetField] | None = cast(
            Sequence[OffsetField] | None, attrs.get(OFFSET_FIELDS_ATTR_KEY)
        )
        if not isinstance(offset_fields, Sequence):
            raise TypeError(
                f"Class {name} has neither a  `_fields_` or `{OFFSET_FIELDS_ATTR_KEY}` attribute."
                f"The class attributes are {'\n'.join(attrs)}"
            )

        struct_size: int | None = cast(int | None, attrs.get(SIZE_FIELDS_ATTR_KEY))
        if not isinstance(struct_size, int):
            raise TypeError(
                f"Class {name} must have an int struct `{SIZE_FIELDS_ATTR_KEY}` attribute."
                f"The class attributes are {'\n'.join(attrs)}"
            )

        sorted_offset_fields = sorted(offset_fields, key=lambda off_field: off_field.offset)

        fields_after_struct_size: list[OffsetField] = []
        for offset_field in reversed(sorted_offset_fields):
            end_offset = offset_field.offset + sizeof(offset_field.field_desc[1])
            if end_offset <= struct_size:
                break
            fields_after_struct_size.append(offset_field)

            if fields_after_struct_size:
                raise TypeError(
                    f"Specified structure fields {fields_after_struct_size} expands pass the specified"
                    f" struct size of {struct_size}. Cannot create structure..."
                )

        # Track the previous field offset where its data end
        prev_offset_field: OffsetField | None = None
        # Stores the list of CType field descriptors which the _fields_ attr will be set to
        ctype_fields: list[tuple[str, type[_CDataType]] | tuple[str, type[_CDataType], int]] = []
        # Used to generate distinct field names
        generated_field_index = 1

        for offset_field in sorted_offset_fields:
            if prev_offset_field:
                prev_field_range = (
                    prev_offset_field.offset,
                    prev_offset_field.offset + sizeof(prev_offset_field.field_desc[1]),
                )
                prev_field_name = prev_offset_field.field_desc[0]
            else:
                prev_field_range = (0, 0)
                prev_field_name = ""
            if prev_field_range[1] == offset_field.offset:
                # Previous specified field ends at current field start offset
                # the current field can be inserted directly
                pass
            elif prev_field_range[1] < offset_field.offset:
                generated_field_desc = (
                    GENERATED_FIELD_KEY_FMT.format(generated_field_index),
                    c_uint8 * (offset_field.offset - prev_field_range[1]),
                )
                ctype_fields.append(generated_field_desc)
                generated_field_index += 1
            else:
                if prev_offset_field:
                    prev_field_range = (prev_offset_field.offset, prev_field_range[1])
                    prev_field_name = prev_offset_field.field_desc[0]
                else:
                    prev_field_range = (0, 0)
                    prev_field_name = ""

                curr_field_range = (offset_field.offset, offset_field.offset + sizeof(offset_field.field_desc[1]))
                raise TypeError(
                    f"The field '{prev_field_name}'"
                    f" overlaps field '{offset_field.field_desc[0]}' in the structure\n"
                    f"Previous field: offset_range=[0x{prev_field_range[0]:x}, 0x{prev_field_range[1]:x})\n"
                    f"Current field: offset_range=[0x{curr_field_range[0]:x}, 0x{curr_field_range[1]:x})\n"
                )

            ctype_fields.append(offset_field.field_desc)
            prev_offset_field = offset_field

        # After the last loop iteration add a generated field that goes from the end of the specified field data
        # offset to the end of the specified structure size
        last_field_to_end_struct_range = (
            prev_offset_field.offset + sizeof(prev_offset_field.field_desc[1]) if prev_offset_field else 0,
            struct_size,
        )
        if last_field_to_end_struct_range[0] < last_field_to_end_struct_range[1]:
            generated_field_desc = (
                f"__generated_field_{generated_field_index}__",
                c_uint8 * (last_field_to_end_struct_range[1] - last_field_to_end_struct_range[0]),
            )
            ctype_fields.append(generated_field_desc)
            generated_field_index += 1

        # Update the _fields_ ClassVar to have the CType structure generate correctly
        attrs["_fields_"] = ctype_fields

        return super().__new__(cls, name, bases, attrs)


class FillEndianSwapStructure(MarshalStructure, metaclass=FillStructureType):
    """EndianSwap structure which supports specifying fields at a specific offset
    Generated fields of ctype (c_char * [size]) will be added to fill gaps
    between offsets
    """

    # Set the size of the struct
    _size_: ClassVar[int] = 0
    _offset_fields_: ClassVar[OffsetFields] = []
