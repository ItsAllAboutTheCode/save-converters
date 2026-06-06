"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_bool, c_uint8, c_uint32

from save_convert.structs.marshal_structure import (
    MarshalStructure,
    assert_struct_size,
)


class PLAYER_SAVE_DATA(MarshalStructure):
    class PlayerData(MarshalStructure):
        _fields_ = [
            ("mVersion", c_uint32),
            ("mOperation", c_uint32),
            ("mHoldDush", c_bool),
            ("__padding__", c_uint8 * 3),
        ]

    _fields_ = [
        ("mPlayerData", PlayerData),
        ("__align_to_16834__", c_uint8 * (0x4000 - 12)),
    ]


assert_struct_size(PLAYER_SAVE_DATA, 0x4000)
