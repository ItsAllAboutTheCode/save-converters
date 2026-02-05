#!/usr/bin/env python
"""
Script for converting the Tales of Vesperia PS3 save to PC save
"""

import argparse
from io import BytesIO
import logging
import pathlib
import bisect
import struct
import tempfile
import shutil
import sys
from typing import Any, cast, override
from save_convert.vesperia_title_id_list import (
    VESPERIA_PC_TITLE_IDS,
    VESPERIA_PS3_TITLE_IDS,
)

from save_convert.save_convert_base import (
    ConvertFormat,
    EndianSwapSize,
    Range,
    RangeNotCoveredException,
    ReplaceMap,
    ReplaceResult,
    ReplaceState,
    SaveConvertBase,
    SaveFormat,
    fill_replace_func_in_offset_range_gaps,
    get_replace_endian_swap,
    get_replace_range_bytes,
    replace_copy,
)

logger = logging.getLogger("vesperia_save_converter")
logger.setLevel(logging.INFO)
stdoutHandler = logging.StreamHandler()
logger.addHandler(stdoutHandler)


VESPERIA_PS3_TO_PC_FORMAT = ConvertFormat(SaveFormat.PS3, SaveFormat.PC)
VESPERIA_PC_TO_PS3_FORMAT = ConvertFormat(SaveFormat.PC, SaveFormat.PS3)
VESPERIA_PS3_SAVE_SIZE = 552 + 838304  # 552 byte save header + 838204 byte save data block
VESPERIA_PC_SAVE_SIZE = VESPERIA_PS3_SAVE_SIZE + 16  # The PC Save block is 16 bytes larget than PS3


# Stores the range offset of all the custom character name offsets in the PS3 save file
# Since the character names are strings, they should not be endian swapped
VESPERIA_FIRST_PC_OFFSET_PS3 = 0xA8928
VESPERIA_PC_BLOCK_SIZE = 16400
VESPERIA_NUM_CHARACTERS = 9
VESPERIA_CUSTOM_CHARACTER_NAME_OFFSET = 0x4
VESPERIA_CUSTOM_CHARACTER_NAME_BUFFER_SIZE = 64

VESPERIA_CUSTOM_CHARACTER_NAME_OFFSET_RANGES = (
    ReplaceMap(
        source_range=Range(
            VESPERIA_FIRST_PC_OFFSET_PS3 + index * VESPERIA_PC_BLOCK_SIZE + VESPERIA_CUSTOM_CHARACTER_NAME_OFFSET,
            VESPERIA_FIRST_PC_OFFSET_PS3
            + index * VESPERIA_PC_BLOCK_SIZE
            + VESPERIA_CUSTOM_CHARACTER_NAME_OFFSET
            + VESPERIA_CUSTOM_CHARACTER_NAME_BUFFER_SIZE,
        ),
        replace_func=replace_copy,
    )
    for index in range(VESPERIA_NUM_CHARACTERS)
)

## Title Section
VESPERIA_TITLE_BITFIELD_OFFSET = (
    0x3C90  # 15504 bytes into the PC character data for character 1 which would be 0xAC5B8 (PS3) 0xAC5C8 (PC)
)
VESPERIA_TITLE_BITFIELD_SIZE = 4 * 15  # There are 15 32-bit ints for title data
# https://github.com/AdmiralCurtiss/HyoutaTools/blob/33f1e42a6efc5c386c654656c2b21991d58fdedb/HyoutaToolsLib/Tales/Vesperia/SaveData/SaveDataBlockPCStatus.cs#L87

# The title information starts in the PS3 menu.svo at offset 0x3800
# PS3 has 445 titles total (offset 0x380C in menu.svo)
# The first title offset is at 0x3818
# ID - 4 byte (Big Endian)
# Name Dictionary ID (for localization) - 4 byte (Big Endian)
# Description Dictionary ID - 4 byte (Big Endian)
# Character ID - 4 byte (Big Endian) Same as the character IDs in the save file
# Custom String - 16 bytes, truncates at a NUL-terminating character
# Bunny Guild Points - 4 bytes (Big Endian)
# Followed by 12 bytes of padding.
# Total size = 48 bytes

# The title info in the PC menu.svo starts at offset 0x3480
# It has the same structure as the PS3 title information.
# The first title at 0x3480 and each title is 48 bytes
# With the restoration of Costume Title Mod the PC version can have a total of 445 title as well


