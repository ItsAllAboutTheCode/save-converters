"""
List of structures mapping to raw binary save file for Tales of Eternia
"""

import logging
import sys
from typing import cast, override

from save_convert.structs.marshal_byte_base import FromBytesResult, MarshalStructByteBase
from save_convert.structs.marshal_dict_base import ToDictResult
from save_convert.structs.marshal_struct_base import ByteorderLiteral, assert_struct_size
from save_convert.structs.marshal_structure import (
    FillEndianSwapStructure,
    OffsetField,
)
from save_convert.tales_of.eternia.structs.tales_of_eternia_save_data_struct import RemasteredSaveData
from save_convert.tales_of.eternia.structs.tales_of_eternia_thumbnail_struct import ThumbnailPngData
from save_convert.tales_of.eternia.tales_of_eternia_dicts import default_remastered_save_dict

LOGGER = logging.getLogger("eternia_structs")
LOGGER.addHandler(logging.StreamHandler(sys.stdout))
LOGGER.setLevel(logging.INFO)

# Save size of Eternia PSP save
ETERNIA_PSP_SAVE_SIZE = 4836
# Save size of Eternia Remastered save
# (cipher_text_size - padding) = 399376 - 16
ETERNIA_REMASTERED_SAVE_SIZE = 399360


class EterniaSaveStruct(FillEndianSwapStructure):  # type: ignore[metaclass]
    """
    Structure providing a mapping for the entire Tales of Eternia decrypted save file
    """

    _size_ = ETERNIA_REMASTERED_SAVE_SIZE
    _offset_fields_ = [
        OffsetField(0x0, ("GameData", RemasteredSaveData)),
        OffsetField(0x1800, ("ThumbnailData", ThumbnailPngData)),
    ]

    def __init__(self):
        """Initializes the game save data and Thumbnail PNG"""
        super().__init__()

    @override
    @staticmethod
    def from_bytes[T: MarshalStructByteBase](
        input_data: memoryview, struct_type: type[T], byteorder: ByteorderLiteral = "little"
    ) -> FromBytesResult[T]:
        """
        Convert entire Eternia Remastered save data to a struct
        """
        # Create the struct instance at this point
        struct_inst = struct_type()

        save_data_section_result = RemasteredSaveData.from_bytes(
            memoryview(input_data), RemasteredSaveData, byteorder="little"
        )

        if not save_data_section_result or not save_data_section_result.value:
            LOGGER.error("Failed reading save data section for Eternia Remastered save")
            return FromBytesResult(False, save_data_section_result.next_memoryview)

        setattr(struct_inst, "GameData", save_data_section_result.value)

        # Update the save section entry view to point to the next entry
        section_entry_view = cast(memoryview, save_data_section_result.next_memoryview)
        from_bytes_result = ThumbnailPngData.from_bytes(section_entry_view, ThumbnailPngData, byteorder="little")
        if not from_bytes_result or not from_bytes_result.value:
            LOGGER.error("Failed to load data for Thumbnail PNG Data. Aborting...")
            return FromBytesResult(False, section_entry_view)

        # NOTE: Set the save section to the loaded struct type
        setattr(struct_inst, "ThumbnailData", from_bytes_result.value)

        return FromBytesResult(True, section_entry_view, struct_inst)

    @override
    def to_dict(self, skip_double_underscore_fields: bool = True) -> ToDictResult:
        """
        Convert entire Eternia save data to a dictionary compatible with the Remaster save format

        The Save JSON other fields are augmented with values from the structure
        """

        # Store the Save section struct as a dict
        remaster_save_dict = default_remastered_save_dict()

        # No-op, Eternia save doesn't use JSON
        # However this could be useful in the future to create a save editor
        # if the binary struct layout is discovered
        return ToDictResult(True, remaster_save_dict)


assert_struct_size(EterniaSaveStruct, ETERNIA_REMASTERED_SAVE_SIZE)
