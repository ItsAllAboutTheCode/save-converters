#!/usr/bin/env python
import argparse
import hashlib
import logging
import sys
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum, IntEnum, StrEnum
from pathlib import Path
from typing import TYPE_CHECKING, Any, NamedTuple, TypeAlias, override

from Crypto.Cipher import AES  # type: ignore[import-not-found]

from save_convert.save_converter_base import (
    PC_TO_PS4_CONVERT_FORMAT,
    PC_TO_PS5_CONVERT_FORMAT,
    PC_TO_XBOXONE_CONVERT_FORMAT,
    PC_TO_XBOXSERIESX_CONVERT_FORMAT,
    PS4_TO_PC_CONVERT_FORMAT,
    PS4_TO_PS5_CONVERT_FORMAT,
    PS4_TO_XBOXONE_CONVERT_FORMAT,
    PS4_TO_XBOXSERIESX_CONVERT_FORMAT,
    PS5_TO_PC_CONVERT_FORMAT,
    PS5_TO_PS4_CONVERT_FORMAT,
    PS5_TO_XBOXONE_CONVERT_FORMAT,
    PS5_TO_XBOXSERIESX_CONVERT_FORMAT,
    XBOXONE_TO_PC_CONVERT_FORMAT,
    XBOXONE_TO_PS4_CONVERT_FORMAT,
    XBOXONE_TO_PS5_CONVERT_FORMAT,
    XBOXONE_TO_XBOXSERIESX_CONVERT_FORMAT,
    XBOXSERIESX_TO_PC_CONVERT_FORMAT,
    XBOXSERIESX_TO_PS4_CONVERT_FORMAT,
    XBOXSERIESX_TO_PS5_CONVERT_FORMAT,
    XBOXSERIESX_TO_XBOXONE_CONVERT_FORMAT,
    ConvertFormat,
    SaveBase,
    SaveConvertBase,
    SaveCryptBase,
    SaveFormat,
)

if TYPE_CHECKING:
    from save_convert.save_converter_base import ConvertPatchTable


SCRIPT_DIR: Path = Path(__file__).parent.resolve()
DEFAULT_PS5_PATCH_FILE: Path = SCRIPT_DIR / "patch/SAVE.ps5"

SUPPORTED_PATCH_FILE_PLATFORMS: list[SaveFormat] = [SaveFormat.PS4, SaveFormat.PS5]

LOGGER = logging.getLogger("arise_save_converter")
LOGGER.addHandler(logging.StreamHandler(sys.stdout))
LOGGER.setLevel(logging.INFO)

# Save Sizes for the PC and PS5 vesions of the game
TALES_OF_ARISE_SAVE_SIZE = 760856
TALES_OF_ARISE_DLC_SAVE_SIZE = 593080

# Magic Byte which identifies save data. Has value 30 16 05 10
TALES_OF_ARISE_SAVE_BLOCK_START = 0x32058
# Size of the encrypted Save Data save section:
TALES_OF_ARISE_SAVE_BLOCK_SIZE_OFFSET = TALES_OF_ARISE_SAVE_BLOCK_START + 0x4
# 20 Byte sha1 hash of save data.
# Hashes data starting at offset 0x32078 (where the first encrypted save block begins)
TALES_OF_ARISE_SAVE_ENCRYPTED_SHA1_OFFSET = TALES_OF_ARISE_SAVE_BLOCK_SIZE_OFFSET + 0x4
# 1 byte sequence - Byte which indicates if the encrypted data went through an XOR cipher before decrption
# If 0,then the encrypted data is XOR cipher'ed, otherwise the encrypted data only went through AES ECB algorithm
TALES_OF_ARISE_SAVE_XOR_CIPHER_OFFSET = TALES_OF_ARISE_SAVE_ENCRYPTED_SHA1_OFFSET + 0x14
# 1 byte sequence - Byte which indicates if the alternatve XOR cipher logic should be performed
# On PC both the regular logic and alternate logic is the same.
# On other platforms the alternative XOR logic is unknown,
# however the save on other platforms always has a value 0x01 therefore uses the regular XOR logic
TALES_OF_ARISE_SAVE_XOR_CIPHER_ALT_LOGIC_OFFSET = TALES_OF_ARISE_SAVE_XOR_CIPHER_OFFSET + 0x1
# 2 byte padding to align the first encrypted block on a 4-byte boundary
TALES_OF_ARISE_SAVE_HEADER_PADDING_OFFSET = TALES_OF_ARISE_SAVE_XOR_CIPHER_ALT_LOGIC_OFFSET + 0x1
# Offset where the encrypted data starts
TALES_OF_ARISE_SAVE_ENCRYPTED_BLOCK_START = TALES_OF_ARISE_SAVE_HEADER_PADDING_OFFSET + 0x2
# Offset after the encrypted offset table
TALES_OF_ARISE_SAVE_ENCRYPTED_OFFSET_BLOCK_END = TALES_OF_ARISE_SAVE_ENCRYPTED_BLOCK_START + 0x40

# Size of the Save Header before the encryption block start
# Should be 0x20 hex
TALES_OF_ARISE_SAVE_HEADER_SIZE = TALES_OF_ARISE_SAVE_ENCRYPTED_BLOCK_START - TALES_OF_ARISE_SAVE_BLOCK_START


# Offset which contains the (different) offset that pionts to of the save item section header
TALES_OF_ARISE_PC_SAVE_ITEM_HEADER_REL = 0x28
TALES_OF_ARISE_PS5_SAVE_ITEM_HEADER_REL = 0x18

TALES_OF_ARISE_SAVE_ITEM_SECTION_HEADER_SIZE = 0x40
TALES_OF_ARISE_SAVE_ITEM_SECTION_HEADER_ITEM_COUNT_OFFSET = 0x4
TALES_OF_ARISE_SAVE_ITEM_SECTION_HEADER_FIRST_ITEM_OFFSET = 0x8
TALES_OF_ARISE_SAVE_ITEM_HEADER_SIZE = 0x10
TALES_OF_ARISE_SAVE_ITEM_HEADER_DATA_SIZE_OFFSET = 0x8
TALES_OF_ARISE_SAVE_ITEM_HEADER_NEXT_ITEM_OFFSET = 0xC


# PC Cipher Key
# Located at 0x332C740 in Tale of Arise.exe
# First 32-bytes are cipher key for AES-256 ECB
TALES_OF_ARISE_PC_AES_SAVE_KEY = bytes.fromhex(
    "66674551354762784658702D6D443674"
    "48545A566D695777674B385077674B35"
    "4D66636E474875726972724A59397856"
    "786B6438692D5679334C443652687800"
)

# 64 byte table which is xor'ed with the AES decrypted
# result to get the decrypted save data
# Located at 0x332C780 in Tale of Arise.exe
TALES_OF_ARISE_PC_XOR_CIPHER_TABLE = bytes.fromhex(
    "4E6A466E534A734E5170694D726E5165"
    "67634272354167725A4147413567524D"
    "6B4341444E4D5A5233697A4557565233"
    "5A69636963585A4E7346794B556D7200"
)


# Found in eboot.bin
# Did a search for strings within the eboot.bin that had length 31 - 33
# and then examined the strings that contained only alphanumeric chracters and underscore
# Also looked at the string to see if the text "appeared" random as that is how the key looked on PC
# Luckily I found 4 candidates that are listed in the save_NOTES.md file
TALES_OF_ARISE_PS5_AES_SAVE_KEY = bytes.fromhex(
    "39514C4A5048585A556E47324C4A414858433677636648596B42567A53487942"
) + bytes.fromhex("2D353374396350666E726950634A2D6B4B637252614362364272695553636400")

# Found in eboot.bin and using the commented code below
TALES_OF_ARISE_PS5_XOR_CIPHER_TABLE = bytes.fromhex(
    "4A45457854703539693651505F706732474B375A6A63573332624A2D586D5257"
) + bytes.fromhex("435859415843345963474D527552526A42685F44375473384D506B5A34473900")


class XorCipherPerformEnum(IntEnum):
    """
    Represents the byte value that determines whether the XOR cipher should be performed on PC
    ON PS5 the value is always 0x3, however the XOR cipher is performed there
    """

    PC = 0
    PS4 = 1
    XBOXONE = 2
    PS5 = 3
    XBOXSERIESX = 4


SUPPORTED_SAVE_FORMATS: list[SaveFormat] = [
    SaveFormat.PC,
    SaveFormat.PS5,
    SaveFormat.PS4,
    SaveFormat.XBOXONE,
    SaveFormat.XBOXSERIESX,
]

SUPPORTED_CONVERT_FORMATS: list[ConvertFormat] = [
    PC_TO_PS5_CONVERT_FORMAT,
    PC_TO_PS4_CONVERT_FORMAT,
    PC_TO_XBOXONE_CONVERT_FORMAT,
    PC_TO_XBOXSERIESX_CONVERT_FORMAT,
    PS5_TO_PC_CONVERT_FORMAT,
    PS5_TO_PS4_CONVERT_FORMAT,
    PS5_TO_XBOXONE_CONVERT_FORMAT,
    PS5_TO_XBOXSERIESX_CONVERT_FORMAT,
    PS4_TO_PC_CONVERT_FORMAT,
    PS4_TO_PS5_CONVERT_FORMAT,
    PS4_TO_XBOXONE_CONVERT_FORMAT,
    PS4_TO_XBOXSERIESX_CONVERT_FORMAT,
    XBOXONE_TO_PC_CONVERT_FORMAT,
    XBOXONE_TO_PS5_CONVERT_FORMAT,
    XBOXONE_TO_PS4_CONVERT_FORMAT,
    XBOXONE_TO_XBOXSERIESX_CONVERT_FORMAT,
    XBOXSERIESX_TO_PC_CONVERT_FORMAT,
    XBOXSERIESX_TO_PS5_CONVERT_FORMAT,
    XBOXSERIESX_TO_PS4_CONVERT_FORMAT,
    XBOXSERIESX_TO_XBOXONE_CONVERT_FORMAT,
]


