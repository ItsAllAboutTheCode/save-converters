#!/usr/bin/env python
"""
Tales of Eternia f Save Decrypter and Encrypter
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import override

from save_convert.save_converter_base import (
    SaveCryptBase,
)
from save_convert.tales_of.eternia.tales_of_eternia_utils import (
    SaveContents,
    add_decrypt_arguments,
    add_encrypt_arguments,
)

SCRIPT_DIR: Path = Path(__file__).parent.resolve()

LOGGER = logging.getLogger("eternia_save_converter")
LOGGER.addHandler(logging.StreamHandler(sys.stdout))
LOGGER.setLevel(logging.INFO)


class SaveDecryptEternia(SaveCryptBase):
    """
    Decrypts an encrypted Tales of Eternia Remastered save
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

        return self._output_io.write(self._save_contents.save_data) == len(self._save_contents.save_data)

    @override
    def _post_transform(self) -> bool:
        # First the base post_transform method to dump the decrypted SaveData.json to disk
        return super()._post_transform()


class SaveEncryptEternia(SaveCryptBase):
    """
    Encrypts a decrypted Tales of Eternia Remastered save
    """

    _decrypted_save_contents: SaveContents

    def __init__(self, args: argparse.Namespace):
        super().__init__(args)
        self._decrypted_save_contents = SaveContents()

        output_path: Path | None = getattr(args, "output", None)
        if not output_path:
            self._output_path: Path = self._output_path.with_suffix(suffix=self._output_path.suffix + ".enc")

    @override
    def _pre_transform(self) -> bool:
        if not super()._pre_transform():
            return False

        self._decrypted_save_contents.save_data = self._input_data
        return True

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
        "Save Decrypter/Encrypter for Tales of Eternia Remastered\n"
        + "Supports encryption/decryption for PC, PS5, PS4, NSW, XBOX saves if they are console decrypted."
    )
    # Default to showing help if a sub command is not supplied
    parser.set_defaults(func=lambda _: parser.print_help(sys.stderr))

    eternia_subparser = parser.add_subparsers()

    def add_decrypt_save_parser():
        decrypt_parser = eternia_subparser.add_parser(
            "decrypt-save",
            description="Decrypt Tales of Eternia Remastered save for the specified save format",
            aliases=["decrypt"],
        )
        add_decrypt_arguments(decrypt_parser)

        def decrypt_save(args: argparse.Namespace):
            if hasattr(args, "loglevel"):
                LOGGER.setLevel(args.loglevel)
            save_decrypter = SaveDecryptEternia(args)
            return save_decrypter.transform()

        decrypt_parser.set_defaults(func=decrypt_save)

    add_decrypt_save_parser()

    def add_encrypt_save_parser():
        encrypt_parser = eternia_subparser.add_parser(
            "encrypt-save",
            description="Encrypt Tales of Eternia Remastered save for the specified save format",
            aliases=["encrypt"],
        )
        add_encrypt_arguments(encrypt_parser)

        def encrypt_save(args: argparse.Namespace):
            if hasattr(args, "loglevel"):
                LOGGER.setLevel(args.loglevel)
            save_encrypter = SaveEncryptEternia(args)
            return save_encrypter.transform()

        encrypt_parser.set_defaults(func=encrypt_save)

    add_encrypt_save_parser()


def main():
    parser = argparse.ArgumentParser(
        description="Tool to decrypt, encrypt saves for Tales of Eternia Remastered between"
        " Nintendo Switch, PS3, PS4, PS5, PC, Xbox Series X",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    _ = parser.add_argument(
        "--loglevel",
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
