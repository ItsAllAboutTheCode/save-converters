"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from typing import TypedDict


class PlayRecordDataArray(TypedDict):
    mValue: list[int]


class PLAY_RECORD_SAVE_DATA(TypedDict):
    mVersion: int
    mPlayRecordData: PlayRecordDataArray


def create_play_record_save_dict() -> PLAY_RECORD_SAVE_DATA:
    return {"mVersion": 100, "mPlayRecordData": {"mValue": [0, 17079, 0, 9] + [0] * 1020}}
