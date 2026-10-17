"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_uint8

from save_convert.structs.marshal_struct_base import assert_struct_no_padding
from save_convert.structs.marshal_structure import (
    FillEndianSwapStructure,
    OffsetField,
)


class RemasteredSaveData(FillEndianSwapStructure):  #  type: ignore[metaclass]
    class PSPSaveData(FillEndianSwapStructure):  #  type: ignore[metaclass]
        _size_ = 0x12D4
        _offset_fields_ = [OffsetField(0x0, ("raw_data", _size_ * c_uint8))]

    _size_ = 0x1800
    _offset_fields_ = [
        OffsetField(0x0, ("psp_save_data", PSPSaveData)),
    ]


assert_struct_no_padding(RemasteredSaveData)
