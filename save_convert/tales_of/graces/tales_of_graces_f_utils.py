"""
Contains utility methods and constants for manipulating Tales of Graces f save data
"""

import argparse
import base64
import json
import logging
import struct
import sys
from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
from pathlib import Path
from typing import Any, TypedDict, override
from zlib import crc32

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
    BinSaveToYamlConvert,
    ConvertFormat,
    SaveFormat,
    SaveTransformBase,
    YamlToBinSaveConvert,
)
from save_convert.tales_of.graces.tales_of_graces_f_big_data import (
    DEFAULT_ICON_PNG_BASE64,
    DEFAULT_ICON_PNG_CAPTURE_SIZE,
    DEFAULT_NATIVE_SYS_PARAM_BASE64,
)
from save_convert.tales_of.graces.tales_of_graces_f_structs import GRACES_F_RAW_SAVE_SIZE, TalesOfGracesFSaveStruct
from save_convert.tales_of.tales_of_utils import COMPACT_JSON_SEPARATORS

SCRIPT_DIR: Path = Path(__file__).parent.resolve()

LOGGER = logging.getLogger("graces_save_converter_utils")
LOGGER.addHandler(logging.StreamHandler(sys.stdout))
LOGGER.setLevel(logging.INFO)

# Formats which supports encryption/decryption
# NOTE: PS3 save files are always decrypted
SUPPORTED_CRYPT_SAVE_FORMATS: list[SaveFormat] = [
    SaveFormat.PC,
    SaveFormat.PS5,
    SaveFormat.PS4,
    SaveFormat.NSW,
    SaveFormat.XBOXONE,
    SaveFormat.XBOXSERIESX,
]

SUPPORTED_YAML_SAVE_FORMATS: list[SaveFormat] = [
    SaveFormat.PC,
    SaveFormat.PS5,
    SaveFormat.PS4,
    SaveFormat.PS3,
    SaveFormat.NSW,
    SaveFormat.XBOXONE,
    SaveFormat.XBOXSERIESX,
]

# Save data file size for the remastered encrypted save file from Assembly-CSharp.dll
# SaveLoadStreamWin
GRACES_F_REMASTERED_SAVE_SIZE = 1015808
# Size of the SaveDataList.sav file containing 31 entries for Tales of Graces game saves
# Each entry is 512 bytes for a total of 512 * 31 = 15872 bytes
GRACES_F_REMASTERED_SAVELIST_COUNT = 31
GRACES_F_REMASTERED_SAVELIST_ENTRY_SIZE = 512
GRACES_F_REMASTERED_SAVELIST_TOTAL_SIZE = GRACES_F_REMASTERED_SAVELIST_COUNT * GRACES_F_REMASTERED_SAVELIST_ENTRY_SIZE


# 128KiB system save
GRACES_F_REMASTERED_SYSTEM_SAVE_SIZE = 128 * 2**10
GRACES_F_RAW_SYSTEM_SAVE_SIZE = 37064

# The Save data for Tales of Graces has 2 sections
# Section 1 which is a metadata section that contains
# the base 64-encoded PNG use for the save file thumbnail and and playtime data
"""
{
    "version": 0.5,
    "listParam": {
        "saveDate": {
            "year": 2026,
            "month": 5,
            "day": 18,
            "hour": 15,
            "minutes": 15,
            "seconds": 10
        },
        "playTime": 13830,
        "leaderLevel": 3,
        "to10": 101010000,
        "sv_sce_no": 3145728,
        "partyLeader": 8,
        "ending": 0,
        "listParam0": 0,
        "sectionClearFlag": 249,
        "isValid": 1,
        "futer_play": 0
    },
    "capture": "<base64-encoded-icon0-png>",
    "captureSize": 251903,
    "pNativeSysParam": "<base64-encoded-system-param-value>"
}
"""

# Section 2 which contains the actual raw save data (stored as base 64 encoded) and a
# NobleData section which is base64 encoded as well, but when decrypted it is 1024 bytes
"""
{
    "NativeData": "<base64-encoded-save data",
    "NobleData": "<base64-encoded-noble-data>"
}
"""

# The raw save data is the same size as the PS3 data at 79104 bytes
# The difference the between PS3 save and all other platforms(PC, PS4, PS5, NSW, etc...)
# Is that the PS3 save file integer and float values are stored in big endian format
# all other platforms are little endian
# Therefore to convert between PS3 and other platforms, the integer values need to be endian swapped

#
# NOTE: For some reason, the save data writes out both the metadata section and the save data section
# twice in succession with no changes.

GRACES_F_SAVE_SIZE_DICT: dict[SaveFormat, int] = {
    SaveFormat.PC: GRACES_F_RAW_SAVE_SIZE,
    SaveFormat.PS5: GRACES_F_RAW_SAVE_SIZE,
    SaveFormat.PS4: GRACES_F_RAW_SAVE_SIZE,
    SaveFormat.PS3: GRACES_F_RAW_SAVE_SIZE,
    SaveFormat.NSW: GRACES_F_RAW_SAVE_SIZE,
    SaveFormat.XBOXONE: GRACES_F_RAW_SAVE_SIZE,
    SaveFormat.XBOXSERIESX: GRACES_F_RAW_SAVE_SIZE,
}

# Each save data section is stored twice within the save file
GRACES_F_SECTION_ITER_COUNT = 2

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


# Absolute offset in save file where the encrypted metadata is stored
GRACES_F_SAVE_METADATA_START_OFFSET_ABS = 0x0
# NOTE: The save file stores each section twice in succession
GRACES_F_SAVE_METADATA_STEP = 0x61000

# Absolute offset in the save file where the encrypted native save data contents are stored
GRACES_F_SAVE_NATIVEDATA_START_OFFSET_ABS = GRACES_F_SAVE_METADATA_STEP * 2
# The save file encrypted native data is stored twice in succession starting at offset 0xC2000 (0x61000 * 2)
GRACES_F_SAVE_NATIVEDATA_STEP = 0x1B000

GRACES_F_ENCRYPTION_START_OFFSET = 0x08
# There are 3 save data sections in the Tales of Graces f Remastered save data
# The first 2 are sections containing identical PNG data for the thumbnail used when saving a file
# The third section contains the actual game data that is base64 encoded in a JSON key of
# NativeData and NobleData
GRACES_F_SAVELIST_KEY = "listParam"
GRACES_F_ICON0_KEY = "capture"
GRACES_F_NATIVE_SAVE_KEY = "NativeData"
GRACES_F_NOBLE_SAVE_KEY = "NobleData"


GRACES_F_METADATA_SAVE_SECTION = "Metadata"
GRACES_F_NATIVE_SAVE_SECTION = "Savedata"


GRACES_F_AES_BLOCK_SIZE = 16
GRACES_F_AES_KEY_LENGTH = 32
GRACES_F_GENERATE_PASSWORD = "1123581321345589"
GRACES_F_SALT = b"saltString"
GRACES_F_GENERATED_KEYS = PBKDF2(GRACES_F_GENERATE_PASSWORD, GRACES_F_SALT, GRACES_F_AES_KEY_LENGTH, count=1000)
GRACES_F_AES_SAVE_KEY = GRACES_F_GENERATED_KEYS[:16]
GRACES_F_AES_SAVE_IV = GRACES_F_GENERATED_KEYS[16:]

# The Playtime data stored in the Remastered game save is read from the metadata section "playTime field"
# However in the PS3 game it is read from offset 0x76D8
GRACES_F_PS3_RAW_SAVE_PLAYTIME_OFFSET = 0x76D8


