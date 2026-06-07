"""
List of structures mapping to raw binary save file for Tales of Xillia
"""

from ctypes import c_char
from typing import cast, override

from save_convert.structs.marshal_dict_base import ToDictResult
from save_convert.structs.marshal_struct_base import assert_struct_size
from save_convert.structs.marshal_structure import (
    MarshalStructure,
)
from save_convert.tales_of.xillia.dicts.tales_of_xillia_change_map_dict import (
    ChangeMapSaveDict,
)


class ChangeMap(MarshalStructure):
    _fields_ = [
        ("map", c_char * 32),
        ("location", c_char * 32),
    ]

    @override
    def to_dict(self, skip_double_underscore_fields: bool = True) -> ToDictResult:
        """
        Override to the set the "location" field if emptry
        """
        dict_result = super().to_dict(skip_double_underscore_fields)

        if not dict_result or not dict_result.value:
            return dict_result

        output_dict = cast(ChangeMapSaveDict, cast(object, dict_result.value))
        if not output_dict["location"]:
            output_dict["location"] = output_dict["map"]

        return ToDictResult(True, output_dict)


assert_struct_size(ChangeMap, 0x40)
