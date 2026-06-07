"""
Contains classes used patch structures types from a save format
Primarily contains method for endian swapping structure data
when converting from a platform with big-endian save data(PS3/Wii)
to a platform using little-endian (most other platform in existence
i.e PC, PS1, PS3, PS4, PS5, NSW, all Xbox platforms)
"""

import logging
from collections import deque
from collections.abc import Callable, MutableMapping
from ctypes import (  # type: ignore[attr-defined]
    Array,
    CField,
    Structure,
    c_bool,
    c_char,
    c_wchar,
    sizeof,
)
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    NamedTuple,
    TypeIs,
    cast,
    overload,
)

from ruamel.yaml import YAML
from save_convert.structs.marshal_byte_base import FieldSetter, MarshalStructByteBase, MarshalUnionByteBase
from save_convert.structs.marshal_struct_base import (
    BYTE_TYPES_PLUS_CHAR,
    FLOAT_TYPES,
    INT_TYPES,
    MarshalStructBase,
    MarshalUnionBase,
    MarshalUnionFieldEnum,
    StructureDict,
    StructureList,
    UnionFieldsToStore,
    UnionFieldToLoad,
)

if TYPE_CHECKING:
    from ctypes import _CData as CData

LOGGER = logging.getLogger("marshal_dict_base")
LOGGER.setLevel(logging.INFO)
stdoutHandler = logging.StreamHandler()
LOGGER.addHandler(stdoutHandler)

SCRIPT_NAME = Path(__file__).name


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


DictFieldSetter = Callable[[Any], None]


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


def should_skip_field(field_name: str) -> bool:
    """
    Determines if a field should be skipped based on the field name
    This is used to prevent propagating __<name>__ fields
    to and from dictionaries
    """
    return field_name.startswith("__")


