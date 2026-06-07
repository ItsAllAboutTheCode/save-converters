"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_bool

from save_convert.structs.marshal_struct_base import assert_struct_size
from save_convert.structs.marshal_structure import (
    MarshalStructure,
)


class BattleBookNewData(MarshalStructure):
    _fields_ = [("mData", c_bool * 100)]


assert_struct_size(BattleBookNewData, 0x64)
