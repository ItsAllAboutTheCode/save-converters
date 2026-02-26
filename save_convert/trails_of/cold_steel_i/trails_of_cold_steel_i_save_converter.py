#!/usr/bin/env python
"""Script for converting the The Legend of Heroes - Trails of Cold Steel I PS4 <-> PC save"""

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

logger = logging.getLogger("cold_steel_i_save_converter")
logger.setLevel(logging.INFO)
stdoutHandler = logging.StreamHandler()
logger.addHandler(stdoutHandler)


TRAILS_OF_COLD_STEEL_I_PS4_SAVE_SIZE = 519392
# The Normal PC Save is 58400 bytes smaller than PS4
PS4_TO_PC_BYTE_REDUCTION = 58400
TRAILS_OF_COLD_STEEL_I_PC_SAVE_SIZE = TRAILS_OF_COLD_STEEL_I_PS4_SAVE_SIZE - PS4_TO_PC_BYTE_REDUCTION


class SaveConvertColdSteelI(SaveConvertColdSteelBase):
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
                    source_range=Range(start=0x0, end=0x0), output_bytes=bytes([0xC0, 0x08, 0x07, 0x00])
                ),
            )
        )
        inplace_to_skip_adjustment -= 4

        # Delete bytes to align character data
        start_offset = inplace_to_skip_adjustment + 0x20
        bytes_to_delete = 20
        PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
            ReplaceMap(
                replace_functor=ReplaceRangeBytes(
                    source_range=Range(start=start_offset, end=start_offset + bytes_to_delete), output_bytes=b""
                ),
            )
        )
        inplace_to_skip_adjustment += bytes_to_delete

        # Align location data for model 1
        start_offset = inplace_to_skip_adjustment + 0x2E24
        bytes_to_delete = 12
        PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
            ReplaceMap(
                replace_functor=ReplaceRangeBytes(
                    source_range=Range(start=start_offset, end=start_offset + bytes_to_delete), output_bytes=b""
                ),
            )
        )
        inplace_to_skip_adjustment += bytes_to_delete

        # Start aligning animation state data for model 1
        start_offset = inplace_to_skip_adjustment + 0x2E94
        bytes_to_delete = 8
        PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
            ReplaceMap(
                replace_functor=ReplaceRangeBytes(
                    source_range=Range(start=start_offset, end=start_offset + bytes_to_delete), output_bytes=b""
                ),
            )
        )
        inplace_to_skip_adjustment += bytes_to_delete

        start_offset = inplace_to_skip_adjustment + 0x2EA8
        bytes_to_delete = 12
        PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
            ReplaceMap(
                replace_functor=ReplaceRangeBytes(
                    source_range=Range(start=start_offset, end=start_offset + bytes_to_delete), output_bytes=b""
                ),
            )
        )
        inplace_to_skip_adjustment += bytes_to_delete

        start_offset = inplace_to_skip_adjustment + 0x2FC8
        bytes_to_delete = 20
        PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
            ReplaceMap(
                replace_functor=ReplaceRangeBytes(
                    source_range=Range(start=start_offset, end=start_offset + bytes_to_delete), output_bytes=b""
                ),
            )
        )
        inplace_to_skip_adjustment += bytes_to_delete

        start_offset = inplace_to_skip_adjustment + 0x302C
        bytes_to_delete = 8
        PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
            ReplaceMap(
                replace_functor=ReplaceRangeBytes(
                    source_range=Range(start=start_offset, end=start_offset + bytes_to_delete), output_bytes=b""
                ),
            )
        )
        inplace_to_skip_adjustment += bytes_to_delete

        start_offset = inplace_to_skip_adjustment + 0x3030
        bytes_to_delete = 4
        PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
            ReplaceMap(
                replace_functor=ReplaceRangeBytes(
                    source_range=Range(start=start_offset, end=start_offset + bytes_to_delete), output_bytes=b""
                ),
            )
        )
        inplace_to_skip_adjustment += bytes_to_delete

        start_offset = inplace_to_skip_adjustment + 0x30F0
        bytes_to_delete = 80
        PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
            ReplaceMap(
                replace_functor=ReplaceRangeBytes(
                    source_range=Range(start=start_offset, end=start_offset + bytes_to_delete), output_bytes=b""
                ),
            )
        )
        inplace_to_skip_adjustment += bytes_to_delete

        start_offset = inplace_to_skip_adjustment + 0x315C
        bytes_to_delete = 12
        PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
            ReplaceMap(
                replace_functor=ReplaceRangeBytes(
                    source_range=Range(start=start_offset, end=start_offset + bytes_to_delete), output_bytes=b""
                ),
            )
        )
        inplace_to_skip_adjustment += bytes_to_delete

        start_offset = inplace_to_skip_adjustment + 0x3214
        bytes_to_delete = 80
        PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
            ReplaceMap(
                replace_functor=ReplaceRangeBytes(
                    source_range=Range(start=start_offset, end=start_offset + bytes_to_delete), output_bytes=b""
                ),
            )
        )
        inplace_to_skip_adjustment += bytes_to_delete

        start_offset = inplace_to_skip_adjustment + 0x3274
        bytes_to_delete = 8
        PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
            ReplaceMap(
                replace_functor=ReplaceRangeBytes(
                    source_range=Range(start=start_offset, end=start_offset + bytes_to_delete), output_bytes=b""
                ),
            )
        )
        inplace_to_skip_adjustment += bytes_to_delete

        start_offset = inplace_to_skip_adjustment + 0x3278
        bytes_to_delete = 4
        PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
            ReplaceMap(
                replace_functor=ReplaceRangeBytes(
                    source_range=Range(start=start_offset, end=start_offset + bytes_to_delete), output_bytes=b""
                ),
            )
        )
        inplace_to_skip_adjustment += bytes_to_delete

        start_offset = inplace_to_skip_adjustment + 0x3338
        bytes_to_delete = 80
        PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
            ReplaceMap(
                replace_functor=ReplaceRangeBytes(
                    source_range=Range(start=start_offset, end=start_offset + bytes_to_delete), output_bytes=b""
                ),
            )
        )
        inplace_to_skip_adjustment += bytes_to_delete

        start_offset = inplace_to_skip_adjustment + 0x33A4
        bytes_to_delete = 12
        PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
            ReplaceMap(
                replace_functor=ReplaceRangeBytes(
                    source_range=Range(start=start_offset, end=start_offset + bytes_to_delete), output_bytes=b""
                ),
            )
        )
        inplace_to_skip_adjustment += bytes_to_delete
        # Finish alignment of animation state data for model 1

        LOCATION_DATA_STRIDE = 1760
        CHARACTER_MODELS = 10
        for i in range(1, CHARACTER_MODELS):
            # Align location data for model (i + 1)
            start_offset = inplace_to_skip_adjustment + 0x2D78 + (LOCATION_DATA_STRIDE * i)
            # Note this is different from Model 1 where only 12 bytes were deleted
            bytes_to_delete = 72
            PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
                ReplaceMap(
                    replace_functor=ReplaceRangeBytes(
                        source_range=Range(start=start_offset, end=start_offset + bytes_to_delete), output_bytes=b""
                    ),
                )
            )
            inplace_to_skip_adjustment += bytes_to_delete

            # Start aligning animation state data for model (i + 1)
            start_offset = inplace_to_skip_adjustment + 0x2E94 + (LOCATION_DATA_STRIDE * i)
            bytes_to_delete = 8
            PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
                ReplaceMap(
                    replace_functor=ReplaceRangeBytes(
                        source_range=Range(start=start_offset, end=start_offset + bytes_to_delete), output_bytes=b""
                    ),
                )
            )
            inplace_to_skip_adjustment += bytes_to_delete

            start_offset = inplace_to_skip_adjustment + 0x2EA8 + (LOCATION_DATA_STRIDE * i)
            bytes_to_delete = 12
            PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
                ReplaceMap(
                    replace_functor=ReplaceRangeBytes(
                        source_range=Range(start=start_offset, end=start_offset + bytes_to_delete), output_bytes=b""
                    ),
                )
            )
            inplace_to_skip_adjustment += bytes_to_delete

            start_offset = inplace_to_skip_adjustment + 0x2FC8 + (LOCATION_DATA_STRIDE * i)
            bytes_to_delete = 20
            PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
                ReplaceMap(
                    replace_functor=ReplaceRangeBytes(
                        source_range=Range(start=start_offset, end=start_offset + bytes_to_delete), output_bytes=b""
                    ),
                )
            )
            inplace_to_skip_adjustment += bytes_to_delete

            start_offset = inplace_to_skip_adjustment + 0x302C + (LOCATION_DATA_STRIDE * i)
            bytes_to_delete = 8
            PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
                ReplaceMap(
                    replace_functor=ReplaceRangeBytes(
                        source_range=Range(start=start_offset, end=start_offset + bytes_to_delete), output_bytes=b""
                    ),
                )
            )
            inplace_to_skip_adjustment += bytes_to_delete

            start_offset = inplace_to_skip_adjustment + 0x3030 + (LOCATION_DATA_STRIDE * i)
            bytes_to_delete = 4
            PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
                ReplaceMap(
                    replace_functor=ReplaceRangeBytes(
                        source_range=Range(start=start_offset, end=start_offset + bytes_to_delete), output_bytes=b""
                    ),
                )
            )
            inplace_to_skip_adjustment += bytes_to_delete

            start_offset = inplace_to_skip_adjustment + 0x30F0 + (LOCATION_DATA_STRIDE * i)
            bytes_to_delete = 80
            PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
                ReplaceMap(
                    replace_functor=ReplaceRangeBytes(
                        source_range=Range(start=start_offset, end=start_offset + bytes_to_delete), output_bytes=b""
                    ),
                )
            )
            inplace_to_skip_adjustment += bytes_to_delete

            start_offset = inplace_to_skip_adjustment + 0x315C + (LOCATION_DATA_STRIDE * i)
            bytes_to_delete = 12
            PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
                ReplaceMap(
                    replace_functor=ReplaceRangeBytes(
                        source_range=Range(start=start_offset, end=start_offset + bytes_to_delete), output_bytes=b""
                    ),
                )
            )
            inplace_to_skip_adjustment += bytes_to_delete

            start_offset = inplace_to_skip_adjustment + 0x3214 + (LOCATION_DATA_STRIDE * i)
            bytes_to_delete = 80
            PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
                ReplaceMap(
                    replace_functor=ReplaceRangeBytes(
                        source_range=Range(start=start_offset, end=start_offset + bytes_to_delete), output_bytes=b""
                    ),
                )
            )
            inplace_to_skip_adjustment += bytes_to_delete

            start_offset = inplace_to_skip_adjustment + 0x3274 + (LOCATION_DATA_STRIDE * i)
            bytes_to_delete = 8
            PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
                ReplaceMap(
                    replace_functor=ReplaceRangeBytes(
                        source_range=Range(start=start_offset, end=start_offset + bytes_to_delete), output_bytes=b""
                    ),
                )
            )
            inplace_to_skip_adjustment += bytes_to_delete

            start_offset = inplace_to_skip_adjustment + 0x3278 + (LOCATION_DATA_STRIDE * i)
            bytes_to_delete = 4
            PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
                ReplaceMap(
                    replace_functor=ReplaceRangeBytes(
                        source_range=Range(start=start_offset, end=start_offset + bytes_to_delete), output_bytes=b""
                    ),
                )
            )
            inplace_to_skip_adjustment += bytes_to_delete

            start_offset = inplace_to_skip_adjustment + 0x3338 + (LOCATION_DATA_STRIDE * i)
            bytes_to_delete = 80
            PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
                ReplaceMap(
                    replace_functor=ReplaceRangeBytes(
                        source_range=Range(start=start_offset, end=start_offset + bytes_to_delete), output_bytes=b""
                    ),
                )
            )
            inplace_to_skip_adjustment += bytes_to_delete

            start_offset = inplace_to_skip_adjustment + 0x33A4 + (LOCATION_DATA_STRIDE * i)
            bytes_to_delete = 12
            PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
                ReplaceMap(
                    replace_functor=ReplaceRangeBytes(
                        source_range=Range(start=start_offset, end=start_offset + bytes_to_delete), output_bytes=b""
                    ),
                )
            )
            inplace_to_skip_adjustment += bytes_to_delete
            # Finish alignment of animation state data for model (i + 1)

        # Align the Inventory and game data
        start_offset = inplace_to_skip_adjustment + 0x40C24
        bytes_to_delete = 53672
        PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
            ReplaceMap(
                replace_functor=ReplaceRangeBytes(
                    source_range=Range(start=start_offset, end=start_offset + bytes_to_delete), output_bytes=b""
                ),
            )
        )
        inplace_to_skip_adjustment += bytes_to_delete

        # Align the Playtime data
        start_offset = inplace_to_skip_adjustment + 0x6B204
        bytes_to_delete = 764
        PATCH_TABLE[PS4_TO_PC_CONVERT_FORMAT].append(
            ReplaceMap(
                replace_functor=ReplaceRangeBytes(
                    source_range=Range(start=start_offset, end=start_offset + bytes_to_delete), output_bytes=b""
                ),
            )
        )
        inplace_to_skip_adjustment += bytes_to_delete

        # Delete padding bytes at the end of the converted PS4 save to have it match the original PC save size
        start_offset = inplace_to_skip_adjustment + TRAILS_OF_COLD_STEEL_I_PC_SAVE_SIZE
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
        logger.error("No convert function is set")
        response = False

    sys.exit(response)


if __name__ == "__main__":
    main()