class MarshalStructDictBase(MarshalStructByteBase):
    """ctype Structure which can marshal its to and from a Python dictionary
    using the to_dict/from_dict method
    """

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

                    if isinstance(field_value, MarshalStructDictBase) and isinstance(child_field, dict):
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

            result: _ToFieldResult = MarshalStructDictBase._field_to_dict(
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
        if issubclass(field_type, MarshalStructDictBase) or issubclass(field_type, MarshalUnionDictBase):
            if not isinstance(field_value, (MarshalStructDictBase, MarshalUnionDictBase)):
                return _ToFieldResult(False)

            sub_dict = StructureDict()
            if isinstance(field_value, MarshalStructDictBase):
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
            to_array_result = MarshalStructDictBase._array_to_dict(
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

    @staticmethod
    def from_yaml(
        input_yaml: bytes, struct_type: type[MarshalStructDictBase], skip_double_underscore_fields: bool = False
    ) -> FromDictResult[MarshalStructDictBase]:
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
            return FromDictResult[MarshalStructDictBase](False)

        # Load struct from dictionary
        from_dict_result: FromDictResult[MarshalStructDictBase] = struct_type.from_dict(
            yaml_data, struct_type, skip_double_underscore_fields=skip_double_underscore_fields
        )

        return from_dict_result

    @staticmethod
    def from_dict(
        input_dict: dict[str, Any], struct_type: type[MarshalStructDictBase], skip_double_underscore_fields: bool = True
    ) -> FromDictResult[MarshalStructDictBase]:
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
        input_dict: dict[str, Any], struct_type: type[MarshalStructDictBase], skip_double_underscore_fields: bool
    ) -> FromDictResult[MarshalStructDictBase]:
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
                return FromDictResult[MarshalStructDictBase](False)

            # Grab the next field descriptor if available
            result = MarshalStructDictBase._field_from_dict(
                field_setter=struct_field_setter,
                dict_value=input_dict[field_name],
                field_name_or_index=field_name,
                field_type=field_type,
                skip_double_underscore_fields=skip_double_underscore_fields,
            )
            if not result:
                return FromDictResult[MarshalStructDictBase](False)

        return FromDictResult[MarshalStructDictBase](True, output_struct)

    @staticmethod
    def _array_from_dict(
        input_array: StructureList | bytes | str, array_type: type[Array[CData]], skip_double_underscore_fields: bool
    ) -> _ToFieldResult:
        """
        Marshal the array into a python dictionary
        """
        field_type = cast("type[CData]", array_type._type_)
        array_length: int = cast(int, cast(object, array_type._length_))

        # Convert any stringified hex dumps to a byte array for the bytes types
        # The character types are stored as plain strings
        if field_type in BYTE_TYPES_PLUS_CHAR:
            if isinstance(input_array, str):
                input_array = bytes.fromhex(input_array) if field_type != c_char else input_array.encode("utf-8")

        if field_type == c_char:
            # Arrays of c_char are treated as bytes by the ctypes module
            try:
                # Truncate any input array to be at maximumg the size of the array field
                return _ToFieldResult(
                    True, input_array if len(input_array) <= array_length else input_array[:array_length]
                )
            except ValueError as err:
                LOGGER.error(f"Could not convert input_array to bytes for field type {field_type}: {err}")
                return _ToFieldResult(False)
        elif field_type == c_wchar:
            # Arrays of c_wchar are treated as str by the ctypes module
            try:
                return _ToFieldResult(
                    True, input_array if len(input_array) <= array_length else input_array[:array_length]
                )
            except ValueError as err:
                LOGGER.error(f"Could not convert input_array to string for field type {field_type}: {err}")
                return _ToFieldResult(False)

        output_array = array_type()
        # Parse each field of the array
        # Truncate to the length of the ctypes Array
        for arr_index in range(output_array._length_):
            # The field descriptor is looked up via the field name on the class type
            # The field value is lookuped via the field name on a class instance
            try:
                elem_value = input_array[arr_index]
            except IndexError as err:
                LOGGER.debug(
                    f"Array from dictionary is smaller than the struct array: {err}\n"
                    "The remaining struct array fields will be left default initialized"
                )
                break

            def array_field_setter(name_or_index: str | int, value: Any) -> None:
                index = cast(int, name_or_index)
                output_array[index] = value

            result: _ToFieldResult = MarshalStructDictBase._field_from_dict(
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
        if issubclass(field_type, MarshalStructDictBase) or issubclass(field_type, MarshalUnionDictBase):
            if is_struct := issubclass(field_type, MarshalStructDictBase):
                from_dict_result: FromDictResult[MarshalStructDictBase] | FromDictResult[MarshalUnionDictBase] = (
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
            result: _ToFieldResult = MarshalStructDictBase._array_from_dict(
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


#
# Marshal Union Dict Definition
#
class MarshalUnionDictBase(MarshalUnionByteBase):
    """ctype Union which can marshal its data to/from a Python dictionary
    using the to_dict/from_dict method
    """

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

            result = MarshalStructDictBase._field_to_dict(
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
    def from_dict(
        input_dict: dict[str, Any],
        union_type: type[MarshalUnionDictBase],
        skip_double_underscore_fields: bool = False,
        field_to_load: UnionFieldToLoad = MarshalUnionFieldEnum.First,
    ) -> FromDictResult[MarshalUnionDictBase]:
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
        union_type: type[MarshalUnionDictBase],
        skip_double_underscore_fields: bool,
        field_to_load: UnionFieldToLoad = MarshalUnionFieldEnum.First,
    ) -> FromDictResult[MarshalUnionDictBase]:
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
            return FromDictResult(False)

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
            return FromDictResult(False)

        def union_field_setter(name_or_index: str | int, value: Any) -> None:
            name = cast(str, name_or_index)
            setattr(output_union, name, value)

        class_field_name = output_union._fields_[field_index][0]
        field_desc: CField = getattr(type(output_union), class_field_name)
        field_name = field_desc.name
        field_type: type[Any] = cast(type[Any], field_desc.type)

        if skip_double_underscore_fields and should_skip_field(field_name):
            return FromDictResult(True, output_union)

        if field_name not in input_dict:
            LOGGER.error(f"Input dictionary is missing field '{field_name}'")
            return FromDictResult(False)

        # Grab the next field descriptor if available
        result = MarshalStructDictBase._field_from_dict(
            field_setter=union_field_setter,
            dict_value=input_dict[field_name],
            field_name_or_index=field_name,
            field_type=field_type,
            skip_double_underscore_fields=skip_double_underscore_fields,
        )
        if not result:
            return FromDictResult(False)

        return FromDictResult(True, output_union)
