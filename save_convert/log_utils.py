"""
Contains General utility methods to help with save conversion
Hex formatting, etc...
"""


def format_hex(buffer: bytes | memoryview[int] | bytearray) -> str:
    """
    Format a byte buffer for human readability
    It will be formatted with the style of
    | XX XX XX XX | XX XX XX XX | XX XX XX XX | XX XX XX XX |
    | XX XX XX XX | XX XX XX XX | XX XX XX XX | XX XX XX XX |
    ...
    | XX XX XX XX | XX XX XX XX | XX XX XX XX | XX XX XX XX |

    Up to the number of bytes in the buffer
    """
    return "".join(
        [
            f"|{value:02X}" if (index % 4 == 0) else f" {value:02X}{'|\n' if index % 16 == 15 else ''}"
            for index, value in enumerate(buffer)
        ]
    )


def pretty_print_hex(buffer: bytes | memoryview[int] | bytearray):
    print(format_hex(buffer), end="")
