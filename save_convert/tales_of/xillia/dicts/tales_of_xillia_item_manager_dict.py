"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from typing import TypedDict


class ItemData(TypedDict):
    mItemDataNumArray: list[int]


class NewItemData(TypedDict):
    mNewItemIDArray: list[int]


class ItemGetData(TypedDict):
    mItemGetFlagArray: list[int]


class BuildNewFlagData(TypedDict):
    mBuildNewFlagArray: list[int]


class DLCUseFlagData(TypedDict):
    mDownloadContentsUseFlag: list[int]


class NewStackItemIDData(TypedDict):
    mNewStackItemIDArray: list[int]


class DLCCheckItemIDData(TypedDict):
    mItemIDArray: list[int]


class SAVE_DATA_ID_ITEM_DATA_MANAGER(TypedDict):
    mItemNum: ItemData
    mNewItemID: NewItemData
    mItemGetFlag: ItemGetData
    mBuildNewFlag: BuildNewFlagData
    mDownloadContentsUseFlag: DLCUseFlagData
    mNewStackItemID: NewStackItemIDData
    mDLCCheckItemID: DLCCheckItemIDData


def create_save_data_id_item_data_manager_save_dict() -> SAVE_DATA_ID_ITEM_DATA_MANAGER:
    return {
        "mItemNum": {"mItemDataNumArray": [0] * 6144},
        "mNewItemID": {
            "mNewItemIDArray": [
                83886083,
                67108941,
                67108868,
                100663365,
                100663364,
                100663363,
                100663362,
                100663361,
                100663360,
                100663352,
                100663351,
                100663350,
                100663349,
                100663297,
                100663298,
                100663299,
                100663300,
                100663301,
                100663302,
                100663303,
                100663304,
                100663305,
                100663306,
                100663307,
                100663308,
                100663309,
                100663310,
                100663311,
                100663312,
                100663313,
                100663314,
                100663315,
                100663316,
                100663317,
                100663318,
                100663319,
                100663320,
                100663321,
                100663322,
                100663326,
                100663327,
                100663328,
                100663329,
                100663330,
                100663331,
                100663339,
                100663340,
                100663341,
                100663342,
                13,
                3,
                1,
                83886088,
                83886087,
                100663379,
                100663378,
                100663377,
                100663348,
                100663347,
                100663346,
                100663345,
                100663344,
                100663343,
            ]
            + [0] * 193
        },
        "mItemGetFlag": {"mItemGetFlagArray": [10, 32] + [0] * 766},
        "mBuildNewFlag": {"mBuildNewFlagArray": [0] * 768},
        "mDownloadContentsUseFlag": {"mDownloadContentsUseFlag": [0] * 64},
        "mNewStackItemID": {
            "mNewStackItemIDArray": [
                83886083,
                67108941,
                67108868,
                100663365,
                100663364,
                100663363,
                100663362,
                100663361,
                100663360,
                100663352,
                100663351,
                100663350,
                100663349,
                100663297,
                100663298,
                100663299,
                100663300,
                100663301,
                100663302,
                100663303,
                100663304,
                100663305,
                100663306,
                100663307,
                100663308,
                100663309,
                100663310,
                100663311,
                100663312,
                100663313,
                100663314,
                100663315,
            ]
        },
        "mDLCCheckItemID": {"mItemIDArray": [0] * 20},
    }
