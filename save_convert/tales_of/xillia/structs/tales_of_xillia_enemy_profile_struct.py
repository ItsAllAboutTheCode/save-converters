"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_uint8, c_uint32

from save_convert.structs.marshal_structure import (
    MarshalStructure,
    assert_struct_size,
)


class ENEMY_PROFILE_SAVE_DATA(MarshalStructure):
    class EnemyProfileData(MarshalStructure):
        _fields_ = [
            ("mFlag", c_uint32),
            ("mElementOpen", c_uint32),
            ("mData", c_uint32 * 2),
        ]

    _fields_ = [
        ("mVersion", c_uint32),
        ("mEnemyProfileData", EnemyProfileData * 1024),
        ("__align_to_next_4096__", c_uint8 * (0x1000 - 4)),
    ]


assert_struct_size(ENEMY_PROFILE_SAVE_DATA, 0x5000)
