#!/usr/bin/env python
"""Frontend script to select which save converter command to run for a specific game"""

import argparse
import logging
import sys
from importlib import import_module

from save_convert import converter_modules

LOGGER = logging.getLogger("save_converter")
LOGGER.setLevel(logging.INFO)
stdoutHandler = logging.StreamHandler()
LOGGER.addHandler(stdoutHandler)


def add_commands(parser: argparse.ArgumentParser) -> None:

    subparsers = parser.add_subparsers(dest="subparser_name")
    for parser_name, module_info in converter_modules.items():
        module = import_module(f"{module_info.module}")
        new_parser = subparsers.add_parser(parser_name, aliases=module_info.aliases)
        try:
            if add_commands := module.add_commands:
                add_commands(new_parser)
        except AttributeError as err:
            LOGGER.error(f"Module {module.__name__} is missing method 'add_commands': {err}")
            continue


def main():
    parser = argparse.ArgumentParser(
        description="Frontend tool to run save conversion/decryption for supported games",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.set_defaults(func=lambda _: parser.print_help(sys.stderr))

    _ = parser.add_argument(
        "--log-level",
        "-l",
        default=logging.getLevelName(logging.INFO),
        type=str,
        choices=logging.getLevelNamesMapping(),
        help="Set log level for tool",
    )

    add_commands(parser)

    args = parser.parse_args()
    LOGGER.setLevel(args.log_level)

    # No arguments have been supplied so print help
    if len(sys.argv) == 1:
        parser._subparsers
        parser.print_help(sys.stderr)
        sys.exit(1)

    if hasattr(args, "func"):
        response = args.func(args)
    else:
        parser.print_help(sys.stderr)
        response = False

    sys.exit(0 if response else 1)


if __name__ == "__main__":
    main()
