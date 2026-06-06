"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_uint8

from save_convert.structs.marshal_structure import (
    MarshalStructure,
    assert_struct_size,
)


class ChatLinkList(MarshalStructure):
    _fields_ = [
        ("booted", c_uint8 * 256),
        ("registered", c_uint8 * 256),
    ]


assert_struct_size(ChatLinkList, 0x200)
