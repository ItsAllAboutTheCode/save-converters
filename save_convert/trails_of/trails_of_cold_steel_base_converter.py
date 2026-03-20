"""Base structures for converting Trails of Cold Steel from PS3 to PC"""

import argparse
import ctypes
import logging
import pathlib
from abc import ABC
from compression import zstd
from io import BytesIO
from typing import Any, cast, override

from save_convert.save_converter_base import (
    PC_TO_PS4_CONVERT_FORMAT,
    PC_TO_PS5_CONVERT_FORMAT,
    PS4_TO_PC_CONVERT_FORMAT,
    PS5_TO_PC_CONVERT_FORMAT,
    SaveConvertBase,
)

LOGGER = logging.getLogger("cold_steel_base_save_converter")
LOGGER.setLevel(logging.INFO)
stdoutHandler = logging.StreamHandler()
LOGGER.addHandler(stdoutHandler)

# Reversed CRC32 polynomial used for checksuming Cold Steel IV and Reverie saves
TRAILS_OF_CRC32_POLYNOMIAL = 0xEDB88320

# 4 byte sequence at the beginning of a save file that indicates if the file is compressed
# using the zstandard algorithm
TRAILS_OF_ZSTD_MAGIC_BYTES = 0xFD2FB528

# The Decompressed file must have at least 12 bytes
# 4 for the decompressed file size, + 4 for the compressed savedata size
# + 4 for the back reference
TRAILS_OF_MIN_DECOMPRESS_SIZE = 12
# Restrict the check the max decompression size to 16 MiB
# The actual largest file size of a Trails of Cold Steel/Reverie is <2 MiB
TRAILS_OF_MAX_DECOMPRESS_SIZE = 2**24


def decompress_zstd(input_data: bytes) -> tuple[bytes, bool]:
    """Decompress ZSTD save data into memory
    This is done by checking if the input_data starts with the ZSTD magic bytes

    Returns a tuple of the (bytes to use for further processing, bool indicating if the bytes were decompressed)
    """
    in_offset = 0
    # Read the first 4 bytes from the input_data to see if it is compressing using ZStandard
    zstd_magic = int.from_bytes(input_data[in_offset : in_offset + 4], byteorder="little")
    in_offset += 4
    if zstd_magic != TRAILS_OF_ZSTD_MAGIC_BYTES:
        LOGGER.debug(
            "File is not compressed using ZStandard. Skipping ZStandard decompression",
        )
        return input_data, False

    try:
        result_data = zstd.decompress(input_data)
    except zstd.ZstdError as err:
        LOGGER.error(f"ZStandard decompressor raised error: {err}")
        return input_data, False

    LOGGER.debug("File was compressed using ZStandard. It has been successfully decompressed")
    return result_data, True


