"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from save_convert.structs.marshal_structure import (
    MarshalStructure,
    assert_struct_size,
)


class FAME_GET_FRAMEWORK_SAVE_DATA(MarshalStructure):
    _fields_ = []


assert_struct_size(FAME_GET_FRAMEWORK_SAVE_DATA, 0x0)