# Absolute offset in save file where the encrypted NobleSystemFileParam json data is stored
GRACES_F_REMASTERED_NOBLE_SYSTEM_FILE_PARAM_OFFSET = 0x0
# NOTE: The NobleSystsemFileParam is stored twice in succession in steps of 2048
GRACES_F_REMASTERED_SYSTEM_FILE_PARAM_STEP = 0x800

# Absolute offset in the save file where the encrypted native save data contents are stored
GRACES_F_REMASTERED_SYSTEM_DATA_PARAM_OFFSET = GRACES_F_REMASTERED_SYSTEM_FILE_PARAM_STEP * 2
# The save file encrypted native data is stored twice in succession starting at offset 0x1000
GRACES_F_REMASTERED_SYSTEM_DATA_PARAM_STEP = 0xF800


DEFAULT_REMASTERED_SAVE_JSON_FILENAME = Path("SaveData.json")
DEFAULT_RAW_SAVE_BIN_FILENAME = Path("TOGAPP.bin")
DEFAULT_NOBLE_SAVE_BIN_FILENAME = Path("TOGNOBLE.bin")
DEFAULT_ICON0_PNG_FILENAME = Path("ICON0.png")


# List of filenames to move to destination directory when decrypting save data
FILENAMES_TO_MOVE = [
    DEFAULT_REMASTERED_SAVE_JSON_FILENAME,
    DEFAULT_ICON0_PNG_FILENAME,
    DEFAULT_RAW_SAVE_BIN_FILENAME,
    DEFAULT_NOBLE_SAVE_BIN_FILENAME,
]


DEFAULT_REMASTERED_SYSTEM_SAVE_JSON_FILENAME = Path("SystemSaveData.json")
DEFAULT_RAW_SYSTEM_SAVE_BIN_FILENAME = Path("TOGSYS.bin")
DEFAULT_NOBLE_SYSTEM_SAVE_BIN_FILENAME = Path("TOGSYSNOBLE.bin")
SYSTEM_FILENAMES_TO_MOVE = [
    DEFAULT_REMASTERED_SYSTEM_SAVE_JSON_FILENAME,
    DEFAULT_RAW_SYSTEM_SAVE_BIN_FILENAME,
    DEFAULT_NOBLE_SYSTEM_SAVE_BIN_FILENAME,
]

# File which is used to add the metadata to the encrypted save file
# if neither the --input-icon0-json nor --input-icon0-json is provided
DEFAULT_ICON0_TEMPLATE_FILE: Path = SCRIPT_DIR / f"default_files/{DEFAULT_ICON0_PNG_FILENAME}"

# File which is used to add the noble to the encrypted save file
# if the --input-noble-bin argument is not provided
DEFAULT_NOBLE_TEMPLATE_FILE: Path = SCRIPT_DIR / f"default_files/{DEFAULT_NOBLE_SAVE_BIN_FILENAME}"


class RemasteredSaveNobleIsValidData(IntEnum):
    notUsed = 0
    valid = 1
    invalid = 2


class RemasteredSaveDate(TypedDict):
    """Dictionary of save date data"""

    year: int
    month: int
    day: int
    hour: int
    minutes: int
    seconds: int


class RemasteredSaveListParam(TypedDict):
    """Dictionary of save data list param used to set save menu metadata
    The list param is also used for the playtime field in game
    """

    saveDate: RemasteredSaveDate
    playTime: int
    leaderLevel: int
    to10: int
    sv_sce_no: int
    partyLeader: int
    ending: int
    listParam0: int
    sectionClearFlag: int
    isValid: RemasteredSaveNobleIsValidData
    futer_play: int


class RemasteredSaveMetadata(TypedDict):
    """Dictionary of metadata for save including the list param,
    the save thumbnail PNG and the native system save data
    """

    version: float
    listParam: RemasteredSaveListParam
    capture: str
    captureSize: int
    pNativeSysParam: str


class RemasteredSaveRaw(TypedDict):
    """Dictionary of the raw save data from TOGAPP.bin
    and the NobleData
    """

    NativeData: str
    NobleData: str


class RemasteredSave(TypedDict):
    """Dictionary of the complete remastered save data"""

    Metadata: RemasteredSaveMetadata
    Savedata: RemasteredSaveRaw


