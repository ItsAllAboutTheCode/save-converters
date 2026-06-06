"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from typing import TypedDict


class ChatLinkList(TypedDict):
    booted: list[int]
    registered: list[int]


def create_chat_link_list_save_dict() -> ChatLinkList:
    return {
        "booted": [0] * 256,
        "registered": [0] * 256,
    }
