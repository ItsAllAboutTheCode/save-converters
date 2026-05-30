"""Base Script file containing base classes and methods
used to perform save patching from a source -> target platform
"""

import argparse
import bisect
import logging
import shutil
import sys
import tempfile
from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum, StrEnum
from io import BytesIO
from itertools import islice
from pathlib import Path
from typing import NamedTuple, Protocol, override

from save_convert.structs.marshal_structure import ByteorderLiteral, MarshalStructure

LOGGER = logging.getLogger("save_converter_base")
LOGGER.setLevel(logging.INFO)
stdoutHandler = logging.StreamHandler()
LOGGER.addHandler(stdoutHandler)

SCRIPT_NAME = Path(__file__).name


def align_up(value: int, alignment: int) -> int:
    """Align value up to the nearest alignment value
    alignment must be power of 2
    """
    return (value + alignment - 1) & ~(alignment - 1)


@dataclass(order=True)
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

    @override
    def __str__(self) -> str:
        return f"[{self.start}, {self.end})"

    @override
    def __format__(self, format_spec) -> str:
        return f"[{self.start.__format__(format_spec)}, {self.end.__format__(format_spec)})"


class PatchRange(NamedTuple):
    """
    A tuple of target, source range
    This is used to represent the range of offsets
    A patch operation touches
    """

    target_range: Range
    source_range: Range


class RangeNotCoveredException(Exception):
    pass


class SaveFormat(StrEnum):
    NSW = "nsw"
    PS3 = "ps3"
    PS4 = "ps4"
    PS5 = "ps5"
    PC = "pc"
    XBOXONE = "xboxone"
    XBOXSERIESX = "xboxseriesx"
    UNK = "unknown"


BIG_ENDIAN_SAVE_PLATFORMS = [SaveFormat.PS3]

LITTLE_ENDIAN_SAVE_PLATFORMS = [
    SaveFormat.NSW,
    SaveFormat.PS4,
    SaveFormat.PS5,
    SaveFormat.PC,
    SaveFormat.XBOXONE,
    SaveFormat.XBOXSERIESX,
]


@dataclass(order=True, frozen=True)
class ConvertFormat:
    """Specifies the source format and target format to use when converting the save"""

    source: SaveFormat
    target: SaveFormat

    @override
    def __str__(self) -> str:
        """
        Generates a string out of the convert format into form
        of <source>-to-target.
        Ex1. PS4 -> PC conversion = ps4-to-pc
        Ex1. PC -> PS4 conversion = pc-to-ps4
        """
        return f"{self.source}-to-{self.target}"

    @staticmethod
    def create_from_string(value_string: str) -> ConvertFormat:
        """Creates a ConvertFormat object from a string

        Raises ValueError if the string is not the correct format
        """

        value_list = value_string.split("-to-")
        if len(value_list) != 2:
            raise ValueError(f"ConvertFormat string {value_string} is missing '-to-' between save format strings")

        if value_list[0] not in SaveFormat:
            raise ValueError(f"Source Save Format {value_list[0]} is not supported")
        if value_list[1] not in SaveFormat:
            raise ValueError(f"Target Save Format {value_list[0]} is not supported")

        return ConvertFormat(source=SaveFormat(value_list[0]), target=SaveFormat(value_list[1]))

    def create_reverse(self) -> ConvertFormat:
        """Creates a ConvertFormat by swapping the source and target save formats"""
        return ConvertFormat(source=self.target, target=self.source)


UNKNOWN_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.UNK, target=SaveFormat.UNK)

# Conversion formats to/from PC
PS5_TO_PC_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.PS5, target=SaveFormat.PC)
PC_TO_PS5_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.PC, target=SaveFormat.PS5)
PS4_TO_PC_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.PS4, target=SaveFormat.PC)
PC_TO_PS4_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.PC, target=SaveFormat.PS4)
PS3_TO_PC_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.PS3, target=SaveFormat.PC)
PC_TO_PS3_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.PC, target=SaveFormat.PS3)
NSW_TO_PC_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.NSW, target=SaveFormat.PC)
PC_TO_NSW_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.PC, target=SaveFormat.NSW)
XBOXONE_TO_PC_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.XBOXONE, target=SaveFormat.PC)
PC_TO_XBOXONE_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.PC, target=SaveFormat.XBOXONE)
XBOXSERIESX_TO_PC_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.XBOXSERIESX, target=SaveFormat.PC)
PC_TO_XBOXSERIESX_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.PC, target=SaveFormat.XBOXSERIESX)

# Conversion formats to/from PS5
PS5_TO_PS4_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.PS5, target=SaveFormat.PS4)
PS4_TO_PS5_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.PS4, target=SaveFormat.PS5)
PS5_TO_PS3_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.PS5, target=SaveFormat.PS3)
PS3_TO_PS5_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.PS3, target=SaveFormat.PS5)
PS5_TO_NSW_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.PS5, target=SaveFormat.NSW)
NSW_TO_PS5_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.NSW, target=SaveFormat.PS5)
XBOXONE_TO_PS5_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.XBOXONE, target=SaveFormat.PS5)
PS5_TO_XBOXONE_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.PS5, target=SaveFormat.XBOXONE)
XBOXSERIESX_TO_PS5_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.XBOXSERIESX, target=SaveFormat.PS5)
PS5_TO_XBOXSERIESX_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.PS5, target=SaveFormat.XBOXSERIESX)