class SaveContents:
    """
    Stores the decrypted JSON contents of the Tales of Graces f Remastered save data
    as well as the decoded thumbnial, native save (original PS3 save data) and noble save (system data)
    as several buffers
    """

    save_json_dict: RemasteredSave

    def __init__(
        self,
    ):
        self.remastered_save_default()

    def to_encrypt_bytes(self, output_data: bytearray, save_format: SaveFormat) -> bool:
        """
        Encrypts the buffers containing the save metadata, native raw data and noble
        data into single byte array
        """
        # PS3 data needs to update file with metadata section list param values from the
        # remastered game save
        if save_format == SaveFormat.PS3:
            _ = self._update_metadata_to_ps3()
            output_data += self.raw_save_binary_buffer
            return True

        output_offset = GRACES_F_SAVE_METADATA_START_OFFSET_ABS

        # Encrypt the metadata json data
        metadata_dict = self.save_json_dict.get(GRACES_F_METADATA_SAVE_SECTION)
        if not isinstance(metadata_dict, dict):
            return False

        padded_metadata_buffer = pad(
            json.dumps(metadata_dict, separators=COMPACT_JSON_SEPARATORS).encode("utf-8"), GRACES_F_AES_BLOCK_SIZE
        )
        encrypt_buffer = bytearray(len(padded_metadata_buffer))
        cipher_cbc = AES.new(GRACES_F_AES_SAVE_KEY, mode=AES.MODE_CBC, iv=GRACES_F_AES_SAVE_IV)
        cipher_cbc.encrypt(padded_metadata_buffer, encrypt_buffer)

        def write_data(target_buffer: bytearray, write_offset: int, section_size: int) -> int:
            """
            Writes out the encrypted data to the byte array twice and return the updated output offset
            """
            for _ in range(GRACES_F_SECTION_ITER_COUNT):
                # Pad the output data array with '00' bytes until it is at the output_offset
                if len(target_buffer) < write_offset:
                    target_buffer.resize(write_offset)
                # First write the size of the decrypted data with padding
                target_buffer += len(encrypt_buffer).to_bytes(length=4, byteorder="little")
                # Next write CRC32 calcuation of the encrypted data
                target_buffer += crc32(encrypt_buffer, 0).to_bytes(length=4, byteorder="little")
                # Write the encrypted contents after the CRC32
                target_buffer += encrypt_buffer
                write_offset += section_size
            return write_offset

        # Write out the encrypted metadata
        output_offset = write_data(output_data, output_offset, GRACES_F_SAVE_METADATA_STEP)

        # Encrypt the raw save json data
        savedata_dict = self.save_json_dict.get(GRACES_F_NATIVE_SAVE_SECTION)
        if not isinstance(savedata_dict, dict):
            return False
        padded_metadata_buffer = pad(
            json.dumps(savedata_dict, separators=COMPACT_JSON_SEPARATORS).encode(), GRACES_F_AES_BLOCK_SIZE
        )
        encrypt_buffer = bytearray(len(padded_metadata_buffer))
        cipher_cbc = AES.new(GRACES_F_AES_SAVE_KEY, mode=AES.MODE_CBC, iv=GRACES_F_AES_SAVE_IV)
        cipher_cbc.encrypt(padded_metadata_buffer, encrypt_buffer)

        # Write out the raw savedata
        output_offset = write_data(output_data, output_offset, GRACES_F_SAVE_NATIVEDATA_STEP)

        # pad save file with 0 bytes until it reaches the save file length constant for game
        if len(output_data) <= GRACES_F_REMASTERED_SAVE_SIZE:
            output_data.resize(GRACES_F_REMASTERED_SAVE_SIZE)

        return True

    @staticmethod
    def from_encrypt_bytes(
        input_data: bytes | memoryview, output_save_contents: SaveContents, save_format: SaveFormat
    ) -> bool:
        """
        Decrypts an encrypted save file into a structure with following format
        The decrypted save metadata JSON block containing the savefile thumbnail PNG in base 64 format
        The thumbnail data is stored in the "capture" JSON key which also gets decoded to a PNG buffer

        The raw save data JSON block containing the "NativeData" (raw save data) and "NobleData" (system save data)
        are each stored base 64 encoded.
        They are both also decoded to a binary buffer

        :return: After invoking this function a structure of string and binary buffers containing the decrypted
        JSON save data is returned along, with decoded ICON0 thumbnail PNG data and decoded raw + system binary data
        """

        # PS3 save is only the decrypted binary file
        # Therefore read the Default Metadata json file
        # as well as use the NobleData from a pre-configured save create a remastered save
        if save_format == SaveFormat.PS3:
            output_save_contents.raw_save_binary_buffer = bytes(input_data)

            # Set the Playtime data in the Metadata JSON file
            _ = output_save_contents._update_metadata_from_ps3()
            return True

        for section_offset in range(0, len(input_data), GRACES_F_SAVE_METADATA_STEP * GRACES_F_SECTION_ITER_COUNT):
            # Decrypt the save data if successfully read into memory
            start_offset = section_offset + GRACES_F_ENCRYPTION_START_OFFSET
            # The first 4 bytes is the size of the save data section
            section_size = int.from_bytes(input_data[section_offset : section_offset + 4], "little")
            if section_size > len(input_data):
                LOGGER.error(
                    f"Save Data section size {section_size} is invalid."
                    f" It must be less than save file size of {len(input_data)}"
                )
                return False

            end_offset = start_offset + section_size
            encrypted_view = memoryview(input_data)[start_offset:end_offset]
            decrypt_buffer = bytearray(len(encrypted_view))
            cipher_cbc = AES.new(GRACES_F_AES_SAVE_KEY, mode=AES.MODE_CBC, iv=GRACES_F_AES_SAVE_IV)
            cipher_cbc.decrypt(encrypted_view, decrypt_buffer)
            unpadded_buffer = unpad(bytes(decrypt_buffer), GRACES_F_AES_BLOCK_SIZE)
            try:
                save_json = json.loads(unpadded_buffer)
            except json.JSONDecodeError as err:
                LOGGER.error(f"Failed to decode string {unpadded_buffer.decode()} as json: {err}")
                return False
            match section_offset:
                case 0x0:
                    output_save_contents.save_json_dict["Metadata"] = save_json
                case 0xC2000:
                    output_save_contents.save_json_dict["Savedata"] = save_json
                case _ as s:
                    LOGGER.warning(f"Offset 0x{s:X} within save file cannot be processed at this time")
                    continue

        return True

    def _update_metadata_from_ps3(self) -> bool:
        """
        Updates the Json metadata section stored within the save file with the playtime data
        The icon_json_buffer and raw_save_binary_buffer fields must be valid
        otherwise no updates to the will metadata section occurs
        """
        if len(self.raw_save_binary_buffer) != GRACES_F_RAW_SAVE_SIZE:
            LOGGER.error(
                f"Raw save file is must have filesize of {GRACES_F_RAW_SAVE_SIZE}.\n"
                + f"Actual size={len(self.raw_save_binary_buffer)}"
            )
            return False

        if not self.save_json_dict:
            LOGGER.error("Metadata Json buffer is empty")
            return False

        metadata_dict: RemasteredSaveMetadata = self.save_json_dict.get("Metadata", {})
        input_list_param: RemasteredSaveListParam | None = metadata_dict.get("listParam")
        if not input_list_param:
            LOGGER.error(f"JSON data is missing `{GRACES_F_SAVELIST_KEY}` key")
            return False

        save_list_param = NobleSaveListParam()
        if not NobleSaveListParam.from_dict(input_list_param, save_list_param):
            LOGGER.error(f'Metadata JSON does not have a "{GRACES_F_SAVELIST_KEY}" field')
            return False
        # Playtime values are 1/60 ticks of a second
        save_list_param.play_time = int.from_bytes(
            self.raw_save_binary_buffer[
                GRACES_F_PS3_RAW_SAVE_PLAYTIME_OFFSET : GRACES_F_PS3_RAW_SAVE_PLAYTIME_OFFSET + 4
            ],
            "big",
        )
        list_param_dict_result = save_list_param.to_dict()
        if not list_param_dict_result:
            return False

        metadata_dict["listParam"] = list_param_dict_result.value
        return True

    def _update_metadata_to_ps3(self) -> bool:
        """
        Updates the raw save data with the playtime data
        from the remastered save metadata section
        The icon_json_buffer and raw_save_binary_buffer fields must be valid
        otherwise not updates to the metadata section occurs
        """
        if len(self.raw_save_binary_buffer) != GRACES_F_RAW_SAVE_SIZE:
            LOGGER.error(
                f"Raw save file is must have filesize of {GRACES_F_RAW_SAVE_SIZE}.\n"
                + f"Actual size={len(self.raw_save_binary_buffer)}"
            )
            return False

        if not self.save_json_dict:
            LOGGER.error("Metadata Json buffer is empty")
            return False

        metadata_dict: RemasteredSaveMetadata = self.save_json_dict.get("Metadata", {})
        input_list_param: RemasteredSaveListParam | None = metadata_dict.get("listParam")
        if not input_list_param:
            LOGGER.error(f"JSON data is missing `{GRACES_F_SAVELIST_KEY}` key")
            return False

        save_list_param = NobleSaveListParam()
        if not NobleSaveListParam.from_dict(input_list_param, save_list_param):
            LOGGER.error(f'Metadata JSON does not have a "{GRACES_F_SAVELIST_KEY}" field')
            return False
        # Playtime values are 1/60 ticks of a second
        playtime_offset = GRACES_F_PS3_RAW_SAVE_PLAYTIME_OFFSET
        writable_buffer = bytearray(self.raw_save_binary_buffer)
        writable_buffer[playtime_offset : playtime_offset + 4] = save_list_param.play_time.to_bytes(4, "big")
        self.raw_save_binary_buffer = bytes(writable_buffer)

        return True

    def remastered_save_default(self) -> None:
        self.save_json_dict = RemasteredSave(
            {
                "Metadata": {
                    "version": 0.5,
                    "listParam": {
                        "saveDate": {"year": 2026, "month": 1, "day": 1, "hour": 0, "minutes": 0, "seconds": 0},
                        "playTime": 0,
                        "leaderLevel": 3,
                        "to10": 101010000,
                        "sv_sce_no": 3145728,
                        "partyLeader": 8,
                        "ending": 0,
                        "listParam0": 0,
                        "sectionClearFlag": 47,
                        "isValid": RemasteredSaveNobleIsValidData.valid,
                        "futer_play": 0,
                    },
                    "capture": DEFAULT_ICON_PNG_BASE64,
                    "captureSize": DEFAULT_ICON_PNG_CAPTURE_SIZE,
                    "pNativeSysParam": DEFAULT_NATIVE_SYS_PARAM_BASE64,
                },
                "Savedata": {
                    "NativeData": base64.b64encode(b"").decode("utf-8"),
                    "NobleData": DEFAULT_ICON_PNG_BASE64,
                },
            }
        )

        # Populate the Metadata section containing the thumbnail PNG from a default file if available
        _ = self.read_icon0_png(DEFAULT_ICON0_TEMPLATE_FILE)

        _ = self.read_binary_noble_data(DEFAULT_NOBLE_TEMPLATE_FILE)

    @property
    def raw_save_binary_buffer(self) -> bytes:
        savedata_dict: RemasteredSaveRaw = self.save_json_dict.get("Savedata", {})
        if native_base64 := savedata_dict.get("NativeData"):
            return base64.b64decode(native_base64)
        return b""

    @raw_save_binary_buffer.setter
    def raw_save_binary_buffer(self, raw_save_bytes: bytes):
        save_data_dict: RemasteredSaveRaw = self.save_json_dict.get("Savedata")
        if save_data_dict:
            save_data_dict["NativeData"] = base64.b64encode(raw_save_bytes).decode("utf-8")

    @property
    def icon0_png_buffer(self) -> bytes:
        metadata_dict: RemasteredSaveMetadata = self.save_json_dict.get("Metadata", {})
        if png_base64 := metadata_dict.get("capture"):
            return base64.b64decode(png_base64)
        return b""

    @icon0_png_buffer.setter
    def icon0_png_buffer(self, icon_0_png_bytes: bytes):
        metadata_dict: RemasteredSaveMetadata = self.save_json_dict.get("Metadata")
        if metadata_dict:
            metadata_dict["capture"] = base64.b64encode(icon_0_png_bytes).decode("utf-8")
            metadata_dict["captureSize"] = len(icon_0_png_bytes)

    @property
    def noble_save_binary_buffer(self) -> bytes:
        savedata_dict: RemasteredSaveRaw = self.save_json_dict.get("Savedata", {})
        if noble_base64 := savedata_dict.get("NobleData"):
            return base64.b64decode(noble_base64)
        return b""

    @noble_save_binary_buffer.setter
    def noble_save_binary_buffer(self, noble_save_bytes: bytes):
        save_data_dict: RemasteredSaveRaw = self.save_json_dict.get("Savedata")
        if save_data_dict:
            save_data_dict["NobleData"] = base64.b64encode(noble_save_bytes).decode("utf-8")

    ## Save file read methods
    def read_json_save(
        self,
        file_path: Path,
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
                self.save_json_dict = json.loads(infile.read())
            except BlockingIOError as err:
                LOGGER.error(f"Unable to read data from input file {file_path}: {err}")
                return False
            except json.JSONDecodeError as dec_err:
                LOGGER.error(f"Failed to decode byte data into utf-8 {file_path}: {dec_err}")
                return False
        return True

    def read_binary_raw_save(self, file_path: Path) -> bool:
        """
        Return a boolean indicating if the raw save data was successfully read from the file_path
        The decrypted_save_contents `raw_save_binary_buffer`, `raw_save_json_buffer` `noble_save_binary_buffer` members
        are set by this function on success
        """
        if not file_path.exists():
            return False

        with file_path.open("rb") as infile:
            try:
                self.raw_save_binary_buffer = infile.read()
            except BlockingIOError as err:
                LOGGER.error(f"Unable to read data from input file {file_path}: {err}")
                return False

        return True

    def read_icon0_png(self, file_path: Path) -> bool:
        """
        Return a boolean indicating if the save metadata was successfully read from the file_path
        The decrypted_save_contents `icon0_json_buffer` and `icon0_png_buffer` members are set by this function
        on success
        """
        if not file_path.exists():
            return False

        with file_path.open("rb") as infile:
            try:
                self.icon0_png_buffer = infile.read()
            except BlockingIOError as err:
                LOGGER.error(f"Unable to read data from input file {file_path}: {err}")
                return False
            except json.JSONDecodeError as dec_err:
                LOGGER.error(f"Failed to decode byte data into utf-8 {file_path}: {dec_err}")
                return False
        return True

    def read_binary_noble_data(
        self,
        file_path: Path,
    ) -> bool:
        """
        Return a boolean indicating if the noble save data was successfully read from the file_path
        The decrypted_save_contents `noble_save_binary_buffer` member
        is set by this function on success
        """
        if not file_path.exists():
            return False

        with file_path.open("rb") as infile:
            try:
                self.noble_save_binary_buffer = infile.read()
            except BlockingIOError as err:
                LOGGER.error(f"Unable to read data from input file {file_path}: {err}")
                return False
        return True


## Save List parsing section
SAVE_LIST_ENTRY_MAGIC: int = 0x01
SAVE_LIST_CURRENT_VERSION: float = 0.3


@dataclass
class NobleSaveDateTime:
    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: int


@dataclass
class NobleSaveListParamToDictResult:
    """
    Encodes the result converting a SaveListParam to a dict
    """

    result: bool
    value: RemasteredSaveListParam

    def __bool__(self) -> bool:
        return self.result


@dataclass
class NobleSaveListParam:
    save_date: NobleSaveDateTime
    play_time: int
    leader_level: int
    to10: int
    sv_sce_no: int
    party_leader: int
    ending: int
    list_param0: int
    section_clear_flag: int
    is_valid: RemasteredSaveNobleIsValidData
    # For the future game scenario
    future_play: int

    def __init__(self):
        current_datetime = datetime.now()
        self.save_date = NobleSaveDateTime(
            current_datetime.year,
            current_datetime.month,
            current_datetime.day,
            current_datetime.hour,
            current_datetime.minute,
            current_datetime.second,
        )
        self.play_time = 0
        self.leader_level = 0
        self.to10 = 0
        self.sv_sce_no = 0
        self.party_leader = 0
        self.ending = 0
        self.list_param0 = 0
        self.section_clear_flag = 0
        self.is_valid = RemasteredSaveNobleIsValidData.notUsed
        self.future_play = 0

    def to_dict(self) -> NobleSaveListParamToDictResult:
        output_dict = RemasteredSaveListParam(
            {
                "saveDate": {
                    "year": self.save_date.year,
                    "month": self.save_date.month,
                    "day": self.save_date.day,
                    "hour": self.save_date.hour,
                    "minutes": self.save_date.minute,
                    "seconds": self.save_date.second,
                },
                "playTime": (self.play_time),
                "leaderLevel": self.leader_level,
                "to10": self.to10,
                "sv_sce_no": self.sv_sce_no,
                "partyLeader": self.party_leader,
                "ending": self.ending,
                "listParam0": self.list_param0,
                "sectionClearFlag": self.section_clear_flag,
                "isValid": self.is_valid,
                "futer_play": self.future_play,
            }
        )
        return NobleSaveListParamToDictResult(True, output_dict)

    @staticmethod
    def from_dict(input_dict: RemasteredSaveListParam, output_list_save_param: NobleSaveListParam) -> bool:
        save_date: RemasteredSaveDate = input_dict.get("saveDate", {})
        year = save_date.get("year")
        month = save_date.get("month")
        day = save_date.get("day")
        hour = save_date.get("hour")
        minute = save_date.get("minutes")
        second = save_date.get("seconds")
        if (
            year is not None
            and month is not None
            and day is not None
            and hour is not None
            and minute is not None
            and second is not None
        ):
            output_list_save_param.save_date = NobleSaveDateTime(year, month, day, hour, minute, second)
        else:
            LOGGER.error(f'Value error converting "saveDate" field to datetime.It has value {save_date}')
            return False

        output_list_save_param.play_time = input_dict.get("playTime", 0)
        output_list_save_param.leader_level = input_dict.get("leaderLevel", 0)
        output_list_save_param.to10 = input_dict.get("to10", 0)
        output_list_save_param.sv_sce_no = input_dict.get("sv_sce_no", 0)
        output_list_save_param.party_leader = input_dict.get("partyLeader", 0)
        output_list_save_param.ending = input_dict.get("ending", 0)
        output_list_save_param.list_param0 = input_dict.get("listParam0", 0)
        output_list_save_param.section_clear_flag = input_dict.get("sectionClearFlag", 0)
        output_list_save_param.is_valid = input_dict.get("isValid", RemasteredSaveNobleIsValidData.notUsed)
        output_list_save_param.future_play = input_dict.get("futer_play", 0)
        return True

    def to_json(
        self,
        output_json_buffer: bytearray,
        indent: int | str | None = None,
        separators: tuple[str, str] | None = COMPACT_JSON_SEPARATORS,
    ) -> bool:
        json_dict_result = self.to_dict()
        if not json_dict_result:
            return False
        output_json_buffer += json.dumps(json_dict_result.value, indent=indent, separators=separators).encode("utf-8")
        return True

    @staticmethod
    def from_json(input_json: str, output_list_save_param: NobleSaveListParam) -> bool:
        try:
            list_param_dict: RemasteredSaveListParam = json.loads(input_json)
        except json.JSONDecodeError as err:
            LOGGER.error(f"Failed to convert string to JSON: {err}")
            return False

        return NobleSaveListParam.from_dict(list_param_dict, output_list_save_param)


class SaveListEntry:
    """
    Stores a single entry in the SaveList
    """

    version: float
    save_list_param: NobleSaveListParam

    def __init__(self):
        self.version = SAVE_LIST_CURRENT_VERSION
        self.save_list_param = NobleSaveListParam()

    def to_encrypt_bytes(self, output_data: bytearray) -> bool:
        """
        Encrypt Save Entry data and append encrypted data into
        byte array output
        :return: True on successful encryption of entry data
        """
        encrypt_data = bytearray(GRACES_F_REMASTERED_SAVELIST_ENTRY_SIZE)
        # Append 512 entries bytes to the output byte array
        # which will get populated with the encrypted contents
        output_index = len(output_data)
        # write the 4 byte magic number which indicates the save entry version logic
        encrypt_data[output_index : output_index + 4] = SAVE_LIST_ENTRY_MAGIC.to_bytes(length=4, byteorder="little")
        output_index += 4
        # write 4 byte float version value
        encrypt_data[output_index : output_index + 4] = struct.pack("<f", self.version)
        output_index += 4

        # Get save list param as compact json
        list_param_json = bytearray()
        if not self.save_list_param.to_json(list_param_json):
            LOGGER.error(f"Failed to encrypt save list param {self.save_list_param}")
            return False

        # Encrypt the json data
        padded_buffer = pad(bytes(list_param_json), GRACES_F_AES_BLOCK_SIZE)
        encrypt_buffer = bytearray(padded_buffer)
        cipher_cbc = AES.new(GRACES_F_AES_SAVE_KEY, mode=AES.MODE_CBC, iv=GRACES_F_AES_SAVE_IV)
        cipher_cbc.encrypt(padded_buffer, encrypt_buffer)
        # write the encrypted data size
        encrypted_size = len(encrypt_buffer)
        encrypt_data[output_index : output_index + 4] = encrypted_size.to_bytes(length=4, byteorder="little")
        output_index += 4
        # write the crc32 value for the encrypted data
        encrypt_data[output_index : output_index + 4] = crc32(encrypt_buffer).to_bytes(length=4, byteorder="little")
        output_index += 4
        # write the encrypted data
        encrypt_data[output_index : output_index + encrypted_size] = encrypt_buffer

        output_data += encrypt_data
        return True

    @staticmethod
    def from_encrypt_bytes(input_data: bytes | memoryview, output_save_entry: SaveListEntry) -> bool:
        """
        Decrypt Save Entry contents from encrypted byte buffer
        Populates the :output_save_entry: parameter on success
        """
        if len(input_data) != GRACES_F_REMASTERED_SAVELIST_ENTRY_SIZE:
            LOGGER.error(
                f"Encrypted SaveEntry file must have size of {GRACES_F_REMASTERED_SAVELIST_ENTRY_SIZE}.\n"
                f"Actual entry size is {len(input_data)}"
            )
            return False

        SAVE_ENTRY_SIZE_OFFSET = 0x08
        SAVE_ENTRY_DATA_OFFSET = 0x10
        # Read the encrypted data size from offset 0x08
        block_size = int.from_bytes(input_data[SAVE_ENTRY_SIZE_OFFSET : SAVE_ENTRY_SIZE_OFFSET + 4], "little")
        if block_size > len(input_data):
            LOGGER.error(
                f"Encrypted entry block size {block_size} is invalid."
                f" It must be less than encrypted entry size of {len(input_data)}"
            )
            return False

        start_offset = SAVE_ENTRY_DATA_OFFSET
        end_offset = start_offset + block_size
        encrypted_view = memoryview(input_data)[start_offset:end_offset]
        decrypt_buffer = bytearray(len(encrypted_view))
        cipher_cbc = AES.new(GRACES_F_AES_SAVE_KEY, mode=AES.MODE_CBC, iv=GRACES_F_AES_SAVE_IV)
        cipher_cbc.decrypt(encrypted_view, decrypt_buffer)
        unpadded_buffer = unpad(bytes(decrypt_buffer), GRACES_F_AES_BLOCK_SIZE)
        try:
            entry_json = json.loads(unpadded_buffer)
        except json.JSONDecodeError as err:
            LOGGER.error(f"Failed to decode string {unpadded_buffer.decode('utf-8')} as json: {err}")
            return False

        if not NobleSaveListParam.from_dict(entry_json, output_save_entry.save_list_param):
            LOGGER.error("Failed to convert entry JSON to Save List entry")
            return False

        return True

    def to_dict(
        self,
    ) -> NobleSaveListParamToDictResult:
        return self.save_list_param.to_dict()

    @staticmethod
    def from_dict(input_dict: RemasteredSaveListParam, output_save_entry: SaveListEntry) -> bool:
        output_save_entry.version = SAVE_LIST_CURRENT_VERSION
        return NobleSaveListParam.from_dict(input_dict, output_save_entry.save_list_param)


class SaveListContents:
    """
    Stores the list of save entries from the SaveDataList.sav file
    """

    save_entries: list[SaveListEntry]

    def __init__(self):
        self.save_entries = []

    def to_encrypt_bytes(self, output_data: bytearray) -> bool:
        """
        Encrypt each save entry of the Save List contents and appends it to the supplied byte array
        Return True if encryption is successful
        """
        # encrypted data is appended to a local bytearray first
        # If the full operation is successful, only then is it appended to the output bytearray
        encrypt_data = bytearray()
        for i, save_entry in enumerate(self.save_entries):
            output_entry_bytes = bytearray()
            if not save_entry.to_encrypt_bytes(output_entry_bytes):
                LOGGER.error(f"Failed to encrypt save entry {i}")
                return False
            encrypt_data += output_entry_bytes

        # Append to output bytearray
        output_data += encrypt_data
        return True

    @staticmethod
    def from_encrypt_bytes(input_data: bytes | memoryview, output_save_list: SaveListContents) -> bool:
        """
        Decrypt Save List contents from encrypted byte buffer
        Populates the :output_save_list: parameter on success
        """
        if len(input_data) != GRACES_F_REMASTERED_SAVELIST_TOTAL_SIZE:
            LOGGER.error(
                f"Encrypted SaveList file must have size of {GRACES_F_REMASTERED_SAVELIST_TOTAL_SIZE}.\n"
                f"Actual file size is {len(input_data)}"
            )
            return False

        output_save_list.save_entries.clear()
        for entry_index in range(0, GRACES_F_REMASTERED_SAVELIST_COUNT):
            entry_offset = entry_index * GRACES_F_REMASTERED_SAVELIST_ENTRY_SIZE
            offset_end = entry_offset + GRACES_F_REMASTERED_SAVELIST_ENTRY_SIZE
            entry_view = memoryview(input_data)[entry_offset:offset_end]
            save_entry = SaveListEntry()
            if not SaveListEntry.from_encrypt_bytes(entry_view, save_entry):
                LOGGER.error(f"Failed to decrypt save entry {entry_index} from SaveDataList.sav")
                return False
            output_save_list.save_entries.append(save_entry)

        return True

    def to_json(
        self,
        output_json_buffer: bytearray,
        indent: int | str | None = None,
        separators: tuple[str, str] | None = COMPACT_JSON_SEPARATORS,
    ) -> bool:
        output_list: list[RemasteredSaveListParam] = []
        for i, save_entry in enumerate(self.save_entries):
            output_entry_dict_result = save_entry.to_dict()
            if not output_entry_dict_result:
                LOGGER.error(f"Failed to convert save entry {i} to json")
                return False
            output_list.append(output_entry_dict_result.value)
        output_json_buffer += json.dumps(output_list, indent=indent, separators=separators).encode("utf-8")
        return True

    @staticmethod
    def from_json(input_json: str | bytes | bytearray, output_save_list: SaveListContents) -> bool:
        try:
            save_list_contents_array: list[RemasteredSaveListParam] = json.loads(input_json)
        except json.JSONDecodeError as err:
            LOGGER.error(f"Failed to convert string to JSON: {err}")
            return False

        if not isinstance(save_list_contents_array, list):
            LOGGER.error(f"JSON data should be an array:\n{save_list_contents_array}")
            return False

        save_entries: list[SaveListEntry] = []
        for save_entry_data in save_list_contents_array:
            save_entries.append(SaveListEntry())
            # Convert the entry back into a dictionary
            if isinstance(save_entry_data, dict) and not SaveListEntry.from_dict(save_entry_data, save_entries[-1]):
                return False

        output_save_list.save_entries = save_entries
        return True


class RemasteredSystemSaveFileParam(TypedDict):
    pass


class RemasteredSystemSaveDataParam(TypedDict):
    NativeData: str
    NobleData: str


class RemasteredSystemSave(TypedDict):
    """Dictionary of the complete remastered system save data"""

    FileParam: RemasteredSystemSaveFileParam
    DataParam: RemasteredSystemSaveDataParam


class SystemSaveContents:
    """
    Stores the system data from the SystemSaveData.sav file
    """

    system_save_json_dict: RemasteredSystemSave

    def __init__(self):
        self.system_save_json_dict = RemasteredSystemSave(FileParam={}, DataParam={"NativeData": "", "NobleData": ""})

    def to_encrypt_bytes(self, output_data: bytearray) -> bool:
        """
        Encrypt system save contents and
        Return True if encryption is successful
        """

        def encrypt_file_param() -> bool:
            # Get system save file param as compact json string
            system_file_param_bytes = json.dumps(
                self.system_save_json_dict["FileParam"], separators=COMPACT_JSON_SEPARATORS
            ).encode("utf-8")

            # Encrypt the json data
            padded_buffer = pad(system_file_param_bytes, GRACES_F_AES_BLOCK_SIZE)
            encrypt_buffer = bytearray(padded_buffer)
            cipher_cbc = AES.new(GRACES_F_AES_SAVE_KEY, mode=AES.MODE_CBC, iv=GRACES_F_AES_SAVE_IV)
            cipher_cbc.encrypt(padded_buffer, encrypt_buffer)
            # write the encrypted data size
            encrypted_size = len(encrypt_buffer)

            encrypt_data = bytearray()
            encrypt_data += encrypted_size.to_bytes(length=4, byteorder="little")
            # write the crc32 value for the encrypted data
            encrypt_data += crc32(encrypt_buffer).to_bytes(length=4, byteorder="little")
            # write the encrypted data
            encrypt_data += encrypt_buffer

            nonlocal output_data
            # Write the data twice to the save file
            for _ in range(GRACES_F_SECTION_ITER_COUNT):
                # Pad the output data array with '00' bytes until it is at the output_offset
                output_data += encrypt_data
                bytes_to_add = GRACES_F_REMASTERED_SYSTEM_FILE_PARAM_STEP - len(encrypt_data)
                if bytes_to_add > 0:
                    output_data += bytes(bytes_to_add)
            return True

        if not encrypt_file_param():
            return False

        def encrypt_data_param() -> bool:

            # Get system save file param as compact json string
            system_data_param_bytes = json.dumps(
                self.system_save_json_dict["DataParam"], separators=COMPACT_JSON_SEPARATORS
            ).encode("utf-8")

            # Encrypt the json data
            padded_buffer = pad(system_data_param_bytes, GRACES_F_AES_BLOCK_SIZE)
            encrypt_buffer = bytearray(padded_buffer)
            cipher_cbc = AES.new(GRACES_F_AES_SAVE_KEY, mode=AES.MODE_CBC, iv=GRACES_F_AES_SAVE_IV)
            cipher_cbc.encrypt(padded_buffer, encrypt_buffer)
            # write the encrypted data size
            encrypted_size = len(encrypt_buffer)

            encrypt_data = bytearray()
            encrypt_data += encrypted_size.to_bytes(length=4, byteorder="little")
            # write the crc32 value for the encrypted data
            encrypt_data += crc32(encrypt_buffer).to_bytes(length=4, byteorder="little")
            # write the encrypted data
            encrypt_data += encrypt_buffer

            nonlocal output_data
            # Write the data twice to the save file
            for _ in range(GRACES_F_SECTION_ITER_COUNT):
                # Pad the output data array with '00' bytes until it is at the output_offset
                output_data += encrypt_data
                bytes_to_add = GRACES_F_REMASTERED_SYSTEM_DATA_PARAM_STEP - len(encrypt_data)
                if bytes_to_add > 0:
                    output_data += bytes(bytes_to_add)
            return True

        if not encrypt_data_param():
            return False
        return True

    @staticmethod
    def from_encrypt_bytes(input_data: bytes | memoryview, output_system_save: SystemSaveContents) -> bool:
        """
        Decrypt System Save contents from encrypted byte buffer
        Populates the :output_save_list: parameter on success
        """
        if len(input_data) != GRACES_F_REMASTERED_SYSTEM_SAVE_SIZE:
            LOGGER.error(
                f"Encrypted System Save file must have size of {GRACES_F_REMASTERED_SYSTEM_SAVE_SIZE}.\n"
                f"Actual file size is {len(input_data)}"
            )
            return False

        SYSTEM_SAVE_SIZE_OFFSET_REL = 0x0
        SYSTEM_SAVE_ENCRYPTION_OFFSET_REL = 0x8

        # Read the encrypted data for the File Param section
        def decrypt_file_param() -> bool:
            file_param_size = int.from_bytes(
                input_data[SYSTEM_SAVE_SIZE_OFFSET_REL : SYSTEM_SAVE_SIZE_OFFSET_REL + 4], "little"
            )
            if file_param_size > len(input_data):
                LOGGER.error(
                    f"Encrypted file param size {file_param_size} is invalid."
                    f" It must be less than encrypted system save size of {len(input_data)}"
                )
                return False

            start_offset = SYSTEM_SAVE_ENCRYPTION_OFFSET_REL
            end_offset = start_offset + file_param_size
            encrypted_view = memoryview(input_data)[start_offset:end_offset]
            decrypt_buffer = bytearray(len(encrypted_view))
            cipher_cbc = AES.new(GRACES_F_AES_SAVE_KEY, mode=AES.MODE_CBC, iv=GRACES_F_AES_SAVE_IV)
            cipher_cbc.decrypt(encrypted_view, decrypt_buffer)
            unpadded_buffer = unpad(bytes(decrypt_buffer), GRACES_F_AES_BLOCK_SIZE)
            try:
                system_file_param_json: RemasteredSystemSaveFileParam = json.loads(unpadded_buffer)
            except json.JSONDecodeError as err:
                LOGGER.error(f"Failed to decode string {unpadded_buffer.decode()} as json: {err}")
                return False

            output_system_save.system_save_json_dict["FileParam"] = system_file_param_json
            return True

        if not decrypt_file_param():
            return False

        # Read the encrypted data for the Data Param section
        def decrypt_data_param() -> bool:
            data_param_offset = GRACES_F_REMASTERED_SYSTEM_DATA_PARAM_OFFSET + SYSTEM_SAVE_SIZE_OFFSET_REL
            data_param_size = int.from_bytes(input_data[data_param_offset : data_param_offset + 4], "little")
            if data_param_size > len(input_data):
                LOGGER.error(
                    f"Encrypted data param size {data_param_size} is invalid."
                    f" It must be less than encrypted system save size of {len(input_data)}"
                )
                return False

            start_offset = data_param_offset + SYSTEM_SAVE_ENCRYPTION_OFFSET_REL
            end_offset = start_offset + data_param_size
            encrypted_view = memoryview(input_data)[start_offset:end_offset]
            decrypt_buffer = bytearray(len(encrypted_view))
            cipher_cbc = AES.new(GRACES_F_AES_SAVE_KEY, mode=AES.MODE_CBC, iv=GRACES_F_AES_SAVE_IV)
            cipher_cbc.decrypt(encrypted_view, decrypt_buffer)
            unpadded_buffer = unpad(bytes(decrypt_buffer), GRACES_F_AES_BLOCK_SIZE)
            try:
                system_data_param_json: RemasteredSystemSaveDataParam = json.loads(unpadded_buffer)
            except json.JSONDecodeError as err:
                LOGGER.error(f"Failed to decode string {unpadded_buffer.decode()} as json: {err}")
                return False

            output_system_save.system_save_json_dict["DataParam"] = system_data_param_json
            return True

        if not decrypt_data_param():
            return False

        return True

    def to_json(
        self,
        output_json_buffer: bytearray,
        indent: int | str | None = None,
        separators: tuple[str, str] | None = COMPACT_JSON_SEPARATORS,
    ) -> bool:
        output_json_buffer += json.dumps(self.system_save_json_dict, indent=indent, separators=separators).encode(
            "utf-8"
        )
        return True

    @staticmethod
    def from_json(input_json: str | bytes | bytearray, output_system_save: SystemSaveContents) -> bool:
        try:
            system_save_dict: RemasteredSystemSave = json.loads(input_json)
        except json.JSONDecodeError as err:
            LOGGER.error(f"Failed to convert string to JSON: {err}")
            return False
        output_system_save.system_save_json_dict = system_save_dict
        return True

    @property
    def raw_save_binary_buffer(self) -> bytes:
        """Return the Native System Save data"""
        save_data_dict: RemasteredSystemSaveDataParam = self.system_save_json_dict.get("DataParam")
        if save_data_dict:
            return base64.b64decode(save_data_dict["NativeData"])
        return b""

    @raw_save_binary_buffer.setter
    def raw_save_binary_buffer(self, raw_save_bytes: bytes):
        """Writes the raw System save data to the "NativeData" key"""
        save_data_dict: RemasteredSystemSaveDataParam = self.system_save_json_dict.get("DataParam")
        if save_data_dict:
            save_data_dict["NativeData"] = base64.b64encode(raw_save_bytes).decode("utf-8")

    @property
    def noble_save_binary_buffer(self) -> bytes:
        save_data_dict: RemasteredSystemSaveDataParam = self.system_save_json_dict.get("DataParam")
        if save_data_dict:
            return base64.b64decode(save_data_dict["NobleData"])
        return b""

    @noble_save_binary_buffer.setter
    def noble_save_binary_buffer(self, noble_save_bytes: bytes):
        """Writes the raw System save data to the "BobleData" key"""
        save_data_dict: RemasteredSystemSaveDataParam = self.system_save_json_dict.get("DataParam")
        if save_data_dict:
            save_data_dict["NobleData"] = base64.b64encode(noble_save_bytes).decode("utf-8")

    def read_json_save(
        self,
        file_path: Path,
    ) -> bool:
        """
        Return a boolean indicating if the JSON system save data was successfully read
        """
        if not file_path.exists():
            return False

        with file_path.open("rb") as infile:
            try:
                self.system_save_json_dict = json.loads(infile.read())
            except BlockingIOError as err:
                LOGGER.error(f"Unable to read data from input file {file_path}: {err}")
                return False
            except json.JSONDecodeError as dec_err:
                LOGGER.error(f"Failed to decode byte data into utf-8 {file_path}: {dec_err}")
                return False
        return True

    def read_binary_raw_save(self, file_path: Path) -> bool:
        """
        Return a boolean indicating if the JSON system save data TOGSYS.bin was successfully read
        """
        if not file_path.exists():
            return False

        with file_path.open("rb") as infile:
            try:
                self.raw_save_binary_buffer = infile.read()
            except BlockingIOError as err:
                LOGGER.error(f"Unable to read data from input file {file_path}: {err}")
                return False

        return True

    def read_binary_noble_data(self, file_path: Path) -> bool:
        """
        Return a boolean indicating if the JSON system save data TOGSYSNOBLE.bin was successfully read
        """
        if not file_path.exists():
            return False

        with file_path.open("rb") as infile:
            try:
                self.noble_save_binary_buffer = infile.read()
            except BlockingIOError as err:
                LOGGER.error(f"Unable to read data from input file {file_path}: {err}")
                return False
            except json.JSONDecodeError as dec_err:
                LOGGER.error(f"Failed to decode byte data into utf-8 {file_path}: {dec_err}")
                return False
        return True


class PngToJsonConvert(SaveTransformBase):
    """
    Convert a PNG file into a JSON file, that can then be stored in the folder
    containing the decrypted save data that gets re-encrypted back into the save file
    """

    @override
    def _pre_transform(self) -> bool:
        return super()._pre_transform()

    @override
    def _transform(self) -> bool:
        return self.convert_png_to_json()

    @override
    def _post_transform(self) -> bool:
        return super()._post_transform()

    def convert_png_to_json(self) -> bool:
        """
        Converts a png file into Json by Base64 encoding it
        """
        png_save_contents = SaveContents()
        png_save_contents.icon0_png_buffer = self._input_data
        output_save_contents = json.dumps(png_save_contents.save_json_dict, separators=COMPACT_JSON_SEPARATORS)
        return self._output_io.write(output_save_contents.encode("utf-8")) == len(output_save_contents)


class JsonToPngConvert(SaveTransformBase):
    """
    Convert a JSON file containing a "capture" field into a PNG
    """

    @override
    def _pre_transform(self) -> bool:
        return super()._pre_transform()

    @override
    def _transform(self) -> bool:
        return self.convert_json_to_png()

    @override
    def _post_transform(self) -> bool:
        return super()._post_transform()

    def convert_json_to_png(self) -> bool:
        """
        Converts a JSON file containing PNG data into PNG file
        The "capture" field contains the base 64 encoded PNG datam which is decoded
        and written to the output buffer
        """
        try:
            save_json_dict: RemasteredSave = json.loads(self._input_data)
        except json.JSONDecodeError as err:
            LOGGER.error(f"Failed to decode string {self._input_data.decode()} as json: {err}")
            return False

        metadata_dict = save_json_dict.get("Metadata")
        if not metadata_dict:
            LOGGER.error(f"Input file {self._input_path} is missing required {GRACES_F_METADATA_SAVE_SECTION} section")
            return False

        png_data = metadata_dict.get("capture")
        if not png_data:
            LOGGER.error(
                f"Input file {self._input_path} {GRACES_F_METADATA_SAVE_SECTION} section is "
                "missing required {GRACES_F_ICON0_KEY} ley"
            )
            return False

        raw_png_data = base64.b64decode(png_data)
        return self._output_io.write(raw_png_data) == len(png_data)


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
        help="If set, outputs the binary TOGAPP.bin file when converting to/from PS3."
        + "This can be used to check if the conversion is correctly endian swapping the data between PS3"
        + " and PC/PS4/etc... Outputs a file of <output-file-path>.debug",
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
        help="Output path to folder to store decrypted files. Defaults to <input-file-path>.<target-format>"
        + " if not specified",
    )


