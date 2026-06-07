"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_uint32

from save_convert.structs.marshal_struct_base import assert_struct_no_padding
from save_convert.structs.marshal_structure import FillEndianSwapStructure, OffsetField


class PLAY_RECORD_SAVE_DATA(FillEndianSwapStructure):  #  type: ignore[metaclass]
    class PlayRecordDataArray(FillEndianSwapStructure):  #  type: ignore[metaclass]
        _size_ = 0x1000
        _offset_fields_ = [OffsetField(0x0, ("mValue", c_uint32 * 1024))]

    _size_ = 0x4000
    _offset_fields_ = [
        OffsetField(0x0, ("mVersion", c_uint32)),
        OffsetField(0x4, ("mPlayRecordData", PlayRecordDataArray)),
    ]


assert_struct_no_padding(PLAY_RECORD_SAVE_DATA)
