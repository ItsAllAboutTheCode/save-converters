#!/usr/bin/env python
"""Script for converting the Tales of Vesperia PS3 save to PC save"""

import argparse
import logging
import pathlib
import struct
import sys
from typing import Any, cast, override

from save_convert.save_converter_base import (
    PC_TO_PS3_CONVERT_FORMAT,
    PS3_TO_PC_CONVERT_FORMAT,
    ConvertFormat,
    ConvertPatchTable,
    EndianSwapSize,
    PatchCopyBytes,
    PatchEndianSwap,
    PatchInsertAndSkipBytes,
    PatchInsertBytes,
    PatchOperationResult,
    PatchOperationState,
    PatchSet,
    Range,
    RangeNotCoveredException,
    SaveConvertBase,
    SaveFormat,
)
from save_convert.tales_of.vesperia.tales_of_vesperia_title_id_list import (
    VESPERIA_PC_TITLE_IDS,
    VESPERIA_PS3_TITLE_IDS,
)

LOGGER = logging.getLogger("vesperia_save_converter")
LOGGER.setLevel(logging.INFO)
stdoutHandler = logging.StreamHandler()
LOGGER.addHandler(stdoutHandler)


VESPERIA_PS3_SAVE_SIZE = 552 + 838304  # 552 byte save header + 838204 byte save data block
VESPERIA_PC_SAVE_SIZE = VESPERIA_PS3_SAVE_SIZE + 16  # The PC Save block is 16 bytes larger than PS3

VESPERIA_SAVE_SIZE_DICT: dict[SaveFormat, int] = {
    SaveFormat.PS3: VESPERIA_PS3_SAVE_SIZE,
    SaveFormat.PC: VESPERIA_PC_SAVE_SIZE,
}

# PC files have an extra 16(0x10) bytes aftet the CUSTOM_DATA block
VESPERIA_PS3_TO_PC_POST_CUSTOM_DATA_OFFSET = 0x10

# Stores the range offset of all the custom character name offsets in the PS3 save file
# Since the character names are strings, they should not be endian swapped
VESPERIA_FIRST_PC_OFFSET_PS3 = 0xA8928
VESPERIA_PC_BLOCK_SIZE = 16400
VESPERIA_NUM_CHARACTERS = 9
VESPERIA_CUSTOM_CHARACTER_NAME_OFFSET = 0x4
VESPERIA_CUSTOM_CHARACTER_NAME_BUFFER_SIZE = 64

VESPERIA_CUSTOM_CHARACTER_NAME_OFFSET_RANGES = (
    PatchCopyBytes(
        target_offset=VESPERIA_FIRST_PC_OFFSET_PS3
        + index * VESPERIA_PC_BLOCK_SIZE
        + VESPERIA_CUSTOM_CHARACTER_NAME_OFFSET
        + VESPERIA_PS3_TO_PC_POST_CUSTOM_DATA_OFFSET,
        source_range=Range(
            VESPERIA_FIRST_PC_OFFSET_PS3 + index * VESPERIA_PC_BLOCK_SIZE + VESPERIA_CUSTOM_CHARACTER_NAME_OFFSET,
            VESPERIA_FIRST_PC_OFFSET_PS3
            + index * VESPERIA_PC_BLOCK_SIZE
            + VESPERIA_CUSTOM_CHARACTER_NAME_OFFSET
            + VESPERIA_CUSTOM_CHARACTER_NAME_BUFFER_SIZE,
        ),
    )
    for index in range(VESPERIA_NUM_CHARACTERS)
)

## Title Section
# 15504 bytes into the PC character data for character 1 which would be 0xAC5B8 (PS3) 0xAC5C8 (PC)
VESPERIA_TITLE_BITFIELD_OFFSET = 0x3C90

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


