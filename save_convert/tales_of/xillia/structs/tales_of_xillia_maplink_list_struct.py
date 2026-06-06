"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_uint32

from save_convert.structs.marshal_structure import (
    MarshalStructure,
    assert_struct_size,
)


class MapLinkList(MarshalStructure):
    _fields_ = [
        ("bootcount", c_uint32),
    ]


assert_struct_size(MapLinkList, 0x4)
