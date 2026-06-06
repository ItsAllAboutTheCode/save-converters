"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from typing import TypedDict


class BattleBookNewData(TypedDict):
    mData: list[bool]


def create_battle_book_new_data_save_dict() -> BattleBookNewData:
    return {"mData": [False] * 100}