# Conversion formats to/from PS4
PS4_TO_PS3_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.PS4, target=SaveFormat.PS3)
PS3_TO_PS4_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.PS3, target=SaveFormat.PS4)
PS4_TO_NSW_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.PS4, target=SaveFormat.NSW)
NSW_TO_PS4_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.NSW, target=SaveFormat.PS4)
XBOXONE_TO_PS4_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.XBOXONE, target=SaveFormat.PS4)
PS4_TO_XBOXONE_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.PS4, target=SaveFormat.XBOXONE)
XBOXSERIESX_TO_PS4_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.XBOXSERIESX, target=SaveFormat.PS4)
PS4_TO_XBOXSERIESX_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.PS4, target=SaveFormat.XBOXSERIESX)

# Conversion formats to/from PS3
PS3_TO_NSW_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.PS3, target=SaveFormat.NSW)
NSW_TO_PS3_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.NSW, target=SaveFormat.PS3)
XBOXONE_TO_PS3_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.XBOXONE, target=SaveFormat.PS3)
PS3_TO_XBOXONE_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.PS3, target=SaveFormat.XBOXONE)
XBOXSERIESX_TO_PS3_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.XBOXSERIESX, target=SaveFormat.PS3)
PS3_TO_XBOXSERIESX_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.PS3, target=SaveFormat.XBOXSERIESX)

# Conversion formats to/from NSW (Nintendo Switch)
XBOXONE_TO_NSW_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.XBOXONE, target=SaveFormat.NSW)
NSW_TO_XBOXONE_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.NSW, target=SaveFormat.XBOXONE)
XBOXSERIESX_TO_NSW_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.XBOXSERIESX, target=SaveFormat.NSW)
NSW_TO_XBOXSERIESX_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.NSW, target=SaveFormat.XBOXSERIESX)

# Conversion formats to/from XBOXONE
XBOXSERIESX_TO_XBOXONE_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.XBOXSERIESX, target=SaveFormat.XBOXONE)
XBOXONE_TO_XBOXSERIESX_CONVERT_FORMAT = ConvertFormat(source=SaveFormat.XBOXONE, target=SaveFormat.XBOXSERIESX)


class PatchOperationState(Enum):
    Partial = 0  # Partial patch at target offset occurred. Patch func should be called again with new offset
    Complete = 1  # Complete patch at target offset occured
    Skip = 2  # No patch operation was performed at target offset


@dataclass(
    order=True,
)
class PatchOperationResult:
    # Data to write to the output buffer
    target_data: bytes
    # Offset to write data in the output buffer
    target_write_offset: int
    # Offset after the input data that was processed
    new_source_offset: int
    # Stores the state of patch operation at the target offset
    patch_complete: PatchOperationState


class PatchBase(ABC):
    """
    Base class for implementing a __call__() operator that write to a target offset
    using an input function

    This class also contains a reverse_patch() class method which can be overridden
    to act as a method to reverse the patch transformation of the __call__() operator
    """

    _target_offset: int
    _source_range: Range

    def __init__(self, target_offset: int, source_range: Range) -> None:
        self._target_offset = target_offset
        self._source_range = source_range

    @abstractmethod
    def __call__(self, source_data: bytes, source_offset: int, convert_format: ConvertFormat) -> PatchOperationResult:
        """
        Invoked to get a list of bytes to copy to the target stream at a specific target
        + update the source stream read offset.

        This function should return PatchOperationComplete if successful
        """
        raise NotImplementedError

    def generate_reverse_patch(self) -> PatchBase:
        """
        Default implementation of the reverse_patch operation is to delegate to a new instance
        of PatchBase derived class
        This implementation works for operations that are naturally invertible such as endian swap
        or a direct byte copy from source -> target.
        i.e (Input * Transform) * Transform = Input
        """
        raise NotImplementedError

    @abstractmethod
    def get_target_covered_range(self) -> Range:
        """
        Should return the range of bytes in the target stream that this functor
        will write to.
        For example if the functor writes at offset 0x20, a sequence of 0x20 bytes
        Then it covers the range [0x20, 0x40)

        Default implementation is that a range of zero bytes at the target offset is covered
        """
        return Range(self._target_offset, self._target_offset)

    def get_source_covered_range(self) -> Range:
        """
        Should return the range of bytes in the source stream that this functor
        will read or skip.
        For example if the functor reads at offset 0x10, a sequence of 0x08 bytes
        Then it covers the range [0x10, 0x18)
        """
        return self._source_range

    @override
    def __repr__(self) -> str:
        return f"covered range: target={self.get_target_covered_range()}, source={self.get_source_covered_range()}"

    @property
    def target_offset(self) -> int:
        return self._target_offset

    @target_offset.setter
    def target_offset(self, target_offset: int) -> None:
        self._target_offset = target_offset

    @property
    def source_range(self) -> Range:
        return self._source_range

    @source_range.setter
    def source_range(self, source_range: Range) -> None:
        self._source_range = source_range

    def __lt__(self, other: PatchBase | int) -> bool:
        if isinstance(other, PatchBase):
            return self._target_offset < other._target_offset
        else:
            return self._target_offset < other