class SaveItemSectionEnum(StrEnum):
    Entitlement = "Entitlement"
    PartyOrder = "Party Order"
    SaveData_GameConfig = "Save Data Game Config"
    PartyProfile = "Party Profile"
    SaveData_ItemManager = "SaveData Item Manager"
    ArisePCStatus_000 = "Player Character 0 Status"
    ArisePCStatus_001 = "Player Character 1 Status"
    ArisePCStatus_002 = "Player Character 2 Status"
    ArisePCStatus_003 = "Player Character 3 Status"
    ArisePCStatus_004 = "Player Character 4 Status"
    ArisePCStatus_005 = "Player Character 5 Status"
    ArisePCStatus_006 = "Player Character 6 Status"
    ArisePCStatus_007 = "Player Character 7 Status"
    SaveData_ShortChat = "Save Data Short Chat"
    MenuSave = "Menu Save"
    SaveData_LongChat = "Save Data Long Chat"
    # The string is spelled correctly, the enum matches what is in the game
    SaveData_ScenaioFlg = "Save Data Scenario Flag"
    SearchOwlSaveData = "Search Owl Save Data"
    TreasurePointSaveData = "Treasure Point Save Data"
    SearchPointSaveData = "Search Point Save Data"
    AriseMiningSaveData = "Arise Mining Save Data"
    BreakPointSaveData = "Break Point Save Data"
    MapGimmickSaveData = "Map Gimmick Save Data"
    OneTopSaveData = "One Top Save Data"
    QuestEnemyCountSaveData = "Quest Enemy Count Save Data"
    QuestSaveDataEx = "Quest Save Data Extra"
    FishingSaveData = "Fishing Save Data"
    CampPointSaveData = "Camp Point Save Data"
    EncountSymbolSaveData = "Encounter Symbol Save Data"
    RecoveryPointSaveData = "Recovery Point Save Data"


class SaveItemSection(NamedTuple):
    """
    Stores a tuple whihc contains the absolute offset in the decrypted save file
    to the section header for the Save Item block, the absolute offset to the
    start of the Save Item block data and finally the size of the Save Item block
    """

    header_offset: int
    data_offset: int
    size: int


SaveItemSectionTable: TypeAlias = dict[SaveItemSectionEnum, SaveItemSection]


class PlainTextAndUpdatedXorTableTuple(NamedTuple):
    plaintext_buffer: memoryview
    xor_table: bytes


class EncryptedTextAndUpdatedXorTableTuple(NamedTuple):
    encrypted_buffer: memoryview
    xor_table: bytes


class CryptionReturnCodes(Enum):
    SUCCESS = 0
    # The next offset to examine is larger than the save payload
    NEXT_OFFSET_OUT_OF_BOUNDS = 1
    FIRST_OFFSET_TABLE_ENTRY_NOT_4_BYTE_ALIGNED = 2
    MISSING_REQUIRED_SECTION_HEADER_BYTE = 4
    UNKNOWN_SAVE_FORMAT = 8


class DecryptionResult(NamedTuple):
    return_code: CryptionReturnCodes
    plaintext_buffer: bytes


class EncryptionResult(NamedTuple):
    return_code: CryptionReturnCodes
    encrypted_buffer: bytes


class DumpItemSectionResult(NamedTuple):
    return_code: CryptionReturnCodes
    save_item_section_table: SaveItemSectionTable


@dataclass
class PlatformCryptionData:
    # The save format for the platform being encrypted/decrypted
    save_format: SaveFormat
    # The relative offset used by the platform whichs contains
    # another offset that points to the save item header section
    first_block_dword_offset: int
    # A method used to transform the XOR Cipher table one that
    # can be used to encrypt/encrypt the platform save
    xor_table_transform_func: Callable[[memoryview, memoryview], bytes]
    # The byte to use for the platform to determine if the XOR cipher table
    # is used for encryption/decryption on that platform
    xor_cipher_byte: int
    # Stores the Cipher Key used to encrypt/decrypt the first block at 0x32078
    first_cipher_key: bytes
    # Stores the XOR Cipher that is XOR against the bytes the first block pre-encrypted/post-decrypted
    # bytes of the block at offset 0x32078
    first_xor_cipher_table: bytes


# Start Helper methods
def abs_to_rel_offset(offset: int, base: int = TALES_OF_ARISE_SAVE_BLOCK_START) -> int:
    """
    Convert an absolute Tales of Arise save offset to a relative save block offset
    """
    return offset - base


def format_hex(buffer: bytes | memoryview[int] | bytearray) -> str:
    """
    Format a byte buffer for human readability
    It will be formatted with the style of
    | XX XX XX XX | XX XX XX XX | XX XX XX XX | XX XX XX XX |
    | XX XX XX XX | XX XX XX XX | XX XX XX XX | XX XX XX XX |
    ...
    | XX XX XX XX | XX XX XX XX | XX XX XX XX | XX XX XX XX |

    Up to the number of bytes in the buffer
    """
    return "".join(
        [
            f"|{value:02X}" if (index % 4 == 0) else f" {value:02X}{'|\n' if index % 16 == 15 else ''}"
            for index, value in enumerate(buffer)
        ]
    )


def pretty_print_hex(buffer: bytes | memoryview[int] | bytearray):
    print(format_hex(buffer), end="")


def rotate_bytes(input: bytes | bytearray | memoryview, n: int) -> bytes:
    """
    Rotates the binary buffer by n bytes in any direction
    Used for adjusting the PC XOR table to make direct XOR comparisons against the plaintext buffer
    """
    return bytes(input[n:]) + input[:n]


def adjust_pc_xor_table(xor_table_buffer: memoryview[int], decrypted_buffer_size: int) -> bytes:
    """
    :Parameters:
        xor_table_buffer: bytes/bytearray/memoryview
            XOR buffer used which is xor'ed against save buffer
            It is offset 2 bytes ahead, so result_buffer[x] = xor_table_buffer[x + 2]
        decrypted_buffer_size: int
            The XOR Table is treated as a circular ring up to the size of the decryption buffer
            If the decryption buffer is < size of the XOR table, then any rotations
            should occur only within that ring
    :Keywords:
        output: bytearray/memoryview
            The location where the plaintext must be written to.
            If `None`, the plaintext is returned.
    :Return:
          If `output_buffer` is `None`, the result_buffer is returned as `bytes`.
          Otherwise, `None`
    """
    adjust_table_size = min(len(xor_table_buffer), decrypted_buffer_size)
    return rotate_bytes(xor_table_buffer[:adjust_table_size], 2) + xor_table_buffer[adjust_table_size:]


def pc_xor_plaintext_savedata(decrypted_buffer: memoryview[int], xor_table_buffer: memoryview[int]) -> bytes:
    """
    :Parameters:
        decrypted_buffer: bytes/bytearray/memoryview
            The piece of data to XOR.
        xor_table_buffer: bytes/bytearray/memoryview
            XOR buffer used which is xor'ed against save buffer
            It is offset 2 bytes ahead, so result_buffer[x] = xor_table_buffer[x + 2]
    :Keywords:
        output: bytearray/memoryview
            The location where the plaintext must be written to.
            If `None`, the plaintext is returned.
    :Return:
          If `output_buffer` is `None`, the result_buffer is returned as `bytes`.
          Otherwise, `None`
    """
    return xor_plaintext_savedata(
        decrypted_buffer, memoryview(adjust_pc_xor_table(xor_table_buffer, len(decrypted_buffer)))
    )


def adjust_ps5_xor_table(xor_table_buffer: memoryview[int], decrypted_buffer_size: int) -> bytes:
    """
    :Parameters:
        xor_table_buffer: bytes/bytearray/memoryview
            XOR buffer used which is xor'ed against save buffer
            It is treated as two byte big endian object compared to the save_data_buffer which is treated
            as a two byte little endian object
            The algorithm is result_buffer[i] = xor_table_buffer[i + 1]; result_buffer[i + 1] = xor_table_buffer[i]
    :Keywords:
        output: bytearray/memoryview
            The location where the plaintext must be written to.
            If `None`, the plaintext is returned.
    :Return:
          If `output_buffer` is `None`, the result_buffer is returned as `bytes`.
          Otherwise, `None`
    """
    adjust_table_size = min(len(xor_table_buffer), decrypted_buffer_size)
    return (
        b"".join(
            [
                int.from_bytes(xor_table_buffer[i : i + 2], "big").to_bytes(2, "little")
                for i in range(0, adjust_table_size, 2)
            ]
        )
        + xor_table_buffer[adjust_table_size:]
    )


def ps5_xor_plaintext_savedata(decrypted_buffer: memoryview[int], xor_table_buffer: memoryview[int]) -> bytes:
    """
    :Parameters:
        decrypted_buffer: bytes/bytearray/memoryview
            The piece of data to XOR.
        xor_table_buffer: bytes/bytearray/memoryview
            XOR buffer used which is xor'ed against save buffer
            It is treated as two byte big endian object compared to the save_data_buffer which is treated
            as a two byte little endian object
            The algorithm is result_buffer[i] = xor_table_buffer[i + 1]; result_buffer[i + 1] = xor_table_buffer[i]
    :Keywords:
        output : bytearray/memoryview
            The location where the plaintext must be written to.
            If `None`, the plaintext is returned.
    :Return:
          If `output_buffer` is `None`, the result_buffer is returned as `bytes`.
          Otherwise, `None`
    """

    return xor_plaintext_savedata(
        decrypted_buffer, memoryview(adjust_ps5_xor_table(xor_table_buffer, len(decrypted_buffer)))
    )


