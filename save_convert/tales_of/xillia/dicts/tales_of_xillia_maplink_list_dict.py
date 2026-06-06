"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from typing import TypedDict


class MapLinkList(TypedDict):
    bootcount: int


def create_map_link_list_save_dict() -> MapLinkList:
    return {"bootcount": 0}
