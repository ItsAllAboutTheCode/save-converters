"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from typing import TypedDict


class EnemyProfileData(TypedDict):
    mFlag: int
    mElementOpen: int
    mData: list[int]


class ENEMY_PROFILE_SAVE_DATA(TypedDict):
    mVersion: int
    mEnemyProfileData: list[EnemyProfileData]


def create_enemy_profile_save_dict() -> ENEMY_PROFILE_SAVE_DATA:
    return {
        "mVersion": 100,
        "mEnemyProfileData": [{"mFlag": 0, "mElementOpen": 0, "mData": [0, 0]}] * 1024,
    }
