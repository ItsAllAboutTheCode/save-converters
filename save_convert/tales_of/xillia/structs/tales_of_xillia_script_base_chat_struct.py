"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from save_convert.structs.marshal_struct_base import assert_struct_size
from save_convert.structs.marshal_structure import (
    MarshalStructure,
)


class ScriptBaseChat(MarshalStructure):
    _fields_ = []


assert_struct_size(ScriptBaseChat, 0x0)
