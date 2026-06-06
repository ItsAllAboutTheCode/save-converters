"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from typing import TypedDict


class NpcLayoutList(TypedDict):
    talked: list[int]


def create_npc_layout_list_save_dict() -> NpcLayoutList:
    return {"talked": [0] * 512}
