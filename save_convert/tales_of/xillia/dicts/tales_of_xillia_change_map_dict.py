"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from typing import TypedDict


class ChangeMapSaveDict(TypedDict):
    map: str
    location: str


def create_change_map_save_dict() -> ChangeMapSaveDict:
    return {"map": "DUN_INS_000", "location": "DUN_INS_000"}