def decompress_type1(input_data: bytes) -> tuple[bytes, bool]:
    """Decompress Falcom Type 1 save data into memory
    Credit: AdmiralCurtiss SenPatcher `DecompressType1` method
    https://github.com/AdmiralCurtiss/SenPatcher/blob/0681f42665cee0945d17c11f6dc41156b0a06a7c/native/sen/pkg_extract.cpp#L17

    Returns a tuple of the (bytes to use for further processing, bool indicating if the bytes were decompressed)
    """

    in_offset = 0

    # Read the decompressed filesize from the first 4 bytes of the file
    decompressed_size = int.from_bytes(input_data[in_offset : in_offset + 4], byteorder="little")
    in_offset += 4
    if not (TRAILS_OF_MIN_DECOMPRESS_SIZE <= decompressed_size <= TRAILS_OF_MAX_DECOMPRESS_SIZE):
        LOGGER.debug(
            "Candidate decompressed size is not in the correct size range to be compressed."
            " The input data is assumed to be uncompressed",
        )
        return input_data, False

    decompress_buffer = ctypes.create_string_buffer(decompressed_size)

    dec_offset = 0

    # Read the compressed savedata size = 4 bytes
    compressed_buffer_size = int.from_bytes(input_data[in_offset : in_offset + 4], byteorder="little")
    in_offset += 4

    if compressed_buffer_size != len(input_data):
        LOGGER.debug(
            "Candidate compressed size in the input file does not match the size of the input data."
            " The input data is assumed to be uncompressed",
        )
        return input_data, False

    # Read the intger that indicates the start of a backwards reference to previously written uncompressed
    # bytes within the decompress stream
    backref_int32 = int.from_bytes(input_data[in_offset : in_offset + 4], byteorder="little")
    in_offset += 4

    while in_offset < compressed_buffer_size:
        if dec_offset >= decompressed_size:
            LOGGER.debug(
                f"Offset in the decompression buffer {dec_offset} is larger than"
                f" the calcualated decompressed size {decompressed_size}\n"
                "The input data is assumed to be uncompressed",
            )
            return input_data, False

        if in_offset >= len(input_data):
            LOGGER.debug(
                f"Offset in the input_data buffer {in_offset} is greater than the loaded input save"
                f" {len(input_data)}\n"
                "The input data is assumed to be uncompressed",
            )
            return input_data, False

        input_byte = input_data[in_offset]
        in_offset += 1
        if input_byte == backref_int32:
            if in_offset >= len(input_data):
                LOGGER.debug(
                    f"Offset in the input_data buffer {in_offset} is greater than the loaded input save"
                    f" {len(input_data)}\n"
                    "The input data is assumed to be uncompressed",
                )
                return input_data, False

            backref_offset = input_data[in_offset]
            in_offset += 1
            # Two back reference bytes in row acts as an escape value, in which case the data is copied directly
            if backref_offset == backref_int32:
                _ = ctypes.memset(ctypes.addressof(decompress_buffer) + dec_offset, input_byte, 1)
                dec_offset += 1
            else:
                if backref_offset > backref_int32:
                    backref_offset -= 1

                if backref_offset == 0:
                    LOGGER.debug(
                        "Back reference offset is 0, A compressed file should not have that value\n"
                        "The input data is assumed to be uncompressed",
                    )
                    return input_data, False
                if in_offset >= len(input_data):
                    LOGGER.debug(
                        f"Offset in the input_data buffer {in_offset} is greater than the loaded input save"
                        f" {len(input_data)}\n"
                        "The input data is assumed to be uncompressed",
                    )
                    return input_data, False

                backref_size = input_data[in_offset]
                in_offset += 1

                if backref_size > 0:
                    if dec_offset < backref_offset:
                        LOGGER.debug(
                            f"Back reference offset {backref_offset} is larger than than current decompression"
                            f" buffer offset {dec_offset}\n"
                            "The input data is assumed to be uncompressed",
                        )
                        return input_data, False
                    if dec_offset + backref_size > TRAILS_OF_MAX_DECOMPRESS_SIZE:
                        LOGGER.debug(
                            f"Decompression buffer offset + back reference bytes size {dec_offset + backref_offset}"
                            " would result in decompressed size larger than the max decompression size"
                            f" {TRAILS_OF_MAX_DECOMPRESS_SIZE}\nThe input data is assumed to be uncompressed",
                        )
                    if dec_offset + backref_size > decompressed_size:
                        LOGGER.debug(
                            f"Decompression buffer offset + back reference bytes size {dec_offset + backref_offset}"
                            f" would result in decompressed size larger than the calculated decompressed size"
                            f" {decompressed_size}\n"
                            "The input data is assumed to be uncompressed",
                        )
                    # At this point the copy the bytes from the decompression buffer
                    # from the back reference offset to the current decompression head offset
                    backref_data_start = dec_offset - backref_offset
                    _ = ctypes.memmove(
                        ctypes.addressof(decompress_buffer) + dec_offset,
                        ctypes.addressof(decompress_buffer) + backref_data_start,
                        backref_size,
                    )
                    # Advanced the decompression buffer by the amount of bytes copied from the back reference offset
                    dec_offset += backref_size

        else:
            _ = ctypes.memset(ctypes.addressof(decompress_buffer) + dec_offset, input_byte, 1)
            dec_offset += 1

    if dec_offset != decompressed_size:
        LOGGER.debug(
            "The complete decompression buffer size does not match the calculated decompressed size from the input file"
            f"\nexpected: {decompressed_size}, actual: {dec_offset}",
        )
        return input_data, False

    output_bytes = bytes(decompress_buffer)
    LOGGER.debug("File was compressed using Falcom Type1 algorithm. It has been successfully decompressed")
    return output_bytes, True


def decompress_savedata(input_data: bytes) -> bytes:
    # Check if the file is compressed using ZSTD
    # If so decompress it using ZSTD
    result_data: bytes
    decompression_result: bool
    result_data, decompression_result = decompress_zstd(input_data)
    if decompression_result:
        return result_data
    # Now try type 1 decompression
    result_data, decompression_result = decompress_type1(input_data)
    if decompression_result:
        return result_data

    return input_data


class SaveConvertColdSteelBase(SaveConvertBase, ABC):
    _decompress_only: bool  # Only perform decompress, no conversion

    @override
    def __init__(self, args: argparse.Namespace):
        super().__init__(args)

        # Parse decompression logic
        self._decompress_only = cast(bool, args.decompress_only)
        output_path: pathlib.Path | None = args.output
        if self._decompress_only and not output_path:
            self._output_path: pathlib.Path = self._input_path.with_suffix(f"{self._input_path.suffix}.dec")

    @override
    def _pre_convert(self) -> bool:
        if not super()._pre_convert():
            return False

        # Attempt to decompress the save data if it is compressed
        self._input_data: bytes = decompress_savedata(self._input_data)
        return True

    @override
    def _convert(self) -> bool:
        if self._decompress_only:
            # Copy decompress bytes to output buffer
            self._output_io: BytesIO = BytesIO()
            _ = self._output_io.write(self._input_data)
            return True
        return super()._convert()

    @override
    def _post_convert(self) -> bool:
        return super()._post_convert()


