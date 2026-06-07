"""
Contains classes used patch structures types from a save format
Primarily contains method for endian swapping structure data
when converting from a platform with big-endian save data(PS3/Wii)
to a platform using little-endian (most other platform in existence
i.e PC, PS1, PS3, PS4, PS5, NSW, all Xbox platforms)
"""

import logging
from collections.abc import Sequence
from ctypes import (  # type: ignore[attr-defined]
    Structure,
    c_uint8,
    sizeof,
)
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    ClassVar,
    NamedTuple,
    cast,
)

from save_convert.structs.marshal_dict_base import MarshalStructDictBase, MarshalUnionDictBase

if TYPE_CHECKING:
    from ctypes import _CDataType

LOGGER = logging.getLogger("marshal_structure")
LOGGER.setLevel(logging.INFO)
stdoutHandler = logging.StreamHandler()
LOGGER.addHandler(stdoutHandler)

SCRIPT_NAME = Path(__file__).name


class MarshalStructure(MarshalStructDictBase):
    """ctype Structure which can marshal its data to a bytearray or dictionary
    using the to_bytes/from_bytes method
    """


class MarshalUnion(MarshalUnionDictBase):
    """ctype Union which can marshal its data to a bytearray or dictionary"""


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
            return super().__new__(cls, name, bases, attrs)

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
                f"Class {name} must have an int `{SIZE_FIELDS_ATTR_KEY}` attribute indicating the size of the struct.\n"
                f"The class attributes are:\n{'\n'.join(attrs)}"
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


class FillEndianSwapStructure(MarshalStructure, metaclass=FillStructureType):  #  type: ignore[metaclass]
    """EndianSwap structure which supports specifying fields at a specific offset
    Generated fields of ctype (c_char * [size]) will be added to fill gaps
    between offsets
    """

    # Set the size of the struct
    _size_: ClassVar[int] = 0
    _offset_fields_: ClassVar[OffsetFields] = []
