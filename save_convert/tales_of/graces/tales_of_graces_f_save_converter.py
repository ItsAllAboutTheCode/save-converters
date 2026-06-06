#!/usr/bin/env python
"""
Tales of Graces f Save Converter, Decrypter and Encrypter
"""

import argparse
import json
import logging
import shutil
import sys
import tempfile
from pathlib import Path
from typing import override

from save_convert.save_converter_base import (
    NSW_TO_PS3_CONVERT_FORMAT,
    PC_TO_PS3_CONVERT_FORMAT,
    PS3_TO_NSW_CONVERT_FORMAT,
    PS3_TO_PC_CONVERT_FORMAT,
    PS3_TO_PS4_CONVERT_FORMAT,
    PS3_TO_PS5_CONVERT_FORMAT,
    PS3_TO_XBOXONE_CONVERT_FORMAT,
    PS3_TO_XBOXSERIESX_CONVERT_FORMAT,
    PS4_TO_PS3_CONVERT_FORMAT,
    PS5_TO_PS3_CONVERT_FORMAT,
    XBOXONE_TO_PS3_CONVERT_FORMAT,
    XBOXSERIESX_TO_PS3_CONVERT_FORMAT,
    ConvertPatchTable,
    PatchCopyBytes,
    PatchSet,
    RangeNotCoveredException,
    SaveConvertBase,
    SaveCryptBase,
    SaveFormat,
)
from save_convert.structs.patch_struct import PatchStructEndianSwap
from save_convert.tales_of.graces.tales_of_graces_f_structs import TalesOfGracesFSaveStruct
from save_convert.tales_of.graces.tales_of_graces_f_utils import (
    DEFAULT_ICON0_PNG_FILENAME,
    DEFAULT_NOBLE_SAVE_BIN_FILENAME,
    DEFAULT_NOBLE_SYSTEM_SAVE_BIN_FILENAME,
    DEFAULT_RAW_SAVE_BIN_FILENAME,
    DEFAULT_RAW_SYSTEM_SAVE_BIN_FILENAME,
    DEFAULT_REMASTERED_SAVE_JSON_FILENAME,
    DEFAULT_REMASTERED_SYSTEM_SAVE_JSON_FILENAME,
    FILENAMES_TO_MOVE,
    GRACES_F_SAVE_SIZE_DICT,
    SYSTEM_FILENAMES_TO_MOVE,
    GracesFBinSaveToYamlConvert,
    GracesFYamlToBinSaveConvert,
    JsonToPngConvert,
    PngToJsonConvert,
    RemasteredSave,
    SaveContents,
    SaveListContents,
    SystemSaveContents,
    add_binary_to_yaml_arguments,
    add_convert_arguments,
    add_decrypt_arguments,
    add_encrypt_arguments,
    add_metadata_arguments,
    add_savelist_crypt_arguments,
    add_system_save_decrypt_arguments,
    add_system_save_encrypt_arguments,
    add_yaml_to_binary_arguments,
)
from save_convert.tales_of.tales_of_utils import COMPACT_JSON_SEPARATORS

SCRIPT_DIR: Path = Path(__file__).parent.resolve()

LOGGER = logging.getLogger("graces_save_converter")
LOGGER.addHandler(logging.StreamHandler(sys.stdout))
LOGGER.setLevel(logging.INFO)