class PatchObtainedTitles(PatchCopyBytes):
    @override
    def __call__(
        self,
        source_data: bytes,
        source_offset: int,
        convert_format: ConvertFormat,
    ) -> PatchOperationResult:
        # The offset must exactly match the beginning of the range to discover the all the titles
        if source_offset != self._source_range.start:
            return PatchOperationResult(
                target_data=b"",
                target_write_offset=self._target_offset,
                new_source_offset=source_offset,
                patch_complete=PatchOperationState.Skip,
            )

        TITLE_PACK_STRIDE = 4  # 32-bits per title bitfield
        TITLE_PACK_BITS = TITLE_PACK_STRIDE * 8
        obtained_titles: set[int] = set()

        for title_bitfield_offset in range(source_offset, self._source_range.end, TITLE_PACK_STRIDE):
            # The Title list also needs to be endian swapped as well
            title_bitfield = int.from_bytes(
                bytes=source_data[title_bitfield_offset : title_bitfield_offset + TITLE_PACK_STRIDE],
                byteorder="big" if convert_format.source == SaveFormat.PS3 else "little",
            )
            for title_bit in range(TITLE_PACK_BITS):
                if (title_bitfield >> title_bit) & 1:
                    obtained_titles.add((title_bitfield_offset - source_offset) * 8 + title_bit)

        platform_title_list = (
            VESPERIA_PS3_TITLE_IDS if convert_format.target == SaveFormat.PS3 else VESPERIA_PC_TITLE_IDS
        )
        invalid_titles: set[int] = set()
        for title in obtained_titles:
            title_name: str | None = platform_title_list.get(title)
            # Explicitly check against None as the first title value is to an empty string
            if title_name is None:
                invalid_titles.add(title)

        if invalid_titles:
            char_index = (
                source_offset - VESPERIA_FIRST_PC_OFFSET_PS3 - VESPERIA_TITLE_BITFIELD_OFFSET
            ) // VESPERIA_PC_BLOCK_SIZE
            LOGGER.info(
                f"Character {char_index} has invalid titles obtained at bits: {invalid_titles}"
                f" from offset 0x{source_offset:X}\n"
                "Invalid titles will set to 0 (not obtained)",
            )

        output_title_array: list[int] = [0] * (VESPERIA_TITLE_BITFIELD_SIZE // TITLE_PACK_STRIDE)
        valid_titles = obtained_titles - invalid_titles
        for title in valid_titles:
            output_title_array[title // TITLE_PACK_BITS] |= 1 << title % TITLE_PACK_BITS

        # Pack the title: int[15] array into bytes taking into account the endianess of the output format
        struct_format = f"{'<' if convert_format.target != SaveFormat.PS3 else '>'}{len(output_title_array)}I"
        output_data = struct.pack(struct_format, *output_title_array)

        return PatchOperationResult(
            target_data=output_data,
            target_write_offset=self._target_offset,
            new_source_offset=self._source_range.end,
            patch_complete=PatchOperationState.Complete,
        )

    @override
    def generate_reverse_patch(self) -> PatchObtainedTitles:
        """Reverse operation of an Endian Swap replaces the source range start with the target offset
        and the target_offset with the source range start
        """
        return PatchObtainedTitles(
            target_offset=self._source_range.start,
            source_range=Range(self._target_offset, self._target_offset + len(self._source_range)),
        )

    @override
    def get_target_covered_range(self) -> Range:
        return Range(self._target_offset, self._target_offset + len(self._source_range))


VESPERIA_CHARACTER_OBTAINED_TITLE_OFFSET_RANGES = (
    PatchObtainedTitles(
        target_offset=VESPERIA_FIRST_PC_OFFSET_PS3
        + index * VESPERIA_PC_BLOCK_SIZE
        + VESPERIA_TITLE_BITFIELD_OFFSET
        + VESPERIA_PS3_TO_PC_POST_CUSTOM_DATA_OFFSET,
        source_range=Range(
            VESPERIA_FIRST_PC_OFFSET_PS3 + index * VESPERIA_PC_BLOCK_SIZE + VESPERIA_TITLE_BITFIELD_OFFSET,
            VESPERIA_FIRST_PC_OFFSET_PS3
            + index * VESPERIA_PC_BLOCK_SIZE
            + VESPERIA_TITLE_BITFIELD_OFFSET
            + VESPERIA_TITLE_BITFIELD_SIZE,
        ),
    )
    for index in range(VESPERIA_NUM_CHARACTERS)
)

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
# Looking through the item list for the games normal items the highest value is 1237, so it is guessed that this is
# where the DLC items start
#
# Based on the number of 32-bit bitfields being check 0x31 thru 0x3D which is 52 bytes total,
# plus the fact that these types of fields tend to be 16 byte aligned, the stride of this check offset will be assumed
# to be 64 bytes(16 int sized bitfields)

VESPERIA_PS3_DLC_ITEM_CHECK_OFFSET = 0xA7E00
VESPERIA_PC_DLC_ITEM_CHECK_OFFSET = VESPERIA_PS3_DLC_ITEM_CHECK_OFFSET + VESPERIA_PS3_TO_PC_POST_CUSTOM_DATA_OFFSET
VESPERIA_DLC_ITEM_CHECK_STRIDE = 64
VESPERIA_DLC_ITEM_CHECK_OFFSET_DICT = {
    SaveFormat.PS3: VESPERIA_PS3_DLC_ITEM_CHECK_OFFSET,
    SaveFormat.PC: VESPERIA_PC_DLC_ITEM_CHECK_OFFSET,
}


class SaveConvertVesperia(SaveConvertBase):
    _patch_dlc_checks: bool

    def __init__(self, args: argparse.Namespace):
        self._patch_dlc_checks = cast("bool", args.patch_dlc_item_checks)
        super().__init__(args)

    @override
    def _pre_transform(self) -> bool:
        return super()._pre_transform()

    @override
    def _transform(self) -> bool:
        return super()._transform()

    @override
    def _post_transform(self) -> bool:
        return super()._post_transform()

    @override
    def create_save_patch_table(self) -> ConvertPatchTable:
        """Returns a dictionary of offset -> byte array entries that indicates which
        actions should be performed when an address is encountered from the input save

        :param: patch_dlc_item_checks - If True, replaces the DLC obtained item bits from the save file to be unobtained
        This should allow bypassing being unable to load the save due to DLC
        """
        # START Replace Offset Table populate
        new_patch_table: ConvertPatchTable = ConvertPatchTable(
            convert_format_to_patch_set={}, save_format_to_save_size_dict=VESPERIA_SAVE_SIZE_DICT
        )
        new_patch_table.convert_format_to_patch_set[PS3_TO_PC_CONVERT_FORMAT] = PatchSet(
            patch_entries=[
                # Replaces the PS3 save header with a working PC save
                # Replace the save block filesize from the PS3 file which is big-endian: 00 0C CA A0 = 838304 bytes
                # With the PC save block size in little-endian: B0 CA 0C 00 = 838320 bytes
                PatchInsertAndSkipBytes(
                    target_offset=0x0C,
                    source_offset=0x0C,
                    output_bytes=bytes([0xB0, 0xCA, 0x0C, 0x00]),
                    reverse_output_bytes=bytes([0x00, 0x0C, 0xCA, 0xA0]),
                ),
                # The date value is stored as a 64-bit seconds since the epoch value (1970-01-01)
                # https://docs.python.org/3/library/datetime.html#datetime.datetime.timestamp
                # Additional info: Playtime is stored 1/60 seconds at offset 0x14,
                # Gald is stored at offset 0x20
                PatchEndianSwap(target_offset=0x18, source_range=Range(0x18, 0x20), swap_size=EndianSwapSize.Size64Bit),
                # Skip swapping the "TO8SAVE" magic bytes
                PatchCopyBytes(target_offset=0x228, source_range=Range(0x228, 0x230)),
                # According to HyoutaTools SaveData research:
                # https://github.com/AdmiralCurtiss/HyoutaTools/blob/33f1e42a6efc5c386c654656c2b21991d58fdedb/HyoutaToolsLib/Tales/Vesperia/SaveData/SaveData.cs#L42
                # This offset contains the size of the save data minus the header 552 (0x228).
                # The PC Save size should be (838872 - 552) = 838320 (in little endian)
                # On PS3 this value is set to 838304 (big endian)
                PatchInsertAndSkipBytes(
                    target_offset=0x230,
                    source_offset=0x230,
                    output_bytes=bytes([0xB0, 0xCA, 0x0C, 0x00]),
                    reverse_output_bytes=bytes([0x00, 0x0C, 0xCA, 0xA0]),
                ),
                # Offset where reference strings start in the Save Data
                # Needs to be increased by 0x10 hex to account for the added bytes from PS3 to PC
                # https://github.com/AdmiralCurtiss/HyoutaTools/blob/33f1e42a6efc5c386c654656c2b21991d58fdedb/HyoutaToolsLib/Tales/Vesperia/SaveData/SaveData.cs#L47
                PatchInsertAndSkipBytes(
                    target_offset=0x254,
                    source_offset=0x254,
                    output_bytes=bytes([0xA0, 0xC9, 0x0C, 0x00]),
                    reverse_output_bytes=bytes([0x00, 0x0C, 0xC9, 0x90]),
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
                PatchInsertAndSkipBytes(
                    target_offset=0x44C,
                    source_offset=0x44C,
                    output_bytes=bytes([0x90, 0x32, 0x00, 0x00]),
                    reverse_output_bytes=bytes([0x00, 0x00, 0x32, 0x80]),
                ),
                # SavePoint block size = 1024
                # Starts at offset (PC file:0x628 + 13488 = 0x3AD8, PS3 file:0x628 + 13472 = 0x3AC8
                #                   PC save:0x400 + 13488 = 0x38B0, PS3 save:0x400 + 13472 = 0x38A0
                PatchInsertAndSkipBytes(
                    target_offset=0x46C,
                    source_offset=0x46C,
                    output_bytes=bytes([0xB0, 0x34, 0x00, 0x00]),
                    reverse_output_bytes=bytes([0x00, 0x00, 0x34, 0xA0]),
                ),
                # MG2Poker block size = 128
                # Starts at offset (PC file:0x628 + 14512 = 0x3ED8, PS3 file:0x628 + 14496 = 0x3EC8
                #                   PC save:0x400 + 14512 = 0x3CB0, PS3 save:0x400 + 14496 = 0x3CA0)
                PatchInsertAndSkipBytes(
                    target_offset=0x48C,
                    source_offset=0x48C,
                    output_bytes=bytes([0xB0, 0x38, 0x00, 0x00]),
                    reverse_output_bytes=bytes([0x00, 0x00, 0x38, 0xA0]),
                ),
                # SnowBoard block size = 655360
                # Starts at offset (PC file:0x628 + 14640 = 0x3F58, PS3 file:0x628 + 14624 = 0x3F48
                #                   PC save:0x400 + 14640 = 0x3D30, PS3 save:0x400 + 14624 = 0x3D20
                PatchInsertAndSkipBytes(
                    target_offset=0x4AC,
                    source_offset=0x4AC,
                    output_bytes=bytes([0x30, 0x39, 0x00, 0x00]),
                    reverse_output_bytes=bytes([0x00, 0x00, 0x39, 0x20]),
                ),
                # PARTY_DATA block size = 18904
                # Starts at offset (PC file:0x628 + 670000 = 0xA3F58, PS3 file:0x628 + 669984 = 0xA3F48
                #                   PC save:0x400 + 670000 = 0xA3D30, PS3 save:0x400 + 669984 = 0xA3D20
                PatchInsertAndSkipBytes(
                    target_offset=0x4CC,
                    source_offset=0x4CC,
                    output_bytes=bytes([0x30, 0x39, 0x0A, 0x00]),
                    reverse_output_bytes=bytes([0x00, 0x0A, 0x39, 0x20]),
                ),
                # PC_STATUS1 block size = 16400
                # Starts at offset (PC file:0x628 + 688912 = 0xA8938, PS3 file:0x628 + 688896 = 0xA8928
                #                   PC save:0x400 + 688912 = 0xA8710, PS3 save:0x400 + 688896 = 0xA8700
                PatchInsertAndSkipBytes(
                    target_offset=0x4EC,
                    source_offset=0x4EC,
                    output_bytes=bytes([0x10, 0x83, 0x0A, 0x00]),
                    reverse_output_bytes=bytes([0x00, 0x0A, 0x83, 0x00]),
                ),
                # PC_STATUS2 block size = 16400
                # Starts at offset (PC file:0x628 + 705312 = 0xAC948, PS3 file:0x628 + 705296 = 0xAC938
                #                   PC save:0x400 + 705312 = 0xAC720, PS3 save:0x400 + 705296 = 0xAC710
                PatchInsertAndSkipBytes(
                    target_offset=0x50C,
                    source_offset=0x50C,
                    output_bytes=bytes([0x20, 0xC3, 0x0A, 0x00]),
                    reverse_output_bytes=bytes([0x00, 0x0A, 0xC3, 0x10]),
                ),
                # PC_STATUS3 block size = 16400
                # Starts at offset (PC file:0x628 + 721712 = 0xB0958, PS3 file:0x628 + 721696 = 0xB0948
                #                   PC save:0x400 + 721712 = 0xB0730, PS3 save:0x400 + 721696 = 0xB0720
                PatchInsertAndSkipBytes(
                    target_offset=0x52C,
                    source_offset=0x52C,
                    output_bytes=bytes([0x30, 0x03, 0x0B, 0x00]),
                    reverse_output_bytes=bytes([0x00, 0x0B, 0x03, 0x20]),
                ),
                # PC_STATUS4 block size = 16400
                # Starts at offset (PC file:0x628 + 738112 = 0xB4968, PS3 file:0x628 + 738096 = 0xB4958
                #                   PC save:0x400 + 738112 = 0xB4740, PS3 save:0x400 + 738096 = 0xB4730
                PatchInsertAndSkipBytes(
                    target_offset=0x54C,
                    source_offset=0x54C,
                    output_bytes=bytes([0x40, 0x43, 0x0B, 0x00]),
                    reverse_output_bytes=bytes([0x00, 0x0B, 0x43, 0x30]),
                ),
                # PC_STATUS5 block size = 16400
                # Starts at offset (PC file:0x628 + 754512 = 0xB8978, PS3 file:0x628 + 754496 = 0xB8968
                #                   PC save:0x400 + 754512 = 0xB8750, PS3 save:0x400 + 754496 = 0xB8740
                PatchInsertAndSkipBytes(
                    target_offset=0x56C,
                    source_offset=0x56C,
                    output_bytes=bytes([0x50, 0x83, 0x0B, 0x00]),
                    reverse_output_bytes=bytes([0x00, 0x0B, 0x83, 0x40]),
                ),
                # PC_STATUS6 block size = 16400
                # Starts at offset (PC file:0x628 + 770912 = 0xBC988, PS3 file:0x628 + 770896 = 0xBC978
                #                   PC save:0x400 + 770912 = 0xBC760, PS3 save:0x400 + 770896 = 0xBC750
                PatchInsertAndSkipBytes(
                    target_offset=0x58C,
                    source_offset=0x58C,
                    output_bytes=bytes([0x60, 0xC3, 0x0B, 0x00]),
                    reverse_output_bytes=bytes([0x00, 0x0B, 0xC3, 0x50]),
                ),
                # PC_STATUS7 block size = 16400
                # Starts at offset (PC file:0x628 + 787312 = 0xC0998, PS3 file:0x628 + 787296 = 0xC0988
                #                   PC save:0x400 + 787312 = 0xC0770, PS3 save:0x400 + 787296 = 0xC0760
                PatchInsertAndSkipBytes(
                    target_offset=0x5AC,
                    source_offset=0x5AC,
                    output_bytes=bytes([0x70, 0x03, 0x0C, 0x00]),
                    reverse_output_bytes=bytes([0x00, 0x0C, 0x03, 0x60]),
                ),
                # PC_STATUS8 block size = 16400
                # Starts at offset (PC file:0x628 + 803712 = 0xC49A8, PS3 file:0x628 + 803696 = 0xC4998
                #                   PC save:0x400 + 803712 = 0xC4780, PS3 save:0x400 + 803696 = 0xC4770
                PatchInsertAndSkipBytes(
                    target_offset=0x5CC,
                    source_offset=0x5CC,
                    output_bytes=bytes([0x80, 0x43, 0x0C, 0x00]),
                    reverse_output_bytes=bytes([0x00, 0x0C, 0x43, 0x70]),
                ),
                # PC_STATUS9 block size = 16400
                # Starts at offset (PC file:0x628 + 820112 = 0xC89B8, PS3 file:0x628 + 820096 = 0xC89A8
                #                   PC save:0x400 + 820112 = 0xC8790, PS3 save:0x400 + 820096 = 0xC8780
                PatchInsertAndSkipBytes(
                    target_offset=0x5EC,
                    source_offset=0x5EC,
                    output_bytes=bytes([0x90, 0x83, 0x0C, 0x00]),
                    reverse_output_bytes=bytes([0x00, 0x0C, 0x83, 0x80]),
                ),
                # FieldGadget block size = 512
                # Starts at offset (PC file:0x628 + 836512 = 0xCC9C8, PS3 file:0x628 + 836496 = 0xCC9B8
                #                   PC save:0x400 + 836512 = 0xCC7A0, PS3 save:0x400 + 836496 = 0xCC790
                PatchInsertAndSkipBytes(
                    target_offset=0x60C,
                    source_offset=0x60C,
                    output_bytes=bytes([0xA0, 0xC3, 0x0C, 0x00]),
                    reverse_output_bytes=bytes([0x00, 0x0C, 0xC3, 0x90]),
                ),
                # Map location is a string, so don't swap it
                PatchCopyBytes(target_offset=0x668, source_range=Range(0x668, 0x670)),
                # Weather condition is a string
                PatchCopyBytes(target_offset=0x688, source_range=Range(0x688, 0x690)),
                # Another string that is set "default"
                PatchCopyBytes(target_offset=0xC30, source_range=Range(0xC30, 0xC38)),
                # The data here appears to be packed tightly without swaps
                PatchCopyBytes(target_offset=0x1728, source_range=Range(0x1728, 0x1828)),
                # The Field Camera and Field Areas sections appear to only contain string data
                PatchCopyBytes(target_offset=0x1A90, source_range=Range(0x1A90, 0x1F00)),
                # Insert 16 bytes at the end of the CUSTOM_DATA section to align the Sound Theater data on PC at
                # The PS3 input offset would be at 0x38A8
                PatchInsertBytes(target_offset=0x38A8, source_offset=0x38A8, output_bytes=bytes([0x0] * 16)),
                # SavePoint data should not be endian swapped
                PatchCopyBytes(
                    target_offset=0x3AC8 + VESPERIA_PS3_TO_PC_POST_CUSTOM_DATA_OFFSET,
                    source_range=Range(0x3AC8, 0x3AC8 + 1024),
                ),
                # Custom Battle Strategy names are strings
                PatchCopyBytes(
                    target_offset=0xA7160 + VESPERIA_PS3_TO_PC_POST_CUSTOM_DATA_OFFSET,
                    source_range=Range(0xA7160, 0xA7160 + 0x40 * 8),
                ),
                # Copy any custom character names without endian swaps
                *VESPERIA_CUSTOM_CHARACTER_NAME_OFFSET_RANGES,
                # Remove any titles that are invalid
                *VESPERIA_CHARACTER_OBTAINED_TITLE_OFFSET_RANGES,
                # Section Name data at the end of the save are strings
                PatchCopyBytes(
                    target_offset=0xCCBB8 + VESPERIA_PS3_TO_PC_POST_CUSTOM_DATA_OFFSET,
                    source_range=Range(0xCCBB8, 0xCCCC8),
                ),
            ]
        )
        # END Replace Offset Table populate

        # Fill the Replace table for each uncovered offset range in the patch table
        # The mapping functor will perform a direct copy of the save data from the input file to the output file.
        for convert_patch_table_key, patch_set in new_patch_table.convert_format_to_patch_set.items():
            ## Add the dlc item check patch range entry
            if self._patch_dlc_checks:
                dlc_check_start = VESPERIA_DLC_ITEM_CHECK_OFFSET_DICT.get(convert_patch_table_key.source, sys.maxsize)
                # Patch the bytes starting at the DLC_ITEM check offset with 64 zeros
                patch_set.add_patch_entry(
                    PatchInsertAndSkipBytes(
                        target_offset=dlc_check_start + VESPERIA_PS3_TO_PC_POST_CUSTOM_DATA_OFFSET,
                        source_offset=dlc_check_start,
                        output_bytes=bytes(VESPERIA_DLC_ITEM_CHECK_STRIDE),
                    )
                )

        # Generate the reverse mmapping
        new_patch_table.convert_format_to_patch_set[PC_TO_PS3_CONVERT_FORMAT] = (
            new_patch_table.convert_format_to_patch_set[PS3_TO_PC_CONVERT_FORMAT].generate_reverse_set()
        )
        new_patch_table.fill_uncovered_target_offset_ranges(
            lambda target_offset, source_range: PatchEndianSwap(
                target_offset, source_range, swap_size=EndianSwapSize.Size32Bit
            )
        )
        valid, error_messages = new_patch_table.validate()
        if not valid:
            raise RangeNotCoveredException("\n".join(error_messages))

        return new_patch_table


### Start of argument parser setup
def start_convert(args: argparse.Namespace):
    if hasattr(args, "log_level"):
        LOGGER.setLevel(args.log_level)
    save_converter = SaveConvertVesperia(args)
    return save_converter.transform()


def add_commands(parser: argparse.ArgumentParser) -> None:
    parser.description = "Save Converter (PS3<->PC) for Tales of Vesperia"
    # Add general connection arguments
    parser.add_argument(  # pyright: ignore[reportUnusedCallResult]
        "--input",
        "-i",
        type=pathlib.Path,
        help="Input path to save file",
        required=True,
    )
    parser.add_argument(  # pyright: ignore[reportUnusedCallResult]
        "--output",
        "-o",
        type=pathlib.Path,
        help="Output path to save file. Defaults to <input-file-path>.<target-format> if not specified",
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
            if values == str(PS3_TO_PC_CONVERT_FORMAT):
                setattr(namespace, self.dest, PS3_TO_PC_CONVERT_FORMAT)
            elif values == str(PC_TO_PS3_CONVERT_FORMAT):
                setattr(namespace, self.dest, PC_TO_PS3_CONVERT_FORMAT)
            else:
                raise ValueError(f"Value {values} is not an appropriate choice for argument {options_string}")

    parser.add_argument(  # pyright: ignore[reportUnusedCallResult]
        "--convert-format",
        "-f",
        action=ConvertFormatAction,
        choices=[str(PS3_TO_PC_CONVERT_FORMAT), str(PC_TO_PS3_CONVERT_FORMAT)],
        default=PS3_TO_PC_CONVERT_FORMAT,
        help="Specifies the input file save format and what should the output file format should be."
        " Only PS3 and PC supported at this time",
    )

    parser.add_argument(  # pyright: ignore[reportUnusedCallResult]
        "--patch-dlc-item-checks",
        "-p",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Patches the DLC item obtained bytes from the save file to allow the saves with incompatible DLC"
        " to be loaded (Default=True)",
    )
    parser.set_defaults(func=start_convert)


def main():
    parser = argparse.ArgumentParser(
        description="Tool to convert a Tales of Vesperia PS3 Save to PC Save",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    _ = parser.add_argument(
        "--log-level",
        "-l",
        default=logging.INFO,
        choices=logging.getLevelNamesMapping(),
        help="Set log level for converter",
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
