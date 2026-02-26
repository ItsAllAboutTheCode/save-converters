"""Base structures for converting Trails of Cold Steel from PS3 to PC"""

import argparse
import bisect
import ctypes
import logging
import pathlib
import shutil
import tempfile
from abc import ABC, abstractmethod
from compression import zstd
from io import BytesIO
from typing import Any, cast, override

from save_convert.save_convert_base import (
    PC_TO_PS4_CONVERT_FORMAT,
    PS4_TO_PC_CONVERT_FORMAT,
    ConvertFormat,
    ReplaceMap,
    ReplaceResult,
    ReplaceState,
    SaveConvertBase,
)

logger = logging.getLogger("cold_steel_base_save_converter")
logger.setLevel(logging.INFO)
stdoutHandler = logging.StreamHandler()
logger.addHandler(stdoutHandler)

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
        logger.info(
            "File is not compressed using ZStandard. Skipping ZStandard decompression",
        )
        return input_data, False

    try:
        result_data = zstd.decompress(input_data)
    except zstd.ZstdError as err:
        logger.info(f"ZStandard decompressor raised error: {err}")
        return input_data, False

    logger.info("File was compressed using ZStandard. It has been successfully decompressed")
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
        logger.info(
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
        logger.info(
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
            logger.info(
                f"Offset in the decompression buffer {dec_offset} is larger than"
                f" the calcualated decompressed size {decompressed_size}\n"
                "The input data is assumed to be uncompressed",
            )
            return input_data, False

        if in_offset >= len(input_data):
            logger.info(
                f"Offset in the input_data buffer {in_offset} is greater than the loaded input save"
                f" {len(input_data)}\n"
                "The input data is assumed to be uncompressed",
            )
            return input_data, False

        input_byte = input_data[in_offset]
        in_offset += 1
        if input_byte == backref_int32:
            if in_offset >= len(input_data):
                logger.info(
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
                    logger.info(
                        "Back reference offset is 0, A compressed file should not have that value\n"
                        "The input data is assumed to be uncompressed",
                    )
                    return input_data, False
                if in_offset >= len(input_data):
                    logger.info(
                        f"Offset in the input_data buffer {in_offset} is greater than the loaded input save"
                        f" {len(input_data)}\n"
                        "The input data is assumed to be uncompressed",
                    )
                    return input_data, False

                backref_size = input_data[in_offset]
                in_offset += 1

                if backref_size > 0:
                    if dec_offset < backref_offset:
                        logger.info(
                            f"Back reference offset {backref_offset} is larger than than current decompression"
                            f" buffer offset {dec_offset}\n"
                            "The input data is assumed to be uncompressed",
                        )
                        return input_data, False
                    if dec_offset + backref_size > TRAILS_OF_MAX_DECOMPRESS_SIZE:
                        logger.info(
                            f"Decompression buffer offset + back reference bytes size {dec_offset + backref_offset}"
                            " would result in decompressed size larger than the max decompression size"
                            f" {TRAILS_OF_MAX_DECOMPRESS_SIZE}\nThe input data is assumed to be uncompressed",
                        )
                    if dec_offset + backref_size > decompressed_size:
                        logger.info(
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
        logger.info(
            "The complete decompression buffer size does not match the calculated decompressed size from the input file"
            f"\nexpected: {decompressed_size}, actual: {dec_offset}",
        )
        return input_data, False

    output_bytes = bytes(decompress_buffer)
    logger.info("File was compressed using Falcom Type1 algorithm. It has been successfully decompressed")
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


def process_input_savedata(
    offset: int,
    input_data: bytes,
    patch_set: list[ReplaceMap],
    current_patch_index: int,
    convert_format: ConvertFormat,
) -> ReplaceResult:
    """Process every 4 bytes(32-bits) of the input data to determine how it should be written to the output
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
    if patch_set:
        # Get the first smallest index > @offset
        lower_bound = bisect.bisect_left(
            patch_set,
            offset,
            lo=current_patch_index,
            key=lambda entry: entry.replace_functor.source_range.start,
        )

        if lower_bound != len(patch_set) and patch_set[lower_bound].replace_functor.source_range.start == offset:
            # If the offset is exactly equal to the lower_bound start offset, use that entry
            replace_index = lower_bound
        elif lower_bound > 0:
            # Otherwise check if the previous index replace entry end offset is >= offset
            if patch_set[lower_bound - 1].replace_functor.source_range.end >= offset:
                replace_index = lower_bound - 1

    if replace_index != -1:
        output_result = patch_set[replace_index].replace_functor(input_data, offset, convert_format)
        return output_result

    return ReplaceResult(data=b"", new_offset=offset, replace_complete=ReplaceState.Skip)


class SaveConvertColdSteelBase(SaveConvertBase, ABC):
    _input_path: pathlib.Path
    _output_path: pathlib.Path
    _convert_format: ConvertFormat
    _input_data: bytes
    _output_io: BytesIO

    def __init__(self, args: argparse.Namespace):
        super().__init__()
        self._input_path = cast("pathlib.Path", args.input)
        self._convert_format = cast("ConvertFormat", args.convert_format)
        output_path: pathlib.Path | None = args.output
        if not output_path:
            output_path = self._input_path.with_suffix(f"{self._input_path.suffix}.{self._convert_format.target}")
            logger.info(f"No Output path specified, it has been set to {output_path}")

        self._output_path = output_path

    @override
    def _pre_convert(self) -> bool:
        """Pre-load save data from the input file into memory"""
        # Read the entire save into memory
        with self._input_path.open("rb") as infile:
            try:
                self._input_data = decompress_savedata(infile.read())
            except BlockingIOError as err:
                logger.error(f"Unable to read data from input file {self._input_path}: {err}")
                return False

        return True

    @override
    def _convert(self) -> bool:
        """Iterates over the input save file, attempting byte replacements from the source save format
        in order to convert the target save format
        """
        self._output_io = BytesIO()  # Create a in-memory binary IO buffer for storing output data
        patch_set = self.create_save_patch_table(
            convert_format=self._convert_format,
        )
        patch_index = 0

        cur_offset = 0
        while cur_offset < len(self._input_data):
            result = process_input_savedata(
                offset=cur_offset,
                input_data=self._input_data,
                patch_set=patch_set,
                current_patch_index=patch_index,
                convert_format=self._convert_format,
            )

            try:
                if self._output_io.write(result.data) != len(result.data):
                    logger.error(
                        f"Unable to write {len(result.data)} bytes  to output. Input offset: {cur_offset}."
                        f" Output offset: {self._output_io.tell()}",
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
            patch_index += 1 if result.replace_complete else 0

        return True

    @override
    def _post_convert(self) -> bool:
        """Writes the output data to the destination file atomically"""
        # Now copy temporary output file to destination
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_output_path = pathlib.Path(f"{tmpdir}/{self._output_path.name}").resolve()
            with tmp_output_path.open("wb") as outfile:
                byte_buffer = self._output_io.getvalue()
                if outfile.write(byte_buffer) != len(byte_buffer):
                    raise IOError(f"Failed to write {len(byte_buffer)} to output file. Aborting...")
                self._output_io.close()
            return bool(shutil.move(tmp_output_path, self._output_path))

    @abstractmethod
    def create_save_patch_table(self, convert_format: ConvertFormat) -> list[ReplaceMap]:
        return []


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


class SaveConvertColdSteelChecksumBase(SaveConvertColdSteelBase, ABC):
    FILESIZE_OFFSET: int = 8
    CHECKSUM_OFFSET: int = FILESIZE_OFFSET + 4
    START_SAVEDATA_OFFSET: int = CHECKSUM_OFFSET + 4

    @override
    def _post_convert(self) -> bool:
        """Fixes the checksum for Trails of Cold Steel IV/Reverie"""
        byte_view = self._output_io.getbuffer()
        # The save checksum is calculated using the remaining filesize in the file
        # filesize = int.from_bytes(byte_view[self.FILESIZE_OFFSET : self.FILESIZE_OFFSET + 4], byteorder="little")
        filesize = len(byte_view)
        # Update filesize value
        byte_view[self.FILESIZE_OFFSET : self.FILESIZE_OFFSET + 4] = filesize.to_bytes(length=4, byteorder="little")
        savedata_size = filesize - self.START_SAVEDATA_OFFSET
        fixed_checksum = calc_crc32(byte_view[self.START_SAVEDATA_OFFSET :], savedata_size)
        # Update checksum value
        byte_view[self.CHECKSUM_OFFSET : self.CHECKSUM_OFFSET + 4] = fixed_checksum.to_bytes(
            length=4, byteorder="little"
        )
        byte_view.release()  # Allow the BytesIO object to be closed
        return super()._post_convert()


def add_argparse_commands(parser: argparse.ArgumentParser) -> None:
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
            else:
                raise ValueError(f"Value {values} is not an appropriate choice for argument {options_string}")

    parser.add_argument(  # pyright: ignore[reportUnusedCallResult]
        "--convert-format",
        "-f",
        action=ConvertFormatAction,
        choices=[str(PS4_TO_PC_CONVERT_FORMAT), str(PC_TO_PS4_CONVERT_FORMAT)],
        default=PS4_TO_PC_CONVERT_FORMAT,
        help="Specifies the input file save format and what should the output file format should be.",
    )
