#!/usr/bin/env python
"""
Frontend script to select which save converter command to run for a specific game
"""

import argparse
from importlib import import_module
import logging
import sys
from save_convert import converter_modules

logger = logging.getLogger("save_converter")
logger.setLevel(logging.INFO)
stdoutHandler = logging.StreamHandler()
logger.addHandler(stdoutHandler)


def add_commands(parser: argparse.ArgumentParser) -> None:

    subparsers = parser.add_subparsers()
    for parser_name, module_name in converter_modules.items():
        module = import_module(f"save_convert.{module_name}")
        new_parser = subparsers.add_parser(parser_name)
        try:
            if add_commands := getattr(module, "add_commands"):
                add_commands(new_parser)
        except AttributeError as err:
            logger.error(
                f"Module {module.__name__} is missing method 'add_commands': {err}"
            )
            continue


def main():
    parser = argparse.ArgumentParser(
        description="Frontend tool to run save conversion for a specified game",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    add_commands(parser)

    args = parser.parse_args()

    # No arguments have been supplied so print help
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    if hasattr(args, "func"):
        response = args.func(args)
    else:
        logger.error("No convert function is set")
        response = False

    sys.exit(0 if response else 1)


if __name__ == "__main__":
    main()
