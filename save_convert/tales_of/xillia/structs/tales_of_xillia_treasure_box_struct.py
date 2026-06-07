"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_char, c_uint8, c_uint32
from typing import override

from save_convert.structs.marshal_dict_base import ToDictResult
from save_convert.structs.marshal_struct_base import assert_struct_no_padding
from save_convert.structs.marshal_structure import FillEndianSwapStructure, OffsetField
from save_convert.tales_of.xillia.dicts.tales_of_xillia_treasure_box_dict import (
    TreasureBoxSaveDict,
    create_treasure_box_save_dict,
)


class TreasureBox(FillEndianSwapStructure):  #  type: ignore[metaclass]
    class TreasureLocation(FillEndianSwapStructure):  #  type: ignore[metaclass]
        class TreeViewCursor(FillEndianSwapStructure):  #  type: ignore[metaclass]
            _size_ = 0xC
            _offset_fields_ = [
                OffsetField(0x0, ("index", c_uint32)),
                OffsetField(0x4, ("row", c_uint32)),
                OffsetField(0x8, ("column", c_uint32)),
            ]

        _size_ = 0x74
        _offset_fields_ = [
            OffsetField(0x0, ("mapid", c_char * 16)),
            OffsetField(0x10, ("max", c_uint32)),
            OffsetField(0x14, ("list", TreeViewCursor * 8)),  #  type: ignore[arg-type,operator]
        ]

    _size_ = 0x1E04
    _offset_fields_ = [
        OffsetField(0x0, ("opend", c_uint8 * 256)),  # offset abs=0x5E1C0
        OffsetField(0x100, ("normal", TreasureLocation * 32)),  #  type: ignore[arg-type,operator] # offset abs=0x5E2C0
        OffsetField(0xF80, ("search", TreasureLocation * 32)),  #  type: ignore[arg-type,operator] # offset abs=0x5F140
        OffsetField(0x1E00, ("location", c_char * 4)),  # offset rel=0xF80, abs=0x5FFC0
        # Seems to not be used in Binary save
        # ("openRandomData", c_uint32 * 32),
    ]

    @override
    def to_dict(self, skip_double_underscore_fields: bool = True) -> ToDictResult:
        """
        Override to the add the "openRandomData" field to the save data
        """
        default_dict: TreasureBoxSaveDict = create_treasure_box_save_dict()
        dict_result = super().to_dict(skip_double_underscore_fields)

        if not dict_result or not dict_result.value:
            return dict_result

        dict_result.value["openRandomData"] = default_dict["openRandomData"]

        return dict_result


assert_struct_no_padding(TreasureBox)
