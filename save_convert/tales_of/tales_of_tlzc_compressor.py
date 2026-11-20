"""
Contains TLZC Compression and Decompression algorithm adapted from HyoutaTools
https://github.com/AdmiralCurtiss/HyoutaTools/blob/master/HyoutaToolsLib/Tales/tlzc/TLZC.cs

NOTE: Python builtin lzma seems to be broken when using the FORMAT_RAW. Using pylzma instead
The result of the decompression is always an empty byte buffer that consumes the entire stream
Filters requires an ID specifying the compression format
"""

import logging
import sys
import zlib
from ctypes import c_uint8, c_uint32, sizeof
from enum import IntEnum, StrEnum
from pathlib import Path

import pylzma  #  type: ignore[import-not-found]

from save_convert.structs.marshal_struct_base import assert_struct_no_padding
from save_convert.structs.marshal_structure import FillEndianSwapStructure, OffsetField

SCRIPT_DIR: Path = Path(__file__).parent.resolve()

LOGGER = logging.getLogger("tlzc_compressor")
LOGGER.addHandler(logging.StreamHandler(sys.stdout))
LOGGER.setLevel(logging.INFO)

TALES_OF_TLZC_MAGIC_BYTE = "TLZC"
COMPRESSION_INPUT_MAX_SIZE = 2**32 - 1

LZMA_DICT_SIZE = 0x10000
LZMA_DICT_SIZE_BITS = 16


class CompressionType(IntEnum):
    ZLIB = 2
    LZMA = 4


class CompressionSubType(StrEnum):
    DEFLATE = "deflate"
    ZLIB = "zlib"


class CompressionHeader(FillEndianSwapStructure):  #  type: ignore[metaclass]
    _size_ = 0x18
    _offset_fields_ = [
        OffsetField(0x0, ("magic_bytes", (c_uint8 * 4))),
        OffsetField(0x4, ("__always_one__", (c_uint8))),
        OffsetField(0x5, ("compression_type", (c_uint8))),
        OffsetField(0x6, ("__padding1__", (c_uint8 * 2))),
        OffsetField(0x8, ("compressed_size", (c_uint32))),
        OffsetField(0xC, ("uncompressed_size", (c_uint32))),
        OffsetField(0x10, ("__always_zero", (c_uint8 * 8))),
    ]


assert_struct_no_padding(CompressionHeader)


class LZMAFilters(FillEndianSwapStructure):  #  type: ignore[metaclass]
    _size_ = 0x5
    _offset_fields_ = [OffsetField(0x0, ("bit_values", c_uint8)), OffsetField(0x1, ("dict_size", c_uint8 * 4))]


assert_struct_no_padding(LZMAFilters)


def can_decompress_tlzc(input_data: memoryview) -> bool:
    tlzc_magic = input_data[0:4].tobytes().decode("utf-8")
    return tlzc_magic == TALES_OF_TLZC_MAGIC_BYTE


def tlzc_decompress(
    input_data: memoryview,
    compression_type: CompressionType | None = None,
    compression_sub_type: CompressionSubType | None = None,
) -> tuple[bytes, bool]:
    if len(input_data) < sizeof(CompressionHeader):
        LOGGER.error(
            f"Input buffer is missing compression header. It must be at least {sizeof(CompressionHeader)} bytes"
        )
        return bytes(input_data), False

    compression_header_result = CompressionHeader.from_bytes(
        input_data[0 : sizeof(CompressionHeader)], CompressionHeader, byteorder="little"
    )
    if not compression_header_result.value:
        LOGGER.error("Failed to read Compression header from compressed buffer")
        return bytes(input_data), False

    compression_header = compression_header_result.value
    if bytes(compression_header.magic_bytes) != TALES_OF_TLZC_MAGIC_BYTE.encode("utf-8"):
        LOGGER.error("Beginning of input buffer is missing TLZC header")
        return bytes(input_data), False

    remaining_data = input_data[sizeof(compression_header) :]
    if compression_header.compressed_size != len(remaining_data):
        LOGGER.error(
            "Compressed size is not equal to remaining input buffer size after the compressed header"
            + f"Compressed size={compression_header.compressed_size}, Remaining buffer size={len(remaining_data)}"
        )
        return bytes(input_data), False

    # The compression type is in byte 5th byte of the buffer
    compression_type = compression_type or CompressionType(compression_header.compression_type)
    match compression_type:
        case CompressionType.ZLIB:
            return decompress_zlib(
                remaining_data,
                compression_sub_type,
            )
        case CompressionType.LZMA:
            return decompress_lzma(remaining_data, compression_header.uncompressed_size)
        case _:
            msg = f"Unknown compression type: {compression_type}"
            LOGGER.error(msg)
            raise ValueError(msg)