class SaveDecryptGracesF(SaveCryptBase):
    """
    Decrypts an encrypted Tales of Graces f Remastered save (Not PS3 save)
    into a folder containing a decrypted TOGAPP.json/TOGAPP.bin and ICON0.json/ICON0.png and TOGNOBLE.bin
    """

    _decrypted_save_contents: SaveContents

    def __init__(self, args: argparse.Namespace):
        super().__init__(args)
        self._decrypted_save_contents = SaveContents()

        # Add .dec for the default output path
        output_path: Path | None = getattr(args, "output", None)
        if not output_path:
            self._output_path: Path = self._output_path.with_suffix(self._output_path.suffix + ".dec")

    @override
    def _pre_transform(self) -> bool:
        return super()._pre_transform()

    @override
    def _transform(self) -> bool:
        if not SaveContents.from_encrypt_bytes(self._input_data, self._decrypted_save_contents, self._save_format):
            LOGGER.error(f"Failed to decrypt save file {self._input_path}")
            return False
        return True

    @override
    def _post_transform(self) -> bool:
        # Now copy temporary temporary to destination
        with tempfile.TemporaryDirectory() as tmpdir:

            def write_json_and_raw_files(
                json_filename: Path, raw_filename: Path, save_dict: RemasteredSave | None, raw_contents: bytes
            ):
                if save_dict:
                    dump_str = json.dumps(save_dict, separators=COMPACT_JSON_SEPARATORS).encode("utf-8")
                    tmp_output_path = Path(f"{tmpdir}/{json_filename}").resolve()
                    with tmp_output_path.open("wb") as outfile:
                        if outfile.write(dump_str) != len(dump_str):
                            raise IOError(f"Failed to write {len(dump_str)} bytes to output file. Aborting...")

                if raw_contents:
                    tmp_output_path = Path(f"{tmpdir}/{raw_filename}").resolve()
                    with tmp_output_path.open("wb") as binfile:
                        if binfile.write(raw_contents) != len(raw_contents):
                            raise IOError(
                                f"Failed to write {len(raw_contents)} to file {tmp_output_path}." + " Aborting..."
                            )

            # Process Save Data sections
            for json_filename, raw_filename, json_contents, raw_contents in [
                (
                    Path(),
                    DEFAULT_ICON0_PNG_FILENAME,
                    None,
                    self._decrypted_save_contents.icon0_png_buffer,
                ),
                (
                    DEFAULT_REMASTERED_SAVE_JSON_FILENAME,
                    DEFAULT_RAW_SAVE_BIN_FILENAME,
                    self._decrypted_save_contents.save_json_dict,
                    self._decrypted_save_contents.raw_save_binary_buffer,
                ),
                (
                    Path(),
                    DEFAULT_NOBLE_SAVE_BIN_FILENAME,
                    None,
                    self._decrypted_save_contents.noble_save_binary_buffer,
                ),
            ]:
                write_json_and_raw_files(json_filename, raw_filename, json_contents, raw_contents)

            # Close the raw savedata file
            self._output_io.close()

            self._output_path.mkdir(parents=True, exist_ok=True)

            filepaths_to_move = [
                (Path(f"{tmpdir}/{filename}").resolve(), Path(f"{self._output_path}/{filename}").resolve())
                for filename in FILENAMES_TO_MOVE
            ]
            result = True
            for src_path, dst_path in filepaths_to_move:
                if not shutil.move(src_path, dst_path):
                    result = False
            return result