def add_encrypt_arguments(parser: argparse.ArgumentParser) -> None:
    add_crypt_arguments(parser)
    # Add encryption specific arguments
    _ = parser.add_argument(
        "--input",
        "-i",
        type=Path,
        help="Input path to folder containing decrypted save. Defaults to reading the files of SaveData.json,"
        + "TOGAPP.bin, ICON0.png, TOGNOBLE.bin",
    )
    # Add a group for the complete remastered save data json and the raw native save binary file
    raw_save_group = parser.add_argument_group(
        "SaveData", description="Options for specifying path to file containing the raw save data"
    )
    _ = raw_save_group.add_argument(
        "--input-json",
        "-nj",
        type=Path,
        help="Input path to decrypted json to re-encrypt. The Filepath is appended onto the --input arg.\n"
        + "To use a file outside of the --input arg path, an absolute path can be specified",
    )
    _ = raw_save_group.add_argument(
        "--input-native-bin",
        "-nb",
        type=Path,
        help="Input path to the raw binary save data to re-encrypt.\n"
        + "To use a file outside of the --input arg path, an absolute path can be specified\n"
        + "NOTE: This option will replace the 'NativeData' key within the --input-json file"
        + " with the raw binary save data after base64 encoding it",
    )

    # option which allows overriding the png files to use as a thumbnail in the load menu
    _ = parser.add_argument(
        "--input-icon0-png",
        "-ip",
        type=Path,
        help="Input path to the PNG data to encrypt"
        + "To use a file outside of the --input arg path, an absolute path can be specified",
    )

    # option to select the binary noble data file
    _ = parser.add_argument(
        "--input-noble-bin",
        "-ob",
        type=Path,
        help="Input path to the raw binary Noble data to encrypt.\n"
        + "To use a file outside of the --input arg path, an absolute path can be specified\n"
        + "NOTE: This option will replace the 'NobleData' key within the --input-json file",
    )

    # output path argument
    _ = parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output path to store encrypted save. Defaults to <input-file-path>.<target-format>" + " if not specified",
    )


