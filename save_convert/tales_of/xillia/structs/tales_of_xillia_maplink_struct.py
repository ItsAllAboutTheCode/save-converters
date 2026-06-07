"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_uint32

from save_convert.structs.marshal_struct_base import assert_struct_size
from save_convert.structs.marshal_structure import (
    MarshalStructure,
)


class MapLink(MarshalStructure):
    _fields_ = [
        ("visits", c_uint32 * 32),
    ]


assert_struct_size(MapLink, 0x80)