def xor_plaintext_savedata(decrypted_buffer: memoryview[int], xor_table_buffer: memoryview[int]) -> bytes:
    """
    :Parameters:
        decrypted_buffer: bytes/bytearray/memoryview
            The piece of data to XOR.
        xor_table_buffer: bytes/bytearray/memoryview
            XOR buffer used which is xor'ed against save buffer
            It is offset 2 bytes ahead, so result_buffer[x] = input_key_buffer[x + 2]
    :Keywords:
        output: bytearray/memoryview
            The location where the plaintext must be written to.
            If `None`, the plaintext is returned.
    :Return:
          If `output_buffer` is `None`, the result_buffer is returned as `bytes`.
          Otherwise, `None`
    """

    result_buffer = bytearray(len(decrypted_buffer))

    xor_table_size = len(xor_table_buffer)
    for buffer_index in range(0, len(decrypted_buffer)):
        xor_byte = xor_table_buffer[buffer_index % xor_table_size]
        result_buffer[buffer_index] = decrypted_buffer[buffer_index] ^ xor_byte

    return bytes(result_buffer)


def update_cipher_key(
    old_cipher_key: bytes | memoryview,
    plaintext_buffer: bytes | memoryview[int],
) -> bytes:
    """
    Update the Cipher Key (First 32-bytes are the AES-ECB key) by performing an XOR with
    with the SHA-1 Hash of the plaintext data.
    After every encryption or decryption round, the plaintext block has a SHA-1 performed against
    it and then the 20 bytes of the SHA-1 is XOR against the 64 bytes of the cipher key
    rotating back to the start when the end of the SHA-! buffer is reached

    If the result of XORing a byte is 0x0, then the existing Cipher key byte is taken
    unless the bytes being XORed are 0x0 in which case the Cipher key is set to 0x20
    This is based on the game code algorithm
    """
    plaintext_sha1 = hashlib.sha1(bytes(plaintext_buffer))
    plaintext_sha1_digest = plaintext_sha1.digest()
    new_cipher_key = bytearray()
    for i, cipher_byte in enumerate(old_cipher_key):
        sha1_byte = plaintext_sha1_digest[i % len(plaintext_sha1_digest)]
        if cipher_byte == sha1_byte:
            # If the current byte in the cipher key is the same as the sha1 hash
            # the xor would result in 0 so what the game code does is force
            # it to be cipher_byte if it is non-zero otherwise it forces the byte to be 0x20
            new_cipher_key.append(cipher_byte if cipher_byte else 0x20)
        else:
            new_cipher_key.append(cipher_byte ^ plaintext_sha1_digest[i % len(plaintext_sha1_digest)])

    # The last byte is always set to 0
    new_cipher_key[-1] = 0
    return bytes(new_cipher_key)


def update_xor_table(
    old_xor_table: bytes | memoryview,
    encrypted_view: memoryview[int],
) -> bytes:
    """
    Update the XOR table with the encrypted table
    Only the bytes that have been encrypted will be replaced in the XOR table
    """
    if len(encrypted_view) < len(old_xor_table):
        new_xor_table: bytes | memoryview[int] = bytes(encrypted_view) + old_xor_table[len(encrypted_view) :]
    else:
        new_xor_table = encrypted_view[: len(old_xor_table)]
    return bytes(new_xor_table)


# End Helper Methods


# Helper Lookup methods to map multiple platforms save functions conversion formats for a specific platform


def create_cryption_data_from_save_format(save_format: SaveFormat) -> PlatformCryptionData:
    match save_format:
        case SaveFormat.PC:
            return PlatformCryptionData(
                save_format=SaveFormat.PC,
                first_block_dword_offset=TALES_OF_ARISE_PC_SAVE_ITEM_HEADER_REL,
                xor_table_transform_func=pc_xor_plaintext_savedata,
                xor_cipher_byte=XorCipherPerformEnum.PC,
                first_cipher_key=TALES_OF_ARISE_PC_AES_SAVE_KEY,
                first_xor_cipher_table=TALES_OF_ARISE_PC_XOR_CIPHER_TABLE,
            )
        case SaveFormat.XBOXONE:
            return PlatformCryptionData(
                save_format=SaveFormat.XBOXONE,
                first_block_dword_offset=TALES_OF_ARISE_PC_SAVE_ITEM_HEADER_REL,
                xor_table_transform_func=pc_xor_plaintext_savedata,
                xor_cipher_byte=XorCipherPerformEnum.XBOXONE,
                first_cipher_key=TALES_OF_ARISE_PC_AES_SAVE_KEY,
                first_xor_cipher_table=TALES_OF_ARISE_PC_XOR_CIPHER_TABLE,
            )
        case SaveFormat.XBOXSERIESX:
            return PlatformCryptionData(
                save_format=SaveFormat.XBOXSERIESX,
                first_block_dword_offset=TALES_OF_ARISE_PC_SAVE_ITEM_HEADER_REL,
                xor_table_transform_func=pc_xor_plaintext_savedata,
                xor_cipher_byte=XorCipherPerformEnum.XBOXSERIESX,
                first_cipher_key=TALES_OF_ARISE_PC_AES_SAVE_KEY,
                first_xor_cipher_table=TALES_OF_ARISE_PC_XOR_CIPHER_TABLE,
            )
        case SaveFormat.PS5:
            return PlatformCryptionData(
                save_format=SaveFormat.PS5,
                first_block_dword_offset=TALES_OF_ARISE_PS5_SAVE_ITEM_HEADER_REL,
                xor_table_transform_func=ps5_xor_plaintext_savedata,
                xor_cipher_byte=XorCipherPerformEnum.PS5,
                first_cipher_key=TALES_OF_ARISE_PS5_AES_SAVE_KEY,
                first_xor_cipher_table=TALES_OF_ARISE_PS5_XOR_CIPHER_TABLE,
            )
        case SaveFormat.PS4:
            return PlatformCryptionData(
                save_format=SaveFormat.PS4,
                first_block_dword_offset=TALES_OF_ARISE_PS5_SAVE_ITEM_HEADER_REL,
                xor_table_transform_func=ps5_xor_plaintext_savedata,
                xor_cipher_byte=XorCipherPerformEnum.PS4,
                first_cipher_key=TALES_OF_ARISE_PS5_AES_SAVE_KEY,
                first_xor_cipher_table=TALES_OF_ARISE_PS5_XOR_CIPHER_TABLE,
            )
        case _:
            raise ValueError(
                f"'{save_format}' is unsupported Cannot create encryption/decryption metadata object for platform"
            )


