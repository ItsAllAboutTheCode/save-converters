"""
Contains utility methods and constants for manipulating Tales of Xillia save data
"""

import argparse
import json
import logging
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, override

from Crypto.Cipher import AES  # type: ignore[import-not-found]
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad, unpad

from save_convert.save_converter_base import (
    NSW_TO_PC_CONVERT_FORMAT,
    NSW_TO_PS3_CONVERT_FORMAT,
    NSW_TO_PS4_CONVERT_FORMAT,
    NSW_TO_PS5_CONVERT_FORMAT,
    NSW_TO_XBOXONE_CONVERT_FORMAT,
    NSW_TO_XBOXSERIESX_CONVERT_FORMAT,
    PC_TO_NSW_CONVERT_FORMAT,
    PC_TO_PS3_CONVERT_FORMAT,
    PC_TO_PS4_CONVERT_FORMAT,
    PC_TO_PS5_CONVERT_FORMAT,
    PC_TO_XBOXONE_CONVERT_FORMAT,
    PC_TO_XBOXSERIESX_CONVERT_FORMAT,
    PS3_TO_NSW_CONVERT_FORMAT,
    PS3_TO_PC_CONVERT_FORMAT,
    PS3_TO_PS4_CONVERT_FORMAT,
    PS3_TO_PS5_CONVERT_FORMAT,
    PS3_TO_XBOXONE_CONVERT_FORMAT,
    PS3_TO_XBOXSERIESX_CONVERT_FORMAT,
    PS4_TO_NSW_CONVERT_FORMAT,
    PS4_TO_PC_CONVERT_FORMAT,
    PS4_TO_PS3_CONVERT_FORMAT,
    PS4_TO_PS5_CONVERT_FORMAT,
    PS4_TO_XBOXONE_CONVERT_FORMAT,
    PS4_TO_XBOXSERIESX_CONVERT_FORMAT,
    PS5_TO_NSW_CONVERT_FORMAT,
    PS5_TO_PC_CONVERT_FORMAT,
    PS5_TO_PS3_CONVERT_FORMAT,
    PS5_TO_PS4_CONVERT_FORMAT,
    PS5_TO_XBOXONE_CONVERT_FORMAT,
    PS5_TO_XBOXSERIESX_CONVERT_FORMAT,
    XBOXONE_TO_NSW_CONVERT_FORMAT,
    XBOXONE_TO_PC_CONVERT_FORMAT,
    XBOXONE_TO_PS3_CONVERT_FORMAT,
    XBOXONE_TO_PS4_CONVERT_FORMAT,
    XBOXONE_TO_PS5_CONVERT_FORMAT,
    XBOXONE_TO_XBOXSERIESX_CONVERT_FORMAT,
    XBOXSERIESX_TO_NSW_CONVERT_FORMAT,
    XBOXSERIESX_TO_PC_CONVERT_FORMAT,
    XBOXSERIESX_TO_PS3_CONVERT_FORMAT,
    XBOXSERIESX_TO_PS4_CONVERT_FORMAT,
    XBOXSERIESX_TO_PS5_CONVERT_FORMAT,
    XBOXSERIESX_TO_XBOXONE_CONVERT_FORMAT,
    ConvertFormat,
    SaveFormat,
)
from save_convert.tales_of.tales_of_utils import COMPACT_JSON_SEPARATORS
from save_convert.tales_of.xillia.tales_of_xillia_dicts import (
    XilliaRemasteredSaveDict,
    default_remastered_save_dict,
)

SCRIPT_DIR: Path = Path(__file__).parent.resolve()

LOGGER = logging.getLogger("xillia_save_converter_utils")
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

