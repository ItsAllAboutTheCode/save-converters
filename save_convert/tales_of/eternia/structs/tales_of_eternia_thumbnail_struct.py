"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_uint8

from save_convert.structs.marshal_struct_base import assert_struct_no_padding
from save_convert.structs.marshal_structure import (
    FillEndianSwapStructure,
    OffsetField,
)


class ThumbnailPngData(FillEndianSwapStructure):  #  type: ignore[metaclass]
    _size_ = 0x46FCC - 0x1800
    _offset_fields_ = [
        OffsetField(0x0, ("png_data", c_uint8 * _size_)),
    ]


assert_struct_no_padding(ThumbnailPngData)
