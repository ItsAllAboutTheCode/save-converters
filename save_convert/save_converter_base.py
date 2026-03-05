"""Base Script file containing base classes and methods
used to perform save patching from a source -> target platform
"""

import logging
import pathlib
import sys
from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum, StrEnum
from typing import Self, override

logger = logging.getLogger("save_converter")
logger.setLevel(logging.INFO)
stdoutHandler = logging.StreamHandler()
logger.addHandler(stdoutHandler)

SCRIPT_NAME = pathlib.Path(__file__).name


@dataclass(order=True, unsafe_hash=True)
class Range:
    """Represents a range offsets within a file.
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


class SaveFormat(StrEnum):
    PS3 = "ps3"
    PS4 = "ps4"
    PC = "pc"


@dataclass(order=True, frozen=True)
class ConvertFormat:
    """Specifies the source format and target format to use when converting the save"""

    source: SaveFormat
    target: SaveFormat

    def __str__(self) -> str:
        """
        Generates a string out of the convert format into form
        of <source>-to-target.
        Ex1. PS4 -> PC conversion = ps4-to-pc
        Ex1. PC -> PS4 conversion = pc-to-ps4
        """
        return f"{self.source}-to-{self.target}"


PS4_TO_PC_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.PS4, target=SaveFormat.PC)
PC_TO_PS4_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.PC, target=SaveFormat.PS4)
PS3_TO_PC_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.PS3, target=SaveFormat.PC)
PC_TO_PS3_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.PC, target=SaveFormat.PS3)


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


class ReplacePatchBase(ABC):
    """
    Base class for implementing a __call__() operator that can transform a source range of bytes
    from an input bytearray into an output bytearray.

    This class also contains a reverse_patch() class method which can be overridden
    to act as a method to reverse the patch transformation of the __call__() operator
    """

    def __init__(self, source_range: Range) -> None:
        self._source_range: Range = source_range

    @abstractmethod
    def __call__(self, input_data: bytes, offset: int, convert_format: ConvertFormat) -> ReplaceResult:
        raise NotImplementedError

    def generate_reverse_patch(self) -> Self:
        """
        Default implementation of the reverse_patch operation is to delegate to a new instance
        of ReplacePatchBase derived class
        This implementation works for operations that are naturally invertible such as endian swap
        or a direct byte copy from source -> target.
        i.e (Input * Transform) * Transform = Input
        """
        return type(self)(self._source_range)

    @property
    def source_range(self) -> Range:
        return self._source_range

    @source_range.setter
    def source_range(self, source_range: Range) -> None:
        self._source_range = source_range


class ReplaceCopy(ReplacePatchBase):
    @override
    def __call__(self, input_data: bytes, offset: int, _convert_format: ConvertFormat) -> ReplaceResult:
        """Copies all the bytes from @offset to to the end offset of the @source_range of the input data
        into an immutable array of bytes
        This is the default passthrough function for copying output from the input file without modification
        """
        if offset < self._source_range.start or offset > self._source_range.end:
            return ReplaceResult(data=b"", new_offset=offset, replace_complete=ReplaceState.Skip)
        return ReplaceResult(
            data=input_data[offset : self._source_range.end],
            new_offset=self._source_range.end,
            replace_complete=ReplaceState.Complete,
        )


class ReplaceRangeBytes(ReplacePatchBase):
    def __init__(self, source_range: Range, output_bytes: bytes) -> None:
        """Binds the @output_bytes variable to the replace_range_bytes callable to
        allow custom array of bytes to be replaced at an offset range within the input data
        """
        super().__init__(source_range)
        self._output_bytes: bytes = output_bytes

    @override
    def __call__(
        self,
        _input_data: bytes,
        offset: int,
        _convert_format: ConvertFormat,
    ) -> ReplaceResult:
        """Replaces the bytes from the source range with the specified output_bytes data
        The offset should be the same as the @source_range.start value
        """
        # If the offset is not in range, there is nothing to replace
        if offset < self._source_range.start or offset > self._source_range.end:
            return ReplaceResult(data=b"", new_offset=offset, replace_complete=ReplaceState.Skip)

        # Offset should be equal to the start offset of the source range
        # But if it is not skip over the difference
        output_data = self._output_bytes[offset - self._source_range.start :]
        return ReplaceResult(
            data=output_data,
            new_offset=self._source_range.end,
            replace_complete=ReplaceState.Complete,
        )

    @override
    def generate_reverse_patch(self) -> Self:
        # The reverse operations fills the output data with 00 bytes
        output_data = bytes([0x00] * len(self._source_range))
        reverse_range = Range(start=self._source_range.start, end=len(self._output_bytes) + self._source_range.start)
        return type(self)(reverse_range, output_data)


class EndianSwapSize(int, Enum):
    Size16Bit = 2
    Size32Bit = 4
    Size64Bit = 8


class ReplaceEndianSwap(ReplacePatchBase):
    def __init__(self, source_range: Range, swap_size: EndianSwapSize) -> None:
        """Binds the @output_bytes variable to the replace_range_bytes callable to
        allow custom array of bytes to be replaced at an offset range within the input data
        """
        super().__init__(source_range)
        self._swap_size: EndianSwapSize = swap_size

    @override
    def __call__(
        self,
        input_data: bytes,
        offset: int,
        _convert_format: ConvertFormat,
    ) -> ReplaceResult:
        """Swaps endian size bytes starting at @offset if it is within the @source_range
        The ReplaceResult object `replace_complete` field is only set to true
        if after the endian swap, the new offset is set to the end of the source_range
        Otherwise replacement of the source range is not complete and would have to continue
        in future calls
        """
        # If the offset is not in range, there is nothing to replace
        if offset < self._source_range.start or offset > self._source_range.end:
            return ReplaceResult(data=b"", new_offset=offset, replace_complete=ReplaceState.Skip)

        # Round down the end offset to nearest multiple of swap_size from the start offset
        offset_end: int = self._source_range.end - (self._source_range.end - offset) % self._swap_size

        output_data = bytearray()
        for byte_offset in range(offset, offset_end, self._swap_size):
            output_data += int.from_bytes(
                bytes=input_data[byte_offset : byte_offset + self._swap_size],
                byteorder="big",
            ).to_bytes(length=self._swap_size, byteorder="little")

        return ReplaceResult(
            data=bytes(output_data),
            new_offset=offset_end,
            replace_complete=ReplaceState.Complete if offset_end == self._source_range.end else ReplaceState.Skip,
        )


@dataclass(order=True)
class ReplaceMap:
    """Stores a functor that can replace an input range of bytes using a functor"""

    replace_functor: ReplacePatchBase


def fill_replace_func_in_offset_range_gaps(
    replace_table: list[ReplaceMap],
    fill_replace_functor: ReplacePatchBase,
    max_offset: int,
) -> list[ReplaceMap]:
    """Add any source range -> replace function mappings for any offset range
    that is not covered in the input @replace_table.

    Example:
    range1 = [0x0, 0x30) and range2 = [0x40, 0x70)
    The range of [0x30, 0x40) is not covered in the @replace_table, therefore a range
    will be added that maps to the supplied function.

    """

    if not replace_table:
        # Replace table is empty so set the entire range to use the replacement fill function
        new_functor: ReplacePatchBase = deepcopy(fill_replace_functor)
        new_functor.source_range = Range(start=0, end=max_offset)
        return [
            ReplaceMap(
                replace_functor=new_functor,
            )
        ]

    # Sort the replace table
    sorted_replace_table: list[ReplaceMap] = sorted(
        replace_table,
        key=lambda entry: (entry.replace_functor.source_range.start, entry.replace_functor.source_range.end),
    )

    new_replace_table: list[ReplaceMap] = []
    prev_entry: ReplaceMap = sorted_replace_table[0]
    # The first entry in the replace table will have the smallest offset.
    # If that offset is >0, then prepend a range mapping of [0, <first-entry-start-offset>) -> replace_func
    if prev_entry.replace_functor.source_range.start > 0:
        new_functor = deepcopy(fill_replace_functor)
        new_functor.source_range = Range(start=0, end=prev_entry.replace_functor.source_range.start)
        new_replace_table.append(
            ReplaceMap(
                replace_functor=new_functor,
            ),
        )

    new_replace_table.append(prev_entry)
    for curr_entry in sorted_replace_table[1:]:
        if prev_entry.replace_functor.source_range.end < curr_entry.replace_functor.source_range.start:
            new_functor = deepcopy(fill_replace_functor)
            new_functor.source_range = Range(
                start=prev_entry.replace_functor.source_range.end, end=curr_entry.replace_functor.source_range.start
            )
            new_replace_table.append(
                ReplaceMap(
                    replace_functor=new_functor,
                ),
            )
        new_replace_table.append(curr_entry)
        prev_entry = curr_entry

    # If the last entry in the replace table end offset value is less than the max_offset,
    # then append one final entry with a mapping of [<last-entry-end-offset>, max_offset)
    if prev_entry.replace_functor.source_range.end < max_offset:
        new_functor = deepcopy(fill_replace_functor)
        new_functor.source_range = Range(start=prev_entry.replace_functor.source_range.end, end=max_offset)
        new_replace_table.append(
            ReplaceMap(
                replace_functor=new_functor,
            ),
        )

    return new_replace_table


def generate_reverse_map(source_table: list[ReplaceMap]) -> list[ReplaceMap]:
    """
    Takes the source table and generates a list of transformation
    that can "pseudo" undo the patching done by the source table.

    The reason it is called "pseudo" undo is because any deleted sequence of bytes
    are then reversed mapped to be filled with '00' bytes sequences.
    i.e If at offset 0x20, 16 bytes were deleted, then the reverse mapping would
    insert 16 '00' bytes at offset 0x20.
    If the the bytes at those indices weren't '00' to begin with, the transformation
    is lossy
    """
    target_table: list[ReplaceMap] = []
    for source_entry in source_table:
        target_table.append(ReplaceMap(replace_functor=source_entry.replace_functor.generate_reverse_patch()))

    return target_table


class SaveConvertBase(ABC):
    def __init__(self): ...

    def convert(self) -> bool:
        op_result = self._pre_convert()
        if not op_result:
            logger.error(f"Pre-convert failed when running {__class__.__name__} converter")
            return False

        op_result = self._convert()
        if not op_result:
            logger.error(f"Convert failed when running {__class__.__name__} converter")
            return False

        op_result = self._post_convert()
        if not op_result:
            logger.error(f"Post-Convert failed when running {__class__.__name__} converter")
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