SUPPORTED_CONVERT_FORMATS: list[ConvertFormat] = [
    PS3_TO_PS4_CONVERT_FORMAT,
    PS3_TO_PS5_CONVERT_FORMAT,
    PS3_TO_PC_CONVERT_FORMAT,
    PS3_TO_NSW_CONVERT_FORMAT,
    PS3_TO_XBOXONE_CONVERT_FORMAT,
    PS3_TO_XBOXSERIESX_CONVERT_FORMAT,
    PC_TO_NSW_CONVERT_FORMAT,
    PC_TO_PS5_CONVERT_FORMAT,
    PC_TO_PS4_CONVERT_FORMAT,
    PC_TO_PS3_CONVERT_FORMAT,
    PC_TO_XBOXONE_CONVERT_FORMAT,
    PC_TO_XBOXSERIESX_CONVERT_FORMAT,
    PS5_TO_NSW_CONVERT_FORMAT,
    PS5_TO_PC_CONVERT_FORMAT,
    PS5_TO_PS4_CONVERT_FORMAT,
    PS5_TO_PS3_CONVERT_FORMAT,
    PS5_TO_XBOXONE_CONVERT_FORMAT,
    PS5_TO_XBOXSERIESX_CONVERT_FORMAT,
    PS4_TO_NSW_CONVERT_FORMAT,
    PS4_TO_PC_CONVERT_FORMAT,
    PS4_TO_PS5_CONVERT_FORMAT,
    PS4_TO_PS3_CONVERT_FORMAT,
    PS4_TO_XBOXONE_CONVERT_FORMAT,
    PS4_TO_XBOXSERIESX_CONVERT_FORMAT,
    NSW_TO_PC_CONVERT_FORMAT,
    NSW_TO_PS5_CONVERT_FORMAT,
    NSW_TO_PS4_CONVERT_FORMAT,
    NSW_TO_PS3_CONVERT_FORMAT,
    NSW_TO_XBOXONE_CONVERT_FORMAT,
    NSW_TO_XBOXSERIESX_CONVERT_FORMAT,
    XBOXONE_TO_NSW_CONVERT_FORMAT,
    XBOXONE_TO_PC_CONVERT_FORMAT,
    XBOXONE_TO_PS5_CONVERT_FORMAT,
    XBOXONE_TO_PS4_CONVERT_FORMAT,
    XBOXONE_TO_PS3_CONVERT_FORMAT,
    XBOXONE_TO_XBOXSERIESX_CONVERT_FORMAT,
    XBOXSERIESX_TO_NSW_CONVERT_FORMAT,
    XBOXSERIESX_TO_PC_CONVERT_FORMAT,
    XBOXSERIESX_TO_PS5_CONVERT_FORMAT,
    XBOXSERIESX_TO_PS4_CONVERT_FORMAT,
    XBOXSERIESX_TO_PS3_CONVERT_FORMAT,
    XBOXSERIESX_TO_XBOXONE_CONVERT_FORMAT,
]


XILLIA_ENCRYPTION_SALT_OFFSET = 0x0
XILLIA_ENCRYPTION_IV_OFFSET = 0x10
XILLIA_ENCRYPTION_START_OFFSET = 0x20


XILLIA_AES_BLOCK_SIZE = 16
XILLIA_AES_KEY_LENGTH = 16
XILLIA_AES_IV_LENGTH = 16
XILLIA_GENERATE_PASSWORD = "guygdbkjnsdnfsl"
# 16 Byte salt
# As the Xillia save encodes the salt in the first 0x10 bytes
# It can be anything
XILLIA_SAVE_SALT = b"saltString123456"
assert len(XILLIA_SAVE_SALT) == 16
XILLIA_GENERATED_KEYS = PBKDF2(
    XILLIA_GENERATE_PASSWORD, XILLIA_SAVE_SALT, XILLIA_AES_KEY_LENGTH + XILLIA_AES_IV_LENGTH, count=1000
)
XILLIA_AES_SAVE_KEY = XILLIA_GENERATED_KEYS[:16]
XILLIA_AES_SAVE_IV = XILLIA_GENERATED_KEYS[16:]


class SaveContents:
    """
    Stores the decrypted JSON contents of the Tales of Xillia Remastered save data
    which contain the complete save data (unlike Tales of Graces f which wraps the original PS3 save format)
    """

    save_json_dict: XilliaRemasteredSaveDict

    def __init__(
        self,
    ):
        self.remastered_save_default()

    def to_encrypt_bytes(self, output_data: bytearray, _save_format: SaveFormat) -> bool:
        """
        Encrypts the json dictionary into a byte array
        """

        padded_savedata_buffer = pad(
            json.dumps(self.save_json_dict, separators=COMPACT_JSON_SEPARATORS).encode("utf-8"), XILLIA_AES_BLOCK_SIZE
        )

        encrypt_buffer = bytearray(len(padded_savedata_buffer) + XILLIA_ENCRYPTION_START_OFFSET)
        # Write out the salt to the beginning of the encrypted buffer
        encrypt_buffer[XILLIA_ENCRYPTION_SALT_OFFSET:XILLIA_ENCRYPTION_IV_OFFSET] = XILLIA_SAVE_SALT
        encrypt_buffer[XILLIA_ENCRYPTION_IV_OFFSET:XILLIA_ENCRYPTION_START_OFFSET] = XILLIA_AES_SAVE_IV

        cipher_cbc = AES.new(XILLIA_AES_SAVE_KEY, mode=AES.MODE_CBC, iv=XILLIA_AES_SAVE_IV)
        cipher_cbc.encrypt(padded_savedata_buffer, memoryview(encrypt_buffer)[XILLIA_ENCRYPTION_START_OFFSET:])

        output_data += encrypt_buffer

        return True

    @staticmethod
    def from_encrypt_bytes(
        input_data: bytes | memoryview, output_save_contents: SaveContents, _save_format: SaveFormat
    ) -> bool:
        """
        Decrypts a byte array into a Tales of Xillia Remastered save file

        :return: After invoking this function the SaveContents instances contains the JSON data
        """

        # Read salt and IV from save file
        save_salt = memoryview(input_data)[XILLIA_ENCRYPTION_SALT_OFFSET:XILLIA_ENCRYPTION_IV_OFFSET]
        aes_iv = memoryview(input_data)[XILLIA_ENCRYPTION_IV_OFFSET:XILLIA_ENCRYPTION_START_OFFSET]
        # Use the PBKDF2 algorithm to generate the AES key using the salt and password
        aes_key = PBKDF2(XILLIA_GENERATE_PASSWORD, bytes(save_salt), XILLIA_AES_KEY_LENGTH, count=1000)

        start_offset = XILLIA_ENCRYPTION_START_OFFSET
        end_offset = len(input_data)
        encrypted_view = memoryview(input_data)[start_offset:end_offset]
        decrypt_buffer = bytearray(len(encrypted_view))

        # Decrypt the save data
        cipher_cbc = AES.new(aes_key, mode=AES.MODE_CBC, iv=aes_iv)
        cipher_cbc.decrypt(encrypted_view, decrypt_buffer)
        unpadded_buffer = unpad(bytes(decrypt_buffer), XILLIA_AES_BLOCK_SIZE)
        try:
            save_json = json.loads(unpadded_buffer)
        except json.JSONDecodeError as err:
            LOGGER.error(f"Failed to decode string {unpadded_buffer.decode()} as json: {err}")
            return False

        output_save_contents.save_json_dict = save_json

        return True

    def remastered_save_default(self) -> None:
        self.save_json_dict = default_remastered_save_dict()