class PatchCopyBytes(PatchBase):
    """
    Copies bytes from source stream to target stream without modification
    """

    @override
    def __call__(self, source_data: bytes, source_offset: int, _convert_format: ConvertFormat) -> PatchOperationResult:
        """Copies all the bytes from source_offset in the source_data
        to the target offset
        This is the default passthrough function for copying output from the source_data without modification
        """
        if source_offset != self._source_range.start:
            return PatchOperationResult(
                target_data=b"",
                target_write_offset=self._target_offset,
                new_source_offset=source_offset,
                patch_complete=PatchOperationState.Skip,
            )

        # Make sure that the source_data buffer is not indexed passed its end
        new_end_offset = min(len(source_data), self._source_range.end)
        return PatchOperationResult(
            target_data=source_data[source_offset:new_end_offset],
            target_write_offset=self._target_offset,
            new_source_offset=source_offset + (new_end_offset - source_offset),
            patch_complete=PatchOperationState.Complete,
        )

    @override
    def generate_reverse_patch(self) -> PatchCopyBytes:
        """Reverse operation copies the data using the target_offset as the start of the source range
        and the amount of bytes to write as the end of the source range.
        The reverse of the target_offset is the start of the source range
        """
        return PatchCopyBytes(
            target_offset=self._source_range.start,
            source_range=Range(self._target_offset, self._target_offset + len(self._source_range)),
        )

    @override
    def get_target_covered_range(self) -> Range:
        return Range(self._target_offset, self._target_offset + len(self._source_range))


class PatchInsertBytes(PatchBase):
    """Insert bytes at a specific target_offset in the target stream"""

    def __init__(
        self, target_offset: int, source_offset: int, output_bytes: bytes, reverse_output_bytes: bytes | None = None
    ) -> None:
        # source offset doesn't update when bytes are inserted so the range end at the source offset as well
        super().__init__(target_offset, Range(source_offset, source_offset))
        self._output_bytes: bytes = output_bytes

    @override
    def __call__(
        self,
        _source_data: bytes,
        source_offset: int,
        _convert_format: ConvertFormat,
    ) -> PatchOperationResult:
        """Writes bytes from the output bytes array to the target stream.
        The source offset is returned unchanged to make sure the source stream
        remains at the same offset for future operations
        """
        if source_offset != self._source_range.start:
            return PatchOperationResult(
                target_data=b"",
                target_write_offset=self._target_offset,
                new_source_offset=source_offset,
                patch_complete=PatchOperationState.Skip,
            )

        return PatchOperationResult(
            target_data=self._output_bytes,
            target_write_offset=self._target_offset,
            new_source_offset=source_offset,
            patch_complete=PatchOperationState.Complete,
        )

    @override
    def generate_reverse_patch(self) -> PatchSkipBytes:
        """The reverse operation is to skip the same amount of bytes that were inserted"""
        return PatchSkipBytes(
            target_offset=self._source_range.start,
            source_range=Range(self._target_offset, self._target_offset + len(self._output_bytes)),
            reverse_output_bytes=self._output_bytes,
        )

    @override
    def get_target_covered_range(self) -> Range:
        return Range(self._target_offset, self._target_offset + len(self._output_bytes))


class PatchSkipBytes(PatchBase):
    """
    Skip over bytes in the source stream.
    Effectively this functor just advances the source_offset to its source range end offset
    """

    def __init__(self, target_offset: int, source_range: Range, reverse_output_bytes: bytes | None = None) -> None:
        # source offset doesn't update when bytes are inserted so the range end at the source offset as well
        super().__init__(target_offset, source_range)
        # Reverse output bytes is used to generate a reverse patch method
        # if unset it is filled with a byte array the same size as the normal output bytes, however all the bytes
        # are '00'
        self._reverse_output_bytes: bytes = reverse_output_bytes if reverse_output_bytes else bytes(len(source_range))

    @override
    def __call__(
        self,
        _source_data: bytes,
        source_offset: int,
        _convert_format: ConvertFormat,
    ) -> PatchOperationResult:
        """Writes  bytes from the source range with the specified output_bytes data
        The offset should be the same as the @source_range.start value
        """
        if source_offset != self._source_range.start:
            return PatchOperationResult(
                target_data=b"",
                target_write_offset=self._target_offset,
                new_source_offset=source_offset,
                patch_complete=PatchOperationState.Skip,
            )

        return PatchOperationResult(
            target_data=b"",
            target_write_offset=self._target_offset,
            new_source_offset=self._source_range.end,
            patch_complete=PatchOperationState.Complete,
        )

    @override
    def generate_reverse_patch(self) -> PatchInsertBytes:
        """The reverse operation inserts the same amount of bytes that were skipped
        The source offset has to be rotated around the target offset by the same amount of bytes
        i.e If source_offset = 0x1C and target_offset = 0x20, the source_offset
        is 4 bytes less than the target offset, so for the insert operation
        it needs to be 4 bytes larger than the target offset
        """
        return PatchInsertBytes(
            target_offset=self._source_range.start,
            source_offset=self._target_offset,
            output_bytes=self._reverse_output_bytes,
        )

    @override
    def get_target_covered_range(self) -> Range:
        """
        Target offset is actually updated in this case. Only the source offset
        is updated to move the source stream along
        """
        return Range(self._target_offset, self._target_offset)


