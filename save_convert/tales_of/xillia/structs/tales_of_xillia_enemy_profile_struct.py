"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_uint32

from save_convert.structs.marshal_struct_base import assert_struct_no_padding
from save_convert.structs.marshal_structure import (
    FillEndianSwapStructure,
    OffsetField,
)


class ENEMY_PROFILE_SAVE_DATA(FillEndianSwapStructure):  #  type: ignore[metaclass]
    class EnemyProfileData(FillEndianSwapStructure):  #  type: ignore[metaclass]
        _size_ = 0x10
        _offset_fields_ = [
            OffsetField(0x0, ("mFlag", c_uint32)),
            OffsetField(0x4, ("mElementOpen", c_uint32)),
            OffsetField(0x8, ("mData", c_uint32 * 2)),
        ]

    _size_ = 0x5000
    _offset_fields_ = [
        OffsetField(0x0, ("mVersion", c_uint32)),
        OffsetField(0x4, ("mEnemyProfileData", EnemyProfileData * 1024)),  # type: ignore[arg-type,operator]
    ]


assert_struct_no_padding(ENEMY_PROFILE_SAVE_DATA)
