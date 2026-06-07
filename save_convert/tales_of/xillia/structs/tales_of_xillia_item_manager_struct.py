"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_uint8, c_uint32

from save_convert.structs.marshal_struct_base import assert_struct_no_padding
from save_convert.structs.marshal_structure import (
    FillEndianSwapStructure,
    OffsetField,
)


class SAVE_DATA_ID_ITEM_DATA_MANAGER(FillEndianSwapStructure):  #  type: ignore[metaclass]
    class ItemData(FillEndianSwapStructure):  #  type: ignore[metaclass]
        _size_ = 0x1800
        _offset_fields_ = [
            OffsetField(0x0, ("mItemDataNumArray", c_uint8 * 6144)),
        ]

    class NewItemData(FillEndianSwapStructure):  #  type: ignore[metaclass]
        _size_ = 0x400
        _offset_fields_ = [
            OffsetField(0x0, ("mNewItemIDArray", c_uint32 * 256)),
        ]

    class ItemGetData(FillEndianSwapStructure):  #  type: ignore[metaclass]
        _size_ = 0x300
        _offset_fields_ = [
            OffsetField(0x0, ("mItemGetFlagArray", c_uint8 * 768)),
        ]

    class BuildNewFlagData(FillEndianSwapStructure):  #  type: ignore[metaclass]
        _size_ = 0x300
        _offset_fields_ = [
            OffsetField(0x0, ("mBuildNewFlagArray", c_uint8 * 768)),
        ]

    class DLCUseFlagData(FillEndianSwapStructure):  #  type: ignore[metaclass]
        _size_ = 0x40
        _offset_fields_ = [
            OffsetField(0x0, ("mDownloadContentsUseFlag", c_uint8 * 64)),
        ]

    class NewStackItemIDData(FillEndianSwapStructure):  #  type: ignore[metaclass]
        _size_ = 0x80
        _offset_fields_ = [
            OffsetField(0x0, ("mNewStackItemIDArray", c_uint32 * 32)),
        ]

    class DLCCheckItemIDData(FillEndianSwapStructure):  #  type: ignore[metaclass]
        _size_ = 0x50
        _offset_fields_ = [
            OffsetField(0x0, ("mItemIDArray", c_uint32 * 20)),
        ]

    _size_ = 0x4000
    _offset_fields_ = [
        OffsetField(0x0, ("mItemNum", ItemData)),  # offset rel=0x0, abs=0x601D0
        OffsetField(0x2000, ("mNewItemID", NewItemData)),  # offset rel=0x2000, abs=0x621D0
        OffsetField(0x2400, ("mItemGetFlag", ItemGetData)),  # offset rel=0x2400, abs=0x625D0
        OffsetField(0x2800, ("mBuildNewFlag", BuildNewFlagData)),  # offset rel=0x2800, abs=0x629D0
        OffsetField(0x2C00, ("mDownloadContentsUseFlag", DLCUseFlagData)),  # offset rel=0x2C00, abs=0x62DD0
        OffsetField(0x2C40, ("mNewStackItemID", NewStackItemIDData)),  # offset rel=0x2C40, abs=0x62E10
        OffsetField(0x2CC0, ("mDLCCheckItemID", DLCCheckItemIDData)),  # offset rel=0x2CC0, abs=0x62E90
    ]


assert_struct_no_padding(SAVE_DATA_ID_ITEM_DATA_MANAGER)