def add_savelist_crypt_arguments(parser: argparse.ArgumentParser) -> None:
    add_general_arguments(parser)
    _ = parser.add_argument(
        "--save-format",
        "-s",
        required=True,
        choices=SUPPORTED_CRYPT_SAVE_FORMATS,
        default=SaveFormat.PC,
        help="Specifies the file save format.",
    )


add_system_save_decrypt_arguments = add_decrypt_arguments


def add_system_save_encrypt_arguments(parser: argparse.ArgumentParser) -> None:
    add_crypt_arguments(parser)
    # Add encryption specific arguments
    _ = parser.add_argument(
        "--input",
        "-i",
        type=Path,
        help="Input path to folder containing decrypted save. Defaults to reading the files of SaveData.json,"
        + "TOGSYS.bin, TOGSYSNOBLE.bin",
    )

    _ = parser.add_argument(
        "--input-json",
        "-nj",
        type=Path,
        help="Input path to decrypted json to re-encrypt. The Filepath is appended onto the --input arg.\n"
        + "To use a file outside of the --input arg path, an absolute path can be specified",
    )
    _ = parser.add_argument(
        "--input-native-bin",
        "-nb",
        type=Path,
        help="Input path to the raw binary save data to re-encrypt.\n"
        + "To use a file outside of the --input arg path, an absolute path can be specified\n"
        + "NOTE: This option will replace the 'NativeData' key within the --input-json file"
        + " with the raw binary save data after base64 encoding it",
    )

    _ = parser.add_argument(
        "--input-noble-bin",
        "-ob",
        type=Path,
        help="Input path to the raw binary Noble data to encrypt.\n"
        + "To use a file outside of the --input arg path, an absolute path can be specified\n"
        + "NOTE: This option will replace the 'NobleData' key within the --input-json file",
    )

    # output path argument
    _ = parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output path to store encrypted save. Defaults to <input-file-path>.<target-format> if not specified",
    )


