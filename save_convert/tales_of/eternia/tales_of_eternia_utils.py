"""
Contains utility methods and constants for manipulating Tales of Eternia save data
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Any, override

from Crypto.Cipher import AES  # type: ignore[import-not-found]
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad, unpad

from save_convert.save_converter_base import (
    NSW_TO_PC_CONVERT_FORMAT,
    NSW_TO_PS4_CONVERT_FORMAT,
    NSW_TO_PS5_CONVERT_FORMAT,
    NSW_TO_XBOXONE_CONVERT_FORMAT,
    NSW_TO_XBOXSERIESX_CONVERT_FORMAT,
    PC_TO_NSW_CONVERT_FORMAT,
    PC_TO_PS4_CONVERT_FORMAT,
    PC_TO_PS5_CONVERT_FORMAT,
    PC_TO_XBOXONE_CONVERT_FORMAT,
    PC_TO_XBOXSERIESX_CONVERT_FORMAT,
    PS4_TO_NSW_CONVERT_FORMAT,
    PS4_TO_PC_CONVERT_FORMAT,
    PS4_TO_PS5_CONVERT_FORMAT,
    PS4_TO_XBOXONE_CONVERT_FORMAT,
    PS4_TO_XBOXSERIESX_CONVERT_FORMAT,
    PS5_TO_NSW_CONVERT_FORMAT,
    PS5_TO_PC_CONVERT_FORMAT,
    PS5_TO_PS4_CONVERT_FORMAT,
    PS5_TO_XBOXONE_CONVERT_FORMAT,
    PS5_TO_XBOXSERIESX_CONVERT_FORMAT,
    XBOXONE_TO_NSW_CONVERT_FORMAT,
    XBOXONE_TO_PC_CONVERT_FORMAT,
    XBOXONE_TO_PS4_CONVERT_FORMAT,
    XBOXONE_TO_PS5_CONVERT_FORMAT,
    XBOXONE_TO_XBOXSERIESX_CONVERT_FORMAT,
    XBOXSERIESX_TO_NSW_CONVERT_FORMAT,
    XBOXSERIESX_TO_PC_CONVERT_FORMAT,
    XBOXSERIESX_TO_PS4_CONVERT_FORMAT,
    XBOXSERIESX_TO_PS5_CONVERT_FORMAT,
    XBOXSERIESX_TO_XBOXONE_CONVERT_FORMAT,
    ConvertFormat,
    SaveFormat,
)

SCRIPT_DIR: Path = Path(__file__).parent.resolve()

LOGGER = logging.getLogger("eternia_save_converter_utils")
LOGGER.addHandler(logging.StreamHandler(sys.stdout))
LOGGER.setLevel(logging.INFO)

# Formats which supports encryption/decryption
SUPPORTED_CRYPT_SAVE_FORMATS: list[SaveFormat] = [
    SaveFormat.PC,
    SaveFormat.PS5,
    SaveFormat.PS4,
    SaveFormat.NSW,
    SaveFormat.XBOXONE,
    SaveFormat.XBOXSERIESX,
]

# Absolute offset in save file where the encrypted metadata is stored
ETERNIA_SAVE_SLOT_START_OFFSET_ABS = 0x0
# NOTE: The save file stores each section twice in succession
ETERNIA_SAVE_SLOT_SIZE = 0x61840
ETERNIA_SAVE_SLOT_HEADER_SIZE = 0x20

ETERNIA_REMASTERED_ENCRYPTED_SAVE_SIZE = ETERNIA_SAVE_SLOT_SIZE * 2

# The offset where the thumbnail PNG data starts
ETERNIA_PNG_START_OFFSET = 0x1800

ETERNIA_SAVE_SIZE_DICT: dict[SaveFormat, int] = {
    SaveFormat.PC: ETERNIA_REMASTERED_ENCRYPTED_SAVE_SIZE,
    SaveFormat.PS5: ETERNIA_REMASTERED_ENCRYPTED_SAVE_SIZE,
    SaveFormat.PS4: ETERNIA_REMASTERED_ENCRYPTED_SAVE_SIZE,
    SaveFormat.NSW: ETERNIA_REMASTERED_ENCRYPTED_SAVE_SIZE,
    SaveFormat.XBOXONE: ETERNIA_REMASTERED_ENCRYPTED_SAVE_SIZE,
    SaveFormat.XBOXSERIESX: ETERNIA_REMASTERED_ENCRYPTED_SAVE_SIZE,
}

# Each save data section is stored twice within the save file
ETERNIA_SECTION_ITER_COUNT = 2

SUPPORTED_CONVERT_FORMATS: list[ConvertFormat] = [
    PC_TO_NSW_CONVERT_FORMAT,
    PC_TO_PS5_CONVERT_FORMAT,
    PC_TO_PS4_CONVERT_FORMAT,
    PC_TO_XBOXONE_CONVERT_FORMAT,
    PC_TO_XBOXSERIESX_CONVERT_FORMAT,
    PS5_TO_NSW_CONVERT_FORMAT,
    PS5_TO_PC_CONVERT_FORMAT,
    PS5_TO_PS4_CONVERT_FORMAT,
    PS5_TO_XBOXONE_CONVERT_FORMAT,
    PS5_TO_XBOXSERIESX_CONVERT_FORMAT,
    PS4_TO_NSW_CONVERT_FORMAT,
    PS4_TO_PC_CONVERT_FORMAT,
    PS4_TO_PS5_CONVERT_FORMAT,
    PS4_TO_XBOXONE_CONVERT_FORMAT,
    PS4_TO_XBOXSERIESX_CONVERT_FORMAT,
    NSW_TO_PC_CONVERT_FORMAT,
    NSW_TO_PS5_CONVERT_FORMAT,
    NSW_TO_PS4_CONVERT_FORMAT,
    NSW_TO_XBOXONE_CONVERT_FORMAT,
    NSW_TO_XBOXSERIESX_CONVERT_FORMAT,
    XBOXONE_TO_NSW_CONVERT_FORMAT,
    XBOXONE_TO_PC_CONVERT_FORMAT,
    XBOXONE_TO_PS5_CONVERT_FORMAT,
    XBOXONE_TO_PS4_CONVERT_FORMAT,
    XBOXONE_TO_XBOXSERIESX_CONVERT_FORMAT,
    XBOXSERIESX_TO_NSW_CONVERT_FORMAT,
    XBOXSERIESX_TO_PC_CONVERT_FORMAT,
    XBOXSERIESX_TO_PS5_CONVERT_FORMAT,
    XBOXSERIESX_TO_PS4_CONVERT_FORMAT,
    XBOXSERIESX_TO_XBOXONE_CONVERT_FORMAT,
]


ETERNIA_ENCRYPTION_VERSION_OFFSET = 0x0
ETERNIA_ENCRYPTION_CIPHERTEXT_SIZE_OFFSET = 0x4
ETERNIA_DATA_START_ADDR_OFFSET = 0xC

ETERNIA_AES_BLOCK_SIZE = 16
ETERNIA_AES_KEY_LENGTH = 16
ETERNIA_AES_IV_LENGTH = 16
ETERNIA_GENERATE_PASSWORD = b"1123581321345589"
ETERNIA_PASSWORD_XOR = bytes.fromhex("8D EF 02 2D 1B DF 05 5A A1 8E 0C C3 37 BE 0B B4")

ETERNIA_XOR_PASSWORD = bytes([pass_c ^ xor_c for pass_c, xor_c in zip(ETERNIA_GENERATE_PASSWORD, ETERNIA_PASSWORD_XOR)])

ETERNIA_SAVE_SALT = b"saltString"
# Replicates the behavior of C# Encoding.UTF8.GetString when it tries to convert bytes outside the UTF-8 range back into
# UTF-8
# https://learn.microsoft.com/en-us/dotnet/api/system.text.encoding.utf8?view=net-10.0#remarks
ETERNIA_GENERATED_KEYS = PBKDF2(
    ETERNIA_XOR_PASSWORD.decode("utf-8", errors="replace").encode("utf-8"),  # type: ignore[arg-type]
    ETERNIA_SAVE_SALT,
    ETERNIA_AES_KEY_LENGTH + ETERNIA_AES_IV_LENGTH,
    count=1000,
)
ETERNIA_AES_SAVE_KEY = ETERNIA_GENERATED_KEYS[:16]
ETERNIA_AES_SAVE_IV = ETERNIA_GENERATED_KEYS[16:]

# Populating header template from a beginning of game PC save
ETERNIA_HEADER_TEMPLATE = bytes.fromhex(
    "01 00 00 00 10 18 06 00 01 4a d5 f3 20 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"
)


class SaveContents:
    """
    Stores the decrypted JSON contents of the Tales of Eternia Remastered save data
    which contain the complete save data (unlike Tales of Graces f which wraps the original PS3 save format)
    """

    save_data: bytes

    def __init__(self):
        self.save_data = bytes()

    def to_encrypt_bytes(self, output_data: bytearray, _save_format: SaveFormat) -> bool:
        """
        Encrypts the save data into a byte array
        """

        # Pad the buffer until it reaches AES block size
        padded_savedata_buffer = pad(self.save_data, ETERNIA_AES_BLOCK_SIZE)

        encrypt_buffer = bytearray(len(padded_savedata_buffer))

        cipher_cbc = AES.new(ETERNIA_AES_SAVE_KEY, mode=AES.MODE_CBC, iv=ETERNIA_AES_SAVE_IV)
        cipher_cbc.encrypt(padded_savedata_buffer, memoryview(encrypt_buffer))

        save_slot_header = bytearray(ETERNIA_HEADER_TEMPLATE)
        # Update the ciphertext size in case it is different from the template
        cipher_size_offset = ETERNIA_ENCRYPTION_CIPHERTEXT_SIZE_OFFSET
        save_slot_header[cipher_size_offset : cipher_size_offset + 4] = len(encrypt_buffer).to_bytes(
            length=4, byteorder="little"
        )

        encrypted_data = bytearray()
        encrypted_data += save_slot_header
        encrypted_data += encrypt_buffer
        # pad data with 0 bytes until it reaches the save slot size
        if len(encrypted_data) <= ETERNIA_SAVE_SLOT_SIZE:
            encrypted_data.resize(ETERNIA_SAVE_SLOT_SIZE)
        # Duplicate the save slot data and write to the output buffer
        output_data += encrypted_data * 2

        return True

    @staticmethod
    def from_encrypt_bytes(
        input_data: bytes | memoryview, output_save_contents: SaveContents, _save_format: SaveFormat
    ) -> bool:
        """
        Decrypts a byte array into a Tales of Eternia Remastered save file

        :return: After invoking this function the SaveContents instances contains the JSON data
        """
        if len(input_data) % 2 == 1:
            LOGGER.error(
                "Save slots must be the the same size. The save data has size %d which is not even" % (len(input_data),)
            )
            return False

        slot_size = len(input_data) // 2
        save_slot_0, save_slot_1 = input_data[:slot_size], input_data[slot_size:]
        if save_slot_0 != save_slot_1:
            LOGGER.warning("Save slot must contain identical data, Using save slot 0 data for decrypting")

        # Decrypt the save data if successfully read into memory
        start_offset = ETERNIA_ENCRYPTION_VERSION_OFFSET
        # The first 4 bytes is the version of the save data
        _version = int.from_bytes(input_data[start_offset : start_offset + 4], "little")

        # Next 4 bytes is the length of the ciphertext
        start_offset = ETERNIA_ENCRYPTION_CIPHERTEXT_SIZE_OFFSET
        ciphertext_size = int.from_bytes(input_data[start_offset : start_offset + 4], "little")

        start_offset = ETERNIA_DATA_START_ADDR_OFFSET
        data_start_offset = int.from_bytes(input_data[start_offset : start_offset + 4], "little")
        if data_start_offset != ETERNIA_SAVE_SLOT_HEADER_SIZE:
            LOGGER.error(
                (
                    "Save Data start offset does not start at the end of the Eternia save slot header.\nData Start=%d,"
                    + " Header end=%d"
                )
                % (data_start_offset, ETERNIA_SAVE_SLOT_HEADER_SIZE)
            )
            return False

        if ciphertext_size + data_start_offset >= len(save_slot_0):
            LOGGER.error(
                "Slot header + cipher text size %d must be less than the save slot size %d"
                % (data_start_offset + ciphertext_size, len(save_slot_0))
            )
            return False

        encrypted_view = memoryview(input_data)[data_start_offset : data_start_offset + ciphertext_size]
        decrypt_buffer = bytearray(len(encrypted_view))
        cipher_cbc = AES.new(ETERNIA_AES_SAVE_KEY, mode=AES.MODE_CBC, iv=ETERNIA_AES_SAVE_IV)
        try:
            cipher_cbc.decrypt(encrypted_view, decrypt_buffer)
            unpadded_buffer = unpad(bytes(decrypt_buffer), ETERNIA_AES_BLOCK_SIZE)
        except ValueError as err:
            LOGGER.error("Failed to decrypt bytes for eternia save: %s" % (err,))
            return False

        output_save_contents.save_data = unpadded_buffer

        return True


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


def add_crypt_arguments(parser: argparse.ArgumentParser) -> None:
    # Add decrypt/encrypt specific arguments
    _ = parser.add_argument(
        "--save-format",
        "-s",
        required=True,
        choices=SUPPORTED_CRYPT_SAVE_FORMATS,
        default=SaveFormat.PC,
        help="Specifies the file save format.",
    )


def add_decrypt_arguments(parser: argparse.ArgumentParser) -> None:
    add_crypt_arguments(parser)
    # Add decryption specific arguments
    _ = parser.add_argument(
        "--input",
        "-i",
        type=Path,
        help="Input path to encrypted save file",
        required=True,
    )
    _ = parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output path to store decrypted save. Defaults to <input-file-path>.<target-format>" + " if not specified",
    )


def add_encrypt_arguments(parser: argparse.ArgumentParser) -> None:
    add_crypt_arguments(parser)
    # Add encryption specific arguments
    _ = parser.add_argument(
        "--input",
        "-i",
        type=Path,
        help="Input path to decrypted save. Defaults to reading the files of SaveData.json," + "and TOGAPP.bin",
    )
    # output path argument
    _ = parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output path to store encrypted save. Defaults to <input-file-path>.<target-format>" + " if not specified",
    )