class PatchInsertAndSkipBytes(PatchBase):
    """Insert bytes at a specific target_offset in the target stream and then skip
    the same a specified number of bytes in the source stream.

    This effectively acts as a replace operation if the streams were modified in place

    NOTE: Does not inherit from PatchInsertBytes as that sets the source_range end offset to the source_offset
    Here the source_range end offset has the count of the output byte array added to it
    """

    def __init__(
        self, target_offset: int, source_offset: int, output_bytes: bytes, reverse_output_bytes: bytes | None = None
    ) -> None:
        super().__init__(target_offset, Range(source_offset, source_offset + len(output_bytes)))
        self._output_bytes: bytes = output_bytes

        # Reverse output bytes is used to generate a reverse patch method
        # if unset it is filled with a byte array the same size as the normal output bytes, however all the bytes
        # are '00'
        self._reverse_output_bytes: bytes = (
            reverse_output_bytes if reverse_output_bytes else bytes(len(self._output_bytes))
        )

    @override
    def __call__(
        self,
        _source_data: bytes,
        source_offset: int,
        _convert_format: ConvertFormat,
    ) -> PatchOperationResult:
        """Writes bytes from the output bytes array to the target stream.
        The source offset is then advanced by the bytes_to_skip amount.

        This combines both the PatchInsertBytes and PatchSkipBytes operation into one
        """

        if source_offset != self._source_range.start:
            return PatchOperationResult(
                target_data=b"",
                target_write_offset=self._target_offset,
                new_source_offset=source_offset,
                patch_complete=PatchOperationState.Skip,
            )

        return PatchOperationResult(
            target_data=self._output_bytes,
            target_write_offset=self._target_offset,
            new_source_offset=self._source_range.end,
            patch_complete=PatchOperationState.Complete,
        )

    @override
    def generate_reverse_patch(self) -> PatchInsertAndSkipBytes:
        """The reverse operation skips the amount of bytes in the output bytes array.
        That is combined with inserting the same number of bytes as the bytes_to_skip amount.
        The new bytes to insert are based on the reverse output byte array, so unless
        it stores the original bytes, the operation might be lossy.
        """
        return PatchInsertAndSkipBytes(
            target_offset=self._source_range.start,
            source_offset=self._target_offset,
            output_bytes=self._reverse_output_bytes,
        )

    @override
    def get_target_covered_range(self) -> Range:
        return Range(self._target_offset, self._target_offset + len(self._output_bytes))


class EndianSwapSize(int, Enum):
    Size16Bit = 2
    Size32Bit = 4
    Size64Bit = 8


class PatchEndianSwap(PatchCopyBytes):
    """Allows swapping of endianess every @swap_size bytes using the
    bytes in the source_range from the source stream. The swapped bytes
    are written to the target offset
    """

    def __init__(self, target_offset: int, source_range: Range, swap_size: EndianSwapSize) -> None:
        super().__init__(target_offset, source_range)
        self._swap_size: EndianSwapSize = swap_size

    @override
    def __call__(
        self,
        source_data: bytes,
        source_offset: int,
        _convert_format: ConvertFormat,
    ) -> PatchOperationResult:
        """Swaps endian size bytes starting at @offset if it is within the @source_range
        The PatchOperationResult object `patch_complete` field is only set to true
        if after the endian swap, the new offset is set to the end of the source_range
        Otherwise replacement of the source range is not complete and would have to continue
        in future calls
        """
        # If the offset is not in range, there is nothing to replace
        if source_offset != self._source_range.start:
            return PatchOperationResult(
                target_data=b"",
                target_write_offset=self._target_offset,
                new_source_offset=source_offset,
                patch_complete=PatchOperationState.Skip,
            )

        # Round down the end offset to nearest multiple of swap_size from the start offset
        offset_end: int = self._source_range.end - (self._source_range.end - source_offset) % self._swap_size

        output_data = bytearray()
        new_source_offset: int = source_offset
        for byte_offset in range(source_offset, offset_end, self._swap_size):
            new_source_offset = byte_offset + self._swap_size
            # Avoid indexing pass the end of the input buffer
            if new_source_offset > len(source_data):
                break

            output_data += int.from_bytes(
                bytes=source_data[byte_offset:new_source_offset],
                byteorder="big",
            ).to_bytes(length=self._swap_size, byteorder="little")

        return PatchOperationResult(
            target_data=bytes(output_data),
            target_write_offset=self._target_offset,
            new_source_offset=new_source_offset,
            patch_complete=PatchOperationState.Complete
            if offset_end == self._source_range.end
            else PatchOperationState.Skip,
        )

    @override
    def generate_reverse_patch(self) -> PatchEndianSwap:
        """Reverse operation of an Endian Swap replaces the source range start with the target offset
        and the target_offset with the source range start
        """
        return PatchEndianSwap(
            target_offset=self._source_range.start,
            source_range=Range(self._target_offset, self._target_offset + len(self._source_range)),
            swap_size=self._swap_size,
        )

    @override
    def get_target_covered_range(self) -> Range:
        return Range(self._target_offset, self._target_offset + len(self._source_range))


class PatchCreatorCallable(Protocol):
    def __call__(self, *, target_offset: int, source_range: Range) -> PatchBase: ...