# Start Manipulation Classes
class SaveDecryptArise(SaveCryptBase):
    """
    Decrypts an encrypted Tales of Arive save for the specified save format
    """

    def __init__(self, args: argparse.Namespace):
        super().__init__(args)

        # Override default output path from base SaveCryptBase
        output_path: Path | None = getattr(args, "output", None)
        if not output_path:
            self._output_path: Path = self._output_path.with_suffix(self._output_path.suffix + ".dec")

    @override
    def _pre_transform(self) -> bool:
        return super()._pre_transform()

    @override
    def _transform(self) -> bool:
        if self._save_format in SUPPORTED_SAVE_FORMATS:
            dec_result = self.decrypt_save_buffer(
                self._input_data, create_cryption_data_from_save_format(self._save_format)
            )
            if dec_result.return_code == CryptionReturnCodes.SUCCESS:
                bytes_written = self._output_io.write(dec_result.plaintext_buffer)
                return bytes_written == len(dec_result.plaintext_buffer)
            LOGGER.error(f"Decryption Failed with rc {dec_result.return_code}")
            return False
        else:
            LOGGER.error(f"Unsupported decrypt save format supplied {self._save_format}. Cannot decrypt...")
            return False

    @override
    def _post_transform(self) -> bool:
        return super()._post_transform()

    @staticmethod
    def decrypt_block(
        cipher_ebc,  # pyright: ignore[reportUnknownParameterType]
        decrypt_buffer: memoryview,
        encrypted_buffer: memoryview,
        perform_xor_cipher: bool,
        xor_table: bytes | memoryview,
        platform_xor_table_transform_func: Callable[[memoryview, memoryview], bytes],
    ) -> PlainTextAndUpdatedXorTableTuple:
        """
        Decrypts the encrypted data in 64 byte chunks and XORs the chunk with the xor_table
        This method then updates the xor table to what was in the encrypted buffer

        If the block > 64 bytes, the XOR table is updated to the encrypted buffer 64 bytes that were just decrypted

        :param: perform_xor_cipher - If True the decrypted data is Xor'ed with a 64-byte cipher table after AES-ECB
                                     to create the plaintext buffer

        :return: Returns a tuple of updated XOR table after the block has been decrypted
        """
        MAX_BLOCK_SIZE = 64
        remaining_bytes_to_decrypt: int = len(encrypted_buffer)
        new_xor_table: bytes = bytes(xor_table)
        offset: int = 0
        decrypted_buffer_string = ""
        while remaining_bytes_to_decrypt != 0:
            encrypted_view = memoryview(encrypted_buffer)[
                offset : offset + min(remaining_bytes_to_decrypt, MAX_BLOCK_SIZE)
            ]
            decrypt_view = memoryview(decrypt_buffer)[offset : offset + len(encrypted_view)]
            cipher_ebc.decrypt(encrypted_view, decrypt_view)
            decrypted_buffer_string += format_hex(decrypt_view)
            if perform_xor_cipher:
                decrypt_view[:] = platform_xor_table_transform_func(decrypt_view, memoryview(new_xor_table))
                # Update the XOR table
                new_xor_table = update_xor_table(new_xor_table, encrypted_view)
            remaining_bytes_to_decrypt -= len(encrypted_view)
            offset += len(encrypted_view)

        LOGGER.debug("The decrypted view is:")
        LOGGER.debug(decrypted_buffer_string)
        return PlainTextAndUpdatedXorTableTuple(decrypt_buffer, new_xor_table)

    @staticmethod
    def decrypt_save_buffer(
        save_file_content: bytes,
        platform_cryption_data: PlatformCryptionData,
    ) -> DecryptionResult:
        """
        Decrypts a Tales of Arise save
        """
        cipher_key: bytes | memoryview = platform_cryption_data.first_cipher_key
        plaintext_xor_table: bytes = platform_cryption_data.first_xor_cipher_table
        save_payload = memoryview(save_file_content)[TALES_OF_ARISE_SAVE_BLOCK_START:]
        decrypted_save_buffer: bytearray = bytearray(save_payload)

        xor_cipher_byte = platform_cryption_data.xor_cipher_byte
        perform_xor_cipher: bool = (
            save_payload[abs_to_rel_offset(TALES_OF_ARISE_SAVE_XOR_CIPHER_OFFSET)] == xor_cipher_byte
        )
        decrypted_block_size: int = 0x40
        next_decrypt_offset: int = TALES_OF_ARISE_SAVE_ENCRYPTED_BLOCK_START - TALES_OF_ARISE_SAVE_BLOCK_START
        encrypted_view: memoryview[int] = memoryview(save_payload)[
            next_decrypt_offset : next_decrypt_offset + decrypted_block_size
        ]

        absolute_offset: int = TALES_OF_ARISE_SAVE_BLOCK_START + next_decrypt_offset
        LOGGER.debug(
            f"Decryption of bytes at (abs offset=0x{absolute_offset:X}, rel offset=0x{next_decrypt_offset:X},"
            f" size={len(encrypted_view)})"
        )
        LOGGER.debug("The cipher key is:")
        LOGGER.debug(format_hex(cipher_key))
        LOGGER.debug("The encrypted view is:")
        LOGGER.debug(format_hex(encrypted_view))

        decrypt_view: memoryview[int] = memoryview(decrypted_save_buffer)[
            next_decrypt_offset : next_decrypt_offset + decrypted_block_size
        ]

        xor_buffer_string = format_hex(plaintext_xor_table)
        cipher_ebc = AES.new(cipher_key[:32], mode=AES.MODE_ECB)
        decrypt_view, plaintext_xor_table = __class__.decrypt_block(  # type: ignore[name-defined]
            cipher_ebc,
            decrypt_view,
            memoryview(encrypted_view),
            perform_xor_cipher,
            memoryview(plaintext_xor_table),
            platform_cryption_data.xor_table_transform_func,
        )
        if perform_xor_cipher:
            LOGGER.debug("The xor table is:")
            LOGGER.debug(xor_buffer_string)
        LOGGER.debug("The plaintext buffer is:")
        LOGGER.debug(format_hex(decrypt_view) + "\n")

        cipher_key = update_cipher_key(cipher_key, decrypt_view)
        # Update the AES key
        cipher_ebc = AES.new(cipher_key[:32], mode=AES.MODE_ECB)

        # For PC platforms, the 10th dword is the offset that is decrypted next.
        # For Sony platforms, the 6th dowrd is the offset that is decrypted next.
        next_decrypt_offset = int.from_bytes(
            decrypt_view[
                platform_cryption_data.first_block_dword_offset : platform_cryption_data.first_block_dword_offset + 4
            ],
            "little",
        )
        if next_decrypt_offset >= len(save_payload):
            LOGGER.error(
                f"Cannot decrypt buffer with next decryption offset 0x{next_decrypt_offset:X} greater"
                f" than the size of the save payload size 0x{len(save_payload):X}.\n"
                " Is this a proper Tales of Arise encrypted save file?"
            )
            return DecryptionResult(CryptionReturnCodes.NEXT_OFFSET_OUT_OF_BOUNDS, b"")
        elif next_decrypt_offset % 4 != 0:
            LOGGER.error(
                "The offset to decrypt from the offset table must be 4-byte aligned\n"
                f"The offset is 0x{next_decrypt_offset:X}."
                " Is this a proper Tales of Arise encrypted save file?"
            )
            return DecryptionResult(CryptionReturnCodes.FIRST_OFFSET_TABLE_ENTRY_NOT_4_BYTE_ALIGNED, b"")

        # Create a memory view of the 64 bytes at the next offset
        encrypted_view = memoryview(save_payload)[next_decrypt_offset : next_decrypt_offset + decrypted_block_size]
        absolute_offset = TALES_OF_ARISE_SAVE_BLOCK_START + next_decrypt_offset
        LOGGER.debug(
            f"Decryption of bytes at (abs offset=0x{absolute_offset:X}, rel offset=0x{next_decrypt_offset:X},"
            f" size={len(encrypted_view)})"
        )
        LOGGER.debug("The cipher key is:")
        LOGGER.debug(format_hex(cipher_key))
        LOGGER.debug("The encrypted view is:")
        LOGGER.debug(format_hex(encrypted_view))

        decrypt_view = memoryview(decrypted_save_buffer)[
            next_decrypt_offset : next_decrypt_offset + decrypted_block_size
        ]

        xor_buffer_string = format_hex(plaintext_xor_table)
        decrypt_view, plaintext_xor_table = __class__.decrypt_block(  # type: ignore[name-defined]
            cipher_ebc,
            decrypt_view,
            memoryview(encrypted_view),
            perform_xor_cipher,
            memoryview(plaintext_xor_table),
            platform_cryption_data.xor_table_transform_func,
        )

        if perform_xor_cipher:
            LOGGER.debug("The xor table is:")
            LOGGER.debug(xor_buffer_string)
        LOGGER.debug("The plaintext buffer is:")
        LOGGER.debug(format_hex(decrypt_view) + "\n")

        if decrypt_view[0] > 0x64:
            # I believe 0x64 is some kind of marker for the beginning of a save section
            # The game uses 30 save sections (0x1E)
            LOGGER.error(
                f"Section marker should be equal to '0x64' at offset 0x{next_decrypt_offset:X}."
                f" The value is {decrypt_view[0]}"
            )
            return DecryptionResult(CryptionReturnCodes.MISSING_REQUIRED_SECTION_HEADER_BYTE, b"")

        cipher_key = update_cipher_key(cipher_key, decrypt_view)

        cipher_ebc = AES.new(cipher_key[:32], mode=AES.MODE_ECB)

        first_item_offset = TALES_OF_ARISE_SAVE_ITEM_SECTION_HEADER_FIRST_ITEM_OFFSET
        next_decrypt_offset = int.from_bytes(
            decrypt_view[first_item_offset : first_item_offset + 4],
            "little",
        )
        if next_decrypt_offset >= len(save_payload):
            LOGGER.error(
                f"Cannot dencrypt buffer with next decryption offset 0x{next_decrypt_offset:X} greater"
                f" than the size of the save payload size 0x{len(save_payload):X}.\n"
                " Is this a proper Tales of Arise encrypted save file?"
            )
            return DecryptionResult(CryptionReturnCodes.NEXT_OFFSET_OUT_OF_BOUNDS, b"")

        # This section looks like the save item section
        # Get the number of save item entries
        item_count_offset = TALES_OF_ARISE_SAVE_ITEM_SECTION_HEADER_ITEM_COUNT_OFFSET
        item_entry_count = int.from_bytes(
            decrypt_view[item_count_offset : item_count_offset + 4],
            "little",
        )
        for _ in range(item_entry_count):
            decrypted_block_size = TALES_OF_ARISE_SAVE_ITEM_HEADER_SIZE
            # Create a memory view at the loop offset
            encrypted_view = memoryview(save_payload)[next_decrypt_offset : next_decrypt_offset + decrypted_block_size]
            absolute_offset = TALES_OF_ARISE_SAVE_BLOCK_START + next_decrypt_offset
            LOGGER.debug(
                f"Decryption of bytes at (abs offset=0x{absolute_offset:X}, rel offset=0x{next_decrypt_offset:X},"
                f" size={len(encrypted_view)})"
            )
            LOGGER.debug("The cipher key is:")
            LOGGER.debug(format_hex(cipher_key))
            LOGGER.debug("The encrypted view is:")
            LOGGER.debug(format_hex(encrypted_view))

            decrypt_view = memoryview(decrypted_save_buffer)[
                next_decrypt_offset : next_decrypt_offset + decrypted_block_size
            ]

            xor_buffer_string = format_hex(plaintext_xor_table)
            decrypt_view, plaintext_xor_table = __class__.decrypt_block(  # type: ignore[name-defined]
                cipher_ebc,
                decrypt_view,
                memoryview(encrypted_view),
                perform_xor_cipher,
                memoryview(plaintext_xor_table),
                platform_cryption_data.xor_table_transform_func,
            )
            if perform_xor_cipher:
                LOGGER.debug("The xor table is:")
                LOGGER.debug(xor_buffer_string)
            LOGGER.debug("The plaintext buffer is:")
            LOGGER.debug(format_hex(decrypt_view))

            next_block_offset = int.from_bytes(
                decrypt_view[
                    TALES_OF_ARISE_SAVE_ITEM_HEADER_NEXT_ITEM_OFFSET : TALES_OF_ARISE_SAVE_ITEM_HEADER_NEXT_ITEM_OFFSET
                    + 4
                ],
                "little",
            )

            # Read the next 16 bytes
            cipher_key = update_cipher_key(
                cipher_key,
                decrypt_view,
            )
            cipher_ebc = AES.new(cipher_key[:32], mode=AES.MODE_ECB)
            next_decrypt_offset += TALES_OF_ARISE_SAVE_ITEM_HEADER_SIZE

            # Read the decrypted block size from decrypt_view + 0x8
            decrypted_block_size = int.from_bytes(
                decrypt_view[
                    TALES_OF_ARISE_SAVE_ITEM_HEADER_DATA_SIZE_OFFSET : TALES_OF_ARISE_SAVE_ITEM_HEADER_DATA_SIZE_OFFSET
                    + 4
                ],
                "little",
            )
            encrypted_view = memoryview(save_payload)[next_decrypt_offset : next_decrypt_offset + decrypted_block_size]
            absolute_offset = TALES_OF_ARISE_SAVE_BLOCK_START + next_decrypt_offset
            LOGGER.debug(
                f"Decryption of bytes at (abs offset=0x{absolute_offset:X}, rel offset=0x{next_decrypt_offset:X},"
                f" size={len(encrypted_view)})"
            )
            LOGGER.debug("The cipher key is:")
            LOGGER.debug(format_hex(cipher_key))
            LOGGER.debug("The encrypted view is:")
            LOGGER.debug(format_hex(encrypted_view))

            decrypt_view = memoryview(decrypted_save_buffer)[
                next_decrypt_offset : next_decrypt_offset + decrypted_block_size
            ]

            xor_buffer_string = format_hex(plaintext_xor_table)
            decrypt_view, plaintext_xor_table = __class__.decrypt_block(  # type: ignore[name-defined]
                cipher_ebc,
                decrypt_view,
                memoryview(encrypted_view),
                perform_xor_cipher,
                memoryview(plaintext_xor_table),
                platform_cryption_data.xor_table_transform_func,
            )
            if perform_xor_cipher:
                LOGGER.debug("The xor table is:")
                LOGGER.debug(xor_buffer_string)
            LOGGER.debug("The plaintext buffer is:")
            LOGGER.debug(format_hex(decrypt_view))

            cipher_key = update_cipher_key(cipher_key, decrypt_view)
            cipher_ebc = AES.new(cipher_key[:32], mode=AES.MODE_ECB)
            next_decrypt_offset = next_block_offset

        complete_save_content: bytes = save_file_content[:TALES_OF_ARISE_SAVE_BLOCK_START] + decrypted_save_buffer
        return DecryptionResult(CryptionReturnCodes.SUCCESS, complete_save_content)