def build_crc_table(crc32_poly: int = TRAILS_OF_CRC32_POLYNOMIAL):
    """Calculate CRC32 for body starting at BODY_OFFSET, init with body length. Returns 4-byte little-endian."""
    table = [0] * 256
    for i in range(256):
        v = i
        for _ in range(8):
            v = (v >> 1) ^ crc32_poly if v & 1 else v >> 1
        table[i] = v
    return table


TRAILS_CRC32_CHECKSUM_TABLE = build_crc_table()


def calc_crc32(data: memoryview[int], init_value: int) -> int:
    crc = init_value
    for b in data:
        crc = TRAILS_CRC32_CHECKSUM_TABLE[(b ^ (crc & 0xFF))] ^ (crc >> 8)
    return crc


class SaveConvertColdSteelFilesizeBase(SaveConvertColdSteelBase, ABC):
    """
    Converter for Trails of Cold Steel III/IV/Reverie which updates the filesize at offset 0x08
    after conversion
    """

    FILESIZE_OFFSET: int = 8

    @override
    def _post_convert(self) -> bool:
        """Fixes the filesize for Trails of Cold Steel III/IV/Reverie"""
        byte_view = self._output_io.getbuffer()
        filesize = len(byte_view)
        # Update filesize value
        byte_view[self.FILESIZE_OFFSET : self.FILESIZE_OFFSET + 4] = filesize.to_bytes(length=4, byteorder="little")

        byte_view.release()  # Allow the BytesIO object to be closed
        return super()._post_convert()


class SaveConvertColdSteelChecksumBase(SaveConvertColdSteelFilesizeBase, ABC):
    """
    Converter for Trails of Cold Steel IV/Reverie which updates the checksum at offset 0x0C
    after conversion
    """

    CHECKSUM_OFFSET: int = SaveConvertColdSteelFilesizeBase.FILESIZE_OFFSET + 4
    START_SAVEDATA_OFFSET: int = CHECKSUM_OFFSET + 4

    @override
    def _post_convert(self) -> bool:
        """Fixes the checksum for Trails of Cold Steel IV/Reverie"""
        byte_view = self._output_io.getbuffer()
        # The save checksum is calculated using the remaining filesize in the file
        filesize = len(byte_view)
        savedata_size = filesize - self.START_SAVEDATA_OFFSET
        fixed_checksum = calc_crc32(byte_view[self.START_SAVEDATA_OFFSET :], init_value=savedata_size)
        # Update checksum value
        byte_view[self.CHECKSUM_OFFSET : self.CHECKSUM_OFFSET + 4] = fixed_checksum.to_bytes(
            length=4, byteorder="little"
        )
        byte_view.release()  # Allow the BytesIO object to be closed
        return super()._post_convert()


def add_argparse_commands(parser: argparse.ArgumentParser) -> None:
    # Add general arguments
    _ = parser.add_argument(
        "--input",
        "-i",
        type=pathlib.Path,
        help="Input path to save file",
        required=True,
    )
    _ = parser.add_argument(
        "--output",
        "-o",
        type=pathlib.Path,
        help="Output path to save file. Defaults to <input-file-path>.<target-format> if not specified",
    )

    class ConvertFormatAction(argparse.Action):
        def __init__(self, option_strings, dest, nargs=None, **kwargs):  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType]
            if nargs is not None:
                raise ValueError("nargs not allowed")
            super().__init__(option_strings, dest, **kwargs)  # pyright: ignore[reportUnknownArgumentType]

        @override
        def __call__(
            self,
            parser: argparse.ArgumentParser,
            namespace: argparse.Namespace,
            values: Any,
            options_string: str | None = None,
        ):
            if values == str(PS4_TO_PC_CONVERT_FORMAT):
                setattr(namespace, self.dest, PS4_TO_PC_CONVERT_FORMAT)
            elif values == str(PC_TO_PS4_CONVERT_FORMAT):
                setattr(namespace, self.dest, PC_TO_PS4_CONVERT_FORMAT)
            elif values == str(PS5_TO_PC_CONVERT_FORMAT):
                setattr(namespace, self.dest, PS5_TO_PC_CONVERT_FORMAT)
            elif values == str(PC_TO_PS5_CONVERT_FORMAT):
                setattr(namespace, self.dest, PC_TO_PS5_CONVERT_FORMAT)
            else:
                raise ValueError(f"Value {values} is not an appropriate choice for argument {options_string}")

    _ = parser.add_argument(
        "--convert-format",
        "-f",
        action=ConvertFormatAction,
        choices=[str(PS4_TO_PC_CONVERT_FORMAT), str(PC_TO_PS4_CONVERT_FORMAT)],
        default=PS4_TO_PC_CONVERT_FORMAT,
        help="Specifies the input file save format and what should the output file format should be.",
    )

    _ = parser.add_argument(
        "--decompress-only",
        "-d",
        action="store_true",
        help="Decompress the input file if compressed, does not perform format conversion.\n"
        "File extension will be <input-path>.dec if --output option is not set",
    )

    _ = parser.add_argument(
        "--log-level",
        "-l",
        default=logging.INFO,
        choices=logging.getLevelNamesMapping(),
        help="Set log level for converter",
    )
