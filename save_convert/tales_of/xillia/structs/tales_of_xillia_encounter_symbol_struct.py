"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_bool, c_uint32

from save_convert.structs.marshal_struct_base import assert_struct_no_padding
from save_convert.structs.marshal_structure import FillEndianSwapStructure, OffsetField


class EncountSymbol(FillEndianSwapStructure):  #  type: ignore[metaclass]
    class IndexCountLimit(FillEndianSwapStructure):  #  type: ignore[metaclass]
        _size_ = 0xC
        _offset_fields_ = [
            OffsetField(0x0, ("index", c_uint32)),
            OffsetField(0x4, ("count", c_uint32)),
            OffsetField(0x8, ("limit", c_uint32)),
        ]

    class Setting(FillEndianSwapStructure):  #  type: ignore[metaclass]
        _size_ = 0x10
        _offset_fields_ = [
            OffsetField(0x0, ("index", c_uint32)),
            OffsetField(0x4, ("group", c_uint32)),
            OffsetField(0x8, ("rare", c_bool)),
            OffsetField(0x9, ("strong", c_bool)),
            OffsetField(0xC, ("frame", c_uint32)),
        ]

    _size_ = 0x1440
    _offset_fields_ = [
        OffsetField(0x0, ("resumes", IndexCountLimit * 256)),  # type: ignore[arg-type,operator] # offset rel=0x0, abs=0x5CD80
        OffsetField(0xC00, ("settings", Setting * 128)),  # type: ignore[arg-type,operator] # offset rel=0xC00, abs=0x5D9800
    ]


assert_struct_no_padding(EncountSymbol)
