"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from save_convert.structs.marshal_structure import (
    MarshalStructure,
    assert_struct_size,
)


class ScriptBaseChat(MarshalStructure):
    _fields_ = []


assert_struct_size(ScriptBaseChat, 0x0)
