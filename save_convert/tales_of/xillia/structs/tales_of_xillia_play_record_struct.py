"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_uint8, c_uint32

from save_convert.structs.marshal_structure import (
    MarshalStructure,
    assert_struct_size,
)


class PLAY_RECORD_SAVE_DATA(MarshalStructure):
    class PlayRecordDataArray(MarshalStructure):
        _fields_ = [("mValue", c_uint32 * 1024)]

    _fields_ = [
        ("mVersion", c_uint32),
        ("mPlayRecordData", PlayRecordDataArray),
        ("__align_to_16384__", c_uint8 * (0x4000 - 0x1004)),
    ]


assert_struct_size(PLAY_RECORD_SAVE_DATA, 0x4000)
