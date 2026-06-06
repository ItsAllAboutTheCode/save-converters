#!/usr/bin/env python
"""
Tales of Xillia f Save Decrypter and Encrypter
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import cast, override

from save_convert.save_converter_base import (
    ConvertPatchTable,
    SaveConvertBase,
    SaveCryptBase,
    SaveFormat,
)
from save_convert.structs.marshal_structure import ToBytesResult
from save_convert.tales_of.xillia.tales_of_xillia_dicts import XilliaRemasteredSaveDict
from save_convert.tales_of.xillia.tales_of_xillia_structs import (
    SAVE_SECTION_TO_CLASS_TABLE,
    XilliaSaveStruct,
)
from save_convert.tales_of.xillia.tales_of_xillia_utils import (
    SaveContents,
    add_convert_arguments,
    add_decrypt_arguments,
    add_encrypt_arguments,
    dump_all_save_block_json_to_directory,
    read_json_save,
)

SCRIPT_DIR: Path = Path(__file__).parent.resolve()

LOGGER = logging.getLogger("xillia_save_converter")
LOGGER.addHandler(logging.StreamHandler(sys.stdout))
LOGGER.setLevel(logging.INFO)


class SaveDecryptXillia(SaveCryptBase):
    """
    Decrypts an encrypted Tales of Xillia Remastered save
    """

    _save_contents: SaveContents
    _dump_save_block_data: bool

    def __init__(self, args: argparse.Namespace):
        super().__init__(args)
        self._save_contents = SaveContents()
        self._dump_save_block_data = getattr(args, "dump_save_block_data", False)

        # Add .dec for the default output path
        output_path: Path | None = getattr(args, "output", None)
        if not output_path:
            self._output_path: Path = self._output_path.with_suffix(self._output_path.suffix + ".dec")

    @override
    def _pre_transform(self) -> bool:
        return super()._pre_transform()

    @override
    def _transform(self) -> bool:
        if not SaveContents.from_encrypt_bytes(self._input_data, self._save_contents, self._save_format):
            LOGGER.error(f"Failed to decrypt save file {self._input_path}")
            return False
        raw_json = json.dumps(self._save_contents.save_json_dict, indent=2).encode("utf-8")
        return self._output_io.write(raw_json) == len(raw_json)

    @override
    def _post_transform(self) -> bool:
        # First the base post_transform method to dump the decrypted SaveData.json to disk
        result = super()._post_transform()
        if not self._dump_save_block_data:
            return result

        dump_all_save_block_json_to_directory(
            self._save_contents, self._output_path.with_suffix(self._output_path.suffix + ".save-block-data")
        )
        # The `result` variable only indicates if the output_path file was successfully written to disk
        # It does not take into account of if a dump file failed to write to disk
        return result


class SaveEncryptXillia(SaveCryptBase):
    """
    Encrypts a decrypted Tales of Xillia Remastered save
    """

    _decrypted_save_contents: SaveContents

    def __init__(self, args: argparse.Namespace):
        super().__init__(args)
        self._decrypted_save_contents = SaveContents()

        output_path: Path | None = getattr(args, "output", None)
        if not output_path:
            self._output_path: Path = self._output_path.with_suffix(self._output_path.suffix + ".enc")

    @override
    def _pre_transform(self) -> bool:
        return read_json_save(self._input_path, self._decrypted_save_contents)

    @override
    def _transform(self) -> bool:
        encrypt_buffer = bytearray()
        if not self._decrypted_save_contents.to_encrypt_bytes(encrypt_buffer, self._save_format):
            LOGGER.error(f"Failed to encrypt save file {self._input_path}")
            return False

        return self._output_io.write(encrypt_buffer) == len(encrypt_buffer)

    @override
    def _post_transform(self) -> bool:
        return super()._post_transform()


class SaveConvertXillia(SaveConvertBase):
    """
    Convert a Tales of Xillia PS3 save to a Tales of Xillia Remastered save
    and vice-versa
    """

    _save_contents: SaveContents
    _debug_ps3_conversion: bool

    def __init__(self, args: argparse.Namespace):
        super().__init__(args)
        self._save_contents = SaveContents()
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

        return self.convert_between_ps3_bin_and_remastered_json_save()

    @override
    def _post_transform(self) -> bool:
        return super()._post_transform()

    @override
    def create_save_patch_table(self) -> ConvertPatchTable:
        return super().create_save_patch_table()

    def convert_between_ps3_bin_and_remastered_json_save(self) -> bool:
        if self._convert_format.source == SaveFormat.PS3:
            if not self.convert_ps3_to_remastered_save():
                return False
            encrypt_buffer = bytearray()

            # Encrypt the save contents before writing to disk
            if not self._save_contents.to_encrypt_bytes(encrypt_buffer, self._convert_format.target):
                LOGGER.error(f"Failed to encrypt save file {self._input_path}")
                return False

            # When the debug option is set, output the converted PS3 save JSON file before encryption
            if self._debug_ps3_conversion:
                LOGGER.debug("Writing binary dump of converted TOGAPP.bin")

                # Write the top level decrypted SaveData JSON. This is what the Remastered game loads
                debug_path: Path = self._output_path.with_suffix(self._output_path.suffix + ".debug")
                with debug_path.open("wb") as dbgfile:
                    _ = dbgfile.write(json.dumps(self._save_contents.save_json_dict, indent=2).encode("utf-8"))

                # Write the inner SaveBlockData JSON files.
                # This is stringified JSON that the Remastered game converts to a structure while loading the top level
                dump_all_save_block_json_to_directory(
                    self._save_contents, debug_path.with_suffix(debug_path.suffix + ".save-block-data")
                )

            return self._output_io.write(encrypt_buffer) == len(encrypt_buffer)
        else:
            to_ps3_result = self.convert_remastered_to_ps3_save()
            if not to_ps3_result or not to_ps3_result.value:
                return False
            output_bytes = to_ps3_result.value
            return self._output_io.write(to_ps3_result.value) == len(output_bytes)

    def convert_ps3_to_remastered_save(self) -> bool:
        xillia_save_struct_result = XilliaSaveStruct.from_bytes(
            memoryview(self._input_data), XilliaSaveStruct, byteorder="big"
        )
        if (
            not xillia_save_struct_result
            or not xillia_save_struct_result.value
            or not xillia_save_struct_result.next_memoryview
        ):
            LOGGER.error(f"Failed to parse {self._input_path} as binary big-endian PS3 save")
            return False

        to_dict_result = xillia_save_struct_result.value.to_dict()
        if not to_dict_result or not to_dict_result.value:
            LOGGER.error("Failed to convert Xillia save structure to dictionary")
            return False

        self._save_contents.save_json_dict = cast(XilliaRemasteredSaveDict, cast(object, to_dict_result.value))
        return True

    def convert_remastered_to_ps3_save(self):

        # Attempt to decrypt input file if not already decrypted
        decrypt_results = SaveContents.from_encrypt_bytes(
            self._input_data,
            self._save_contents,
            self._convert_format.source,
        )
        if not decrypt_results:
            try:
                self._save_contents.save_json_dict = json.loads(self._input_data)
            except json.JSONDecodeError as err:
                LOGGER.error(
                    f"Failed decrypting and converting input file {self._input_path} to"
                    f" Tales of Xillia Remastered save JSON: {err}"
                )
                return ToBytesResult(False)

        output_struct = XilliaSaveStruct()
        for save_section_entry in self._save_contents.save_json_dict["mSaveBlockData"]:
            save_section_class = SAVE_SECTION_TO_CLASS_TABLE.get(save_section_entry["Key"])
            if not save_section_class:
                # If the Save Section class is None, then the binary PS3 save has a size of 0 for the data.
                continue

            save_section_struct = getattr(output_struct, save_section_entry["Key"])
            if not save_section_struct:
                LOGGER.error(f"Tales of Xillia Remastered output struct is missing field: {save_section_entry['Key']}")
                return ToBytesResult(False)

            try:
                save_section_data = json.loads(save_section_entry["Value"])
            except json.JSONDecodeError as err:
                LOGGER.error(f"Failed decoding save block section {save_section_entry['Key']} to JSON: {err}.")
                return ToBytesResult(False)

            section_to_dict_result = type(save_section_struct).from_dict(save_section_data, type(save_section_struct))
            if not section_to_dict_result:
                LOGGER.error(
                    f"Could not create binary structure from JSON key {save_section_entry['Key']}. Aborting..."
                )
                return False

            setattr(output_struct, save_section_entry["Key"], section_to_dict_result.value)

        return output_struct.to_bytes(byteorder="big")


def add_commands(parser: argparse.ArgumentParser) -> None:
    parser.description = (
        "Save Decrypter/Encrtper for Tales of Xillia Remastered\n"
        + "Supports encryption/decryption for PC, PS5, PS4, Nintendo Switch, XBOX saves if they are console decrypted."
    )
    # Default to showing help if a sub command is not supplied
    parser.set_defaults(func=lambda _: parser.print_help(sys.stderr))

    xillia_subparser = parser.add_subparsers()

    def add_decrypt_save_parser():
        decrypt_parser = xillia_subparser.add_parser(
            "decrypt-save",
            description="Decrypt Tales of Xillia Remastered save for the specified save format",
            aliases=["decrypt"],
        )
        add_decrypt_arguments(decrypt_parser)

        def decrypt_save(args: argparse.Namespace):
            if hasattr(args, "loglevel"):
                LOGGER.setLevel(args.loglevel)
            save_decrypter = SaveDecryptXillia(args)
            return save_decrypter.transform()

        decrypt_parser.set_defaults(func=decrypt_save)

    add_decrypt_save_parser()

    def add_encrypt_save_parser():
        encrypt_parser = xillia_subparser.add_parser(
            "encrypt-save",
            description="Encrypt Tales of Xillia Remastered save for the specified save format",
            aliases=["encrypt"],
        )
        add_encrypt_arguments(encrypt_parser)

        def encrypt_save(args: argparse.Namespace):
            if hasattr(args, "loglevel"):
                LOGGER.setLevel(args.loglevel)
            save_encrypter = SaveEncryptXillia(args)
            return save_encrypter.transform()

        encrypt_parser.set_defaults(func=encrypt_save)

    add_encrypt_save_parser()

    def add_convert_save_parser():
        convert_parser = xillia_subparser.add_parser(
            "convert-save",
            description="Convert a Tales of Xillia PS3 save to/from a Tales of Xillia Remastered save",
            aliases=["convert"],
        )
        add_convert_arguments(convert_parser)

        def convert_save(args: argparse.Namespace):
            if hasattr(args, "loglevel"):
                LOGGER.setLevel(args.loglevel)
            save_converter = SaveConvertXillia(args)
            return save_converter.transform()

        convert_parser.set_defaults(func=convert_save)

    add_convert_save_parser()


def main():
    parser = argparse.ArgumentParser(
        description="Tool to decrypt, encrypt saves for Tales of Xillia Remastered between"
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
