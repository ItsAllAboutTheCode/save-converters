"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_bool

from save_convert.structs.marshal_struct_base import assert_struct_no_padding
from save_convert.structs.marshal_structure import (
    FillEndianSwapStructure,
    OffsetField,
)


class BTL_BGM_SET_SAVE_DATA(FillEndianSwapStructure):  #  type: ignore[metaclass]
    _size_ = 0x64
    _offset_fields_ = [
        OffsetField(0x0, ("bgmOpenData", c_bool * 100)),
    ]


assert_struct_no_padding(BTL_BGM_SET_SAVE_DATA)
