"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_bool

from save_convert.structs.marshal_struct_base import assert_struct_no_padding
from save_convert.structs.marshal_structure import FillEndianSwapStructure, OffsetField


class SAVE_DATA_ID_SKILL_DATA_MANAGER(FillEndianSwapStructure):  #  type: ignore[metaclass]
    class SkillNewID(FillEndianSwapStructure):  #  type: ignore[metaclass]
        _size_ = 0x400
        _offset_fields_ = [
            OffsetField(0x0, ("mSkillNewArray", c_bool * 1024)),
        ]

    class MagicArtsNewID(FillEndianSwapStructure):  #  type: ignore[metaclass]
        _size_ = 0x800
        _offset_fields_ = [
            OffsetField(0x0, ("mMagicArtsNewArray", c_bool * 2048)),
        ]

    _size_ = 0xA800
    _offset_fields_ = [
        OffsetField(0x0, ("mSkillNewIDArray", SkillNewID * 7)),  #  type: ignore[arg-type,operator]
        OffsetField(0x1C00, ("mSkillNewEndIDArray", SkillNewID * 7)),  #  type: ignore[arg-type,operator]
        OffsetField(0x3800, ("mMagicArtsNewIDArray", MagicArtsNewID * 7)),  #  type: ignore[arg-type,operator]
        OffsetField(0x7000, ("mMagicArtsNewEndIDArray", MagicArtsNewID * 7)),  #  type: ignore[arg-type,operator]
    ]


assert_struct_no_padding(SAVE_DATA_ID_SKILL_DATA_MANAGER)
