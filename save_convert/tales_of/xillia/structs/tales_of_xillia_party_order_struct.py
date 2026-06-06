"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_uint8, c_uint32

from save_convert.structs.marshal_structure import (
    MarshalStructure,
    assert_struct_size,
)


class PARTY_ORDER_SAVE_DATA(MarshalStructure):
    class PartyOrderData(MarshalStructure):
        class PartyOrderStackEntry(MarshalStructure):
            _fields_ = [("mPartyId", c_uint32), ("mOrder", c_uint32)]

        _fields_ = [
            ("mVersion", c_uint32),  # offset rel=0x0, abs=0x6AD90
            ("mTop", c_uint32),  # offset rel=0x4, abs=0x6AD94
            ("mOrder", c_uint32 * 6),  # offset rel=0x8, abs=0x6AD98
            ("mOrderBackup", c_uint32 * 30),  # offset rel=0x20, abs=0x6ADB0
            ("mOrderStack", PartyOrderStackEntry * 6),  # offset rel=0x98, abs=0x6AE08
            ("__align_to_16384__", c_uint8 * (0x4000 - 0xC8)),  # offset rel=0xC8, abs=0x6AE38
        ]

    _fields_ = [
        ("mPartyOrderData", PartyOrderData),
    ]


assert_struct_size(PARTY_ORDER_SAVE_DATA, 0x4000)
