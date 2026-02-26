#!/usr/bin/env python
"""Script for converting the The Legend of Heroes - Trails of Cold Steel II PS4 <-> PC save"""

import argparse
import logging
import sys
from typing import override

from save_convert.save_convert_base import (
    PC_TO_PS4_CONVERT_FORMAT,
    PS4_TO_PC_CONVERT_FORMAT,
    ConvertFormat,
    Range,
    RangeNotCoveredException,
    ReplaceCopy,
    ReplaceMap,
    ReplaceRangeBytes,
    SaveFormat,
    fill_replace_func_in_offset_range_gaps,
    generate_reverse_map,
)
from save_convert.trails_of.trails_of_cold_steel_base_converter import (
    SaveConvertColdSteelBase,
    add_argparse_commands,
)

logger = logging.getLogger("cold_steel_ii_save_converter")
logger.setLevel(logging.INFO)
stdoutHandler = logging.StreamHandler()
logger.addHandler(stdoutHandler)

TRAILS_OF_COLD_STEEL_II_PS4_SAVE_SIZE = 496880
# The Normal PC Save is 2904 bytes smaller than PS4
PS4_TO_PC_BYTE_REDUCTION = 2904
TRAILS_OF_COLD_STEEL_II_PC_SAVE_SIZE = TRAILS_OF_COLD_STEEL_II_PS4_SAVE_SIZE - PS4_TO_PC_BYTE_REDUCTION


