"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from typing import TypedDict


class MapLink(TypedDict):
    visits: list[int]


def create_map_link_save_dict() -> MapLink:
    return {"visits": [0] * 32}