class SaveEncryptArise(SaveCryptBase):
    """
    Encrypts a decrypted Tales of Arive save using the specified save format
    """

    _patch_metadata_file: Path | None = None

    def __init__(self, args: argparse.Namespace):
        super().__init__(args)
        if getattr(args, "patch_metadata", self._save_format in SUPPORTED_PATCH_FILE_PLATFORMS):
            self._patch_metadata_file = args.patch_metadata_file

        # Override default output path from base SaveCryptBase
        output_path: Path | None = getattr(args, "output", None)
        if not output_path:
            self._output_path: Path = self._output_path.with_suffix(self._output_path.suffix + ".enc")

    @override
    def _pre_transform(self) -> bool:
        return super()._pre_transform()

    @override
    def _transform(self) -> bool:

        if self._save_format in SUPPORTED_SAVE_FORMATS:
            enc_result = self.encrypt_save_buffer(
                self._input_data, create_cryption_data_from_save_format(self._save_format)
            )
            if enc_result.return_code == CryptionReturnCodes.SUCCESS:
                output_buffer = enc_result.encrypted_buffer
                # Patch metadata logic
                if self._patch_metadata_file and self._patch_metadata_file.exists():
                    with self._patch_metadata_file.open("rb") as f:
                        # Write out the patch file bytes if it exist and the platform is supported
                        output_buffer = (
                            f.read(TALES_OF_ARISE_SAVE_BLOCK_START)
                            + enc_result.encrypted_buffer[TALES_OF_ARISE_SAVE_BLOCK_START:]
                        )
                bytes_written = self._output_io.write(output_buffer)
                return bytes_written == len(output_buffer)
            else:
                LOGGER.error(f"Encryption Failed with rc {enc_result.return_code}")
                return False
        else:
            LOGGER.error(f"Unsupported encrypt save format supplied {self._save_format}. Cannot encrypt...")
            return False

    @override
    def _post_transform(self) -> bool:
        return super()._post_transform()

    @staticmethod
    def sha1_save_buffer(save_payload: bytes | bytearray | memoryview) -> bytes:
        """
        Sha1 a block of encrypted save data
        Check range is relative to offset 0x32058
        """
        hash = hashlib.sha1(save_payload)
        return hash.digest()

    @staticmethod
    def encrypt_block(
        cipher_ebc,
        encrypt_buffer: memoryview,
        decrypted_buffer: memoryview,
        perform_xor_cipher: bool,
        xor_table: bytes | memoryview,
        xor_table_transform_func: Callable[[memoryview, memoryview], bytes],
    ) -> EncryptedTextAndUpdatedXorTableTuple:
        """
        XORs the plain text data with the xor_table in 64 byte chunks and then runs that data through AES encryption
        This method then updates the xor table to the new encrypted buffer

        If the block > 64 bytes, the XOR table is updated to the new encrypted buffer 64 bytes every iteration

        :param: perform_xor_cipher - If True the plaintext data is Xored with a 64-byte cipher before AES-ECB encryption

        :return: Returns a tuple of the encrypted data updated XOR table after the block has been encrypted
        """
        MAX_BLOCK_SIZE = 64
        remaining_bytes_to_encrypt: int = len(decrypted_buffer)
        new_xor_table: bytes = bytes(xor_table)
        offset: int = 0
        xored_view_buffer_string = ""
        while remaining_bytes_to_encrypt != 0:
            decrypted_view = memoryview(decrypted_buffer)[
                offset : offset + min(remaining_bytes_to_encrypt, MAX_BLOCK_SIZE)
            ]
            encrypt_view = memoryview(encrypt_buffer)[offset : offset + len(decrypted_view)]
            xored_buffer: memoryview | bytes = decrypted_view
            if perform_xor_cipher:
                # XOR the plaintext data with the XOR Cipher
                xored_buffer = xor_table_transform_func(decrypted_view, memoryview(new_xor_table))
                xored_view_buffer_string += format_hex(xored_buffer)

            # Next run the XOR'ed text through encryption
            cipher_ebc.encrypt(xored_buffer, encrypt_view)
            # Update the XOR table with the newly encrypted data
            new_xor_table = update_xor_table(new_xor_table, encrypt_view)
            remaining_bytes_to_encrypt -= len(decrypted_view)
            offset += len(decrypted_view)

        if perform_xor_cipher:
            LOGGER.debug("The xor'ed view is:")
            LOGGER.debug(xored_view_buffer_string)
        return EncryptedTextAndUpdatedXorTableTuple(encrypt_buffer, new_xor_table)

    @staticmethod
    def encrypt_save_buffer(
        save_file_content: bytes,
        platform_cryption_data: PlatformCryptionData,
    ) -> EncryptionResult:
        """
        Encrypts a Tales of Arise save
        """
        cipher_key: bytes | memoryview = platform_cryption_data.first_cipher_key
        plaintext_xor_table: bytes = platform_cryption_data.first_xor_cipher_table
        save_payload = memoryview(save_file_content)[TALES_OF_ARISE_SAVE_BLOCK_START:]
        encrypted_save_buffer: bytearray = bytearray(save_payload)

        xor_cipher_byte = platform_cryption_data.xor_cipher_byte
        perform_xor_cipher: bool = (
            save_payload[abs_to_rel_offset(TALES_OF_ARISE_SAVE_XOR_CIPHER_OFFSET)] == xor_cipher_byte
        )
        encrypted_block_size: int = 0x40
        next_encrypt_offset: int = abs_to_rel_offset(TALES_OF_ARISE_SAVE_ENCRYPTED_BLOCK_START)
        decrypted_view: memoryview[int] = memoryview(save_payload)[
            next_encrypt_offset : next_encrypt_offset + encrypted_block_size
        ]

        absolute_offset: int = TALES_OF_ARISE_SAVE_BLOCK_START + next_encrypt_offset
        LOGGER.debug(
            f"Encryption of bytes at (abs offset=0x{absolute_offset:X}, rel offset=0x{next_encrypt_offset:X},"
            f" size={len(decrypted_view)})"
        )
        LOGGER.debug("The cipher key is:")
        LOGGER.debug(format_hex(cipher_key))
        LOGGER.debug("The decrypted_view is:")
        LOGGER.debug(format_hex(decrypted_view))

        encrypt_view: memoryview[int] = memoryview(encrypted_save_buffer)[
            next_encrypt_offset : next_encrypt_offset + encrypted_block_size
        ]

        cipher_ebc = AES.new(cipher_key[:32], mode=AES.MODE_ECB)
        if perform_xor_cipher:
            xor_buffer_string = format_hex(plaintext_xor_table)
            LOGGER.debug("The xor table is:")
            LOGGER.debug(xor_buffer_string)

        encrypt_view, plaintext_xor_table = __class__.encrypt_block(  # type: ignore[name-defined]
            cipher_ebc,
            encrypt_view,
            memoryview(decrypted_view),
            perform_xor_cipher,
            memoryview(plaintext_xor_table),
            platform_cryption_data.xor_table_transform_func,
        )
        LOGGER.debug("The encrypted buffer is:")
        LOGGER.debug(format_hex(encrypt_view))

        cipher_key = update_cipher_key(cipher_key, decrypted_view)
        # Update the AES key
        cipher_ebc = AES.new(cipher_key[:32], mode=AES.MODE_ECB)

        # For PC platforms, the 10th dword is the offset that is decrypted next.
        # For Sony platforms, the 6th dowrd is the offset that is decrypted next.
        next_encrypt_offset = int.from_bytes(
            decrypted_view[
                platform_cryption_data.first_block_dword_offset : platform_cryption_data.first_block_dword_offset + 4
            ],
            "little",
        )
        if next_encrypt_offset >= len(save_payload):
            LOGGER.error(
                f"Cannot encrypt buffer with a next encryption offset {next_encrypt_offset} that greater"
                f" than the size of the save payload size {len(save_payload)}.\n"
                " Is this a proper Tales of Arise decrypted save file?"
            )
            return EncryptionResult(CryptionReturnCodes.NEXT_OFFSET_OUT_OF_BOUNDS, b"")
        elif next_encrypt_offset % 4 != 0:
            LOGGER.error(
                "The offset to encrypt from the offset table must be 4-byte aligned\n"
                f"The alignment is {next_encrypt_offset % 4}."
                " Is this a proper Tales of Arise decrypted save file?"
            )
            return EncryptionResult(CryptionReturnCodes.FIRST_OFFSET_TABLE_ENTRY_NOT_4_BYTE_ALIGNED, b"")

        # Create a memory view of the 64 bytes at the next offset
        decrypted_view = memoryview(save_payload)[next_encrypt_offset : next_encrypt_offset + encrypted_block_size]
        absolute_offset = TALES_OF_ARISE_SAVE_BLOCK_START + next_encrypt_offset
        LOGGER.debug(
            f"Encryption of bytes at (abs offset=0x{absolute_offset:X}, rel offset=0x{next_encrypt_offset:X},"
            f" size={len(decrypted_view)})"
        )
        LOGGER.debug("The cipher key is:")
        LOGGER.debug(format_hex(cipher_key))
        LOGGER.debug("The decrypted_view is:")
        LOGGER.debug(format_hex(decrypted_view))

        encrypt_view = memoryview(encrypted_save_buffer)[
            next_encrypt_offset : next_encrypt_offset + encrypted_block_size
        ]

        if perform_xor_cipher:
            xor_buffer_string = format_hex(plaintext_xor_table)
            LOGGER.debug("The xor table is:")
            LOGGER.debug(xor_buffer_string)
        encrypt_view, plaintext_xor_table = __class__.encrypt_block(  # type: ignore[name-defined]
            cipher_ebc,
            encrypt_view,
            memoryview(decrypted_view),
            perform_xor_cipher,
            memoryview(plaintext_xor_table),
            platform_cryption_data.xor_table_transform_func,
        )

        LOGGER.debug("The encrypted buffer is:")
        LOGGER.debug(format_hex(encrypt_view))

        if decrypted_view[0] > 0x64:
            LOGGER.error(
                f"Section marker should be 0x64 hex at offset 0x{next_encrypt_offset}. The value is {decrypted_view[0]}"
            )
            return EncryptionResult(CryptionReturnCodes.MISSING_REQUIRED_SECTION_HEADER_BYTE, b"")

        cipher_key = update_cipher_key(cipher_key, decrypted_view)

        cipher_ebc = AES.new(cipher_key[:32], mode=AES.MODE_ECB)

        first_item_offset = TALES_OF_ARISE_SAVE_ITEM_SECTION_HEADER_FIRST_ITEM_OFFSET
        next_encrypt_offset = int.from_bytes(
            decrypted_view[first_item_offset : first_item_offset + 4],
            "little",
        )
        if next_encrypt_offset >= len(save_payload):
            LOGGER.error(
                f"Cannot encrypt buffer with a next encryption offset {next_encrypt_offset} that greater"
                f" than the size of the save payload size {len(save_payload)}.\n"
                " Is this a proper Tales of Arise decrypted save file?"
            )
            return EncryptionResult(CryptionReturnCodes.NEXT_OFFSET_OUT_OF_BOUNDS, b"")

        # This section looks like the save item section
        # Get the number of save item entries
        item_count_offset = TALES_OF_ARISE_SAVE_ITEM_SECTION_HEADER_ITEM_COUNT_OFFSET
        item_entry_count = int.from_bytes(
            decrypted_view[item_count_offset : item_count_offset + 4],
            "little",
        )
        for _ in range(item_entry_count):
            encrypted_block_size = TALES_OF_ARISE_SAVE_ITEM_HEADER_SIZE
            # Create a memory view at the loop offset
            decrypted_view = memoryview(save_payload)[next_encrypt_offset : next_encrypt_offset + encrypted_block_size]
            absolute_offset = TALES_OF_ARISE_SAVE_BLOCK_START + next_encrypt_offset
            LOGGER.debug(
                f"Encryption of bytes at (abs offset=0x{absolute_offset:X}, rel offset=0x{next_encrypt_offset:X},"
                f" size={len(decrypted_view)})"
            )
            LOGGER.debug("The cipher key is:")
            LOGGER.debug(format_hex(cipher_key))
            LOGGER.debug("The decrypted_view is:")
            LOGGER.debug(format_hex(decrypted_view))

            encrypt_view = memoryview(encrypted_save_buffer)[
                next_encrypt_offset : next_encrypt_offset + encrypted_block_size
            ]

            if perform_xor_cipher:
                xor_buffer_string = format_hex(plaintext_xor_table)
                LOGGER.debug("The xor table is:")
                LOGGER.debug(xor_buffer_string)
            encrypt_view, plaintext_xor_table = __class__.encrypt_block(  # type: ignore[name-defined]
                cipher_ebc,
                encrypt_view,
                memoryview(decrypted_view),
                perform_xor_cipher,
                memoryview(plaintext_xor_table),
                platform_cryption_data.xor_table_transform_func,
            )
            LOGGER.debug("The encrypted buffer is:")
            LOGGER.debug(format_hex(encrypt_view))

            next_block_offset = int.from_bytes(
                decrypted_view[
                    TALES_OF_ARISE_SAVE_ITEM_HEADER_NEXT_ITEM_OFFSET : TALES_OF_ARISE_SAVE_ITEM_HEADER_NEXT_ITEM_OFFSET
                    + 4
                ],
                "little",
            )

            # Update the AES cipher key and advance 0x10 bytes to read the save data actual data
            cipher_key = update_cipher_key(
                cipher_key,
                decrypted_view,
            )
            cipher_ebc = AES.new(cipher_key[:32], mode=AES.MODE_ECB)
            next_encrypt_offset += TALES_OF_ARISE_SAVE_ITEM_HEADER_SIZE

            # Read the decrypted block size from decrypt_view + 0x8
            encrypted_block_size = int.from_bytes(
                decrypted_view[
                    TALES_OF_ARISE_SAVE_ITEM_HEADER_DATA_SIZE_OFFSET : TALES_OF_ARISE_SAVE_ITEM_HEADER_DATA_SIZE_OFFSET
                    + 4
                ],
                "little",
            )
            decrypted_view = memoryview(save_payload)[next_encrypt_offset : next_encrypt_offset + encrypted_block_size]
            absolute_offset = TALES_OF_ARISE_SAVE_BLOCK_START + next_encrypt_offset
            LOGGER.debug(
                f"Encryption of bytes at (abs offset=0x{absolute_offset:X}, rel offset=0x{next_encrypt_offset:X},"
                f" size={len(decrypted_view)})"
            )
            LOGGER.debug("The cipher key is:")
            LOGGER.debug(format_hex(cipher_key))
            LOGGER.debug("The decrypted_view is:")
            LOGGER.debug(format_hex(decrypted_view))

            encrypt_view = memoryview(encrypted_save_buffer)[
                next_encrypt_offset : next_encrypt_offset + encrypted_block_size
            ]

            xor_buffer_string = format_hex(plaintext_xor_table)
            if perform_xor_cipher:
                LOGGER.debug("The xor table is:")
                LOGGER.debug(xor_buffer_string)

            encrypt_view, plaintext_xor_table = __class__.encrypt_block(  # type: ignore[name-defined]
                cipher_ebc,
                encrypt_view,
                memoryview(decrypted_view),
                perform_xor_cipher,
                memoryview(plaintext_xor_table),
                platform_cryption_data.xor_table_transform_func,
            )
            LOGGER.debug("The plaintext buffer is:")
            LOGGER.debug(format_hex(encrypt_view))

            cipher_key = update_cipher_key(cipher_key, decrypted_view)
            cipher_ebc = AES.new(cipher_key[:32], mode=AES.MODE_ECB)
            next_encrypt_offset = next_block_offset

        # Update the sha1 hash of the encrypted save
        encrypted_block_start = TALES_OF_ARISE_SAVE_ENCRYPTED_BLOCK_START - TALES_OF_ARISE_SAVE_BLOCK_START
        encrypyted_sha1_start = TALES_OF_ARISE_SAVE_ENCRYPTED_SHA1_OFFSET - TALES_OF_ARISE_SAVE_BLOCK_START
        encrypted_sha1_view = memoryview(encrypted_save_buffer)[encrypyted_sha1_start : encrypyted_sha1_start + 0x14]
        encrypted_save_view = memoryview(encrypted_save_buffer)[encrypted_block_start:]
        encrypted_save_sha1_digest = __class__.sha1_save_buffer(encrypted_save_view)  # type: ignore[name-defined]
        encrypted_sha1_view[:] = encrypted_save_sha1_digest

        complete_save_content: bytes = save_file_content[:TALES_OF_ARISE_SAVE_BLOCK_START] + encrypted_save_buffer
        return EncryptionResult(CryptionReturnCodes.SUCCESS, complete_save_content)


