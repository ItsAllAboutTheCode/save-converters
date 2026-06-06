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


def format_bitarray(
    buffer: bytes | memoryview[int] | bytearray,
    *,
    bitarray_prefix: str = "0b",
    bitarray_suffix: str = "",
    byte_separator: str = "",
    bit_separator: str = "_",
    bit_separator_count: int | None = None,
) -> str:
    """
    Format a byte buffer as an array of bits

    Example output:
    0b0111000010111001

    Optionally a byte separatorcan be provided to determine the separation between bytes
    Also a bit separator count can be provided to separate every N bits with an underscore '_'

    """
    output_bits_list: list[str] = []
    for value in buffer:
        byte_bits: list[str] = []
        for bit_offset in range(8):
            # The math is inverted

            byte_bits.append(str((value >> bit_offset) & 0b1))
        # reverse the bit list as the bits were added low to high from left to right
        output_bits_list += reversed(byte_bits)

    transform_bits: list[str] = []
    for bit_index in range(len(output_bits_list)):
        if bit_index > 0:
            if byte_separator and (bit_index % 8) == 0:
                transform_bits.append(byte_separator)
            elif bit_separator_count and (bit_index % bit_separator_count) == 0:
                transform_bits.append(bit_separator)
        transform_bits.append(output_bits_list[bit_index])

    return bitarray_prefix + "".join(transform_bits) + bitarray_suffix