class PatchSet:
    """Stores set of PatchBase objects which can be used to replace bytes
    in a target file at a specific offset
    """

    _patch_entries: list[PatchBase] = []

    def __init__(self, patch_entries: Iterable[PatchBase] = ()):
        self._patch_entries = list(sorted(patch_entries))

    @property
    def patch_entries(self) -> list[PatchBase]:
        return self._patch_entries

    def add_patch_entry(self, patch_entry: PatchBase):
        """Add patch_entry and sort it into the patch entries sorted set"""
        bisect.insort_right(self._patch_entries, patch_entry)

    def find_next_patch_entry(self, target_offset: int, start_index: int) -> PatchBase | None:
        ### Determine if offset references a value within the patch set
        patch_index: int = -1
        if self._patch_entries:
            # Get the first smallest index > @target_offset
            lower_bound = bisect.bisect_left(self._patch_entries, target_offset, lo=start_index)

            if (
                lower_bound != len(self._patch_entries)
                and self._patch_entries[lower_bound].target_offset == target_offset
            ):
                # If the offset is exactly equal to the lower_bound start offset, use that entry
                patch_index = lower_bound
            elif lower_bound > 0:
                # Otherwise check if the previous index patch entry end offset is >= offset
                if self._patch_entries[lower_bound - 1].get_target_covered_range().end >= target_offset:
                    patch_index = lower_bound - 1

        if patch_index == -1:
            return None

        return self._patch_entries[patch_index]

    def generate_reverse_set(self) -> PatchSet:
        """
        Takes the source table and generates a list of transformation
        that can reverse the patching done by the source table in a lossy fashion.

        The reason it is "lossy" is because any deleted sequence of bytes
        are then reversed mapped to be filled with '00' bytes sequences.
        i.e If at offset 0x20, 16 bytes were deleted, then the reverse mapping would
        insert 16 '00' bytes at offset 0x20.
        If the the bytes at those indices weren't '00' to begin with, the transformation
        will be lossy. If the bytes orginally deleted were '00', then the reverse transformation
        will be loseless.
        """
        target_table: list[PatchBase] = []
        for source_entry in self._patch_entries:
            target_table.append(source_entry.generate_reverse_patch())

        return PatchSet(patch_entries=target_table)

    def get_covered_patch_range_set(
        self,
    ) -> list[PatchRange]:
        """
        Return the set of continuous patch range offsets covered by the Patch Set
        """

        if not self._patch_entries:
            return []

        # Track the continuous range of covered
        active_patch_range = PatchRange(
            self._patch_entries[0].get_target_covered_range(), self._patch_entries[0].get_source_covered_range()
        )

        covered_range_set: list[PatchRange] = []
        for curr_entry in islice(self._patch_entries, 1, None):
            next_range = PatchRange(curr_entry.get_target_covered_range(), curr_entry.get_source_covered_range())
            if active_patch_range.target_range.end == next_range.target_range.start:
                # The active range can be extended to end of the next range
                active_patch_range = PatchRange(
                    Range(active_patch_range.target_range.start, next_range.target_range.end),
                    Range(active_patch_range.source_range.start, next_range.source_range.end),
                )
            elif active_patch_range.target_range.end > next_range.target_range.start:
                LOGGER.error(
                    f"Covered patch offset {active_patch_range.target_range:#x} overlaps the next patch"
                    f" offset {next_range.target_range:#x}"
                )
                active_patch_range = PatchRange(
                    Range(active_patch_range.target_range.start, next_range.target_range.end),
                    Range(active_patch_range.source_range.start, next_range.source_range.end),
                )
            else:
                # The start of the next range is discontinuous with the end of the active range therefore
                # 1. append the active_patch_range to the covered_range_set (if it is not empty)
                # 2. set the active_patch_range to be the next range
                covered_range_set.append(active_patch_range)
                active_patch_range = next_range

        covered_range_set.append(active_patch_range)

        return covered_range_set

    def get_uncovered_patch_range_set(self, target_range: Range, source_range: Range) -> list[PatchRange]:
        """
        Return the set of continuous target range offsets NOT covered by the Patch Set
        """
        covered_range_set: list[PatchRange] = self.get_covered_patch_range_set()

        # If there isn't a covered range then the entire patch range is uncovered
        if not covered_range_set:
            return [PatchRange(target_range, source_range)]

        uncovered_range_set: list[PatchRange] = []
        prev_covered_range = covered_range_set[0]
        if target_range.start < prev_covered_range.target_range.start:
            uncovered_range_set.append(
                PatchRange(
                    target_range=Range(target_range.start, prev_covered_range.target_range.start),
                    source_range=Range(source_range.start, prev_covered_range.source_range.start),
                )
            )

        for curr_covered_range in islice(covered_range_set, 1, None):
            uncovered_range_set.append(
                PatchRange(
                    target_range=Range(prev_covered_range.target_range.end, curr_covered_range.target_range.start),
                    source_range=Range(prev_covered_range.source_range.end, curr_covered_range.source_range.start),
                )
            )
            prev_covered_range = curr_covered_range

        if prev_covered_range.target_range.end < target_range.end:
            uncovered_range_set.append(
                PatchRange(
                    target_range=Range(prev_covered_range.target_range.end, target_range.end),
                    source_range=Range(prev_covered_range.source_range.end, source_range.end),
                )
            )

        return uncovered_range_set

    def fill_uncovered_target_offset_ranges(
        self,
        create_patch_class_functor: PatchCreatorCallable,
        target_range: Range,
        source_range: Range,
    ) -> None:
        """Add PatchBase functors to patch any target offsets
        not covered by the PatchSet

        Example:
        range1 = [0x0, 0x30) and range2 = [0x40, 0x70)
        The range of [0x30, 0x40) is not covered in the patch set, therefore a range
        will be added that maps to the supplied function.

        """
        uncovered_patch_range_set: list[PatchRange] = self.get_uncovered_patch_range_set(target_range, source_range)
        if not uncovered_patch_range_set:
            # The entire range is covered, nothing to do
            return

        for uncovered_patch_range in uncovered_patch_range_set:
            self.add_patch_entry(
                create_patch_class_functor(
                    target_offset=uncovered_patch_range.target_range.start,
                    source_range=uncovered_patch_range.source_range,
                )
            )

    def validate(self, target_range: Range, source_range: Range) -> tuple[bool, str]:
        """
        Validates that the patch entries covers every address within the target range of [start, end)
        If a target range isn't covered, then when patching occurs then the uncovered target address range
        will not have valid bytes written to it.

        Returns a tuple of (bool, str) where the bool indicates if validation was successfuly
        and the string contains any error messages in the case of unsuccessful validation
        """

        uncovered_patch_range_set: list[PatchRange] = self.get_uncovered_patch_range_set(target_range, source_range)
        if not uncovered_patch_range_set:
            return True, ""

        error_message = ""
        for uncovered_patch_range in uncovered_patch_range_set:
            error_message += f"PatchRange: {uncovered_patch_range} is not covered by a PatchBase functor\n"

        if error_message:
            return False, error_message

        return True, ""


