"""
Contains utility methods and constants for manipulating Tales of Xillia save data
"""

import logging
import sys
from pathlib import Path

SCRIPT_DIR: Path = Path(__file__).parent.resolve()

LOGGER = logging.getLogger("tales_of_utils")
LOGGER.addHandler(logging.StreamHandler(sys.stdout))
LOGGER.setLevel(logging.INFO)

COMPACT_JSON_SEPARATORS = (",", ":")
