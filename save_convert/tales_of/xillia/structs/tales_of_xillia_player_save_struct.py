"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_bool, c_uint32

from save_convert.structs.marshal_struct_base import assert_struct_no_padding
from save_convert.structs.marshal_structure import (
    FillEndianSwapStructure,
    OffsetField,
)


class PLAYER_SAVE_DATA(FillEndianSwapStructure):  #  type: ignore[metaclass]
    class PlayerData(FillEndianSwapStructure):  #  type: ignore[metaclass]
        _size_ = 0xC
        _offset_fields_ = [
            OffsetField(0x0, ("mVersion", c_uint32)),
            OffsetField(0x4, ("mOperation", c_uint32)),
            OffsetField(0x8, ("mHoldDush", c_bool)),
        ]

    _size_ = 0x4000
    _offset_fields_ = [
        OffsetField(0x0, ("mPlayerData", PlayerData)),
    ]

    assert_struct_no_padding(PlayerData)


assert_struct_no_padding(PLAYER_SAVE_DATA)