class ConvertPatchTable:
    """Stores a mapping of convert format (source -> target) platforms
    to a PatchSet object which can be used to patch a save file from
    a given source platform to target platform
    """

    # Map the ConvertFormat to a set of patch entries which contains functors
    # to transform the source save format to the target save format
    convert_format_to_patch_set: dict[ConvertFormat, PatchSet] = {}
    # Stores a mapping of SaveFormat type to expected save size
    # For example a PS3 save format for a game might have an expected size of 0x40
    # while the PC save format for a game might have an expected size of 0x30
    save_format_to_save_size_dict: dict[SaveFormat, int] = {}

    def __init__(
        self,
        convert_format_to_patch_set: dict[ConvertFormat, PatchSet],
        save_format_to_save_size_dict: dict[SaveFormat, int],
    ):
        self.convert_format_to_patch_set = convert_format_to_patch_set
        self.save_format_to_save_size_dict = save_format_to_save_size_dict

    def get_patch_set_for_convert_format(self, convert_format: ConvertFormat) -> PatchSet:
        return self.convert_format_to_patch_set.get(convert_format, PatchSet())

    def get_save_size_for_format(self, save_format: SaveFormat) -> int | None:
        return self.save_format_to_save_size_dict.get(save_format, None)

    def fill_uncovered_target_offset_ranges(self, create_patch_class_functor: PatchCreatorCallable) -> None:
        """
        Fill every patch_set uncovered offset ranges
        """
        for convert_format, patch_set in self.convert_format_to_patch_set.items():
            target_range = Range(0, self.save_format_to_save_size_dict.get(convert_format.target, sys.maxsize))
            source_range = Range(0, self.save_format_to_save_size_dict.get(convert_format.source, sys.maxsize))
            patch_set.fill_uncovered_target_offset_ranges(
                create_patch_class_functor, target_range=target_range, source_range=source_range
            )

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validates each convert_format to patch_set mapping in the patch table

        Returns a tuple (bool, list[str]) where the bool value is True only
        if all the patch_set mappings are valid.
        The list[str] value contains any error messages if any validations failed
        """
        valid = True
        error_messages: list[str] = []
        for convert_format, patch_set in self.convert_format_to_patch_set.items():
            target_range = Range(0, self.save_format_to_save_size_dict.get(convert_format.target, sys.maxsize))
            source_range = Range(0, self.save_format_to_save_size_dict.get(convert_format.source, sys.maxsize))
            valid, error_message = patch_set.validate(target_range, source_range)
            if not valid:
                valid = False
                error_messages.append(f"{convert_format}:\n{error_message}")

        return valid, error_messages


class SaveBase(ABC):
    """
    Base Class that can be used for any custom logic
    (Read data from a save, converting, decrypting/encryption, etc...)
    """

    def transform(self) -> bool:
        op_result = self._pre_transform()
        if not op_result:
            LOGGER.error(f"Pre-convert failed when running {type(self).__name__} converter")  # type:ignore[name-defined]
            return False

        op_result = self._transform()
        if not op_result:
            LOGGER.error(f"Convert failed when running {type(self).__name__} converter")  # type:ignore[name-defined]
            return False

        op_result = self._post_transform()
        if not op_result:
            LOGGER.error(f"Post-Convert failed when running {type(self).__name__} converter")  # type:ignore[name-defined]
            return False

        return True

    @abstractmethod
    def _pre_transform(self) -> bool:
        """Implement to pre-load the save data before parsing"""
        raise NotImplementedError

    @abstractmethod
    def _transform(self) -> bool:
        """Implement to parse the save data"""
        raise NotImplementedError

    @abstractmethod
    def _post_transform(self) -> bool:
        """Implement to perform action with parsed save data"""
        raise NotImplementedError


class SaveTransformBase(SaveBase, ABC):
    """
    Base Class for save transformation from a source file to a target file
    """

    _input_path: Path
    _output_path: Path
    _input_data: bytes
    _output_io: BytesIO

    def __init__(self, args: argparse.Namespace):
        self._input_path = args.input
        self._output_path = args.output
        self._input_data = b""
        self._output_io = BytesIO()  # Create a in-memory binary IO buffer for storing output data

    @override
    @abstractmethod
    def _pre_transform(self) -> bool:
        """Pre-load save data from the input file into memory"""
        # Read the entire save into memory
        with self._input_path.open("rb") as infile:
            try:
                self._input_data = infile.read()
            except BlockingIOError as err:
                LOGGER.error(f"Unable to read data from input file {self._input_path}: {err}")
                return False

        return True

    @override
    @abstractmethod
    def _transform(self) -> bool:
        """Default implementation just copies the save file to the output buffer"""
        return self._output_io.write(self._input_data) == len(self._input_data)

    @override
    @abstractmethod
    def _post_transform(self) -> bool:
        """Writes the output data to the destination file atomically"""
        # Now copy temporary output file to destination
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_output_path = Path(f"{tmpdir}/{self._output_path.name}").resolve()
            with tmp_output_path.open("wb") as outfile:
                byte_buffer = self._output_io.getvalue()
                if outfile.write(byte_buffer) != len(byte_buffer):
                    raise IOError(f"Failed to write {len(byte_buffer)} to output file. Aborting...")
                self._output_io.close()

            self._output_path.parent.mkdir(parents=True, exist_ok=True)
            return bool(shutil.move(tmp_output_path, self._output_path))

    @staticmethod
    def process_input_savedata(
        input_result: PatchOperationResult,
        source_data: bytes,
        patch_set: PatchSet,
        current_patch_index: int,
        convert_format: ConvertFormat,
    ) -> PatchOperationResult:
        """Process the input data to determine how it should be written to the output
        It checks the offset against the patch_set to see if it contains a functor that can replace
        the data from the input offset into and output buffer

        :param: offset Offset being examined from the input save data
        :param: input_data Data from the input save file
        :param: patch_set Ordered list of offset range -> patch functors
                This set is used to patch data at the offset range
        :param: current_patch_index Index in the patch set to start to search for the offset within
                This value gets updated by this method and returned. It should initially be set to 0
                and then passed back into this method every iteration.

        :return: PatchOperationResult set (bytes_to_write_to_output, updated_input_offset,
                replacement status for the current input range)
        """

        if patch_entry := patch_set.find_next_patch_entry(
            input_result.target_write_offset, start_index=current_patch_index
        ):
            output_result = patch_entry(source_data, input_result.new_source_offset, convert_format)
            return output_result

        return PatchOperationResult(
            target_data=b"",
            target_write_offset=input_result.target_write_offset,
            new_source_offset=input_result.new_source_offset,
            patch_complete=PatchOperationState.Skip,
        )


class SaveConvertBase(SaveTransformBase, ABC):
    """
    Base Class used to convert a save from a source platform format to a target platform format
    """

    _convert_format: ConvertFormat
    _patch_table: ConvertPatchTable

    def __init__(self, args: argparse.Namespace):
        super().__init__(args)
        self._convert_format = getattr(args, "convert_format", UNKNOWN_CONVERT_FORMAT)
        if not self._output_path:
            self._output_path: Path = self._input_path.with_suffix(
                f"{self._input_path.suffix}.{self._convert_format.target}"
            )
            LOGGER.debug(f'No Output path specified, it has updated to "{self._output_path}"')

        self._patch_table = self.create_save_patch_table()

    @override
    @abstractmethod
    def _transform(self) -> bool:
        """Iterates over the input save file, attempting byte replacements from the source save format
        in order to convert to the target save format
        """
        if output_data := self.apply_patch(self._input_data, self._patch_table, self._convert_format):
            try:
                if self._output_io.write(output_data) != len(output_data):
                    LOGGER.error(
                        f"Unable to write {len(output_data)} bytes to output.\n"
                        f" ByteIO buffer offset: 0x{self._output_io.tell():X}",
                    )
                    return False
            except OSError as _err:
                LOGGER.exception("Failed to write to output\n")
                return False
            return True

        return False

    @abstractmethod
    def create_save_patch_table(self) -> ConvertPatchTable:
        return ConvertPatchTable(convert_format_to_patch_set={}, save_format_to_save_size_dict={})

    @staticmethod
    def apply_patch(input_data: bytes, patch_table: ConvertPatchTable, convert_format: ConvertFormat) -> bytes:
        """Patches the input buffer using the patch table and returns a bytes object"""

        convert_patch_set: PatchSet = patch_table.get_patch_set_for_convert_format(convert_format)
        target_save_size = patch_table.get_save_size_for_format(convert_format.target)
        if not target_save_size:
            LOGGER.error(
                f"Target save format {convert_format.target} does not have an expected save size mapped.\n"
                f"It will be assumed to be {sys.maxsize}",
            )
            target_save_size = sys.maxsize

        output_buffer = bytearray()
        patch_index = 0

        result: PatchOperationResult = PatchOperationResult(
            target_data=b"", target_write_offset=0, new_source_offset=0, patch_complete=PatchOperationState.Skip
        )
        while result.target_write_offset < target_save_size:
            result = SaveTransformBase.process_input_savedata(
                input_result=result,
                source_data=input_data,
                patch_set=convert_patch_set,
                current_patch_index=patch_index,
                convert_format=convert_format,
            )

            if len(output_buffer) != result.target_write_offset:
                LOGGER.error(
                    f"Target write offset 0x{result.target_write_offset:X} does not match the end of the"
                    + f" Byte buffer. Byte buffer offset: 0x{len(output_buffer):X}",
                )
                return b""
            output_buffer += result.target_data

            # If no progress has been made in the processing of the input data
            # Then return to prevent an infinite loop
            if result.patch_complete == PatchOperationState.Skip:
                LOGGER.error(
                    "Failed to to make progress processing source data, target stream has stopped writing"
                    f" at offset: 0x{len(output_buffer):X}\nPatch Operation failed at index {patch_index}"
                    f" for conversion of {convert_format}:\n"
                    f"  Patch Operation Result: {result}"
                )
                return b""

            # Update the current offset being processed and the patch set index
            patch_index += 1 if result.patch_complete else 0
            result.target_write_offset += len(result.target_data)

        return bytes(output_buffer)


class SaveCryptBase(SaveTransformBase, ABC):
    """
    Base Class used to (en)decrypt a save for the save format
    """

    _save_format: SaveFormat

    def __init__(self, args: argparse.Namespace):
        super().__init__(args)
        self._save_format = getattr(args, "save_format", SaveFormat.UNK)

        if not self._output_path:
            self._output_path: Path = self._input_path.with_suffix(f"{self._input_path.suffix}.{self._save_format}")
            LOGGER.debug(f'No Output path specified, it has updated to "{self._output_path}"')


class BinSaveToYamlConvert(SaveTransformBase):
    """
    Convert a binary save file to YAML file based on a defiend MarshalStructure derived class
    """

    _byteorder: ByteorderLiteral
    _struct_type: type[MarshalStructure]
    _with_comments: bool  # If set yaml will be annotated with comments about the structure fields

    def __init__(self, args: argparse.Namespace, struct_type: type[MarshalStructure]):
        """
        param :struct_type MarshalStructure derived class that specifies
        the fields of a c-like binary structure
        """
        super().__init__(args)
        self._struct_type = struct_type
        self._with_comments = getattr(args, "with_comments", False)
        # Use any specified byteorder option if provided for the endianess
        # If not specified, attempt to use the save_format option endianess
        # and if that is not specified use the system byteorder
        byteorder: ByteorderLiteral | None = getattr(args, "byteorder", None)
        if not byteorder:
            save_format = getattr(args, "save_format", SaveFormat.UNK)
            if save_format in LITTLE_ENDIAN_SAVE_PLATFORMS:
                byteorder = "little"
            elif save_format in BIG_ENDIAN_SAVE_PLATFORMS:
                byteorder = "big"
            else:
                byteorder = sys.byteorder

        self._byteorder = byteorder

        if not self._output_path:
            self._output_path: Path = self._input_path.with_suffix(".yaml")
            LOGGER.debug(f'No Output path specified, it has updated to "{self._output_path}"')

    @override
    def _pre_transform(self) -> bool:
        return super()._pre_transform()

    @override
    def _transform(self) -> bool:
        return self.convert_bin_save_to_yaml()

    @override
    def _post_transform(self) -> bool:
        return super()._post_transform()

    def convert_bin_save_to_yaml(self) -> bool:
        """
        Convert binary to save
        """
        struct_inst = self._struct_type()
        result = struct_inst.from_bytes(memoryview(self._input_data), struct_inst, self._byteorder)
        if not result:
            return False

        to_yaml_result = struct_inst.to_yaml(self._with_comments)
        if not to_yaml_result:
            return False

        return self._output_io.write(to_yaml_result.value) == len(to_yaml_result.value)


class YamlToBinSaveConvert(SaveTransformBase):
    """
    Convert a Yaml file of to a ctypes struct derived from MarshalStructure
    """

    _byteorder: ByteorderLiteral
    _struct_type: type[MarshalStructure]

    def __init__(self, args: argparse.Namespace, struct_type: type[MarshalStructure]):
        """
        param :struct_type MarshalStructure derived class that specifies
        the fields of a c-like binary structure
        """
        super().__init__(args)
        self._struct_type = struct_type
        # Use any specified byteorder option if provided for the endianess
        # If not specified, attempt to use the save_format option endianess
        # and if that is not specified use the system byteorder
        byteorder: ByteorderLiteral | None = getattr(args, "byteorder", None)
        if not byteorder:
            save_format = getattr(args, "save_format", SaveFormat.UNK)
            if save_format in LITTLE_ENDIAN_SAVE_PLATFORMS:
                byteorder = "little"
            elif save_format in BIG_ENDIAN_SAVE_PLATFORMS:
                byteorder = "big"
            else:
                byteorder = sys.byteorder

        self._byteorder = byteorder

        if not self._output_path:
            self._output_path: Path = self._input_path.with_suffix(".bin")
            LOGGER.debug(f'No Output path specified, it has updated to "{self._output_path}"')

    @override
    def _pre_transform(self) -> bool:
        return super()._pre_transform()

    @override
    def _transform(self) -> bool:
        return self.convert_yaml_to_bin_save()

    @override
    def _post_transform(self) -> bool:
        return super()._post_transform()

    def convert_yaml_to_bin_save(self) -> bool:
        """
        Convert a YAML file to a binary save file based on a defiend MarshalStructure derived class
        """
        result = self._struct_type.from_yaml(self._input_data, self._struct_type)
        if not result or not result.value:
            return False

        struct_inst = result.value

        output_byte_buffer = bytearray()
        to_bytes_result = struct_inst.to_bytes(output_byte_buffer, self._byteorder)
        if not to_bytes_result:
            return False

        return self._output_io.write(output_byte_buffer) == len(output_byte_buffer)
