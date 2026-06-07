"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_uint32

from save_convert.structs.marshal_struct_base import assert_struct_no_padding
from save_convert.structs.marshal_structure import (
    FillEndianSwapStructure,
    OffsetField,
)


class PARTY_ORDER_SAVE_DATA(FillEndianSwapStructure):  #  type: ignore[metaclass]
    class PartyOrderData(FillEndianSwapStructure):  #  type: ignore[metaclass]
        class PartyOrderStackEntry(FillEndianSwapStructure):  #  type: ignore[metaclass]
            _size_ = 0x8
            _offset_fields_ = [OffsetField(0x0, ("mPartyId", c_uint32)), OffsetField(0x4, ("mOrder", c_uint32))]

        _size_ = 0x4000
        _offset_fields_ = [
            OffsetField(0x0, ("mVersion", c_uint32)),  # offset rel=0x0, abs=0x6AD90
            OffsetField(0x4, ("mTop", c_uint32)),  # offset rel=0x4, abs=0x6AD94
            OffsetField(0x8, ("mOrder", c_uint32 * 6)),  # offset rel=0x8, abs=0x6AD98
            OffsetField(0x20, ("mOrderBackup", c_uint32 * 30)),  # offset rel=0x20, abs=0x6ADB0
            OffsetField(0x98, ("mOrderStack", PartyOrderStackEntry * 6)),  #  type: ignore[arg-type,operator] # offset rel=0x98, abs=0x6AE08
        ]

    _size_ = 0x4000
    _offset_fields_ = [
        OffsetField(0x0, ("mPartyOrderData", PartyOrderData)),
    ]


assert_struct_no_padding(PARTY_ORDER_SAVE_DATA)