def decompress_zlib(
    compressed_data: memoryview,
    compression_sub_type: CompressionSubType | None,
) -> tuple[bytes, bool]:

    match compression_sub_type:
        case CompressionSubType.ZLIB:
            return decompress_zlib_zlib(compressed_data)
        case CompressionSubType.DEFLATE:
            return decompress_zlib_deflate(compressed_data)
        case _:
            # If no compression sub type has been provided try both zlib decompression algorithms
            decompress_result = decompress_zlib_zlib(compressed_data)
            if not decompress_result[1]:
                decompress_result = decompress_zlib_deflate(compressed_data)
            return decompress_result


def decompress_zlib_zlib(
    compressed_data: memoryview,
) -> tuple[bytes, bool]:
    try:
        output_data = zlib.decompress(compressed_data)
    except zlib.error as err:
        LOGGER.error(f"Compression of input buffer using ZLIB algorithm has failed with error: {err}")
        return bytes(compressed_data), False

    return output_data, True


def decompress_zlib_deflate(
    compressed_data: memoryview,
) -> tuple[bytes, bool]:
    try:
        deflate_decompressor = zlib.decompressobj()
        output_data = bytearray(deflate_decompressor.decompress(compressed_data))
    except zlib.error as err:
        LOGGER.error(f"Compression of input buffer using ZLIB algorithm has failed with error: {err}")
        return bytes(compressed_data), False

    return bytes(output_data), True


def decompress_lzma(
    compressed_data: memoryview,
    uncompressed_size: int,
) -> tuple[bytes, bool]:

    # The compressed data was written in 64KiB chunks, so calculate the number of chunks
    chunk_count = (uncompressed_size + 0xFFFF) >> 16
    lzma_filter_bytes = bytes(compressed_data[: sizeof(LZMAFilters)])

    compressed_payload_data = compressed_data[len(lzma_filter_bytes) :]
    chunk_size_array = list[int]()
    for _ in range(chunk_count):
        chunk_size_array.append(int.from_bytes(compressed_payload_data[:2], byteorder="little"))
        compressed_payload_data = compressed_payload_data[2:]

    uncompressed_bytes_left = uncompressed_size
    output_data = bytearray()
    for chunk_size in chunk_size_array:
        decompressed_chunk_size = min(uncompressed_bytes_left, LZMA_DICT_SIZE)
        if chunk_size != 0:
            try:
                decompressed_slice = pylzma.decompress(
                    lzma_filter_bytes + compressed_payload_data[:chunk_size], maxlength=decompressed_chunk_size
                )
            except (TypeError, ValueError) as err:
                LOGGER.error(f"Error occurred when decompressing input buffer using LZMA algorithm: {err}")
                return bytes(compressed_data), False

            output_data.extend(decompressed_slice)
        else:
            # When the chunk size is 0, the data was stored uncompressed, so copy it as is
            output_data.extend(compressed_payload_data[:decompressed_chunk_size])
        uncompressed_bytes_left -= decompressed_chunk_size
        compressed_payload_data = compressed_payload_data[chunk_size:]

    return bytes(output_data), True


def tlzc_compress(
    input_data: memoryview,
    compression_type: CompressionType,
    compression_sub_type: CompressionSubType | None = None,
    num_fast_bytes: int = 64,
) -> tuple[bytes, bool]:
    match compression_type:
        case CompressionType.ZLIB:
            return compress_zlib(input_data, compression_sub_type)
        case CompressionType.LZMA:
            return compress_lzma(input_data, num_fast_bytes)
        case _:
            msg = f"Unknown compression type: {compression_type}"
            LOGGER.error(msg)
            raise ValueError(msg)


def compress_zlib(input_data: memoryview, compression_sub_type: CompressionSubType | None) -> tuple[bytes, bool]:
    if len(input_data) > COMPRESSION_INPUT_MAX_SIZE:
        LOGGER.error(
            f"The input_data has a size {len(input_data)} greater than the max compression input size of"
            + f" {COMPRESSION_INPUT_MAX_SIZE}.\nCompression will not occur"
        )
        return bytes(input_data), False

    # Use Zlib if the compression type is not set
    if compression_sub_type is None or compression_sub_type != CompressionSubType.DEFLATE:
        compression_sub_type = CompressionSubType.ZLIB

    if compression_sub_type == CompressionSubType.ZLIB:
        try:
            compressed_data = zlib.compress(input_data, zlib.Z_BEST_COMPRESSION)
        except zlib.error as err:
            LOGGER.error(f"Compression of input buffer using ZLIB algorithm has failed with error: {err}")
            return bytes(input_data), False

        compression_header = CompressionHeader()
        for i, byte_val in enumerate(TALES_OF_TLZC_MAGIC_BYTE.encode("utf-8")):
            compression_header.magic_bytes[i] = byte_val
        compression_header.__always_one__ = 1
        compression_header.compression_type = int(CompressionType.ZLIB)
        compression_header.compressed_size = len(compressed_data)
        compression_header.uncompressed_size = len(input_data)

        if result := compression_header.to_bytes("little"):
            return result.value + compressed_data, True

        raise ValueError("Failed to convert compression header to bytes. This should never occur")
    else:
        try:
            deflate_compressor = zlib.compressobj(zlib.Z_BEST_COMPRESSION)
            compressed_data = bytearray(deflate_compressor.compress(input_data))
            compressed_data.extend(deflate_compressor.flush())
        except zlib.error as err:
            LOGGER.error(f"Compression of input buffer using ZLIB algorithm has failed with error: {err}")
            return bytes(input_data), False

        compression_header = CompressionHeader()
        for i, byte_val in enumerate(TALES_OF_TLZC_MAGIC_BYTE.encode("utf-8")):
            compression_header.magic_bytes[i] = byte_val
        compression_header.__always_one__ = 1
        compression_header.compression_type = int(CompressionType.ZLIB)
        compression_header.uncompressed_size = len(input_data)

        compression_header.compressed_size = len(compressed_data)
        if result := compression_header.to_bytes("little"):
            return result.value + compressed_data, True

        raise ValueError("Failed to convert compression header to bytes. This should never occur")


