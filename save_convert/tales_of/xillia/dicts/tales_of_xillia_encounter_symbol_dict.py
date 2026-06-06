"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from typing import TypedDict


class IndexCountLimit(TypedDict):
    index: int
    count: int
    limit: int


class Setting(TypedDict):
    index: int
    group: int
    rare: bool
    strong: bool
    frame: int


class EncountSymbol(TypedDict):
    resumes: list[IndexCountLimit]
    settings: list[Setting]


def create_encount_symbol_save_dict() -> EncountSymbol:
    return {
        "resumes": [{"index": 0, "count": 0, "limit": 0}] * 256,
        "settings": [{"index": 0, "group": 0, "rare": False, "strong": False, "frame": 0}] * 128,
    }
