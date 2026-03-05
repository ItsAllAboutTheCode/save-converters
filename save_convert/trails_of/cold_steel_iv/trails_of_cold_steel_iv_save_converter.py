#!/usr/bin/env python
"""Script for converting the The Legend of Heroes - Trails of Cold Steel IV PS4 <-> PC save"""

import argparse
import logging
import sys
from typing import override

from save_convert.save_converter_base import (
    PC_TO_PS4_CONVERT_FORMAT,
    PS4_TO_PC_CONVERT_FORMAT,
    ConvertPatchTable,
    PatchCopyBytes,
    PatchSet,
    PatchSkipBytes,
    Range,
    RangeNotCoveredException,
    SaveFormat,
)
from save_convert.trails_of.trails_of_cold_steel_base_converter import (
    SaveConvertColdSteelChecksumBase,
    add_argparse_commands,
)

logger = logging.getLogger("cold_steel_iv_save_converter")
logger.setLevel(logging.INFO)
stdoutHandler = logging.StreamHandler()
logger.addHandler(stdoutHandler)

# This is the size of the PS4 save after decompression
TRAILS_OF_COLD_STEEL_IV_PS4_SAVE_SIZE = 1466304
# The Normal PC Save is 2320 bytes smaller than PS4
PS4_TO_PC_BYTE_REDUCTION = 2328
TRAILS_OF_COLD_STEEL_IV_PC_SAVE_SIZE = TRAILS_OF_COLD_STEEL_IV_PS4_SAVE_SIZE - PS4_TO_PC_BYTE_REDUCTION
TRAILS_OF_COLD_STEEL_IV_SAVE_SIZE_DICT = {
    SaveFormat.PS4: TRAILS_OF_COLD_STEEL_IV_PS4_SAVE_SIZE,
    SaveFormat.PC: TRAILS_OF_COLD_STEEL_IV_PC_SAVE_SIZE,
}


class SaveConvertColdSteelIV(SaveConvertColdSteelChecksumBase):
    @override
    def create_save_patch_table(self) -> ConvertPatchTable:
        """Returns a dictionary of offset -> byte array entries that indicates which
        actions should be performed when an address is encountered from the input save
        """
        new_patch_table: ConvertPatchTable = ConvertPatchTable(
            convert_format_to_patch_set={PS4_TO_PC_CONVERT_FORMAT: PatchSet()},
            save_format_to_save_size_dict=TRAILS_OF_COLD_STEEL_IV_SAVE_SIZE_DICT,
        )

        # The save_NOTES.md details how to transform a PS4 save file to a PC save file.
        # The transformation is performed inplace with bytes being added and deleted to the input file
        # As the save patch data copies the unchanged input bytes to the output file
        # the bytes in the input file that were deleted are instead skip

        # Keeps tracks of the total bytes appended to the output file + bytes skipped in the input file
        byte_count_tracker = 0

        # Align location data for model 1
        start_offset = 0x152DC
        bytes_to_skip = 4
        new_patch_table.convert_format_to_patch_set[PS4_TO_PC_CONVERT_FORMAT].add_patch_entry(
            PatchSkipBytes(
                target_offset=start_offset,
                source_range=Range(
                    start_offset + byte_count_tracker, start_offset + byte_count_tracker + bytes_to_skip
                ),
            )
        )
        byte_count_tracker += bytes_to_skip

        LOCATION_DATA_STRIDE = 960  # Documented in save_NOTES.md
        CHARACTER_MODELS = 18
        for i in range(0, CHARACTER_MODELS):
            # Align location/animation data for model (i + 1)
            start_offset = 0x153A0 + (LOCATION_DATA_STRIDE * i)
            bytes_to_skip = 16
            new_patch_table.convert_format_to_patch_set[PS4_TO_PC_CONVERT_FORMAT].add_patch_entry(
                PatchSkipBytes(
                    target_offset=start_offset,
                    source_range=Range(
                        start_offset + byte_count_tracker, start_offset + byte_count_tracker + bytes_to_skip
                    ),
                )
            )

            byte_count_tracker += bytes_to_skip

        # Align the Inventory data
        start_offset = 0x36F1C
        bytes_to_skip = 2016
        new_patch_table.convert_format_to_patch_set[PS4_TO_PC_CONVERT_FORMAT].add_patch_entry(
            PatchSkipBytes(
                target_offset=start_offset,
                source_range=Range(
                    start_offset + byte_count_tracker, start_offset + byte_count_tracker + bytes_to_skip
                ),
            )
        )
        byte_count_tracker += bytes_to_skip

        # Align the Playtime data
        start_offset = 0x7CA20
        bytes_to_skip = 12
        new_patch_table.convert_format_to_patch_set[PS4_TO_PC_CONVERT_FORMAT].add_patch_entry(
            PatchSkipBytes(
                target_offset=start_offset,
                source_range=Range(
                    start_offset + byte_count_tracker, start_offset + byte_count_tracker + bytes_to_skip
                ),
            )
        )
        byte_count_tracker += bytes_to_skip

        # Delete padding bytes at the end to have converted PS4 save have the same size as PC
        start_offset = TRAILS_OF_COLD_STEEL_IV_PC_SAVE_SIZE
        bytes_to_skip = 8
        new_patch_table.convert_format_to_patch_set[PS4_TO_PC_CONVERT_FORMAT].add_patch_entry(
            PatchSkipBytes(
                target_offset=start_offset,
                source_range=Range(
                    start_offset + byte_count_tracker, start_offset + byte_count_tracker + bytes_to_skip
                ),
            )
        )
        byte_count_tracker += bytes_to_skip

        if byte_count_tracker != PS4_TO_PC_BYTE_REDUCTION:
            raise ValueError(
                f"Expected reduction of {PS4_TO_PC_BYTE_REDUCTION} count bytes when converting PS4 -> PC save.\n"
                f"Actual adjustment is {byte_count_tracker}.\n"
                " This is a code issue and needs to be fixed by a developer"
            )

        # Now generate the reverse mapping of PC -> PS4 conversion
        new_patch_table.convert_format_to_patch_set[PC_TO_PS4_CONVERT_FORMAT] = (
            new_patch_table.convert_format_to_patch_set[PS4_TO_PC_CONVERT_FORMAT].generate_reverse_set()
        )
        # Fill the patch table entries with offset ranges mappings from [0x0, <platform-save-size>) that copies the data
        new_patch_table.fill_uncovered_target_offset_ranges(
            lambda target_offset, source_range: PatchCopyBytes(target_offset, source_range=source_range)
        )

        valid, error_messages = new_patch_table.validate()
        if not valid:
            raise RangeNotCoveredException("\n".join(error_messages))
        return new_patch_table


### Start of argument parser setup
def start_convert(args: argparse.Namespace):
    save_converter = SaveConvertColdSteelIV(args)
    return save_converter.convert()


def add_commands(parser: argparse.ArgumentParser) -> None:
    parser.description = "Save Converter (PS4<->PC) for Trails of Cold Steel IV"
    add_argparse_commands(parser)
    parser.set_defaults(func=start_convert)


def main():
    parser = argparse.ArgumentParser(
        description="Tool to convert a Trails of Cold Steel IV save between PS4 <-> PC",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    add_commands(parser)

    args = parser.parse_args()

    if hasattr(args, "func"):
        response = args.func(args)
    else:
        logger.error("No convert function is set")
        response = False

    sys.exit(response)


if __name__ == "__main__":
    main()
