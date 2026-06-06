"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_bool

from save_convert.structs.marshal_structure import (
    MarshalStructure,
    assert_struct_size,
)


class SAVE_DATA_ID_SKILL_DATA_MANAGER(MarshalStructure):
    class SkillNewID(MarshalStructure):
        _fields_ = [
            ("mSkillNewArray", c_bool * 1024),
        ]

    class MagicArtsNewID(MarshalStructure):
        _fields_ = [
            ("mMagicArtsNewArray", c_bool * 2048),
        ]

    _fields_ = [
        ("mSkillNewIDArray", SkillNewID * 7),
        ("mSkillNewEndIDArray", SkillNewID * 7),
        ("mMagicArtsNewIDArray", MagicArtsNewID * 7),
        ("mMagicArtsNewEndIDArray", MagicArtsNewID * 7),
    ]


assert_struct_size(SAVE_DATA_ID_SKILL_DATA_MANAGER, 0xA800)