add_metadata_arguments = add_savelist_crypt_arguments


def add_binary_to_yaml_arguments(parser: argparse.ArgumentParser) -> None:
    # Add general arguments
    _ = parser.add_argument(
        "--input",
        "-i",
        type=Path,
        help="Input path to TOGBIN.app",
        required=True,
    )
    _ = parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output path for yaml file. Defaults to <input-file-path-no-ext>.yaml if not specified",
    )
    _ = parser.add_argument(
        "--save-format",
        "-s",
        required=True,
        choices=SUPPORTED_YAML_SAVE_FORMATS,
        help="Specifies the binary file save format.",
    )
    _ = parser.add_argument(
        "--with-comments",
        "-c",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="When set, annotate the yaml thait is output with comments about the save offset and sizes",
    )


def add_yaml_to_binary_arguments(parser: argparse.ArgumentParser) -> None:
    # Add general arguments
    _ = parser.add_argument(
        "--input",
        "-i",
        type=Path,
        help="Input path to TOGBIN.yaml file",
        required=True,
    )
    _ = parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output path fro binary save file. Defaults to <input-file-path-no-ext>.bin",
    )
    _ = parser.add_argument(
        "--save-format",
        "-s",
        required=True,
        choices=SUPPORTED_YAML_SAVE_FORMATS,
        help="Specifies the binary file save format.",
    )


class GracesFBinSaveToYamlConvert(BinSaveToYamlConvert):
    """
    Convert a TOGAPP.bin binary save to a YAML file
    """

    def __init__(self, args: argparse.Namespace):
        super().__init__(args, struct_type=TalesOfGracesFSaveStruct)

    @override
    def _pre_transform(self) -> bool:
        return super()._pre_transform()

    @override
    def _transform(self) -> bool:
        return super()._transform()

    @override
    def _post_transform(self) -> bool:
        return super()._post_transform()


class GracesFYamlToBinSaveConvert(YamlToBinSaveConvert):
    """
    Convert a YAML file containing Tales of Graces Save Data to TOGAPP.bin binary save
    """

    def __init__(self, args: argparse.Namespace):
        super().__init__(args, struct_type=TalesOfGracesFSaveStruct)

    @override
    def _pre_transform(self) -> bool:
        return super()._pre_transform()

    @override
    def _transform(self) -> bool:
        return super()._transform()

    @override
    def _post_transform(self) -> bool:
        return super()._post_transform()
