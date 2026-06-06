"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_char, c_uint8

from save_convert.structs.marshal_structure import (
    MarshalStructure,
    assert_struct_size,
)


class BindingData(MarshalStructure):
    _fields_ = [
        ("keyboardMouseUser", c_uint8),
        ("fieldData", (c_char * 32) * 21),
        ("battleData00", (c_char * 32) * 23),
        ("battleData01", (c_char * 32) * 23),
        ("battleData02", (c_char * 32) * 23),
        ("battleData03", (c_char * 32) * 23),
    ]


assert_struct_size(BindingData, 0xE21)
