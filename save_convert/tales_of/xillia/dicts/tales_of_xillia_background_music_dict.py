"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from typing import TypedDict


class BTL_BGM_SET_SAVE_DATA(TypedDict):
    bgmOpenData: list[bool]


def create_btl_bgm_set_save_data_save_dict() -> BTL_BGM_SET_SAVE_DATA:
    return {"bgmOpenData": [False] * 100}