def patch_obtained_titles(
    input_data: bytes, offset: int, source_range: Range, convert_format: ConvertFormat
) -> ReplaceResult:
    # The offset must exactly match the beginning of the range to discover the all the titles
    if offset != source_range.start:
        return ReplaceResult(data=bytes(), new_offset=offset, replace_complete=ReplaceState.Skip)

    TITLE_PACK_STRIDE = 4  # 32-bits per title bitfield
    TITLE_PACK_BITS = TITLE_PACK_STRIDE * 8
    obtained_titles: set[int] = set()

    for title_bitfield_offset in range(offset, source_range.end, TITLE_PACK_STRIDE):
        # The Title list also needs to be endian swapped as well
        title_bitfield = int.from_bytes(
            bytes=input_data[title_bitfield_offset : title_bitfield_offset + TITLE_PACK_STRIDE],
            byteorder="big" if convert_format.source == SaveFormat.PS3 else "little",
        )
        for title_bit in range(TITLE_PACK_BITS):
            if (title_bitfield >> title_bit) & 1:
                obtained_titles.add((title_bitfield_offset - offset) * 8 + title_bit)

    platform_title_list = VESPERIA_PS3_TITLE_IDS if convert_format.target == SaveFormat.PS3 else VESPERIA_PC_TITLE_IDS
    invalid_titles: set[int] = set()
    for title in obtained_titles:
        title_name: str | None = platform_title_list.get(title)
        # Explicitly check against None as the first title has an empty string value which would make it a valid title without a name
        if title_name is None:
            invalid_titles.add(title)

    if invalid_titles:
        char_index = (offset - VESPERIA_FIRST_PC_OFFSET_PS3 - VESPERIA_TITLE_BITFIELD_OFFSET) // VESPERIA_PC_BLOCK_SIZE
        logger.info(
            f"Character {char_index} has invalid titles obtained at bits: {invalid_titles} from offset 0x{offset:X}\n"
            + "Invalid titles will set to 0 (not obtained)"
        )

    output_title_array: list[int] = [0] * (VESPERIA_TITLE_BITFIELD_SIZE // TITLE_PACK_STRIDE)
    valid_titles = obtained_titles - invalid_titles
    for title in valid_titles:
        output_title_array[title // TITLE_PACK_BITS] |= 1 << title % TITLE_PACK_BITS

    # Pack the title: int[15] array into bytes taking into account the endianess of the output format
    struct_format = f"{'<' if convert_format.target != SaveFormat.PS3 else '>'}{len(output_title_array)}I"
    output_data = struct.pack(struct_format, *output_title_array)
    return ReplaceResult(
        data=output_data,
        new_offset=source_range.end,
        replace_complete=ReplaceState.Complete,
    )


VESPERIA_CHARACTER_OBTAINED_TITLE_OFFSET_RANGES = (
    ReplaceMap(
        source_range=Range(
            VESPERIA_FIRST_PC_OFFSET_PS3 + index * VESPERIA_PC_BLOCK_SIZE + VESPERIA_TITLE_BITFIELD_OFFSET,
            VESPERIA_FIRST_PC_OFFSET_PS3
            + index * VESPERIA_PC_BLOCK_SIZE
            + VESPERIA_TITLE_BITFIELD_OFFSET
            + VESPERIA_TITLE_BITFIELD_SIZE,
        ),
        replace_func=patch_obtained_titles,
    )
    for index in range(VESPERIA_NUM_CHARACTERS)
)

# PC files have an extra 16(0x10) bytes
VESPERIA_PC_TO_PS3_POST_CUSTOM_DATA_OFFSET = 0x10

# The following offset appears to be be where the game checks if DLC items has been obtained
# The assembly instructions for the check are:
# ---
# TOV_DE.exe+5BC4F7 - 43 8B 8C 84 F43D0000  - mov ecx,[r12+r8*4+00003DF4]
# TOV_DE.exe+5BC4FF - 0FA3 D1               - bt ecx,edx
# TOV_DE.exe+5BC502 - 73 2E                 - jae TOV_DE.exe+5BC532
#
# r12 = Start of the PARTY_DATA block from the save file (0xA3F48 PS3 / 0xA3F58 PC)
# r8 = Can be between [0x31 - 0x3D] based on debugging DLC check routine of a converted PS3 save that triggered failure
# The value of 0x31  appears to be where DLC items start at. It appears it is a bitfield of obtained items
# So 0x31 (count) * 4 (bytes) * 8 ( bits per byte) = 0x620 = 1568 for the Item ID.
# Looking through the item list for the games normal items the highest value is 1237, so it is guessed that this is where the DLC items start
#
# Based on the number of 32-bit bitfields being check 0x31 thru 0x3D which is 52 bytes total,
# plus the fact that these types of fields tend to be 16 byte aligned, the stride of this check offset will be assumed to be 64 bytes(16 int sized bitfields)

VESPERIA_PS3_DLC_ITEM_CHECK_OFFSET = 0xA7E00
VESPERIA_PC_DLC_ITEM_CHECK_OFFSET = VESPERIA_PS3_DLC_ITEM_CHECK_OFFSET + VESPERIA_PC_TO_PS3_POST_CUSTOM_DATA_OFFSET
VESPERIA_DLC_ITEM_CHECK_STRIDE = 64


REPLACE_OFFSET_TABLE: dict[ConvertFormat, list[ReplaceMap]] = {
    ConvertFormat(SaveFormat.PS3, SaveFormat.PC): [
        # Replaces the PS3 save header with a working PC save
        # ReplaceMap(
        #    source_range=Range(0x0, 0x230),
        #    replace_bytes=bytes.fromhex(
        #        "660000000000000018020000B0CA0C006400000052E3D20136B6796900000000E4C98800550000000B3333303332300009000A000B00FFFF09000C000B000D00FFFF0C000E000D000F00FFFF0900080010001100120013001400150016001700180019001A001B0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004000000070000000300000008000000050000000600000005000000040000007F0000003E2200003E220000E7030000E70300000B323030303900005E005F00600061006200630064006500FFFF660065006700020000007F000000D9220000D9220000E7030000E70300000B3230303035000000000000000000000000000000000000000000000000000001000000800000000F2700000F270000E7030000E70300000B32303030300000000000000000000000000000000000000000000000000000090000007F0000000F2700000F270000E7030000E70300000B3230303234000000000000000000000000000000000000000000000000000001000000544F385341564500"
        #    ),
        # ),
        # Replace the save block filesize from the PS3 file which is big-endian: 00 0C CA A0 = 838304 bytes
        # With the PC save block size in little-endian: B0 CA 0C 00 = 838320 bytes
        ReplaceMap(
            source_range=Range(0x0C, 0x10),
            replace_func=get_replace_range_bytes(bytes([0xB0, 0xCA, 0x0C, 0x00])),
        ),
        # The date value is stored as a 64-bit seconds since the epoch value (1970-01-01)
        # https://docs.python.org/3/library/datetime.html#datetime.datetime.timestamp
        # Additional info: Playtime is stored 1/60 seconds at offset 0x14,
        # Gald is stored at offset 0x20
        ReplaceMap(
            source_range=Range(0x18, 0x20),
            replace_func=get_replace_endian_swap(swap_size=EndianSwapSize.Size64Bit),
        ),
        # Skip swapping the "TO8SAVE" magic bytes
        ReplaceMap(source_range=Range(0x228, 0x230), replace_func=replace_copy),
        # According to HyoutaTools SaveData research:
        # https://github.com/AdmiralCurtiss/HyoutaTools/blob/33f1e42a6efc5c386c654656c2b21991d58fdedb/HyoutaToolsLib/Tales/Vesperia/SaveData/SaveData.cs#L42
        # This offset contains the size of the save data minus the header 552 (0x228).
        # The PC Save size should be (838872 - 552) = 838320 (in little endian)
        # On PS3 this value is set to 838304 (big endian)
        ReplaceMap(
            source_range=Range(0x230, 0x234),
            replace_func=get_replace_range_bytes(bytes([0xB0, 0xCA, 0x0C, 0x00])),
        ),
        # Offset where reference strings start in the Save Data
        # Needs to be increased by 0x10 hex to account for the added bytes from PS3 to PC
        # https://github.com/AdmiralCurtiss/HyoutaTools/blob/33f1e42a6efc5c386c654656c2b21991d58fdedb/HyoutaToolsLib/Tales/Vesperia/SaveData/SaveData.cs#L47
        ReplaceMap(
            source_range=Range(0x254, 0x258),
            replace_func=get_replace_range_bytes(bytes([0xA0, 0xC9, 0x0C, 0x00])),
        ),
        # The offset of the section data start is located at 0x250 in the file (The value is always 0x400).
        # Therefore data starts at 0x628(0x228 header + 0x400)
        # Scenario block size = 4864,
        # Starts at offset (file:0x628 + 0 = 0x628, save:0x400 + 0 = 0x400)
        # Field Camera block size = 256,
        # Starts at offset (file:0x628 + 4864 = 0x1928, save:0x400 + 4864 = 0x1700)
        # Field Area block size = 2048,
        # Starts at offset (file:0x628 + 5120 = 0x1A28, save:0x400 + 5120 = 0x1800)
        # Field Car block size = 256,
        # Starts at offset (file:0x628 + 7168 = 0x2228, save:0x400 + 7168 = 0x2000)
        # Camp block size = 256,
        # Starts at offset (file:0x628 + 7424 = 0x2328, save:0x400 + 7424 = 0x2100)
        # FIELD_SAVE block size = 1244,
        # Starts at offset (file:0x628 + 7680 = 0x2428, save:0x400 + 7680 = 0x2200)
        # STANDBYENEMY block size = 3112,
        # Starts at offset (file:0x628 + 8928 = 0x2908, save:0x400 + 8928 = 0x26E0)
        # TreasureSaveData block size = 588,
        # Starts at offset (file:0x628 + 12048 = 0x3538, save:0x400 + 12048 = 0x3310)
        # CUSTOM_DATA block size = 288 on PS3, 292 on PC
        # Starts at offset (file:0x628 + 12640 = 0x3788, save:0x400 + 12640 = 0x3560)
        #
        ## Now because the PC custom data is 292(0x124) and the data section has be aligned to 0x10
        ## All the other sections are pushed down by 0x10 bytes
        ## The CUSTOM_DATA block could be treated as being 304(0x130) bytes
        ## Therefore modifications to the remaining section offsets occur below
        # SoundTheater block size = 544
        # Starts at offset (PC file:0x628 + 12944 = 0x38B8, PS3 file:0x628 + 12928 = 0x38A8
        #                   PC save:0x400 + 12944 = 0x3690, PS3 save:0x400 + 12928 = 0x3680
        ReplaceMap(
            source_range=Range(0x44C, 0x450),
            replace_func=get_replace_range_bytes(bytes([0x90, 0x32, 0x00, 0x00])),
        ),
        # SavePoint block size = 1024
        # Starts at offset (PC file:0x628 + 13488 = 0x3AD8, PS3 file:0x628 + 13472 = 0x3AC8
        #                   PC save:0x400 + 13488 = 0x38B0, PS3 save:0x400 + 13472 = 0x38A0
        ReplaceMap(
            source_range=Range(0x46C, 0x470),
            replace_func=get_replace_range_bytes(bytes([0xB0, 0x34, 0x00, 0x00])),
        ),
        # MG2Poker block size = 128
        # Starts at offset (PC file:0x628 + 14512 = 0x3ED8, PS3 file:0x628 + 14496 = 0x3EC8
        #                   PC save:0x400 + 14512 = 0x3CB0, PS3 save:0x400 + 14496 = 0x3CA0)
        ReplaceMap(
            source_range=Range(0x48C, 0x490),
            replace_func=get_replace_range_bytes(bytes([0xB0, 0x38, 0x00, 0x00])),
        ),
        # SnowBoard block size = 655360
        # Starts at offset (PC file:0x628 + 14640 = 0x3F58, PS3 file:0x628 + 14624 = 0x3F48
        #                   PC save:0x400 + 14640 = 0x3D30, PS3 save:0x400 + 14624 = 0x3D20
        ReplaceMap(
            source_range=Range(0x4AC, 0x4B0),
            replace_func=get_replace_range_bytes(bytes([0x30, 0x39, 0x00, 0x00])),
        ),
        # PARTY_DATA block size = 18904
        # Starts at offset (PC file:0x628 + 670000 = 0xA3F58, PS3 file:0x628 + 669984 = 0xA3F48
        #                   PC save:0x400 + 670000 = 0xA3D30, PS3 save:0x400 + 669984 = 0xA3D20
        ReplaceMap(
            source_range=Range(0x4CC, 0x4D0),
            replace_func=get_replace_range_bytes(bytes([0x30, 0x39, 0x0A, 0x00])),
        ),
        # PC_STATUS1 block size = 16400
        # Starts at offset (PC file:0x628 + 688912 = 0xA8938, PS3 file:0x628 + 688896 = 0xA8928
        #                   PC save:0x400 + 688912 = 0xA8710, PS3 save:0x400 + 688896 = 0xA8700
        ReplaceMap(
            source_range=Range(0x4EC, 0x4F0),
            replace_func=get_replace_range_bytes(bytes([0x10, 0x83, 0x0A, 0x00])),
        ),
        # PC_STATUS2 block size = 16400
        # Starts at offset (PC file:0x628 + 705312 = 0xAC948, PS3 file:0x628 + 705296 = 0xAC938
        #                   PC save:0x400 + 705312 = 0xAC720, PS3 save:0x400 + 705296 = 0xAC710
        ReplaceMap(
            source_range=Range(0x50C, 0x510),
            replace_func=get_replace_range_bytes(bytes([0x20, 0xC3, 0x0A, 0x00])),
        ),
        # PC_STATUS3 block size = 16400
        # Starts at offset (PC file:0x628 + 721712 = 0xB0958, PS3 file:0x628 + 721696 = 0xB0948
        #                   PC save:0x400 + 721712 = 0xB0730, PS3 save:0x400 + 721696 = 0xB0720
        ReplaceMap(
            source_range=Range(0x52C, 0x530),
            replace_func=get_replace_range_bytes(bytes([0x30, 0x03, 0x0B, 0x00])),
        ),
        # PC_STATUS4 block size = 16400
        # Starts at offset (PC file:0x628 + 738112 = 0xB4968, PS3 file:0x628 + 738096 = 0xB4958
        #                   PC save:0x400 + 738112 = 0xB4740, PS3 save:0x400 + 738096 = 0xB4730
        ReplaceMap(
            source_range=Range(0x54C, 0x550),
            replace_func=get_replace_range_bytes(bytes([0x40, 0x43, 0x0B, 0x00])),
        ),
        # PC_STATUS5 block size = 16400
        # Starts at offset (PC file:0x628 + 754512 = 0xB8978, PS3 file:0x628 + 754496 = 0xB8968
        #                   PC save:0x400 + 754512 = 0xB8750, PS3 save:0x400 + 754496 = 0xB8740
        ReplaceMap(
            source_range=Range(0x56C, 0x570),
            replace_func=get_replace_range_bytes(bytes([0x50, 0x83, 0x0B, 0x00])),
        ),
        # PC_STATUS6 block size = 16400
        # Starts at offset (PC file:0x628 + 770912 = 0xBC988, PS3 file:0x628 + 770896 = 0xBC978
        #                   PC save:0x400 + 770912 = 0xBC760, PS3 save:0x400 + 770896 = 0xBC750
        ReplaceMap(
            source_range=Range(0x58C, 0x590),
            replace_func=get_replace_range_bytes(bytes([0x60, 0xC3, 0x0B, 0x00])),
        ),
        # PC_STATUS7 block size = 16400
        # Starts at offset (PC file:0x628 + 787312 = 0xC0998, PS3 file:0x628 + 787296 = 0xC0988
        #                   PC save:0x400 + 787312 = 0xC0770, PS3 save:0x400 + 787296 = 0xC0760
        ReplaceMap(
            source_range=Range(0x5AC, 0x5B0),
            replace_func=get_replace_range_bytes(bytes([0x70, 0x03, 0x0C, 0x00])),
        ),
        # PC_STATUS8 block size = 16400
        # Starts at offset (PC file:0x628 + 803712 = 0xC49A8, PS3 file:0x628 + 803696 = 0xC4998
        #                   PC save:0x400 + 803712 = 0xC4780, PS3 save:0x400 + 803696 = 0xC4770
        ReplaceMap(
            source_range=Range(0x5CC, 0x5D0),
            replace_func=get_replace_range_bytes(bytes([0x80, 0x43, 0x0C, 0x00])),
        ),
        # PC_STATUS9 block size = 16400
        # Starts at offset (PC file:0x628 + 820112 = 0xC89B8, PS3 file:0x628 + 820096 = 0xC89A8
        #                   PC save:0x400 + 820112 = 0xC8790, PS3 save:0x400 + 820096 = 0xC8780
        ReplaceMap(
            source_range=Range(0x5EC, 0x5F0),
            replace_func=get_replace_range_bytes(bytes([0x90, 0x83, 0x0C, 0x00])),
        ),
        # FieldGadget block size = 512
        # Starts at offset (PC file:0x628 + 836512 = 0xCC9C8, PS3 file:0x628 + 836496 = 0xCC9B8
        #                   PC save:0x400 + 836512 = 0xCC7A0, PS3 save:0x400 + 836496 = 0xCC790
        ReplaceMap(
            source_range=Range(0x60C, 0x610),
            replace_func=get_replace_range_bytes(bytes([0xA0, 0xC3, 0x0C, 0x00])),
        ),
        # Map location is a string, so don't swap it
        ReplaceMap(source_range=Range(0x668, 0x670), replace_func=replace_copy),
        # Weather condition is a string
        ReplaceMap(source_range=Range(0x688, 0x690), replace_func=replace_copy),
        # Another string that is set "default"
        ReplaceMap(source_range=Range(0xC30, 0xC38), replace_func=replace_copy),
        # The data here appears to be packed tightly without swaps
        ReplaceMap(source_range=Range(0x1728, 0x1828), replace_func=replace_copy),
        # The Field Camera and Field Areas sections appear to only contain string data
        ReplaceMap(source_range=Range(0x1A90, 0x1F00), replace_func=replace_copy),
        # Insert 16 bytes at the end of the CUSTOM_DATA section to align the Sound Theater data on PC at
        # The PS3 input offset would be at 0x38A8
        ReplaceMap(
            source_range=Range(0x38A8, 0x38A8),
            replace_func=get_replace_range_bytes(bytes([0x0] * 16)),
        ),
        # SavePoint data should not be endian swapped
        ReplaceMap(source_range=Range(0x3AC8, 0x3AC8 + 1024), replace_func=replace_copy),
        # Custom Battle Strategy names are strings
        ReplaceMap(
            source_range=Range(0xA7160, 0xA7160 + 0x40 * 8),
            replace_func=replace_copy,
        ),
        # Copy any custom character names without endian swaps
        *VESPERIA_CUSTOM_CHARACTER_NAME_OFFSET_RANGES,
        # Remove any titles that are invalid
        *VESPERIA_CHARACTER_OBTAINED_TITLE_OFFSET_RANGES,
        # Section Name data at the end of the save are strings
        ReplaceMap(
            source_range=Range(0xCCBB8, 0xCCCC8),
            replace_func=replace_copy,
        ),
    ],
    ## Create reverse entry of PC -> PS3 conversion for vesperia
    ConvertFormat(SaveFormat.PC, SaveFormat.PS3): [
        ReplaceMap(
            source_range=Range(0x0C, 0x10),
            replace_func=get_replace_range_bytes(bytes([0x00, 0x0C, 0xCA, 0xA0])),
        ),
        ReplaceMap(
            source_range=Range(0x18, 0x20),
            replace_func=get_replace_endian_swap(swap_size=EndianSwapSize.Size64Bit),
        ),
        ReplaceMap(source_range=Range(0x228, 0x230), replace_func=replace_copy),
        ReplaceMap(
            source_range=Range(0x230, 0x234),
            replace_func=get_replace_range_bytes(bytes([0x00, 0x0C, 0xCA, 0xA0])),
        ),
        ReplaceMap(
            source_range=Range(0x254, 0x258),
            replace_func=get_replace_range_bytes(bytes([0x00, 0x0C, 0xC9, 0x90])),
        ),
        ReplaceMap(
            source_range=Range(0x44C, 0x450),
            replace_func=get_replace_range_bytes(bytes([0x00, 0x00, 0x32, 0x80])),
        ),
        ReplaceMap(
            source_range=Range(0x46C, 0x470),
            replace_func=get_replace_range_bytes(bytes([0x00, 0x00, 0x34, 0xA0])),
        ),
        ReplaceMap(
            source_range=Range(0x48C, 0x490),
            replace_func=get_replace_range_bytes(bytes([0x00, 0x00, 0x38, 0xA0])),
        ),
        ReplaceMap(
            source_range=Range(0x4AC, 0x4B0),
            replace_func=get_replace_range_bytes(bytes([0x00, 0x00, 0x39, 0x20])),
        ),
        ReplaceMap(
            source_range=Range(0x4CC, 0x4D0),
            replace_func=get_replace_range_bytes(bytes([0x00, 0x0A, 0x39, 0x20])),
        ),
        ReplaceMap(
            source_range=Range(0x4EC, 0x4F0),
            replace_func=get_replace_range_bytes(bytes([0x00, 0x0A, 0x83, 0x00])),
        ),
        ReplaceMap(
            source_range=Range(0x50C, 0x510),
            replace_func=get_replace_range_bytes(bytes([0x00, 0x0A, 0xC3, 0x10])),
        ),
        ReplaceMap(
            source_range=Range(0x52C, 0x530),
            replace_func=get_replace_range_bytes(bytes([0x00, 0x0B, 0x03, 0x20])),
        ),
        ReplaceMap(
            source_range=Range(0x54C, 0x550),
            replace_func=get_replace_range_bytes(bytes([0x00, 0x0B, 0x43, 0x30])),
        ),
        ReplaceMap(
            source_range=Range(0x56C, 0x570),
            replace_func=get_replace_range_bytes(bytes([0x00, 0x0B, 0x83, 0x40])),
        ),
        ReplaceMap(
            source_range=Range(0x58C, 0x590),
            replace_func=get_replace_range_bytes(bytes([0x00, 0x0B, 0xC3, 0x50])),
        ),
        ReplaceMap(
            source_range=Range(0x5AC, 0x5B0),
            replace_func=get_replace_range_bytes(bytes([0x00, 0x0C, 0x03, 0x60])),
        ),
        ReplaceMap(
            source_range=Range(0x5CC, 0x5D0),
            replace_func=get_replace_range_bytes(bytes([0x00, 0x0C, 0x43, 0x70])),
        ),
        ReplaceMap(
            source_range=Range(0x5EC, 0x5F0),
            replace_func=get_replace_range_bytes(bytes([0x00, 0x0C, 0x83, 0x80])),
        ),
        ReplaceMap(
            source_range=Range(0x60C, 0x610),
            replace_func=get_replace_range_bytes(bytes([0x00, 0x0C, 0xC3, 0x90])),
        ),
        ReplaceMap(source_range=Range(0x668, 0x670), replace_func=replace_copy),
        ReplaceMap(source_range=Range(0x688, 0x690), replace_func=replace_copy),
        ReplaceMap(source_range=Range(0xC30, 0xC38), replace_func=replace_copy),
        ReplaceMap(source_range=Range(0x1728, 0x1828), replace_func=replace_copy),
        ReplaceMap(source_range=Range(0x1A90, 0x1F00), replace_func=replace_copy),
        # Delete 16 bytes at the end of the CUSTOM_DATA block
        # The PS3 input offset would be at 0x38A8
        ReplaceMap(
            source_range=Range(0x38A8, 0x38B8),
            replace_func=get_replace_range_bytes(bytes()),
        ),
        #### Any source_range after this point requires 0x10 to be added to translated from the PC offset.
        ReplaceMap(
            source_range=Range(
                0x3AC8 + VESPERIA_PC_TO_PS3_POST_CUSTOM_DATA_OFFSET,
                0x3AC8 + VESPERIA_PC_TO_PS3_POST_CUSTOM_DATA_OFFSET + 1024,
            ),
            replace_func=replace_copy,
        ),
        ReplaceMap(
            source_range=Range(
                0xA7160 + VESPERIA_PC_TO_PS3_POST_CUSTOM_DATA_OFFSET,
                0xA7160 + VESPERIA_PC_TO_PS3_POST_CUSTOM_DATA_OFFSET + 0x40 * 8,
            ),
            replace_func=replace_copy,
        ),
        *[
            ReplaceMap(
                source_range=char_name_replace_entry.source_range + VESPERIA_PC_TO_PS3_POST_CUSTOM_DATA_OFFSET,
                replace_func=char_name_replace_entry.replace_func,
            )
            for char_name_replace_entry in VESPERIA_CUSTOM_CHARACTER_NAME_OFFSET_RANGES
        ],
        *[
            ReplaceMap(
                source_range=char_name_replace_entry.source_range + VESPERIA_PC_TO_PS3_POST_CUSTOM_DATA_OFFSET,
                replace_func=char_name_replace_entry.replace_func,
            )
            for char_name_replace_entry in VESPERIA_CHARACTER_OBTAINED_TITLE_OFFSET_RANGES
        ],
        ReplaceMap(
            source_range=Range(
                0xCCBB8 + VESPERIA_PC_TO_PS3_POST_CUSTOM_DATA_OFFSET,
                0xCCCC8 + VESPERIA_PC_TO_PS3_POST_CUSTOM_DATA_OFFSET,
            ),
            replace_func=replace_copy,
        ),
    ],
}


def create_replace_offset_dict(convert_format: ConvertFormat, patch_dlc_item_checks: bool) -> list[ReplaceMap]:
    """
    Returns a dictionary of offset -> byte array entries that indicates which
    actions should be performed when an address is encountered from the input save

    :param: patch_dlc_item_checks - If True, replaces the DLC obtained item bits from the save file to be 0(unobtained)
    This should allow bypassing being unable to load the save due to DLC
    """
    game_replace_table: list[ReplaceMap] = sorted(
        REPLACE_OFFSET_TABLE.get(convert_format, []),
        key=lambda entry: (entry.source_range.start, entry.source_range.end),
    )

    ## Add the dlc item check patch range entry
    if patch_dlc_item_checks:
        dlc_check_start = (
            VESPERIA_PS3_DLC_ITEM_CHECK_OFFSET
            if convert_format.source == SaveFormat.PS3
            else VESPERIA_PC_DLC_ITEM_CHECK_OFFSET
        )
        # Patch the bytes starting at the DLC_ITEM check offset with 64 zeros
        bisect.insort(
            game_replace_table,
            ReplaceMap(
                source_range=Range(dlc_check_start, dlc_check_start + VESPERIA_DLC_ITEM_CHECK_STRIDE),
                replace_func=get_replace_range_bytes(bytes(VESPERIA_DLC_ITEM_CHECK_STRIDE)),
            ),
        )

    # Now fill in any non-converted range gaps with the endian swap method to have endian swapping occur for the save
    if convert_format.source == SaveFormat.PS3 and convert_format.target != SaveFormat.PS3:
        game_replace_table = fill_replace_func_in_offset_range_gaps(
            game_replace_table,
            fill_replace_func=get_replace_endian_swap(swap_size=EndianSwapSize.Size32Bit),
            max_offset=VESPERIA_PS3_SAVE_SIZE,
        )
    elif convert_format.source != SaveFormat.PS3 and convert_format.target == SaveFormat.PS3:
        game_replace_table = fill_replace_func_in_offset_range_gaps(
            game_replace_table,
            fill_replace_func=get_replace_endian_swap(swap_size=EndianSwapSize.Size32Bit),
            max_offset=VESPERIA_PC_SAVE_SIZE,
        )

    if not game_replace_table:
        return []

    error_message = ""
    prev_value: ReplaceMap = game_replace_table[0]
    if prev_value.source_range.start != 0:
        error_message += f"First range entry must start at offset 0x0. It is {prev_value.source_range.start}\n"
    for value in game_replace_table[1:]:
        if prev_value.source_range.end != value.source_range.start:
            error_message += (
                "The previous range entry end offset must be equal to the current range entry start offset."
                f"Previous entry: {prev_value.source_range.end}, Current entry {value.source_range.start}.\n"
            )
        prev_value = value

    if convert_format.source == SaveFormat.PS3:
        input_save_size = VESPERIA_PS3_SAVE_SIZE
    elif convert_format.source == SaveFormat.PC:
        input_save_size = VESPERIA_PC_SAVE_SIZE
    else:
        raise ValueError(f"Source convert format {convert_format.source} does not have known save size. Aborting...")
    if game_replace_table[-1].source_range.end < input_save_size:
        error_message += f"The last range entry end offset must be at least {input_save_size:x}. It is {game_replace_table[-1].source_range.end}\n"

    if error_message:
        raise RangeNotCoveredException(error_message)

    return game_replace_table


def process_input_savedata(
    offset: int,
    input_data: bytes,
    replace_set: list[ReplaceMap],
    replace_start_index: int,
    convert_format: ConvertFormat,
) -> ReplaceResult:
    """
    Process every 4 bytes(32-bits) of the input data to determine how it should be written to the output
    The order of precendence for operations are:
    1. Determine if bytes should be replaced at an offset (Replace bytes)
    2. Determine if the bytes at an offset should be endian swaped based on the endian_swap_size value (Swap Bytes)


    :param: offset Offset being examined from the input save data
    :param: input_data Data from the input save file
    :param: replace_set Ordered list of offset range -> bytes to replace
            This set is used to replace data that between the offset range
    :param: replace_start_index Index in the replace set to start to search for the offset within
            This value gets updated by this method and returned. It should initially be set to 0
            and then passed back into this method every iteration.

    :return: Result class containing (bytes_to_write_to_output, updated_input_offset,
             replacement for the current input range has completed)
    """

    ### Determine if offset references a value within the replace set
    replace_index: int = -1
    if replace_set:
        # Get the first smallest index > @offset
        lower_bound = bisect.bisect_left(
            replace_set,
            offset,
            lo=replace_start_index,
            key=lambda entry: entry.source_range.start,
        )

        if lower_bound != len(replace_set) and replace_set[lower_bound].source_range.start == offset:
            # If the offset is exactly equal to the lower_bound start offset, use that entry
            replace_index = lower_bound
        elif lower_bound > 0:
            # Otherwise check if the previous index replace entry end offset is >= offset
            if replace_set[lower_bound - 1].source_range.end >= offset:
                replace_index = lower_bound - 1

    if replace_index != -1:
        source_range = replace_set[replace_index].source_range
        output_result = replace_set[replace_index].replace_func(input_data, offset, source_range, convert_format)
        return output_result

    return ReplaceResult(data=bytes(), new_offset=offset, replace_complete=ReplaceState.Skip)


class SaveConvertVesperia(SaveConvertBase):
    _input_path: pathlib.Path
    _output_path: pathlib.Path
    _convert_format: ConvertFormat
    _patch_dlc_checks: bool
    _input_data: bytes
    _output_io: BytesIO

    def __init__(self, args: argparse.Namespace):
        super().__init__()
        self._input_path = cast(pathlib.Path, args.input)
        self._convert_format = cast(ConvertFormat, args.convert_format)
        self._patch_dlc_checks = cast(bool, args.patch_dlc_item_checks)
        output_path: pathlib.Path | None = args.output  # pyright: ignore[reportAny]
        if not output_path:
            output_path = self._input_path.with_suffix(f"{self._input_path.suffix}.{self._convert_format.target}")
            logger.info(f"No Output path specified, it has been set to {output_path}")

        self._output_path = output_path

    @override
    def _pre_convert(self) -> bool:
        """
        Pre-load save data from the input file into memory
        """
        # Read the entire save into memory
        with self._input_path.open("rb") as infile:
            try:
                self._input_data = infile.read()
            except BlockingIOError as err:
                logger.error(f"Unable to read data from input file {self._input_path}: {err}")
                return False

        return True

    @override
    def _convert(self) -> bool:
        """
        Iterates over the input save file, attempting byte replacements from the source save format
        in order to convert the target save format
        """

        self._output_io = BytesIO()  # Create a in-memory binary IO buffer for storing output data
        replace_set = create_replace_offset_dict(
            convert_format=self._convert_format,
            patch_dlc_item_checks=self._patch_dlc_checks,
        )
        replace_set_index = 0

        cur_offset = 0
        while cur_offset < len(self._input_data):
            result = process_input_savedata(
                cur_offset,
                self._input_data,
                replace_set,
                replace_set_index,
                self._convert_format,
            )

            try:
                if self._output_io.write(result.data) != len(result.data):
                    logger.error(
                        f"Unable to write {len(result.data)} bytes  to output. Input offset: {cur_offset}."
                        + f" Output offset: {self._output_io.tell()}"
                    )
                    return False
            except OSError as _err:
                logger.exception("Failed to write to output\n")
                return False

            # If no progress has been made in the processing of the input data
            # Then break to prevent an infinite loop
            if result.replace_complete == ReplaceState.Skip:
                break

            # Update the current offset being processed and the replace set index
            cur_offset = result.new_offset
            replace_set_index += 1 if result.replace_complete else 0

        return True

    @override
    def _post_convert(self) -> bool:
        """
        Writes the output data to the destination file atomically
        """
        # Now copy temporary output file to destination
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_output_path = pathlib.Path(f"{tmpdir}/{self._output_path.name}").resolve()
            with tmp_output_path.open("wb") as outfile:
                byte_buffer = self._output_io.getvalue()
                assert outfile.write(byte_buffer) == len(byte_buffer)
                self._output_io.close()
            shutil.move(tmp_output_path, self._output_path)
        return True


### Start of argument parser setup
def start_convert(args: argparse.Namespace):
    save_converter = SaveConvertVesperia(args)
    return save_converter.convert()


def add_commands(parser: argparse.ArgumentParser) -> None:
    # Add general connection arguments
    parser.add_argument(  # pyright: ignore[reportUnusedCallResult]
        "--input",
        "-i",
        type=pathlib.Path,
        help="Input path to PS3 Save file",
        required=True,
    )
    parser.add_argument(  # pyright: ignore[reportUnusedCallResult]
        "--output",
        "-o",
        type=pathlib.Path,
        help="Output path to PC Save file. Defaults to <input-file-path>.pc if not specified",
    )

    class ConvertFormatAction(argparse.Action):
        def __init__(self, option_strings, dest, nargs=None, **kwargs):
            if nargs is not None:
                raise ValueError("nargs not allowed")
            super().__init__(option_strings, dest, **kwargs)

        @override
        def __call__(
            self,
            parser: argparse.ArgumentParser,
            namespace: argparse.Namespace,
            values: Any,
            options_string: str | None = None,
        ):
            if values == "ps3-to-pc":
                setattr(namespace, self.dest, VESPERIA_PS3_TO_PC_FORMAT)
            elif values == "pc-to-ps3":
                setattr(namespace, self.dest, VESPERIA_PC_TO_PS3_FORMAT)
            else:
                raise ValueError(f"Value {values} is not an appropriate choice for argument {options_string}")

    parser.add_argument(  # pyright: ignore[reportUnusedCallResult]
        "--convert-format",
        "-f",
        action=ConvertFormatAction,
        choices=["ps3-to-pc", "pc-to-ps3"],
        default=VESPERIA_PS3_TO_PC_FORMAT,
        help="Specifies the input file save format and what should the output file format should be. Only PS3 and PC supported at this time",
    )

    parser.add_argument(  # pyright: ignore[reportUnusedCallResult]
        "--patch-dlc-item-checks",
        "-p",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Patches the DLC item obtained bytes from the save file to allow the saves with incompatible DLC to be loaded (Default=True)",
    )
    parser.set_defaults(func=start_convert)


def main():
    parser = argparse.ArgumentParser(
        description="Tool to convert a Tales of Vesperia PS3 Save to PC Save",
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
