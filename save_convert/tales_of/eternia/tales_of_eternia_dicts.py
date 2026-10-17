"""
List of structures mapping to raw binary save file for Tales of Eternia
"""

from typing import TypedDict


class EterniaRemasteredSaveDict(TypedDict):
    pass


def default_remastered_save_dict() -> EterniaRemasteredSaveDict:
    return EterniaRemasteredSaveDict()