class SaveEncryptGracesF(SaveCryptBase):
    """
    Encrypts folder containing decrypted save contents for Tales of Graces f
    The result is a single file containing the encrypted contents
    """

    _save_contents: SaveContents

    _remastered_json_path: Path | None = None
    _icon0_png_path: Path | None = None
    _native_binary_path: Path | None = None
    _noble_binary_path: Path | None = None

    def __init__(self, args: argparse.Namespace):
        super().__init__(args)
        self._save_contents = SaveContents()

        output_path: Path | None = getattr(args, "output", None)
        if not output_path:
            self._output_path: Path = self._output_path.with_suffix(self._output_path.suffix + ".enc")

        # Raw native save data file
        native_binary_path: Path | None = getattr(args, "input_native_bin", None)
        if native_binary_path:
            self._native_binary_path = self._input_path / native_binary_path if self._input_path else native_binary_path

        # Remastered decrypted save json file
        native_json_path: Path | None = getattr(args, "input_json", None)
        if native_json_path:
            self._remastered_json_path = self._input_path / native_json_path if self._input_path else native_json_path

        # Save thumbnail file
        icon0_png_path: Path | None = getattr(args, "input_icon0_png", None)
        if icon0_png_path:
            self._icon0_png_path = self._input_path / icon0_png_path if self._input_path else icon0_png_path

        # noble save data file
        noble_binary_path: Path | None = getattr(args, "input_noble_bin", None)
        if noble_binary_path:
            self._noble_binary_path = self._input_path / noble_binary_path if self._input_path else noble_binary_path

    @override
    def _pre_transform(self) -> bool:
        # Metadata file processing
        if self._remastered_json_path:
            if not self._save_contents.read_json_save(self._remastered_json_path):
                LOGGER.error(f"Failed to remastered encrypted JSON save data from {self._remastered_json_path}")
                return False
        else:
            default_remastered_json_path = (
                self._input_path / DEFAULT_REMASTERED_SAVE_JSON_FILENAME
                if self._input_path
                else DEFAULT_REMASTERED_SAVE_JSON_FILENAME
            )
            _ = self._save_contents.read_json_save(default_remastered_json_path)

        # Native Data processing
        # The raw binary path is preferred and overrides the JSON base 64 data are mutually exclusive AND required
        if self._native_binary_path:
            if not self._save_contents.read_binary_raw_save(self._native_binary_path):
                LOGGER.error(f"Failed to read raw save data from {self._native_binary_path}")
                return False

        if not self._save_contents.raw_save_binary_buffer:
            default_native_binary_path = (
                self._input_path / DEFAULT_RAW_SAVE_BIN_FILENAME if self._input_path else DEFAULT_RAW_SAVE_BIN_FILENAME
            )
            # Use default metadata file in this case
            if not self._save_contents.read_binary_raw_save(default_native_binary_path):
                LOGGER.error(f"Failed to read raw save data from {default_native_binary_path}")
                return False

        # Load the ICON png data for PNG path
        if self._icon0_png_path:
            if not self._save_contents.read_icon0_png(self._icon0_png_path):
                LOGGER.error(
                    f"Failed to read save thumbnail from {self._icon0_png_path}.\n"
                    "This can be skipped by not specifying the '--input-icon0-png' argument"
                )
                return False
        else:
            default_icon0_png_path = (
                self._input_path / DEFAULT_ICON0_PNG_FILENAME if self._input_path else DEFAULT_ICON0_PNG_FILENAME
            )
            _ = self._save_contents.read_icon0_png(default_icon0_png_path)

        # Noble data processing
        if self._noble_binary_path:
            if not self._save_contents.read_binary_noble_data(self._noble_binary_path):
                LOGGER.error(
                    f"Failed to read NobleData from {self._noble_binary_path}.\n"
                    "This can be skipped by not specifying the '--input-noble-bin' argument"
                )
                return False
        else:
            default_noble_data_path = (
                self._input_path / DEFAULT_NOBLE_SAVE_BIN_FILENAME
                if self._input_path
                else DEFAULT_NOBLE_SAVE_BIN_FILENAME
            )
            # Use default noble data file in this case
            _ = self._save_contents.read_binary_noble_data(default_noble_data_path)

        return True

    @override
    def _transform(self) -> bool:
        encrypt_buffer = bytearray()
        if not self._save_contents.to_encrypt_bytes(encrypt_buffer, self._save_format):
            LOGGER.error(f"Failed to encrypt save file {self._input_path}")
            return False

        return self._output_io.write(encrypt_buffer) == len(encrypt_buffer)

    @override
    def _post_transform(self) -> bool:
        return super()._post_transform()