class SaveConvertColdSteelII(SaveConvertColdSteelBase):
    def __init__(self, args: argparse.Namespace):
        super().__init__(args)

    @override
    def _pre_convert(self) -> bool:
        return super()._pre_convert()

    @override
    def _convert(self) -> bool:
        return super()._convert()

    @override
    def _post_convert(self) -> bool:
        return super()._post_convert()

    @override
    def create_save_patch_table(self, convert_format: ConvertFormat) -> list[ReplaceMap]:
        """Returns a dictionary of offset -> byte array entries that indicates which
        actions should be performed when an address is encountered from the input save
        """
        PATCH_TABLE: dict[ConvertFormat, list[ReplaceMap]] = {
            ConvertFormat(source=SaveFormat.PS4, target=SaveFormat.PC): [],
        }

        # The save_NOTES.md details how to transform a PS4 save file to a PC save file.
        # The transformation is performed inplace with bytes being added and deleted to the input file
        # As the save patch data copies the unchanged input bytes to the output file
        # the bytes in the input file that were deleted are instead skip and therefore
        # the offsets from the save_NOTES.md must be adjusted to work
        inplace_to_skip_adjustment = 0

        # Append magic bytes to identify save
        PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
            ReplaceMap(
                replace_functor=ReplaceRangeBytes(
                    source_range=Range(start=0x0, end=0x0), output_bytes=bytes([0x98, 0x89, 0x07, 0x00])
                ),
            )
        )
        inplace_to_skip_adjustment -= 4

        # Align location data for model 1
        start_offset = inplace_to_skip_adjustment + 0xCF2C
        bytes_to_delete = 8
        PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
            ReplaceMap(
                replace_functor=ReplaceRangeBytes(
                    source_range=Range(start=start_offset, end=start_offset + bytes_to_delete), output_bytes=b""
                ),
            )
        )
        inplace_to_skip_adjustment += bytes_to_delete

        # Align animation state data for model 1
        start_offset = inplace_to_skip_adjustment + 0xCFAC
        bytes_to_delete = 20
        PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
            ReplaceMap(
                replace_functor=ReplaceRangeBytes(
                    source_range=Range(start=start_offset, end=start_offset + bytes_to_delete), output_bytes=b""
                ),
            )
        )
        inplace_to_skip_adjustment += bytes_to_delete

        LOCATION_DATA_STRIDE = 1148  # Documented in save_NOTES.md
        CHARACTER_MODELS = 28
        for i in range(1, CHARACTER_MODELS):
            # Align location data for model (i + 1)
            start_offset = inplace_to_skip_adjustment + 0xCFAC + (LOCATION_DATA_STRIDE * i)
            bytes_to_delete = 8
            PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
                ReplaceMap(
                    replace_functor=ReplaceRangeBytes(
                        source_range=Range(start=start_offset, end=start_offset + bytes_to_delete), output_bytes=b""
                    ),
                )
            )
            inplace_to_skip_adjustment += bytes_to_delete

            # Align animation state data for model (i + 1)
            start_offset = inplace_to_skip_adjustment + 0xCFC0 + (LOCATION_DATA_STRIDE * i)
            bytes_to_delete = 12
            PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
                ReplaceMap(
                    replace_functor=ReplaceRangeBytes(
                        source_range=Range(start=start_offset, end=start_offset + bytes_to_delete), output_bytes=b""
                    ),
                )
            )
            inplace_to_skip_adjustment += bytes_to_delete

        # Align the Inventory and game data
        start_offset = inplace_to_skip_adjustment + 0x354EC
        bytes_to_delete = 2320
        PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
            ReplaceMap(
                replace_functor=ReplaceRangeBytes(
                    source_range=Range(start=start_offset, end=start_offset + bytes_to_delete), output_bytes=b""
                ),
            )
        )
        inplace_to_skip_adjustment += bytes_to_delete

        # Align the Playtime data
        start_offset = inplace_to_skip_adjustment + 0x70BDC
        bytes_to_delete = 12
        PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
            ReplaceMap(
                replace_functor=ReplaceRangeBytes(
                    source_range=Range(start=start_offset, end=start_offset + bytes_to_delete), output_bytes=b""
                ),
            )
        )
        inplace_to_skip_adjustment += bytes_to_delete

        # Delete 8 padding bytes at the end to have Converted PS4 save have the same size as PC
        start_offset = inplace_to_skip_adjustment + TRAILS_OF_COLD_STEEL_II_PC_SAVE_SIZE
        bytes_to_delete = 8
        PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
            ReplaceMap(
                replace_functor=ReplaceRangeBytes(
                    source_range=Range(start=start_offset, end=start_offset + bytes_to_delete), output_bytes=b""
                ),
            )
        )
        inplace_to_skip_adjustment += bytes_to_delete

        if inplace_to_skip_adjustment != PS4_TO_PC_BYTE_REDUCTION:
            raise ValueError(
                f"Expected reduction of {PS4_TO_PC_BYTE_REDUCTION} count bytes when converting PS4 -> PC save"
                f"Actual adjustment is {inplace_to_skip_adjustment}."
                " This is a code issue and needs to be fixed by a developer"
            )

        # Now generate the reverse mapping of PC -> PS4 conversion
        PATCH_TABLE[PC_TO_PS4_CONVERT_FORMAT] = generate_reverse_map(PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT])

        platform_patch_table = PATCH_TABLE.get(convert_format, [])

        # Fill the Replace table for each uncovered offset range in the save file
        # The mapping function will perform a direct copy of the save data from the input file to the output file.
        platform_patch_table = fill_replace_func_in_offset_range_gaps(
            replace_table=platform_patch_table,
            fill_replace_functor=ReplaceCopy(source_range=Range()),
            max_offset=len(self._input_data),
        )

        platform_patch_table.sort(
            key=lambda entry: (entry.replace_functor.source_range.start, entry.replace_functor.source_range.end)
        )
        if not platform_patch_table:
            return []

        error_message = ""
        prev_value: ReplaceMap = platform_patch_table[0]
        if prev_value.replace_functor.source_range.start != 0:
            error_message += (
                f"First range entry must start at offset 0x0. It is {prev_value.replace_functor.source_range.start}\n"
            )
        for value in platform_patch_table[1:]:
            if prev_value.replace_functor.source_range.end != value.replace_functor.source_range.start:
                error_message += (
                    "The previous range entry end offset must be equal to the current range entry start offset."
                    f"Previous entry: {prev_value.replace_functor.source_range.end},"
                    f" Current entry {value.replace_functor.source_range.start}.\n"
                )
            prev_value = value

        if platform_patch_table[-1].replace_functor.source_range.end < len(self._input_data):
            error_message += f"The last range entry end offset must be at least {len(self._input_data):x}."
            f" It is {platform_patch_table[-1].replace_functor.source_range.end}\n"

        if error_message:
            raise RangeNotCoveredException(error_message)

        return platform_patch_table


### Start of argument parser setup
def start_convert(args: argparse.Namespace):
    save_converter = SaveConvertColdSteelII(args)
    return save_converter.convert()


def add_commands(parser: argparse.ArgumentParser) -> None:
    parser.description = "Save Converter (PS4<->PC) for Trails of Cold Steel II"
    add_argparse_commands(parser)
    parser.set_defaults(func=start_convert)


def main():
    parser = argparse.ArgumentParser(
        description="Tool to convert a Trails of Cold Steel II save between PS4 <-> PC",
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