### Save file read methods
def read_json_save(
    file_path: Path,
    decrypted_save_contents: SaveContents,
) -> bool:
    """
    Return a boolean indicating if the raw save datga was successfully read from the file_path
    The decrypted_save_contents `raw_save_binary_buffer`, `raw_save_json_buffer` `noble_save_binary_buffer` members
    are set by this function on success
    """
    if not file_path.exists():
        return False

    with file_path.open("rb") as infile:
        try:
            decrypted_save_contents.save_json_dict = json.loads(infile.read())
        except BlockingIOError as err:
            LOGGER.error(f"Unable to read data from input file {file_path}: {err}")
            return False
        except json.JSONDecodeError as dec_err:
            LOGGER.error(f"Failed to decode byte data into utf-8 {file_path}: {dec_err}")
            return False
    return True


### Debug dump methods
def dump_all_save_block_json_to_directory(save_contents: SaveContents, dump_output_dir: Path):
    """
    Dumps SaveDataN.data Save Block JSON fields to a directory
    """
    # As this code path is called when the BundleData.sav is decrypted as well
    # check that the save dictionary has a mSaveBlockData key
    if "mSaveBlockData" not in save_contents.save_json_dict:
        return

    files_to_move: list[Path] = []
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        for save_block_entry in save_contents.save_json_dict["mSaveBlockData"]:
            save_block_key = save_block_entry["Key"]
            save_block_data = save_block_entry["Value"]
            if not save_block_key or not save_block_data:
                continue
            tmp_save_block_path = tmp_path / f"{save_block_key}.json"
            with tmp_save_block_path.open("wb") as outfile:
                # pretty print JSON
                try:
                    save_block_dict = json.loads(save_block_data)
                except json.JSONDecodeError as err:
                    LOGGER.warning(f"Failed to decode save block '{save_block_key}' data to JSON: {err}")
                    continue
                dump_bytes = json.dumps(save_block_dict, indent=2, separators=None).encode("utf-8")
                if outfile.write(dump_bytes) != len(dump_bytes):
                    LOGGER.warning(f"Failed to write '{save_block_key}' {len(dump_bytes)} to file")
                    raise IOError(f"Failed to write {len(dump_bytes)} bytes to dump file: {tmp_save_block_path}")
                # Dump successful, append to the list of files to move to dump directory
                files_to_move.append(tmp_save_block_path)

        # Create output directory if it doesn't exist
        dump_output_dir.mkdir(parents=True, exist_ok=True)
        filepaths_to_move = [(tmp_path, dump_output_dir / tmp_path.name) for tmp_path in files_to_move]
        for src_path, dst_path in filepaths_to_move:
            if not shutil.move(src_path, dst_path):
                LOGGER.warning(f"Failed to move dump file '{src_path}' to {dst_path}")


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

    # Debug option
    _ = parser.add_argument(
        "--debug",
        "-d",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="If set, outputs the decrypted JSON file when converting from PS3 to other platforms."
        + " Outputs a file of <output-file-path>.debug",
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
    _ = parser.add_argument(
        "--dump-save-block-data",
        "-d",
        action=argparse.BooleanOptionalAction,
        default=False,
        help='If set, dump the "mSaveBlockData" string entries as JSON files.'
        + "The files will be output a folder of <output-file-path>.save-block-data",
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