class SaveConvertGracesFEncrypted(SaveConvertBase):
    """
    Converts between Tales of Graces f(PS3) and Tales of Graces f Remastered saves
    The result is a file of the encrypted save data
    """

    _save_contents: SaveContents
    _debug_ps3_conversion: bool

    def __init__(self, args: argparse.Namespace):
        super().__init__(args)
        self._save_contents = SaveContents()

        # When set, a decrypted dump of the TOGAPP.bin afte converting to/from PS3 Big-Endian
        # to other platforms Little-Endian
        self._debug_ps3_conversion = getattr(args, "debug", False)

    @override
    def _pre_transform(self) -> bool:
        return super()._pre_transform()

    @override
    def _transform(self) -> bool:
        # when not converting between PS3 and other platforms just copy the save data with no modifications
        if (self._convert_format.source != SaveFormat.PS3 and self._convert_format.target != SaveFormat.PS3) or (
            self._convert_format.source == SaveFormat.PS3 and self._convert_format.target == SaveFormat.PS3
        ):
            return self._output_io.write(self._input_data) == len(self._input_data)

        # Decrypt byte buffer into SaveContents structure
        if not SaveContents.from_encrypt_bytes(self._input_data, self._save_contents, self._convert_format.source):
            LOGGER.error(f"Failed to decrypt save file {self._input_path}")
            return False

        # Apply the save patch for conversion to/from PS3 data
        converted_data = self.apply_patch(
            self._save_contents.raw_save_binary_buffer, self._patch_table, self._convert_format
        )
        if not converted_data:
            LOGGER.error(f"Failed to convert data save data using the convert format of {self._convert_format}")
            return False

        # Update the raw save binary and JSON values
        self._save_contents.raw_save_binary_buffer = converted_data

        # Re-encrypt SaveContents structure to byte buffer
        encrypted_buffer = bytearray()
        if not self._save_contents.to_encrypt_bytes(encrypted_buffer, self._convert_format.target):
            LOGGER.error(f"Failed to re-encrypt save data from file {self._input_path} after conversion")
            return False

        if self._debug_ps3_conversion:
            LOGGER.debug("Writing binary dump of converted TOGAPP.bin")
            debug_path: Path = self._output_path.with_suffix(self._output_path.suffix + ".debug")
            with debug_path.open("wb") as dbgfile:
                _ = dbgfile.write(converted_data)

        return self._output_io.write(encrypted_buffer) == len(encrypted_buffer)

    @override
    def _post_transform(self) -> bool:
        return super()._post_transform()

    @override
    def create_save_patch_table(self) -> ConvertPatchTable:
        """Returns a dictionary of offset -> byte array entries that indicates which
        actions should be performed when an address is encountered from the input save

        :param: patch_dlc_item_checks - If True, replaces the DLC obtained item bits from the save file to be unobtained
        This should allow bypassing being unable to load the save due to DLC
        """
        # START Replace Offset Table populate
        new_patch_table: ConvertPatchTable = ConvertPatchTable(
            convert_format_to_patch_set={}, save_format_to_save_size_dict=GRACES_F_SAVE_SIZE_DICT
        )

        new_patch_table.convert_format_to_patch_set[PS3_TO_PC_CONVERT_FORMAT] = PatchSet()
        new_patch_table.convert_format_to_patch_set[PS3_TO_PC_CONVERT_FORMAT].add_patch_entry(
            PatchStructEndianSwap(
                target_offset=0, source_offset=0, struct_type=TalesOfGracesFSaveStruct, byteorder="big"
            )
        )

        # Generate the reverse mmapping
        new_patch_table.convert_format_to_patch_set[PC_TO_PS3_CONVERT_FORMAT] = (
            new_patch_table.convert_format_to_patch_set[PS3_TO_PC_CONVERT_FORMAT].generate_reverse_set()
        )

        # Use the patch table entries for other platforms
        new_patch_table.convert_format_to_patch_set[PS4_TO_PS3_CONVERT_FORMAT] = (
            new_patch_table.convert_format_to_patch_set[PC_TO_PS3_CONVERT_FORMAT]
        )
        new_patch_table.convert_format_to_patch_set[PS3_TO_PS4_CONVERT_FORMAT] = (
            new_patch_table.convert_format_to_patch_set[PS3_TO_PC_CONVERT_FORMAT]
        )
        new_patch_table.convert_format_to_patch_set[PS5_TO_PS3_CONVERT_FORMAT] = (
            new_patch_table.convert_format_to_patch_set[PC_TO_PS3_CONVERT_FORMAT]
        )
        new_patch_table.convert_format_to_patch_set[PS3_TO_PS5_CONVERT_FORMAT] = (
            new_patch_table.convert_format_to_patch_set[PS3_TO_PC_CONVERT_FORMAT]
        )
        new_patch_table.convert_format_to_patch_set[NSW_TO_PS3_CONVERT_FORMAT] = (
            new_patch_table.convert_format_to_patch_set[PC_TO_PS3_CONVERT_FORMAT]
        )
        new_patch_table.convert_format_to_patch_set[PS3_TO_NSW_CONVERT_FORMAT] = (
            new_patch_table.convert_format_to_patch_set[PS3_TO_PC_CONVERT_FORMAT]
        )
        new_patch_table.convert_format_to_patch_set[XBOXONE_TO_PS3_CONVERT_FORMAT] = (
            new_patch_table.convert_format_to_patch_set[PC_TO_PS3_CONVERT_FORMAT]
        )
        new_patch_table.convert_format_to_patch_set[PS3_TO_XBOXONE_CONVERT_FORMAT] = (
            new_patch_table.convert_format_to_patch_set[PS3_TO_PC_CONVERT_FORMAT]
        )
        new_patch_table.convert_format_to_patch_set[XBOXSERIESX_TO_PS3_CONVERT_FORMAT] = (
            new_patch_table.convert_format_to_patch_set[PC_TO_PS3_CONVERT_FORMAT]
        )
        new_patch_table.convert_format_to_patch_set[PS3_TO_XBOXSERIESX_CONVERT_FORMAT] = (
            new_patch_table.convert_format_to_patch_set[PS3_TO_PC_CONVERT_FORMAT]
        )

        # By default copy uncovered range of bytes
        new_patch_table.fill_uncovered_target_offset_ranges(
            lambda target_offset, source_range: PatchCopyBytes(target_offset, source_range)
        )
        valid, error_messages = new_patch_table.validate()
        if not valid:
            raise RangeNotCoveredException("\n".join(error_messages))

        return new_patch_table


