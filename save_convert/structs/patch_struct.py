"""
Contains classes used patch structures types from a save format
Primarily contains method for endian swapping structure data
when converting from a platform with big-endian save data(PS3/Wii)
to a platform using little-endian (most other platform in existence
i.e PC, PS1, PS3, PS4, PS5, NSW, all Xbox platforms)
"""

import logging
from ctypes import sizeof
from pathlib import Path
from typing import override

from save_convert.save_converter_base import (
    ConvertFormat,
    PatchBase,
    PatchOperationResult,
    PatchOperationState,
    Range,
)
from save_convert.structs.marshal_structure import ByteorderLiteral, EndianSwapStructure, OffsetField

LOGGER = logging.getLogger("patch_struct")
LOGGER.setLevel(logging.INFO)
stdoutHandler = logging.StreamHandler()
LOGGER.addHandler(stdoutHandler)

SCRIPT_NAME = Path(__file__).name


class PatchStructEndianSwap(PatchBase):
    """Replaces the bytes with represented by a structure
    with the endian swapped equivalent.

    As a structure is used only integer types with size >= 2 have there fields endian swapped
    string, byte buffers and 1-byte objects will maintain the same order
    This acts as a smart PatchEndianSwap class that knows how to swap a structure between 2 OS platforms
    of different endianess (Wii/PS3 and PC/PS4/PS5/NSW/XBOX)
    """

    offset_fields: OffsetField

    def __init__(
        self,
        target_offset: int,
        source_offset: int,
        struct_type: type[EndianSwapStructure],
        byteorder: ByteorderLiteral,
    ) -> None:
        self._struct_type: type[EndianSwapStructure] = struct_type
        self._byteorder: ByteorderLiteral = byteorder
        super().__init__(target_offset, Range(source_offset, source_offset + sizeof(self._struct_type)))

    @override
    def __call__(
        self,
        source_data: bytes,
        source_offset: int,
        _convert_format: ConvertFormat,
    ) -> PatchOperationResult:
        """Reads the source data into a user provided structure type and then
        serialize that structure type back out to binary using a different byte order
        """

        if source_offset != self._source_range.start:
            return PatchOperationResult(
                target_data=b"",
                target_write_offset=self._target_offset,
                new_source_offset=source_offset,
                patch_complete=PatchOperationState.Skip,
            )

        struct_inst: EndianSwapStructure = self._struct_type()
        if not struct_inst.from_bytes(
            memoryview(source_data)[source_offset : self._source_range.end], struct_inst, byteorder=self._byteorder
        ):
            # Could not load struct from bytes, so the patch operation has failed
            return PatchOperationResult(
                target_data=b"",
                target_write_offset=self._target_offset,
                new_source_offset=source_offset,
                patch_complete=PatchOperationState.Skip,
            )

        output_bytes = bytearray()
        inverted_byteorder: ByteorderLiteral = "little" if self._byteorder == "big" else "big"
        if not struct_inst.to_bytes(output_bytes, byteorder=inverted_byteorder):
            # Converting to bytes has failed, so skip the patch operation
            return PatchOperationResult(
                target_data=b"",
                target_write_offset=self._target_offset,
                new_source_offset=source_offset,
                patch_complete=PatchOperationState.Skip,
            )

        return PatchOperationResult(
            target_data=bytes(output_bytes),
            target_write_offset=self._target_offset,
            new_source_offset=self._source_range.end,
            patch_complete=PatchOperationState.Complete,
        )

    @override
    def generate_reverse_patch(self) -> PatchStructEndianSwap:
        """The reverse operation is the same form of load struct from bytes using
        specified endianess and store struct to bytes using opposite bytoerder
        However the byte order is value is inverted in this case
        """
        inverted_byteorder: ByteorderLiteral = "little" if self._byteorder == "big" else "big"
        return PatchStructEndianSwap(
            target_offset=self._source_range.start,
            source_offset=self._target_offset,
            struct_type=self._struct_type,
            byteorder=inverted_byteorder,
        )

    @override
    def get_target_covered_range(self) -> Range:
        return Range(self._target_offset, self._target_offset + sizeof(self._struct_type))
