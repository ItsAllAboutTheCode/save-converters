"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from typing import TypedDict


class AutoItemSlotData(TypedDict):
    mIsValid: bool
    mItemId: int
    mAutoItemDataId: int
    mItemLimitNum: int


class AUTO_ITEM_SLOT_SAVE_DATA(TypedDict):
    mVersion: int
    mAutoItemSlotData: list[AutoItemSlotData]


def create_auto_item_slot_save_dict() -> AUTO_ITEM_SLOT_SAVE_DATA:
    return {
        "mVersion": 110,
        "mAutoItemSlotData": [
            AutoItemSlotData(mIsValid=True, mItemId=13, mAutoItemDataId=13, mItemLimitNum=2),
            AutoItemSlotData(mIsValid=True, mItemId=1, mAutoItemDataId=2, mItemLimitNum=2),
            AutoItemSlotData(mIsValid=True, mItemId=3, mAutoItemDataId=4, mItemLimitNum=2),
        ]
        + [AutoItemSlotData(mIsValid=False, mItemId=0, mAutoItemDataId=0, mItemLimitNum=0)] * 29,
    }