class SavelistDecryptGracesF(SaveCryptBase):
    """
    Decrypts file contain list of up to 31 save entries for Tales of Graces f remastered
    The file can be edited to modify the save list entries available for load
    """

    _save_list_contents: SaveListContents

    def __init__(self, args: argparse.Namespace):
        super().__init__(args)
        self._save_list_contents = SaveListContents()

        # Add .dec for the default output path
        output_path: Path | None = getattr(args, "output", None)
        if not output_path:
            self._output_path: Path = self._output_path.with_suffix(self._output_path.suffix + ".dec")

    @override
    def _pre_transform(self) -> bool:
        return super()._pre_transform()

    @override
    def _transform(self) -> bool:
        """
        Decrypt the save list entries into the SaveList structure and write it out
        as a json array
        """
        if not SaveListContents.from_encrypt_bytes(self._input_data, self._save_list_contents):
            LOGGER.error(f'Failed to decrypt input file "{self._input_path}" to save list')
            return False

        output_data = bytearray()
        # Pretty print json when outputting to a file
        if not self._save_list_contents.to_json(output_data, indent=2, separators=None):
            return False
        return self._output_io.write(output_data) == len(output_data)

    @override
    def _post_transform(self) -> bool:
        return super()._post_transform()


class SavelistEncryptGracesF(SaveCryptBase):
    """
    Encrypts file contain list of up to 31 save entries for Tales of Graces f remastered
    The file is used to display the list of saves to load
    """

    _save_list_contents: SaveListContents

    def __init__(self, args: argparse.Namespace):
        super().__init__(args)
        self._save_list_contents = SaveListContents()

        output_path: Path | None = getattr(args, "output", None)
        if not output_path:
            self._output_path: Path = self._output_path.with_suffix(self._output_path.suffix + ".enc")

    @override
    def _pre_transform(self) -> bool:
        if not super()._pre_transform():
            return False

        return SaveListContents.from_json(self._input_data, self._save_list_contents)

    @override
    def _transform(self) -> bool:
        """
        Encrypt the save list from a json file
        """
        output_data = bytearray()
        if not self._save_list_contents.to_encrypt_bytes(output_data):
            return False
        return self._output_io.write(output_data) == len(output_data)

    @override
    def _post_transform(self) -> bool:
        return super()._post_transform()


class SystemSaveDecryptGracesF(SaveCryptBase):
    """
    Decrypts system save file for Tales of Graces f remastered
    """

    _system_save_contents: SystemSaveContents

    def __init__(self, args: argparse.Namespace):
        super().__init__(args)
        self._system_save_contents = SystemSaveContents()

        # Add .dec for the default output path
        output_path: Path | None = getattr(args, "output", None)
        if not output_path:
            self._output_path: Path = self._output_path.with_suffix(self._output_path.suffix + ".dec")

    @override
    def _pre_transform(self) -> bool:
        return super()._pre_transform()

    @override
    def _transform(self) -> bool:
        """
        Decrypt the system save and output it as a JSON string
        """
        if not SystemSaveContents.from_encrypt_bytes(self._input_data, self._system_save_contents):
            LOGGER.error(f'Failed to decrypt input file "{self._input_path}" to system save')
            return False

        return True

    @override
    def _post_transform(self) -> bool:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Store the Complete JSON file (includes the Raw and Noble Save data)
            tmp_output_path = Path(f"{tmpdir}/{DEFAULT_REMASTERED_SYSTEM_SAVE_JSON_FILENAME}").resolve()
            with tmp_output_path.open("wb") as outfile:
                dump_bytes = bytearray()
                # pretty print JSON
                _ = self._system_save_contents.to_json(dump_bytes, indent=2, separators=None)
                if outfile.write(dump_bytes) != len(dump_bytes):
                    raise IOError(f"Failed to write {len(dump_bytes)} bytes to output file. Aborting...")

            # Write the NativeData section to a binary file
            tmp_output_path = Path(f"{tmpdir}/{DEFAULT_RAW_SYSTEM_SAVE_BIN_FILENAME}").resolve()
            with tmp_output_path.open("wb") as outfile:
                output_bytes = self._system_save_contents.raw_save_binary_buffer
                if outfile.write(output_bytes) != len(output_bytes):
                    raise IOError(f"Failed to write {len(output_bytes)} bytes to output file. Aborting...")

            # Write the NobleData section to a binary file
            tmp_output_path = Path(f"{tmpdir}/{DEFAULT_NOBLE_SYSTEM_SAVE_BIN_FILENAME}").resolve()
            with tmp_output_path.open("wb") as outfile:
                output_bytes = self._system_save_contents.noble_save_binary_buffer
                if outfile.write(output_bytes) != len(output_bytes):
                    raise IOError(f"Failed to write {len(output_bytes)} bytes to output file. Aborting...")

            # Close the raw savedata file
            self._output_io.close()

            self._output_path.mkdir(parents=True, exist_ok=True)

            filepaths_to_move = [
                (Path(f"{tmpdir}/{filename}").resolve(), Path(f"{self._output_path}/{filename}").resolve())
                for filename in SYSTEM_FILENAMES_TO_MOVE
            ]
            result = True
            for src_path, dst_path in filepaths_to_move:
                if not shutil.move(src_path, dst_path):
                    result = False
            return result


