"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_bool, c_uint8, c_uint32

from save_convert.structs.marshal_structure import (
    MarshalStructure,
    assert_struct_size,
)


class AUTO_ITEM_SLOT_SAVE_DATA(MarshalStructure):
    class AutoItemSlotData(MarshalStructure):
        _fields_ = [
            ("mIsValid", c_bool),  # offset abs=0x641D4
            ("__padding__", c_uint8 * 3),  # offset abs=0x641D5
            ("mItemId", c_uint32),  # offset abs=0x641D8
            ("mAutoItemDataId", c_uint32),  # offset abs=0x641DC
            ("mItemLimitNum", c_uint32),  # offset abs=0x641E0
        ]

    _fields_ = [
        ("mVersion", c_uint32),  # offset abs=0x641D0
        ("mAutoItemSlotData", AutoItemSlotData * 20),  # offset rel=0x4, abs=0x641D4
        ("__slotdata_align__", AutoItemSlotData * 12),  # Align up to power of 2: offset rel=0x144, abs=0x64314
        ("__align_up_to_2048__", c_uint8 * (0x800 - 0x204)),  # offset rel=0x204, abs=0x643D4
    ]


assert_struct_size(AUTO_ITEM_SLOT_SAVE_DATA, 0x800)
