"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from typing import TypedDict


class BindingData(TypedDict):
    keyboardMouseUser: int
    fieldData: list[str]
    battleData00: list[str]
    battleData01: list[str]
    battleData02: list[str]
    battleData03: list[str]


def create_binding_data_save_dict() -> BindingData:
    return {
        "keyboardMouseUser": 0,
        "fieldData": [""] * 21,
        "battleData00": [""] * 23,
        "battleData01": [""] * 23,
        "battleData02": [""] * 23,
        "battleData03": [""] * 23,
    }