class SystemSaveEncryptGracesF(SaveCryptBase):
    """
    Encrypts file contain list of up to 31 save entries for Tales of Graces f remastered
    The file is used to display the list of saves to load
    """

    _system_save_contents: SystemSaveContents

    _remastered_json_path: Path | None = None
    _native_binary_path: Path | None = None
    _noble_binary_path: Path | None = None

    def __init__(self, args: argparse.Namespace):
        super().__init__(args)
        self._system_save_contents = SystemSaveContents()

        output_path: Path | None = getattr(args, "output", None)
        if not output_path:
            self._output_path: Path = self._output_path.with_suffix(self._output_path.suffix + ".enc")

        # Raw native save data file
        native_binary_path: Path | None = getattr(args, "input_native_bin", None)
        if native_binary_path:
            self._native_binary_path = self._input_path / native_binary_path if self._input_path else native_binary_path

        # Remastered decrypted save json file
        native_json_path: Path | None = getattr(args, "input_json", None)
        if native_json_path:
            self._remastered_json_path = self._input_path / native_json_path if self._input_path else native_json_path

        # noble save data file
        noble_binary_path: Path | None = getattr(args, "input_noble_bin", None)
        if noble_binary_path:
            self._noble_binary_path = self._input_path / noble_binary_path if self._input_path else noble_binary_path

    @override
    def _pre_transform(self) -> bool:
        if self._remastered_json_path:
            if not self._system_save_contents.read_json_save(self._remastered_json_path):
                LOGGER.error(f"Failed to remastered encrypted JSON save data from {self._remastered_json_path}")
                return False
        else:
            default_remastered_json_path = (
                self._input_path / DEFAULT_REMASTERED_SYSTEM_SAVE_JSON_FILENAME
                if self._input_path
                else DEFAULT_REMASTERED_SYSTEM_SAVE_JSON_FILENAME
            )
            _ = self._system_save_contents.read_json_save(default_remastered_json_path)

        # Native Data processing
        if self._native_binary_path:
            if not self._system_save_contents.read_binary_raw_save(self._native_binary_path):
                LOGGER.error(f"Failed to read raw save data from {self._native_binary_path}")
                return False

        if not self._system_save_contents.raw_save_binary_buffer:
            default_native_binary_path = (
                self._input_path / DEFAULT_RAW_SYSTEM_SAVE_BIN_FILENAME
                if self._input_path
                else DEFAULT_RAW_SYSTEM_SAVE_BIN_FILENAME
            )
            # Use default metadata file in this case
            if not self._system_save_contents.read_binary_raw_save(default_native_binary_path):
                LOGGER.error(f"Failed to read raw save data from {default_native_binary_path}")
                return False

        # Noble data processing
        if self._noble_binary_path:
            if not self._system_save_contents.read_binary_noble_data(self._noble_binary_path):
                LOGGER.error(
                    f"Failed to read NobleData from {self._noble_binary_path}.\n"
                    "This can be skipped by not specifying the '--input-noble-bin' argument"
                )
                return False
        else:
            default_noble_data_path = (
                self._input_path / DEFAULT_NOBLE_SYSTEM_SAVE_BIN_FILENAME
                if self._input_path
                else DEFAULT_NOBLE_SYSTEM_SAVE_BIN_FILENAME
            )
            # Use default noble data file in this case
            _ = self._system_save_contents.read_binary_noble_data(default_noble_data_path)

        return True

    @override
    def _transform(self) -> bool:
        """
        Encrypt the save list from a json file
        """
        output_data = bytearray()
        if not self._system_save_contents.to_encrypt_bytes(output_data):
            LOGGER.error(f"Failed to encrypt save file {self._input_path}")
            return False
        return self._output_io.write(output_data) == len(output_data)

    @override
    def _post_transform(self) -> bool:
        return super()._post_transform()


