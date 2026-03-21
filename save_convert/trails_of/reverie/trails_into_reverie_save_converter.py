#!/usr/bin/env python
"""Script for converting the The Legend of Heroes - Trails into Reverie PS4/PS5 <-> PC save"""

import argparse
import logging
import sys
from typing import override

from save_convert.save_converter_base import (
    PC_TO_PS4_CONVERT_FORMAT,
    PC_TO_PS5_CONVERT_FORMAT,
    PS4_TO_PC_CONVERT_FORMAT,
    PS5_TO_PC_CONVERT_FORMAT,
    ConvertPatchTable,
    PatchCopyBytes,
    PatchSet,
    PatchSkipBytes,
    Range,
    SaveFormat,
)
from save_convert.trails_of.trails_of_cold_steel_base_converter import (
    SaveConvertColdSteelChecksumBase,
    add_argparse_commands,
)

LOGGER = logging.getLogger("reverie_save_converter")
LOGGER.setLevel(logging.INFO)
stdoutHandler = logging.StreamHandler()
LOGGER.addHandler(stdoutHandler)

# This is the size of the PS4 save after decompression
TRAILS_INTO_REVERIE_PS4_SAVE_SIZE = 1724096
# The Normal PC Save is 2320 bytes smaller than PS4
PS4_TO_PC_BYTE_REDUCTION = 4064
TRAILS_INTO_REVERIE_PC_SAVE_SIZE = TRAILS_INTO_REVERIE_PS4_SAVE_SIZE - PS4_TO_PC_BYTE_REDUCTION

TRAILS_INTO_REVERIE_SAVE_SIZE_DICT: dict[SaveFormat, int] = {
    SaveFormat.PS4: TRAILS_INTO_REVERIE_PS4_SAVE_SIZE,
    SaveFormat.PS5: TRAILS_INTO_REVERIE_PS4_SAVE_SIZE,
    SaveFormat.PC: TRAILS_INTO_REVERIE_PC_SAVE_SIZE,
}


class SaveConvertReverie(SaveConvertColdSteelChecksumBase):
    def __init__(self, args: argparse.Namespace):
        super().__init__(args)

    @override
    def create_save_patch_table(self) -> ConvertPatchTable:
        """Returns a dictionary of offset -> byte array entries that indicates which
        actions should be performed when an address is encountered from the input save
        """
        new_patch_table: ConvertPatchTable = ConvertPatchTable(
            convert_format_to_patch_set={PS4_TO_PC_CONVERT_FORMAT: PatchSet()},
            save_format_to_save_size_dict=TRAILS_INTO_REVERIE_SAVE_SIZE_DICT,
        )

        # The save_NOTES.md details how to transform a PS4 save file to a PC save file.
        # The transformation is performed inplace with bytes being added and deleted to the input file
        # As the save patch data copies the unchanged input bytes to the output file
        # the bytes in the input file that were deleted are instead skipped

        # Keeps tracks of the total bytes appended to the output file + bytes skipped in the input file
        byte_count_tracker = 0

        LOCATION_DATA_STRIDE = 932  # Documented in save_NOTES.md
        CHARACTER_MODELS = 18
        for i in range(0, CHARACTER_MODELS):
            # Align location data for model (i + 1)
            start_offset = 0x18204 + (LOCATION_DATA_STRIDE * i)
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

            # Align animation data for model (i + 1)
            start_offset = 0x182E8 + (LOCATION_DATA_STRIDE * i)
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
        start_offset = 0x38E84
        bytes_to_skip = 3540
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
        start_offset = 0x94E78
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
        start_offset = TRAILS_INTO_REVERIE_PC_SAVE_SIZE
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

        # The PS4 and PS5 files are the exact same format so use the same conversion table for PS5 <-> PC
        # Now generate the reverse mapping of PC -> PS4 conversion
        new_patch_table.convert_format_to_patch_set[PC_TO_PS4_CONVERT_FORMAT] = (
            new_patch_table.convert_format_to_patch_set[PS4_TO_PC_CONVERT_FORMAT].generate_reverse_set()
        )
        new_patch_table.convert_format_to_patch_set[PC_TO_PS5_CONVERT_FORMAT] = (
            new_patch_table.convert_format_to_patch_set[PC_TO_PS4_CONVERT_FORMAT]
        )
        new_patch_table.convert_format_to_patch_set[PS5_TO_PC_CONVERT_FORMAT] = (
            new_patch_table.convert_format_to_patch_set[PS4_TO_PC_CONVERT_FORMAT]
        )
        # Fill the patch table entries with offset ranges mappings from [0x0, <platform-save-size>) that copies the data
        new_patch_table.fill_uncovered_target_offset_ranges(
            lambda target_offset, source_range: PatchCopyBytes(target_offset, source_range=source_range)
        )

        return new_patch_table


### Start of argument parser setup
def start_convert(args: argparse.Namespace):
    if hasattr(args, "log_level"):
        LOGGER.setLevel(args.log_level)
    save_converter = SaveConvertReverie(args)
    return save_converter.transform()


def add_commands(parser: argparse.ArgumentParser) -> None:
    parser.description = "Save Converter (PS4/PS5<->PC) for Trails into Reverie"
    add_argparse_commands(parser)

    # Update the --convert-format argument to add PS5 choices
    for action in reversed(parser._actions):
        if action.dest == "convert_format":
            if isinstance(action.choices, list):
                action.choices += [str(PS5_TO_PC_CONVERT_FORMAT), str(PC_TO_PS5_CONVERT_FORMAT)]
            break

    parser.set_defaults(func=start_convert)


def main():
    parser = argparse.ArgumentParser(
        description="Tool to convert a Trails into Reverie save between PS4/PS5 <-> PC",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    add_commands(parser)

    args = parser.parse_args()

    if hasattr(args, "func"):
        response = args.func(args)
    else:
        LOGGER.error("No convert function is set")
        response = False

    sys.exit(response)


if __name__ == "__main__":
    main()
