"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from typing import TypedDict


class SkillNewID(TypedDict):
    mSkillNewArray: list[bool]


class MagicArtsNewID(TypedDict):
    mMagicArtsNewArray: list[bool]


class SAVE_DATA_ID_SKILL_DATA_MANAGER(TypedDict):
    mSkillNewIDArray: list[SkillNewID]
    mSkillNewEndIDArray: list[SkillNewID]
    mMagicArtsNewIDArray: list[MagicArtsNewID]
    mMagicArtsNewEndIDArray: list[MagicArtsNewID]


def create_save_data_id_skill_data_manager_save_dict() -> SAVE_DATA_ID_SKILL_DATA_MANAGER:
    return {
        "mSkillNewIDArray": [
            SkillNewID(mSkillNewArray=[False] * 1024),
        ]
        * 2
        + [SkillNewID(mSkillNewArray=[i in [1, 4, 7, 10, 13, 16, 19, 22, 25, 29, 60, 93, 97] for i in range(1024)])]
        + [SkillNewID(mSkillNewArray=[i in [19, 29] for i in range(1024)])]
        + [SkillNewID(mSkillNewArray=[i in [19] for i in range(1024)])]
        + [SkillNewID(mSkillNewArray=[i in [19, 29, 30, 38, 39, 56, 59, 60, 66] for i in range(1024)])]
        + [SkillNewID(mSkillNewArray=[i in [19, 25, 29, 30, 31, 38, 39, 56, 59, 60, 66, 175] for i in range(1024)])],
        "mSkillNewEndIDArray": [SkillNewID(mSkillNewArray=[False] * 1024)] * 7,
        "mMagicArtsNewIDArray": [MagicArtsNewID(mMagicArtsNewArray=[False] * 2048)]
        + [MagicArtsNewID(mMagicArtsNewArray=[i in [13, 15] for i in range(2048)])]
        + [MagicArtsNewID(mMagicArtsNewArray=[i in [55, 56, 57, 58, 59, 63] for i in range(2048)])]
        + [MagicArtsNewID(mMagicArtsNewArray=[i in [83, 84] for i in range(2048)])]
        + [MagicArtsNewID(mMagicArtsNewArray=[i in [110, 119] for i in range(2048)])]
        + [MagicArtsNewID(mMagicArtsNewArray=[i in [138, 142, 143, 147] for i in range(2048)])]
        + [MagicArtsNewID(mMagicArtsNewArray=[i in [168, 171, 178, 181] for i in range(2048)])],
        "mMagicArtsNewEndIDArray": [MagicArtsNewID(mMagicArtsNewArray=[False] * 2048)] * 7,
    }