def add_commands(parser: argparse.ArgumentParser) -> None:
    parser.description = (
        "Save Converter for Tales of Graces f Remastered\n"
        + "Supports encryption/decryption for PC, PS5, PS4, Nintendo Switch, XBOX saves if they are console decrypted."
        + "Supports conversion from the Tales of Graces f PS3 save to Tales of Graces f Remastered platform saves."
    )
    # Default to showing help if a sub command is not supplied
    parser.set_defaults(func=lambda _: parser.print_help(sys.stderr))

    graces_subparser = parser.add_subparsers()

    def add_convert_encrypted_save_parser():
        convert_encrypted_save_parser = graces_subparser.add_parser(
            "convert-save",
            description="Convert encrypted Tales of Graces f Remastered save from the source to target format",
        )
        add_convert_arguments(convert_encrypted_save_parser)

        def convert_encrypted_save(args: argparse.Namespace):
            if hasattr(args, "loglevel"):
                LOGGER.setLevel(args.loglevel)
            save_converter = SaveConvertGracesFEncrypted(args)
            return save_converter.transform()

        convert_encrypted_save_parser.set_defaults(func=convert_encrypted_save)

    add_convert_encrypted_save_parser()

    def add_decrypt_save_parser():
        decrypt_parser = graces_subparser.add_parser(
            "decrypt-save",
            description="Decrypt Tales of Graces f Remastered save for the specified save format",
            aliases=["decrypt"],
        )
        add_decrypt_arguments(decrypt_parser)

        def decrypt_save(args: argparse.Namespace):
            if hasattr(args, "loglevel"):
                LOGGER.setLevel(args.loglevel)
            save_decrypter = SaveDecryptGracesF(args)
            return save_decrypter.transform()

        decrypt_parser.set_defaults(func=decrypt_save)

    add_decrypt_save_parser()

    def add_encrypt_save_parser():
        encrypt_parser = graces_subparser.add_parser(
            "encrypt-save",
            description="Encrypt Tales of Graces f Remastered save for the specified save format",
            aliases=["encrypt"],
        )
        add_encrypt_arguments(encrypt_parser)

        def encrypt_save(args: argparse.Namespace):
            if hasattr(args, "loglevel"):
                LOGGER.setLevel(args.loglevel)
            save_encrypter = SaveEncryptGracesF(args)
            return save_encrypter.transform()

        encrypt_parser.set_defaults(func=encrypt_save)

    add_encrypt_save_parser()

    def add_decrypt_savelist_parser():
        decrypt_savelist_parser = graces_subparser.add_parser(
            "decrypt-savelist",
            description="Decrypt Tales of Graces f Remastered SaveDataList.sav."
            + " The file contains the list of save entries",
        )
        add_savelist_crypt_arguments(decrypt_savelist_parser)

        def decrypt_savelist(args: argparse.Namespace):
            if hasattr(args, "loglevel"):
                LOGGER.setLevel(args.loglevel)
            save_decrypter = SavelistDecryptGracesF(args)
            return save_decrypter.transform()

        decrypt_savelist_parser.set_defaults(func=decrypt_savelist)

    add_decrypt_savelist_parser()

    def add_encrypt_savelist_parser():
        encrypt_savelist_parser = graces_subparser.add_parser(
            "encrypt-savelist",
            description="Encrypt Tales of Graces f Remastered SaveDataList.sav."
            + " The file contains the list of save entries",
        )
        add_savelist_crypt_arguments(encrypt_savelist_parser)

        def encrypt_savelist(args: argparse.Namespace):
            if hasattr(args, "loglevel"):
                LOGGER.setLevel(args.loglevel)
            save_encrypter = SavelistEncryptGracesF(args)
            return save_encrypter.transform()

        encrypt_savelist_parser.set_defaults(func=encrypt_savelist)

    add_encrypt_savelist_parser()

    def add_decrypt_system_save_parser():
        decrypt_system_save_parser = graces_subparser.add_parser(
            "decrypt-system-save",
            description="Decrypt Tales of Graces f Remastered SystemSaveData.sav.",
        )
        add_system_save_decrypt_arguments(decrypt_system_save_parser)

        def decrypt_system_save(args: argparse.Namespace):
            if hasattr(args, "loglevel"):
                LOGGER.setLevel(args.loglevel)
            save_decrypter = SystemSaveDecryptGracesF(args)
            return save_decrypter.transform()

        decrypt_system_save_parser.set_defaults(func=decrypt_system_save)

    add_decrypt_system_save_parser()

    def add_encrypt_system_save_parser():
        encrypt_system_save_parser = graces_subparser.add_parser(
            "encrypt-system-save",
            description="Encrypt Tales of Graces f Remastered SystemSaveData.sav",
        )
        add_system_save_encrypt_arguments(encrypt_system_save_parser)

        def encrypt_system_save(args: argparse.Namespace):
            if hasattr(args, "loglevel"):
                LOGGER.setLevel(args.loglevel)
            save_encrypter = SystemSaveEncryptGracesF(args)
            return save_encrypter.transform()

        encrypt_system_save_parser.set_defaults(func=encrypt_system_save)

    add_encrypt_system_save_parser()

    def add_png_to_json_parser():
        png_parser = graces_subparser.add_parser(
            "convert-png-to-json",
            description="Convert a raw png file to JSON",
        )
        add_metadata_arguments(png_parser)

        def convert_png_to_json(args: argparse.Namespace):
            if hasattr(args, "loglevel"):
                LOGGER.setLevel(args.loglevel)
            png_to_json_converter = PngToJsonConvert(args)
            return png_to_json_converter.transform()

        png_parser.set_defaults(func=convert_png_to_json)

    add_png_to_json_parser()

    def add_json_to_png_parser():
        json_parser = graces_subparser.add_parser(
            "convert-json-to-png",
            description="Convert a raw png file to JSON",
        )
        add_metadata_arguments(json_parser)

        def convert_json_to_png(args: argparse.Namespace):
            if hasattr(args, "loglevel"):
                LOGGER.setLevel(args.loglevel)
            json_to_png_converter = JsonToPngConvert(args)
            return json_to_png_converter.transform()

        json_parser.set_defaults(func=convert_json_to_png)

    add_json_to_png_parser()

    def add_binary_save_to_yaml_parser():
        png_parser = graces_subparser.add_parser(
            "convert-save-to-yaml",
            description="Convert TOGAPP.bin file to YAML",
        )
        add_binary_to_yaml_arguments(png_parser)

        def convert_save_to_yaml(args: argparse.Namespace):
            if hasattr(args, "loglevel"):
                LOGGER.setLevel(args.loglevel)
            save_to_yaml_converter = GracesFBinSaveToYamlConvert(args)
            return save_to_yaml_converter.transform()

        png_parser.set_defaults(func=convert_save_to_yaml)

    add_binary_save_to_yaml_parser()

    def add_yaml_to_binary_save_parser():
        png_parser = graces_subparser.add_parser(
            "convert-yaml-to-save",
            description="Convert TOGAPP.bin file to YAML",
        )
        add_yaml_to_binary_arguments(png_parser)

        def convert_yaml_to_save(args: argparse.Namespace):
            if hasattr(args, "loglevel"):
                LOGGER.setLevel(args.loglevel)
            yaml_to_save_converter = GracesFYamlToBinSaveConvert(args)
            return yaml_to_save_converter.transform()

        png_parser.set_defaults(func=convert_yaml_to_save)

    add_yaml_to_binary_save_parser()


def main():
    parser = argparse.ArgumentParser(
        description="Tool to convert, decrypt, encrypt saves for Tales of Graces f Remastered between"
        " Nintendo Switch, PS3, PS4, PS5, PC, XBox One, XBox Series X",
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
