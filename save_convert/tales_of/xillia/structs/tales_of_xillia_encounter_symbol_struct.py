"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_bool, c_uint8, c_uint32

from save_convert.structs.marshal_structure import (
    MarshalStructure,
    assert_struct_size,
)


class EncountSymbol(MarshalStructure):
    class IndexCountLimit(MarshalStructure):
        _fields_ = [
            ("index", c_uint32),
            ("count", c_uint32),
            ("limit", c_uint32),
        ]

    class Setting(MarshalStructure):
        _fields_ = [
            ("index", c_uint32),
            ("group", c_uint32),
            ("rare", c_bool),
            ("strong", c_bool),
            ("__padding1__", c_uint8 * 2),
            ("frame", c_uint32),
        ]

    _fields_ = [
        ("resumes", IndexCountLimit * 256),  # offset rel=0x0, abs=0x5CD80
        ("settings", Setting * 128),  # offset rel=0xC00, abs=0x5D980
        ("__pad_to_0x1440__", c_uint8 * 64),  # offset rel=0x1400, abs=0x5E180
    ]


assert_struct_size(EncountSymbol, 0x1440)
