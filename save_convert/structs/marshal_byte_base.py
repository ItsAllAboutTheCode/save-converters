"""
Contains classes used patch structures types from a save format
Primarily contains method for endian swapping structure data
when converting from a platform with big-endian save data(PS3/Wii)
to a platform using little-endian (most other platform in existence
i.e PC, PS1, PS3, PS4, PS5, NSW, all Xbox platforms)
"""

import logging
import struct
from collections.abc import Callable
from ctypes import (  # type: ignore[attr-defined]
    Array,
    CField,
    c_bool,
    c_char,
    c_float,
    c_wchar,
    sizeof,
)
from dataclasses import dataclass
from itertools import islice, zip_longest
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    cast,
    overload,
)

from save_convert.structs.marshal_struct_base import (
    FLOAT_TYPES,
    INT_TYPES,
    SIGNED_TYPES,
    ByteorderLiteral,
    MarshalStructBase,
    MarshalUnionBase,
    MarshalUnionFieldEnum,
    UnionFieldsToStore,
    UnionFieldToLoad,
)

if TYPE_CHECKING:
    from ctypes import _CData as CData

LOGGER = logging.getLogger("marshal_byte_base")
LOGGER.setLevel(logging.INFO)
stdoutHandler = logging.StreamHandler()
LOGGER.addHandler(stdoutHandler)

SCRIPT_NAME = Path(__file__).name


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


FieldSetter = Callable[[str | int, Any], None]


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


class MarshalStructByteBase(MarshalStructBase):
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

            result = MarshalStructByteBase._field_to_bytes(
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
        if issubclass(field_type, MarshalStructByteBase) or issubclass(field_type, MarshalUnionByteBase):
            if not isinstance(field_value, (MarshalStructByteBase, MarshalUnionByteBase)):
                return _FieldToBytesResult(False)

            if isinstance(field_value, MarshalStructByteBase):
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

            if not MarshalStructByteBase._array_to_bytes(array_field, marshal_buffer, field_type, byteorder):
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

    # Make sure the output_struct is a subclass of the MarshalByteBase (i.e supports to_bytes and from_bytes method)
    @staticmethod
    def from_bytes[T: MarshalStructByteBase](
        input_data: memoryview, struct_type: type[T], byteorder: ByteorderLiteral = "big"
    ) -> FromBytesResult[T]:
        """
        Marshals the bytes from the input byte buffer into the output structure using the specified byte order
        """
        output_struct: T = struct_type()

        result = MarshalStructByteBase._struct_from_bytes(input_data, output_struct, byteorder)
        if not result:
            return FromBytesResult[T](False, result.next_memoryview)

        return FromBytesResult[T](True, result.next_memoryview, output_struct)

    @staticmethod
    def _struct_from_bytes(
        input_data: memoryview, output_struct: MarshalStructByteBase, byteorder: ByteorderLiteral = "big"
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
            result = MarshalStructByteBase._field_from_bytes(
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

            result = MarshalStructByteBase._field_from_bytes(
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

        if issubclass(field_type, MarshalStructByteBase) or issubclass(field_type, MarshalUnionByteBase):
            if is_struct := issubclass(field_type, MarshalStructByteBase):
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

            result = MarshalStructByteBase._array_from_bytes(curr_data_view, output_buffer, field_type, byteorder)
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


#
### MarshalUnionByteBase
#
class MarshalUnionByteBase(MarshalUnionBase):
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

            result = MarshalStructByteBase._field_to_bytes(
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

    @staticmethod
    def from_bytes[T: MarshalUnionByteBase](
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

        result = MarshalUnionByteBase._union_from_bytes(input_data, output_union, byteorder, field_to_load)
        if not result:
            return FromBytesResult[T](False, result.next_memoryview)

        return FromBytesResult[T](True, result.next_memoryview, output_union)

    @staticmethod
    def _union_from_bytes(
        input_data: memoryview,
        output_union: MarshalUnionByteBase,
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

        result = MarshalStructByteBase._field_from_bytes(
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
