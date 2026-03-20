#!/usr/bin/env python
"""Script for converting the The Legend of Heroes - Trails of Cold Steel I PS4 <-> PC save"""

import argparse
import logging
import sys
from typing import override

from save_convert.save_converter_base import (
    PC_TO_PS4_CONVERT_FORMAT,
    PS4_TO_PC_CONVERT_FORMAT,
    ConvertPatchTable,
    PatchCopyBytes,
    PatchInsertBytes,
    PatchSet,
    PatchSkipBytes,
    Range,
    RangeNotCoveredException,
    SaveFormat,
)
from save_convert.trails_of.trails_of_cold_steel_base_converter import (
    SaveConvertColdSteelBase,
    add_argparse_commands,
)

LOGGER = logging.getLogger("cold_steel_i_save_converter")
LOGGER.setLevel(logging.INFO)
stdoutHandler = logging.StreamHandler()
LOGGER.addHandler(stdoutHandler)


TRAILS_OF_COLD_STEEL_I_PS4_SAVE_SIZE = 519392
# The Normal PC Save is 58400 bytes smaller than PS4
PS4_TO_PC_BYTE_REDUCTION = 58400
TRAILS_OF_COLD_STEEL_I_PC_SAVE_SIZE = TRAILS_OF_COLD_STEEL_I_PS4_SAVE_SIZE - PS4_TO_PC_BYTE_REDUCTION

TRAILS_OF_COLD_STEEL_I_SAVE_SIZE_DICT: dict[SaveFormat, int] = {
    SaveFormat.PS4: TRAILS_OF_COLD_STEEL_I_PS4_SAVE_SIZE,
    SaveFormat.PC: TRAILS_OF_COLD_STEEL_I_PC_SAVE_SIZE,
}


