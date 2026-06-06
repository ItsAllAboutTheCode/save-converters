"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_uint8, c_uint32

from save_convert.structs.marshal_structure import (
    MarshalStructure,
    assert_struct_size,
)


class SAVE_DATA_ID_ITEM_DATA_MANAGER(MarshalStructure):
    class ItemData(MarshalStructure):
        _fields_ = [
            ("mItemDataNumArray", c_uint8 * 6144),
            ("__itemdatanum_align__", c_uint8 * 2048),  # Align up to power of 2
        ]

    class NewItemData(MarshalStructure):
        _fields_ = [
            ("mNewItemIDArray", c_uint32 * 256),
        ]

    class ItemGetData(MarshalStructure):
        _fields_ = [
            ("mItemGetFlagArray", c_uint8 * 768),
            ("__itemgetflag_align__", c_uint8 * 256),  # Align up to power of 2
        ]

    class BuildNewFlagData(MarshalStructure):
        _fields_ = [
            ("mBuildNewFlagArray", c_uint8 * 768),
            ("__buildnewflag_align__", c_uint8 * 256),  # Align up to power of 2
        ]

    class DLCUseFlagData(MarshalStructure):
        _fields_ = [
            ("mDownloadContentsUseFlag", c_uint8 * 64),
        ]

    class NewStackItemIDData(MarshalStructure):
        _fields_ = [
            ("mNewStackItemIDArray", c_uint32 * 32),
        ]

    class DLCCheckItemIDData(MarshalStructure):
        _fields_ = [
            ("mItemIDArray", c_uint32 * 20),
            ("__itemid_align__", c_uint32 * 12),  # Align up to power of 2
        ]

    _fields_ = [
        ("mItemNum", ItemData),  # offset rel=0x0, abs=0x601D0
        ("mNewItemID", NewItemData),  # offset rel=0x2000, abs=0x621D0
        ("mItemGetFlag", ItemGetData),  # offset rel=0x2400, abs=0x625D0
        ("mBuildNewFlag", BuildNewFlagData),  # offset rel=0x2800, abs=0x629D0
        ("mDownloadContentsUseFlag", DLCUseFlagData),  # offset rel=0x2C00, abs=0x62DD0
        ("mNewStackItemID", NewStackItemIDData),  # offset rel=0x2C40, abs=0x62E10
        ("mDLCCheckItemID", DLCCheckItemIDData),  # offset rel=0x2CC0, abs=0x62E90
        ("__align_up_to_16384__", c_uint8 * (0x4000 - 0x2D40)),
    ]


assert_struct_size(SAVE_DATA_ID_ITEM_DATA_MANAGER, 0x4000)