class SaveConvertAriseDecrypted(SaveConvertBase):
    """
    Converts between a Source Format<->Target Format decrypted save

    What the conversion does is the following:
    1. Set the XOR Cipher byte to useindicate that the XOR cipher should be used
       to the appropriate value for the platform
    2. Swap the dwords that point to the start of the save item section header
       Those offsets are 0x32090 and 0x320A0 in the save data
    """

    def __init__(self, args: argparse.Namespace):
        super().__init__(args)

        # Override default output path from base SaveConvertBase
        output_path: Path | None = getattr(args, "output", None)
        if not output_path:
            self._output_path: Path = self._output_path.with_suffix(self._output_path.suffix + ".dec")

    @override
    def _pre_transform(self) -> bool:
        return super()._pre_transform()

    @override
    def _transform(self) -> bool:
        converted_offset_bytes = SaveConvertAriseDecrypted.convert_decrypyted_save_header(
            self._input_data, self._convert_format
        )
        expected_converted_bytes_size = TALES_OF_ARISE_SAVE_ENCRYPTED_OFFSET_BLOCK_END - TALES_OF_ARISE_SAVE_BLOCK_START
        if len(converted_offset_bytes) != expected_converted_bytes_size:
            LOGGER.error(
                f"Decrypted save conversion expected to transform {expected_converted_bytes_size} bytes.\n"
                f"However only {len(converted_offset_bytes)} would be transformed. Skipping..."
            )
            return False

        pre_header_stop = TALES_OF_ARISE_SAVE_BLOCK_START
        post_offset_stop = TALES_OF_ARISE_SAVE_ENCRYPTED_OFFSET_BLOCK_END
        bytes_written = self._output_io.write(
            self._input_data[:pre_header_stop] + converted_offset_bytes + self._input_data[post_offset_stop:]
        )
        return bytes_written != 0

    @override
    def _post_transform(self) -> bool:
        return super()._post_transform()

    @override
    def create_save_patch_table(self) -> ConvertPatchTable:
        return super().create_save_patch_table()

    @staticmethod
    def convert_decrypyted_save_header(
        source_buffer: bytes | bytearray | memoryview, convert_format: ConvertFormat
    ) -> bytes:
        """Swaps the 6th and 10th word of the offset block to convert between between platforms"""
        offset_block_end = TALES_OF_ARISE_SAVE_ENCRYPTED_OFFSET_BLOCK_END
        save_header_block = memoryview(source_buffer)[TALES_OF_ARISE_SAVE_BLOCK_START:offset_block_end]
        new_header_block: bytearray = bytearray(save_header_block)
        offset_block = memoryview(save_header_block)[TALES_OF_ARISE_SAVE_HEADER_SIZE:]
        new_offset_block = memoryview(new_header_block)[TALES_OF_ARISE_SAVE_HEADER_SIZE:]

        # Modify the Save Header block
        use_xor_cipher_offset = TALES_OF_ARISE_SAVE_XOR_CIPHER_OFFSET
        if convert_format.target in SUPPORTED_SAVE_FORMATS:
            cryption_data = create_cryption_data_from_save_format(convert_format.target)
            new_header_block[abs_to_rel_offset(use_xor_cipher_offset)] = cryption_data.xor_cipher_byte
        else:
            LOGGER.error(
                "Target Save Format not supported."
                f" The XOR_CIPHER_BYTE value at offset 0x{use_xor_cipher_offset:X} has been left unchanged"
            )

        # Modify the offset table entry that points to the Save Item Section
        if convert_format in SUPPORTED_CONVERT_FORMATS:
            # Swap the 6th(0x1C) and 10th(0x28) dwords in the offset block depending on the platform
            source_cryption_data = create_cryption_data_from_save_format(convert_format.source)
            target_cryption_data = create_cryption_data_from_save_format(convert_format.target)
            source_save_offset = source_cryption_data.first_block_dword_offset
            target_save_offset = target_cryption_data.first_block_dword_offset

            # If the source save offset and target sae offset are the same, then there is nothing
            # to swap. So return the header block unchanged.
            if source_save_offset != target_save_offset:
                new_offset_block[source_save_offset : source_save_offset + 4] = offset_block[
                    target_save_offset : target_save_offset + 4
                ]
                new_offset_block[target_save_offset : target_save_offset + 4] = offset_block[
                    source_save_offset : source_save_offset + 4
                ]
        elif convert_format.source != convert_format.target:
            LOGGER.error(f"Unsupported decryption conversion {convert_format}")
            return b""

        return bytes(new_header_block)


