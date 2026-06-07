"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_uint32

from save_convert.structs.marshal_struct_base import assert_struct_size
from save_convert.structs.marshal_structure import (
    MarshalStructure,
)


class NpcLayoutList(MarshalStructure):
    _fields_ = [
        ("talked", c_uint32 * 512),
    ]


assert_struct_size(NpcLayoutList, 0x800)
