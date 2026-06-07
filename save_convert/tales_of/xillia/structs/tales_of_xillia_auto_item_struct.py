"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_bool, c_uint32

from save_convert.structs.marshal_struct_base import assert_struct_no_padding
from save_convert.structs.marshal_structure import (
    FillEndianSwapStructure,
    OffsetField,
)


class AUTO_ITEM_SLOT_SAVE_DATA(FillEndianSwapStructure):  #  type: ignore[metaclass]
    class AutoItemSlotData(FillEndianSwapStructure):  #  type: ignore[metaclass]
        _size_ = 0x10
        _offset_fields_ = [
            OffsetField(0x0, ("mIsValid", c_bool)),  # offset abs=0x641D4
            OffsetField(0x4, ("mItemId", c_uint32)),  # offset abs=0x641D8
            OffsetField(0x8, ("mAutoItemDataId", c_uint32)),  # offset abs=0x641DC
            OffsetField(0xC, ("mItemLimitNum", c_uint32)),  # offset abs=0x641E0
        ]

    _size_ = 0x800
    _offset_fields_ = [
        OffsetField(0x0, ("mVersion", c_uint32)),  # offset abs=0x641D0
        OffsetField(0x4, ("mAutoItemSlotData", AutoItemSlotData * 20)),  # type: ignore[arg-type,operator] # offset rel=0x4, abs=0x641D4
    ]


assert_struct_no_padding(AUTO_ITEM_SLOT_SAVE_DATA)
