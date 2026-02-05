"""
Script for converting the Tales of Vesperia PS3 save to PC save
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from enum import Enum
import logging
import pathlib
from dataclasses import dataclass
import sys
from typing import Self

logger = logging.getLogger("save_converter")
logger.setLevel(logging.INFO)
stdoutHandler = logging.StreamHandler()
logger.addHandler(stdoutHandler)

SCRIPT_NAME = pathlib.Path(__file__).name


@dataclass(order=True, unsafe_hash=True)
class Range:
    """
    Represents a range offsets within a file.
    The start value is inclusive and the end value is exclusive.
    Therefore forming the range of [start, end)
    """

    start: int = sys.maxsize
    end: int = sys.maxsize

    def __post_init__(self):
        if self.end < self.start:
            self.start, self.end = self.end, self.start

    def __len__(self) -> int:
        return self.end - self.start

    def __add__(self: Self, int_val: int) -> Self:
        self.start += int_val
        self.end += int_val
        return self

    def __sub__(self: Self, int_val: int) -> Self:
        return self.__add__(-int_val)

    def __iadd__(self, int_val: int) -> Self:
        self.start += int_val
        self.end += int_val
        return self

    def __isub__(self, int_val: int) -> Self:
        return self.__iadd__(-int_val)


class RangeNotCoveredException(Exception):
    pass


class SaveFormat(str, Enum):
    PS3 = "ps3"
    PS4 = "ps4"
    PC = "pc"


@dataclass(order=True, frozen=True)
class ConvertFormat:
    """Specifies the source format and target format to use when converting the save"""

    source: SaveFormat
    target: SaveFormat


class ReplaceState(Enum):
    Partial = 0  # Partial replacement of source range occured. Replace func should be called again with new offset
    Complete = 1  # Complete replacement of source range occured
    Skip = 2  # No replacement were done on source range


@dataclass(
    order=True,
)
class ReplaceResult:
    # Data to write to the output buffer
    data: bytes
    # Offset after the input data that was processed
    new_offset: int
    # Stores the state of replacement for source range
    replace_complete: ReplaceState


def replace_copy(
    input_data: bytes, offset: int, source_range: Range, _convert_format: ConvertFormat
) -> ReplaceResult:
    """Copies all the bytes from @offset to to the end offset of the @source_range of the input data
    into an immutable array of bytes
    This is the default passthrough function for copying output from the input file without modification
    """
    if offset < source_range.start or offset > source_range.end:
        return ReplaceResult(
            data=bytes(), new_offset=offset, replace_complete=ReplaceState.Skip
        )
    return ReplaceResult(
        data=input_data[offset : source_range.end],
        new_offset=source_range.end,
        replace_complete=ReplaceState.Complete,
    )


def get_replace_range_bytes(output_bytes: bytes) -> Callable[..., ReplaceResult]:
    """
    Binds the @output_bytes variable to the replace_range_bytes callable to
    allow custom array of bytes to be replaced at an offset range within the input data
    """

    def replace_range_bytes(
        _input_data: bytes,
        offset: int,
        source_range: Range,
        _convert_format: ConvertFormat,
    ) -> ReplaceResult:
        """Replaces the bytes from the source range with the specified output_bytes data
        The offset should be the same as the @source_range.start value
        """
        # If the offset is not in range, there is nothing to replace
        if offset < source_range.start or offset > source_range.end:
            return ReplaceResult(
                data=bytes(), new_offset=offset, replace_complete=ReplaceState.Skip
            )

        # Offset should be equal to the start offset of the source range
        # But if it is not skip over the difference
        output_data = output_bytes[offset - source_range.start :]
        return ReplaceResult(
            data=output_data,
            new_offset=source_range.end,
            replace_complete=ReplaceState.Complete,
        )

    return replace_range_bytes


class EndianSwapSize(int, Enum):
    Size16Bit = 2
    Size32Bit = 4
    Size64Bit = 8


def get_replace_endian_swap(swap_size: EndianSwapSize) -> Callable[..., ReplaceResult]:
    """
    Binds the @output_bytes variable to the replace_range_bytes callable to
    allow custom array of bytes to be replaced at an offset range within the input data
    """

    def replace_endian_swap(
        input_data: bytes,
        offset: int,
        source_range: Range,
        _convert_format: ConvertFormat,
    ) -> ReplaceResult:
        """Swaps endian size bytes starting at @offset if it is within the @source_range
        The ReplaceResult object `replace_complete` field is only set to true
        if after the endian swap, the new offset is set to the end of the source_range
        Otherwise replacement of the source range is not complete and would have to continue
        in future calls
        """
        # If the offset is not in range, there is nothing to replace
        if offset < source_range.start or offset > source_range.end:
            return ReplaceResult(
                data=bytes(), new_offset=offset, replace_complete=ReplaceState.Skip
            )

        # Round down the end offset to nearest multiple of swap_size from the start offset
        offset_end: int = source_range.end - (source_range.end - offset) % swap_size

        output_data = bytearray()
        for byte_offset in range(offset, offset_end, swap_size):
            output_data += int.from_bytes(
                bytes=input_data[byte_offset : byte_offset + swap_size], byteorder="big"
            ).to_bytes(length=swap_size, byteorder="little")

        return ReplaceResult(
            data=bytes(output_data),
            new_offset=offset_end,
            replace_complete=ReplaceState.Complete
            if offset_end == source_range.end
            else ReplaceState.Skip,
        )

    return replace_endian_swap


@dataclass(order=True)
class ReplaceMap:
    """
    Maps a range of offset from the input data to a view of byte to replace the input in the output
    """

    source_range: Range = Range()
    replace_func: Callable[[bytes, int, Range, ConvertFormat], ReplaceResult] = (
        replace_copy
    )


def fill_replace_func_in_offset_range_gaps(
    replace_table: list[ReplaceMap],
    fill_replace_func: Callable[[bytes, int, Range, ConvertFormat], ReplaceResult],
    max_offset: int,
) -> list[ReplaceMap]:
    """
    Add any source range -> replace function mappings for any offset range
    that is not covered in the input @replace_table.
    Example:
    range1 = [0x0, 0x30) and range2 = [0x40, 0x70)
    The range of [0x30, 0x40) is not covered in the @replace_table, therefore a range
    will be added that maps to the supplied function.
    """
    if not replace_table:
        return []

    # Sort the replace table
    sorted_replace_table = sorted(
        replace_table,
        key=lambda entry: (entry.source_range.start, entry.source_range.end),
    )

    new_replace_table: list[ReplaceMap] = []
    prev_entry = sorted_replace_table[0]
    # The first entry in the replace table will have the smallest offset.
    # If that offset is >0, then prepend a range mapping of [0, <first-entry-start-offset>) -> replace_func
    if prev_entry.source_range.start > 0:
        new_replace_table.append(
            ReplaceMap(
                source_range=Range(0, prev_entry.source_range.start),
                replace_func=fill_replace_func,
            )
        )

    new_replace_table.append(prev_entry)
    for curr_entry in sorted_replace_table[1:]:
        if prev_entry.source_range.end < curr_entry.source_range.start:
            new_replace_table.append(
                ReplaceMap(
                    source_range=Range(
                        prev_entry.source_range.end, curr_entry.source_range.start
                    ),
                    replace_func=fill_replace_func,
                )
            )
        new_replace_table.append(curr_entry)
        prev_entry = curr_entry

    # If the last entry in the replace table end offset value is less than the max_offset,
    # then append one final entry with a mapping of [<last-entry-end-offset>, max_offset)
    if prev_entry.source_range.end < max_offset:
        new_replace_table.append(
            ReplaceMap(
                source_range=Range(prev_entry.source_range.end, max_offset),
                replace_func=fill_replace_func,
            )
        )

    return new_replace_table


class SaveConvertBase(ABC):
    def __init__(self): ...

    def convert(self) -> bool:
        op_result = self._pre_convert()
        if not op_result:
            logger.error(
                f"Pre-convert failed when running {__class__.__name__} converter"
            )
            return False

        op_result = self._convert()
        if not op_result:
            logger.error(f"Convert failed when running {__class__.__name__} converter")
            return False

        op_result = self._post_convert()
        if not op_result:
            logger.error(
                f"Post-Convert failed when running {__class__.__name__} converter"
            )
            return False

        return True

    @abstractmethod
    def _pre_convert(self) -> bool:
        return False

    @abstractmethod
    def _convert(self) -> bool:
        return False

    @abstractmethod
    def _post_convert(self) -> bool:
        return False
