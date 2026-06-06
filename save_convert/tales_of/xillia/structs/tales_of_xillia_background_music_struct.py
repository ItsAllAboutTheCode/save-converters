"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_bool

from save_convert.structs.marshal_structure import (
    MarshalStructure,
    assert_struct_size,
)


class BTL_BGM_SET_SAVE_DATA(MarshalStructure):
    _fields_ = [
        ("bgmOpenData", c_bool * 100),
    ]


assert_struct_size(BTL_BGM_SET_SAVE_DATA, 0x64)