def compress_lzma(
    input_data: memoryview,
    num_fast_bytes: int = 64,
    lit_context_bits: int = 3,
    lit_pos_bits: int = 0,
    pos_state_bits: int = 2,
) -> tuple[bytes, bool]:
    if len(input_data) > COMPRESSION_INPUT_MAX_SIZE:
        LOGGER.error(
            f"The input_data has a size {len(input_data)} greater than the max compression input size of"
            + f" {COMPRESSION_INPUT_MAX_SIZE}.\nCompression will not occur"
        )
        return bytes(input_data), False

    # Streams are 64KiB each, round up to the nearest 64 KiB
    chunk_count = (len(input_data) + 0xFFFF) >> 16
    chunk_size_array = list[bytes]()

    compressed_data = bytearray()
    sliding_data = memoryview(input_data)
    for idx in range(chunk_count):
        chunk_size = min(len(sliding_data), LZMA_DICT_SIZE)
        try:
            compressed_slice = pylzma.compress(
                bytes(sliding_data[:chunk_size]),
                dictionary=LZMA_DICT_SIZE_BITS,
                fastBytes=num_fast_bytes,
                literalContextBits=lit_context_bits,
                literalPosBits=lit_pos_bits,
                posBits=pos_state_bits,
                eos=0,
            )
        except TypeError as err:
            LOGGER.error(f"Error occured when compression input buffer using LZMA algorithm: {err}")
            return bytes(input_data), False

        # Strip off the lzma_filters from the beginning of each compressed chunk that pylzma adds
        compressed_slice = compressed_slice[sizeof(LZMAFilters) :]
        if len(compressed_slice) < LZMA_DICT_SIZE:
            compressed_data.extend(compressed_slice)
        else:
            LOGGER.warning(
                f"Unable to compresssed chunk of size {chunk_size:x} to be below the LZMA dict"
                + " size of {DICT_SIZE:x}. Chunk will be stored uncompressed"
            )
            # Set the compressed slice size to 0 and copy the chunk directly to the output buffer
            compressed_slice = b""
            compressed_data.extend(sliding_data[:chunk_size])

        # Shrink the memoryview by he chunksize that was procesed
        sliding_data = sliding_data[chunk_size:]
        chunk_size_array.append(len(compressed_slice).to_bytes(length=2, byteorder="little"))

    # The LZMA filter is the same for all chunks, so it is prepended in front
    # of the chunk size uint16 array
    filter_bytes = LZMAFilters()
    filter_bytes.bit_values = lit_context_bits + 9 * (lit_pos_bits + pos_state_bits * 5)
    for i, byte_val in enumerate(LZMA_DICT_SIZE.to_bytes(length=4, byteorder="little")):
        filter_bytes.dict_size[i] = byte_val

    filter_to_bytes = filter_bytes.to_bytes("little")
    if not filter_to_bytes.value:
        raise ValueError("Failed to convert LZMA filters to 5-byte sequence. This should never occur")

    chunk_size_data = b"".join(chunk_size_array)
    # Update the compression header before converting it to bytes
    # For save data the 0x18 byte header is NOT counted in the compressed size
    compression_header = CompressionHeader()
    for i, byte_val in enumerate(TALES_OF_TLZC_MAGIC_BYTE.encode("utf-8")):
        compression_header.magic_bytes[i] = byte_val
    compression_header.__always_one__ = 1
    compression_header.compression_type = int(CompressionType.LZMA)
    compression_header.uncompressed_size = len(input_data)
    compression_header.compressed_size = len(filter_to_bytes.value) + len(chunk_size_data) + len(compressed_data)

    header_to_bytes = compression_header.to_bytes("little")
    if not header_to_bytes.value:
        raise ValueError("Failed to convert compression header to bytes. This should never occur")

    return header_to_bytes.value + filter_to_bytes.value + b"".join(chunk_size_array) + compressed_data, True
