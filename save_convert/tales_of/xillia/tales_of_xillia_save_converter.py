#!/usr/bin/env python
"""
Tales of Xillia f Save Decrypter and Encrypter
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import override

from save_convert.save_converter_base import (
    SaveCryptBase,
)
from save_convert.tales_of.xillia.tales_of_xillia_utils import (
    COMPACT_JSON_SEPARATORS,
    SaveContents,
    add_decrypt_arguments,
    add_encrypt_arguments,
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
        raw_json = json.dumps(self._decrypted_save_contents.save_json_dict, separators=COMPACT_JSON_SEPARATORS).encode(
            "utf-8"
        )
        return self._output_io.write(raw_json) == len(raw_json)

    @override
    def _post_transform(self) -> bool:
        return super()._post_transform()


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
