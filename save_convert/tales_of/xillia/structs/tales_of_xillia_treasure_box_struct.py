"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_char, c_uint8, c_uint32
from typing import override

from save_convert.structs.marshal_structure import (
    MarshalStructure,
    ToDictResult,
    assert_struct_size,
)
from save_convert.tales_of.xillia.dicts.tales_of_xillia_treasure_box_dict import (
    TreasureBoxSaveDict,
    create_treasure_box_save_dict,
)


class TreasureBox(MarshalStructure):
    class TreasureLocation(MarshalStructure):
        class TreeViewCursor(MarshalStructure):
            _fields_ = [
                ("index", c_uint32),
                ("row", c_uint32),
                ("column", c_uint32),
            ]

        _fields_ = [
            ("mapid", c_char * 16),
            ("max", c_uint32),
            ("list", TreeViewCursor * 8),
        ]

    _fields_ = [
        ("opend", c_uint8 * 256),  # offset abs=0x5E1C0
        ("normal", TreasureLocation * 32),  # offset abs=0x5E2C0
        ("search", TreasureLocation * 32),  # offset abs=0x5F140
        ("location", c_char * 4),  # offset rel=0xF80, abs=0x5FFC0
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


assert_struct_size(TreasureBox, 0x1E04)