class SaveConvertAriseEncrypted(SaveConvertBase):
    """
    Converts a Tales of Arise Encrypted save from a source to a target format
    It combines all three of the encryption operations above.
    1. Decrypts the source save using the @source key of the ConvertFormat
    2. Converts the decrypted save data from the source save format to the target save format
    3. Encrypts the converted save data to the @target key of the ConvertFormat
    """

    # Path to file to patch first 0x32058 of the save with
    # Used for the menu thumbnail and whether the PS5 would allow the save the load
    _patch_metadata_file: Path | None = None

    def __init__(self, args: argparse.Namespace):
        super().__init__(args)
        if getattr(args, "patch_metadata", self._convert_format.target in SUPPORTED_PATCH_FILE_PLATFORMS):
            self._patch_metadata_file = args.patch_metadata_file

        # Override default output path from base SaveConvertBase
        output_path: Path | None = getattr(args, "output", None)
        if not output_path:
            self._output_path: Path = self._output_path.with_suffix(self._output_path.suffix + ".enc")

    @override
    def _pre_transform(self) -> bool:
        return super()._pre_transform()

    @override
    def _transform(self) -> bool:
        if self._convert_format.source not in SUPPORTED_SAVE_FORMATS:
            LOGGER.error(f"Unsupported source save format supplied {self._convert_format.source}. Cannot decrypt...")
            return False

        if self._convert_format.target not in SUPPORTED_SAVE_FORMATS:
            LOGGER.error(f"Unsupported target save format supplied {self._convert_format.target}. Cannot encrypt...")
            return False

        # Decrypt save using source cipher key and XOR table
        dec_result = SaveDecryptArise.decrypt_save_buffer(
            self._input_data, create_cryption_data_from_save_format(self._convert_format.source)
        )
        if dec_result.return_code != CryptionReturnCodes.SUCCESS:
            LOGGER.error(f"Decryption Failed with rc {dec_result.return_code}")
            return False

        # Convert Decrypted Save between source and target formats
        converted_offset_bytes = SaveConvertAriseDecrypted.convert_decrypyted_save_header(
            dec_result.plaintext_buffer, self._convert_format
        )
        expected_converted_bytes_size = TALES_OF_ARISE_SAVE_ENCRYPTED_OFFSET_BLOCK_END - TALES_OF_ARISE_SAVE_BLOCK_START
        if len(converted_offset_bytes) != expected_converted_bytes_size:
            LOGGER.error(
                f"Decrypted save conversion expected to transform {expected_converted_bytes_size} bytes.\n"
                f"However only {len(converted_offset_bytes)} would be transformed. Skipping..."
            )
            return False

        pre_header_stop = TALES_OF_ARISE_SAVE_BLOCK_START
        post_offset_stop = TALES_OF_ARISE_SAVE_ENCRYPTED_OFFSET_BLOCK_END
        converted_plaintext_buffer: bytes = (
            dec_result.plaintext_buffer[:pre_header_stop]
            + converted_offset_bytes
            + dec_result.plaintext_buffer[post_offset_stop:]
        )

        # Encrypt save using the target cipher key and XOR table
        enc_result = SaveEncryptArise.encrypt_save_buffer(
            converted_plaintext_buffer, create_cryption_data_from_save_format(self._convert_format.target)
        )
        if enc_result.return_code == CryptionReturnCodes.SUCCESS:
            output_buffer = enc_result.encrypted_buffer
            # Patch metadata logic
            if self._patch_metadata_file and self._patch_metadata_file.exists():
                with self._patch_metadata_file.open("rb") as f:
                    # Write out the patch file bytes if it exist and the platform is supported
                    output_buffer = (
                        f.read(TALES_OF_ARISE_SAVE_BLOCK_START)
                        + enc_result.encrypted_buffer[TALES_OF_ARISE_SAVE_BLOCK_START:]
                    )
            bytes_written = self._output_io.write(output_buffer)
            return bytes_written == len(output_buffer)
        LOGGER.error(f"Encryption Failed with rc {enc_result.return_code}")
        return False

    @override
    def _post_transform(self) -> bool:
        return super()._post_transform()

    @override
    def create_save_patch_table(self) -> ConvertPatchTable:
        return super().create_save_patch_table()


class SaveDumpItemOffsetsArise(SaveBase):
    """
    Dumps the 30(0x1E) Save Item offsets from a decrypted save file
    Can be used to determine where to build a save editor
    """

    _input_path: Path
    _input_data: bytes
    _save_format: SaveFormat
    _save_section_table: SaveItemSectionTable

    def __init__(self, args: argparse.Namespace):
        self._input_path = args.input
        self._input_data = b""
        self._save_format = getattr(args, "save_format", SaveFormat.UNK)
        self._save_section_table = SaveItemSectionTable()

    @override
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
    def _transform(self) -> bool:
        if self._save_format in SUPPORTED_SAVE_FORMATS:
            dump_result = self.dump_save_section_offsets(self._input_data, self._save_format)
            if dump_result.return_code != CryptionReturnCodes.SUCCESS:
                LOGGER.error(f"Data dump Failed with rc {dump_result.return_code}")
                return False
            self._save_section_table = dump_result.save_item_section_table
        else:
            LOGGER.error(f"Unsupported decrypt save format supplied {self._save_format}. Cannot dump...")
            return False

        return True

    @override
    def _post_transform(self) -> bool:
        """
        Write the save section offsets to stdout
        """
        for index, (section_name, (header_offset, data_offset, size)) in enumerate(self._save_section_table.items()):
            print(f"SectionName {index}: {section_name}")
            print(f"  HeaderOffset: rel=0x{header_offset:X}, abs=0x{header_offset + TALES_OF_ARISE_SAVE_BLOCK_START:X}")
            print(f"  DataOffset: rel=0x{data_offset:X}, abs=0x{data_offset + TALES_OF_ARISE_SAVE_BLOCK_START:X}")
            print(f"  Size: 0x{size:X}")
        return True

    @staticmethod
    def dump_save_section_offsets(
        save_file_content: bytes,
        save_format: SaveFormat,
    ) -> DumpItemSectionResult:
        """
        Dumps the offsets to the Save Item sections within the decrypted save file
        The size of the section is dumped along size the offset where the section header and data begins
        """
        save_payload = memoryview(save_file_content)[TALES_OF_ARISE_SAVE_BLOCK_START:]

        offset_block = save_payload[
            abs_to_rel_offset(TALES_OF_ARISE_SAVE_ENCRYPTED_BLOCK_START) : abs_to_rel_offset(
                TALES_OF_ARISE_SAVE_ENCRYPTED_OFFSET_BLOCK_END
            )
        ]

        # For Microsoft platforms, the 10th dword is the offset that to the save item section header.
        # For Sony platforms, the 6th dowrd is the offset that to the save item section header.
        if save_format in SUPPORTED_SAVE_FORMATS:
            platform_cryption_data = create_cryption_data_from_save_format(save_format)
            first_block_dword_offset = platform_cryption_data.first_block_dword_offset
            save_item_section_header_offset: int = int.from_bytes(
                offset_block[first_block_dword_offset : first_block_dword_offset + 4],
                "little",
            )
        else:
            LOGGER.error(f"Unknown Save Format: Cannot read section item header for save format {save_format}")
            return DumpItemSectionResult(CryptionReturnCodes.UNKNOWN_SAVE_FORMAT, SaveItemSectionTable())

        # Create a memory view to the Save Item Section Header
        save_item_section_header = memoryview(save_payload)[
            save_item_section_header_offset : save_item_section_header_offset
            + TALES_OF_ARISE_SAVE_ITEM_SECTION_HEADER_SIZE
        ]
        item_count_offset = TALES_OF_ARISE_SAVE_ITEM_SECTION_HEADER_ITEM_COUNT_OFFSET
        item_entry_count: int = int.from_bytes(
            save_item_section_header[item_count_offset : item_count_offset + 4],
            "little",
        )

        save_item_table: SaveItemSectionTable = SaveItemSectionTable()

        # Read the offset for the first save item section - Should be the "Entitlement" section
        first_item_offset = TALES_OF_ARISE_SAVE_ITEM_SECTION_HEADER_FIRST_ITEM_OFFSET
        save_item_header_offset = int.from_bytes(
            save_item_section_header[first_item_offset : first_item_offset + 4],
            "little",
        )
        for _, section_name in zip(range(item_entry_count), SaveItemSectionEnum):
            save_item_header = memoryview(save_payload)[
                save_item_header_offset : save_item_header_offset + TALES_OF_ARISE_SAVE_ITEM_HEADER_SIZE
            ]
            save_item_data_offset: int = save_item_header_offset + TALES_OF_ARISE_SAVE_ITEM_HEADER_SIZE
            # Read the size of the save item section
            save_item_size = int.from_bytes(
                save_item_header[
                    TALES_OF_ARISE_SAVE_ITEM_HEADER_DATA_SIZE_OFFSET : TALES_OF_ARISE_SAVE_ITEM_HEADER_DATA_SIZE_OFFSET
                    + 4
                ],
                "little",
            )
            save_item_table[section_name] = SaveItemSection(
                save_item_header_offset, save_item_data_offset, save_item_size
            )

            # Update the the next save item header  offsete
            save_item_header_offset = int.from_bytes(
                save_item_header[
                    TALES_OF_ARISE_SAVE_ITEM_HEADER_NEXT_ITEM_OFFSET : TALES_OF_ARISE_SAVE_ITEM_HEADER_NEXT_ITEM_OFFSET
                    + 4
                ],
                "little",
            )

        return DumpItemSectionResult(CryptionReturnCodes.SUCCESS, save_item_table)


