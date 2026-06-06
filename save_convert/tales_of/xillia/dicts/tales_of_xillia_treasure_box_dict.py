"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from typing import TypedDict


class TreeViewCursor(TypedDict):
    index: int
    row: int
    column: int


class TreasureLocation(TypedDict):
    mapid: str
    max: int
    list: list[TreeViewCursor]


class TreasureBoxSaveDict(TypedDict):
    opend: list[int]
    normal: list[TreasureLocation]
    search: list[TreasureLocation]
    location: str
    openRandomData: list[int]


def create_treasure_box_save_dict() -> TreasureBoxSaveDict:
    return {
        "opend": [0] * 256,
        "normal": [
            TreasureLocation({"mapid": "DUN_INS_000", "max": 0, "list": [{"index": 0, "row": 0, "column": 0}] * 8})
        ]
        + [TreasureLocation({"mapid": "", "max": 0, "list": [{"index": 0, "row": 0, "column": 0}] * 8})] * 32,
        "search": [
            TreasureLocation({"mapid": "DUN_INS_000", "max": 1, "list": [{"index": 25, "row": 5, "column": 1}] * 8})
        ]
        + [TreasureLocation({"mapid": "", "max": 0, "list": [{"index": 0, "row": 0, "column": 0}] * 8})] * 32,
        "location": "DUN_INS_000",
        "openRandomData": [0] * 32,
    }