class SaveConvertColdSteelI(SaveConvertColdSteelBase):
    @override
    def create_save_patch_table(
        self,
    ) -> ConvertPatchTable:
        """Returns a dictionary of offset -> byte array entries that indicates which
        actions should be performed when an address is encountered from the input save
        """
        new_patch_table: ConvertPatchTable = ConvertPatchTable(
            convert_format_to_patch_set={PS4_TO_PC_CONVERT_FORMAT: PatchSet()},
            save_format_to_save_size_dict=TRAILS_OF_COLD_STEEL_I_SAVE_SIZE_DICT,
        )

        # The save_NOTES.md details how to transform a PS4 save file to a PC save file.
        # The transformation is performed inplace with bytes being added and deleted to the input file
        # As the save patch data copies the unchanged input bytes to the output file
        # the bytes in the input file that were deleted are instead skip

        # Keeps tracks of the total bytes appended to the output file + bytes skipped in the input file
        byte_count_tracker = 0

        # Append magic bytes to identify save
        new_patch_table.convert_format_to_patch_set[PS4_TO_PC_CONVERT_FORMAT].add_patch_entry(
            PatchInsertBytes(target_offset=0x0, source_offset=0x0, output_bytes=bytes([0xC0, 0x08, 0x07, 0x00]))
        )
        byte_count_tracker -= 4
        # Bytes were appended to output file, input file offset doesn't change

        # Delete bytes to align character data
        start_offset = 0x400
        bytes_to_skip = 20
        new_patch_table.convert_format_to_patch_set[PS4_TO_PC_CONVERT_FORMAT].add_patch_entry(
            PatchSkipBytes(
                target_offset=start_offset,
                source_range=Range(
                    start_offset + byte_count_tracker, start_offset + byte_count_tracker + bytes_to_skip
                ),
            )
        )
        byte_count_tracker += bytes_to_skip

        # Align location data for model 1
        start_offset = 0x2E24
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

        # Start aligning animation state data for model 1
        start_offset = 0x2E94
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

        start_offset = 0x2EA8
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

        start_offset = 0x2FC8
        bytes_to_skip = 20
        new_patch_table.convert_format_to_patch_set[PS4_TO_PC_CONVERT_FORMAT].add_patch_entry(
            PatchSkipBytes(
                target_offset=start_offset,
                source_range=Range(
                    start_offset + byte_count_tracker, start_offset + byte_count_tracker + bytes_to_skip
                ),
            )
        )
        byte_count_tracker += bytes_to_skip

        start_offset = 0x302C
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

        start_offset = 0x3030
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

        start_offset = 0x30F0
        bytes_to_skip = 80
        new_patch_table.convert_format_to_patch_set[PS4_TO_PC_CONVERT_FORMAT].add_patch_entry(
            PatchSkipBytes(
                target_offset=start_offset,
                source_range=Range(
                    start_offset + byte_count_tracker, start_offset + byte_count_tracker + bytes_to_skip
                ),
            )
        )
        byte_count_tracker += bytes_to_skip

        start_offset = 0x315C
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

        start_offset = 0x3214
        bytes_to_skip = 80
        new_patch_table.convert_format_to_patch_set[PS4_TO_PC_CONVERT_FORMAT].add_patch_entry(
            PatchSkipBytes(
                target_offset=start_offset,
                source_range=Range(
                    start_offset + byte_count_tracker, start_offset + byte_count_tracker + bytes_to_skip
                ),
            )
        )
        byte_count_tracker += bytes_to_skip

        start_offset = 0x3274
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

        start_offset = 0x3278
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

        start_offset = 0x3338
        bytes_to_skip = 80
        new_patch_table.convert_format_to_patch_set[PS4_TO_PC_CONVERT_FORMAT].add_patch_entry(
            PatchSkipBytes(
                target_offset=start_offset,
                source_range=Range(
                    start_offset + byte_count_tracker, start_offset + byte_count_tracker + bytes_to_skip
                ),
            )
        )
        byte_count_tracker += bytes_to_skip

        start_offset = 0x33A4
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
        # Finish alignment of animation state data for model 1

        LOCATION_DATA_STRIDE = 1760
        CHARACTER_MODELS = 10
        for i in range(1, CHARACTER_MODELS):
            # Align location data for model (i + 1)
            start_offset = 0x2D78 + (LOCATION_DATA_STRIDE * i)
            # Note this is different from Model 1 where only 12 bytes were deleted
            bytes_to_skip = 72
            new_patch_table.convert_format_to_patch_set[PS4_TO_PC_CONVERT_FORMAT].add_patch_entry(
                PatchSkipBytes(
                    target_offset=start_offset,
                    source_range=Range(
                        start_offset + byte_count_tracker, start_offset + byte_count_tracker + bytes_to_skip
                    ),
                )
            )

            byte_count_tracker += bytes_to_skip

            # Start aligning animation state data for model (i + 1)
            start_offset = 0x2E94 + (LOCATION_DATA_STRIDE * i)
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

            start_offset = 0x2EA8 + (LOCATION_DATA_STRIDE * i)
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

            start_offset = 0x2FC8 + (LOCATION_DATA_STRIDE * i)
            bytes_to_skip = 20
            new_patch_table.convert_format_to_patch_set[PS4_TO_PC_CONVERT_FORMAT].add_patch_entry(
                PatchSkipBytes(
                    target_offset=start_offset,
                    source_range=Range(
                        start_offset + byte_count_tracker, start_offset + byte_count_tracker + bytes_to_skip
                    ),
                )
            )

            byte_count_tracker += bytes_to_skip

            start_offset = 0x302C + (LOCATION_DATA_STRIDE * i)
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

            start_offset = 0x3030 + (LOCATION_DATA_STRIDE * i)
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

            start_offset = 0x30F0 + (LOCATION_DATA_STRIDE * i)
            bytes_to_skip = 80
            new_patch_table.convert_format_to_patch_set[PS4_TO_PC_CONVERT_FORMAT].add_patch_entry(
                PatchSkipBytes(
                    target_offset=start_offset,
                    source_range=Range(
                        start_offset + byte_count_tracker, start_offset + byte_count_tracker + bytes_to_skip
                    ),
                )
            )

            byte_count_tracker += bytes_to_skip

            start_offset = 0x315C + (LOCATION_DATA_STRIDE * i)
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

            start_offset = 0x3214 + (LOCATION_DATA_STRIDE * i)
            bytes_to_skip = 80
            new_patch_table.convert_format_to_patch_set[PS4_TO_PC_CONVERT_FORMAT].add_patch_entry(
                PatchSkipBytes(
                    target_offset=start_offset,
                    source_range=Range(
                        start_offset + byte_count_tracker, start_offset + byte_count_tracker + bytes_to_skip
                    ),
                )
            )

            byte_count_tracker += bytes_to_skip

            start_offset = 0x3274 + (LOCATION_DATA_STRIDE * i)
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

            start_offset = 0x3278 + (LOCATION_DATA_STRIDE * i)
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

            start_offset = 0x3338 + (LOCATION_DATA_STRIDE * i)
            bytes_to_skip = 80
            new_patch_table.convert_format_to_patch_set[PS4_TO_PC_CONVERT_FORMAT].add_patch_entry(
                PatchSkipBytes(
                    target_offset=start_offset,
                    source_range=Range(
                        start_offset + byte_count_tracker, start_offset + byte_count_tracker + bytes_to_skip
                    ),
                )
            )

            byte_count_tracker += bytes_to_skip

            start_offset = 0x33A4 + (LOCATION_DATA_STRIDE * i)
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
            # Finish alignment of animation state data for model (i + 1)

        # Align the Inventory and game data
        start_offset = 0x40C24
        bytes_to_skip = 53672
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
        start_offset = 0x6B204
        bytes_to_skip = 764
        new_patch_table.convert_format_to_patch_set[PS4_TO_PC_CONVERT_FORMAT].add_patch_entry(
            PatchSkipBytes(
                target_offset=start_offset,
                source_range=Range(
                    start_offset + byte_count_tracker, start_offset + byte_count_tracker + bytes_to_skip
                ),
            )
        )
        byte_count_tracker += bytes_to_skip

        # Delete padding bytes at the end of the converted PS4 save to have it match the original PC save size
        start_offset = TRAILS_OF_COLD_STEEL_I_PC_SAVE_SIZE
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
    if hasattr(args, "log_level"):
        LOGGER.setLevel(args.log_level)
    save_converter = SaveConvertColdSteelI(args)
    return save_converter.convert()


def add_commands(parser: argparse.ArgumentParser) -> None:
    parser.description = "Save Converter (PS4<->PC) for Trails of Cold Steel I"
    add_argparse_commands(parser)
    parser.set_defaults(func=start_convert)


def main():
    parser = argparse.ArgumentParser(
        description="Tool to convert a Trails of Cold Steel I save between PS4 <-> PC",
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