### Start of argument parser setup
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
        if values in [str(format) for format in SUPPORTED_CONVERT_FORMATS]:
            setattr(namespace, self.dest, ConvertFormat.create_from_string(values))
        else:
            raise ValueError(f"Value {values} is not an appropriate choice for argument {options_string}")


def add_general_arguments(parser: argparse.ArgumentParser) -> None:
    # Add general arguments
    _ = parser.add_argument(
        "--input",
        "-i",
        type=Path,
        help="Input path to save file",
        required=True,
    )
    _ = parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output path to save file. Defaults to <input-file-path>.<target-format>.[dec|enc] if not specified",
    )


def add_convert_arguments(parser: argparse.ArgumentParser) -> None:
    add_general_arguments(parser)
    # Add convert specific arguments
    _ = parser.add_argument(
        "--convert-format",
        "-f",
        required=True,
        action=ConvertFormatAction,
        choices=[str(format) for format in SUPPORTED_CONVERT_FORMATS],
        help="Specifies the input file save format and desired the output file format.",
    )
    _ = parser.add_argument(
        "--patch-metadata",
        "-p",
        action=argparse.BooleanOptionalAction,
        default=argparse.SUPPRESS,
        help="Patches the save metadata which contains the thumbnail and state data shown in the save menu.\n"
        "This is needed when converting a native PC save -> PS4/PS5 to allow the Save Menu to load the save.\n"
        f"This replaces the first 0x{TALES_OF_ARISE_SAVE_BLOCK_START:X} bytes within the save file with values"
        " from a new game save for PS4/PS5\n"
        "(PS4/PS5) Default=True, (Other) Default=False",
    )
    _ = parser.add_argument(
        "--patch-metadata-file",
        "-m",
        default=DEFAULT_PS5_PATCH_FILE,
        help="Override for the file used for patching metadata.",
    )


def add_crypt_arguments(parser: argparse.ArgumentParser) -> None:
    add_general_arguments(parser)
    # Add decrypt/encrypt specific arguments
    _ = parser.add_argument(
        "--save-format",
        "-s",
        required=True,
        choices=SUPPORTED_SAVE_FORMATS,
        default=SaveFormat.PC,
        help="Specifies the file save format.",
    )
    _ = parser.add_argument(
        "--patch-metadata",
        "-p",
        action=argparse.BooleanOptionalAction,
        default=argparse.SUPPRESS,
        help="Patches the save metadata which contains the thumbnail and state data shown in the save menu.\n"
        "This is needed when converting a native PC save -> PS4/PS5 to allow the Save Menu to load the save.\n"
        f"This replaces the first 0x{TALES_OF_ARISE_SAVE_BLOCK_START:X} bytes within the save file with values"
        " from a new game save for PS4/PS5\n"
        "(PS4/PS5) Default=True, (Other) Default=False",
    )
    _ = parser.add_argument(
        "--patch-metadata-file",
        "-m",
        default=DEFAULT_PS5_PATCH_FILE,
        help="Override for the file used for patching metadata.",
    )


def add_item_dumper_arguments(parser: argparse.ArgumentParser) -> None:
    _ = parser.add_argument(
        "--input",
        "-i",
        type=Path,
        help="Input path to decrypted save file",
        required=True,
    )
    _ = parser.add_argument(
        "--save-format",
        "-s",
        required=True,
        choices=SUPPORTED_SAVE_FORMATS,
        default=SaveFormat.PC,
        help="Specifies the decrypted file save format.",
    )


def add_commands(parser: argparse.ArgumentParser) -> None:
    parser.description = (
        "Save Converter and Encrypter/Decrypter for Tales of Arise\n"
        + "Supports PC, PS5, PS4 with experimental support for XBOX saves if they can be decrypted"
    )
    # Default to showing help if a sub command is not supplied
    parser.set_defaults(func=lambda _: parser.print_help(sys.stderr))

    arise_subparser = parser.add_subparsers()

    def add_convert_decrypted_save_parser():
        convert_decrypted_save_parser = arise_subparser.add_parser(
            "convert-decrypted-save",
            description="Convert decrypted Tales of Arise save from the source to target format",
        )
        add_convert_arguments(convert_decrypted_save_parser)

        def convert_decrypted_save(args: argparse.Namespace):
            if hasattr(args, "loglevel"):
                LOGGER.setLevel(args.loglevel)
            save_converter = SaveConvertAriseDecrypted(args)
            return save_converter.transform()

        convert_decrypted_save_parser.set_defaults(func=convert_decrypted_save)

    add_convert_decrypted_save_parser()

    def add_convert_encrypted_save_parser():
        convert_encrypted_save_parser = arise_subparser.add_parser(
            "convert-encrypted-save",
            description="Convert encrypted Tales of Arise save from the source to target format",
            aliases=["convert-save"],
        )
        add_convert_arguments(convert_encrypted_save_parser)

        def convert_encrypted_save(args: argparse.Namespace):
            if hasattr(args, "loglevel"):
                LOGGER.setLevel(args.loglevel)
            save_decrypter = SaveConvertAriseEncrypted(args)
            return save_decrypter.transform()

        convert_encrypted_save_parser.set_defaults(func=convert_encrypted_save)

    add_convert_encrypted_save_parser()

    def add_decrypt_save_parser():
        decrypt_parser = arise_subparser.add_parser(
            "decrypt-save", description="Decrypt Tales of Arise save for the specified save format", aliases=["decrypt"]
        )
        add_crypt_arguments(decrypt_parser)

        def decrypt_save(args: argparse.Namespace):
            if hasattr(args, "loglevel"):
                LOGGER.setLevel(args.loglevel)
            save_decrypter = SaveDecryptArise(args)
            return save_decrypter.transform()

        decrypt_parser.set_defaults(func=decrypt_save)

    add_decrypt_save_parser()

    def add_encrypt_save_parser():
        encrypt_parser = arise_subparser.add_parser(
            "encrypt-save", description="Encrypt Tales of Arise save for the specified save format", aliases=["encrypt"]
        )
        add_crypt_arguments(encrypt_parser)

        def encrypt_save(args: argparse.Namespace):
            if hasattr(args, "loglevel"):
                LOGGER.setLevel(args.loglevel)
            save_converter = SaveEncryptArise(args)
            return save_converter.transform()

        encrypt_parser.set_defaults(func=encrypt_save)

    add_encrypt_save_parser()

    def add_dump_save_item_offsets_parser():
        dump_save_item_offset_parser = arise_subparser.add_parser(
            "dump-decrypted-save-item-offsets",
            description="Dump the Save Item Section offsets of the specifed save format\n"
            "This can be used to build to determine the offsets to manipulate for a tool such as a save editor",
            aliases=["dump-save-item-offsets", "dump-save-offsets"],
        )
        add_item_dumper_arguments(dump_save_item_offset_parser)

        def dump_save_item(args: argparse.Namespace):
            if hasattr(args, "loglevel"):
                LOGGER.setLevel(args.loglevel)
            offset_dumper = SaveDumpItemOffsetsArise(args)
            return offset_dumper.transform()

        dump_save_item_offset_parser.set_defaults(func=dump_save_item)

    add_dump_save_item_offsets_parser()


def main():
    parser = argparse.ArgumentParser(
        description="Tool to convert, decrypt, encrypt or dump save offsets for Tales of Arise between"
        " PS4, PS5, PC, XBox One, XBox Series X",
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
        response = False

    sys.exit(response)


if __name__ == "__main__":
    main()
