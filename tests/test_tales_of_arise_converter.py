from argparse import ArgumentParser
from io import BytesIO
from pathlib import Path
from typing import NamedTuple
from unittest import TestCase
from unittest.mock import MagicMock, patch

from save_convert.save_converter_base import (
    PC_TO_PS4_CONVERT_FORMAT,
    PC_TO_PS5_CONVERT_FORMAT,
    PS4_TO_PC_CONVERT_FORMAT,
    PS4_TO_PS5_CONVERT_FORMAT,
    PS5_TO_PC_CONVERT_FORMAT,
    PS5_TO_PS4_CONVERT_FORMAT,
    ConvertFormat,
    SaveFormat,
)
from save_convert.tales_of.arise.tales_of_arise_save_converter import (
    TALES_OF_ARISE_DLC_SAVE_SIZE,
    TALES_OF_ARISE_SAVE_SIZE,
    add_commands,
)

SCRIPT_DIR = Path(__file__).parent.resolve()


class TestCryptSaveTuple(NamedTuple):
    save_path: Path
    save_size: int


class TestCryptSaveConvertTuple(NamedTuple):
    save_path: Path
    save_size: int
    convert_formats: list[ConvertFormat]


# Test the decrypt-save logic
TEST_DECRYPT_PARAM_LIST: list[TestCryptSaveTuple] = [
    TestCryptSaveTuple(Path("SAVE.ps5.enc"), TALES_OF_ARISE_SAVE_SIZE),
    TestCryptSaveTuple(Path("SAVE.ps4.enc"), TALES_OF_ARISE_SAVE_SIZE),
    TestCryptSaveTuple(Path("SAVE.pc.enc"), TALES_OF_ARISE_SAVE_SIZE),
    TestCryptSaveTuple(Path("DLC_SAVE.ps5.enc"), TALES_OF_ARISE_DLC_SAVE_SIZE),
    TestCryptSaveTuple(Path("DLC_SAVE.pc.enc"), TALES_OF_ARISE_DLC_SAVE_SIZE),
]

# Test the encrypt-save logic
TEST_ENCRYPT_PARAM_LIST: list[TestCryptSaveTuple] = [
    TestCryptSaveTuple(Path("SAVE.ps5.dec"), TALES_OF_ARISE_SAVE_SIZE),
    TestCryptSaveTuple(Path("SAVE.ps4.dec"), TALES_OF_ARISE_SAVE_SIZE),
    TestCryptSaveTuple(Path("SAVE.pc.dec"), TALES_OF_ARISE_SAVE_SIZE),
    TestCryptSaveTuple(Path("DLC_SAVE.ps5.dec"), TALES_OF_ARISE_DLC_SAVE_SIZE),
    TestCryptSaveTuple(Path("DLC_SAVE.pc.dec"), TALES_OF_ARISE_DLC_SAVE_SIZE),
]

# Test the convert-encrypted-save logic which peforms decryption, save-conversion between formats and then encryption
TEST_CONVERT_ENCRYPT_PARAM_LIST: list[TestCryptSaveConvertTuple] = [
    TestCryptSaveConvertTuple(
        Path("SAVE.ps5.enc"), TALES_OF_ARISE_SAVE_SIZE, [PS5_TO_PC_CONVERT_FORMAT, PS5_TO_PS4_CONVERT_FORMAT]
    ),
    TestCryptSaveConvertTuple(
        Path("SAVE.pc.enc"), TALES_OF_ARISE_SAVE_SIZE, [PC_TO_PS5_CONVERT_FORMAT, PC_TO_PS4_CONVERT_FORMAT]
    ),
    TestCryptSaveConvertTuple(
        Path("SAVE.ps4.enc"), TALES_OF_ARISE_SAVE_SIZE, [PS4_TO_PC_CONVERT_FORMAT, PS4_TO_PS5_CONVERT_FORMAT]
    ),
    TestCryptSaveConvertTuple(
        Path("DLC_SAVE.ps5.enc"), TALES_OF_ARISE_DLC_SAVE_SIZE, [PS5_TO_PC_CONVERT_FORMAT, PS5_TO_PS4_CONVERT_FORMAT]
    ),
    TestCryptSaveConvertTuple(
        Path("DLC_SAVE.pc.enc"), TALES_OF_ARISE_DLC_SAVE_SIZE, [PC_TO_PS5_CONVERT_FORMAT, PC_TO_PS4_CONVERT_FORMAT]
    ),
]

# Test the sequential logic of decrypt-save followed by encrypt-save
TEST_DECRYPT_ENCRYPT_ROUND_TRIP_PARAM_LIST: list[TestCryptSaveTuple] = [
    TestCryptSaveTuple(Path("SAVE.ps5.enc"), TALES_OF_ARISE_SAVE_SIZE),
    TestCryptSaveTuple(Path("SAVE.pc.enc"), TALES_OF_ARISE_SAVE_SIZE),
    TestCryptSaveTuple(Path("SAVE.ps4.enc"), TALES_OF_ARISE_SAVE_SIZE),
    TestCryptSaveTuple(Path("DLC_SAVE.ps5.enc"), TALES_OF_ARISE_DLC_SAVE_SIZE),
    TestCryptSaveTuple(Path("DLC_SAVE.pc.enc"), TALES_OF_ARISE_DLC_SAVE_SIZE),
]

TEST_DUMP_ITEM_OFFSETS_PARAM_LIST: list[TestCryptSaveTuple] = [
    TestCryptSaveTuple(Path("SAVE.ps5.enc"), TALES_OF_ARISE_SAVE_SIZE),
    TestCryptSaveTuple(Path("SAVE.pc.enc"), TALES_OF_ARISE_SAVE_SIZE),
    TestCryptSaveTuple(Path("SAVE.ps4.enc"), TALES_OF_ARISE_SAVE_SIZE),
    TestCryptSaveTuple(Path("DLC_SAVE.ps5.enc"), TALES_OF_ARISE_DLC_SAVE_SIZE),
    TestCryptSaveTuple(Path("DLC_SAVE.pc.enc"), TALES_OF_ARISE_DLC_SAVE_SIZE),
]


class TestConvertAriseSave(TestCase):
    def setUp(self):
        self.test_filepath: Path = Path(SCRIPT_DIR) / "test_files/arise"

    def test_encrypt_success(self):
        for save_filename, expected_save_size in TEST_ENCRYPT_PARAM_LIST:
            with self.subTest((save_filename)):
                if save_filename.suffixes[0] == ".ps5":
                    save_format = SaveFormat.PS5
                elif save_filename.suffixes[0] == ".ps4":
                    save_format = SaveFormat.PS4
                elif save_filename.suffixes[0] == ".pc":
                    save_format = SaveFormat.PC
                else:
                    raise ValueError("Invalid save format for test")
                test_file = self.test_filepath / save_filename
                assert test_file.exists()

                expected_save_bytes = test_file.read_bytes()

                test_bytes: bytearray = bytearray()
                wrapped_bytesio = BytesIO()
                mock_output_byteio = MagicMock(wraps=wrapped_bytesio)

                def store_output_bytes(output_data: bytes):
                    test_bytes.extend(output_data)
                    return len(output_data)

                mock_output_context_enter = MagicMock()
                mock_output_byteio.__enter__.return_value = mock_output_context_enter
                mock_output_context_enter.write.side_effect = store_output_bytes

                def redirect_data_byte_io(file, mode, *args):
                    if mode == "wb":
                        return mock_output_byteio
                    return BytesIO(expected_save_bytes)

                mock_open_method = MagicMock(side_effect=redirect_data_byte_io)

                with (
                    patch("io.open", mock_open_method) as _mock_file_open,
                    patch("shutil.move") as _mock_shutil_move,
                ):
                    parser = ArgumentParser(
                        description="Test Parser",
                    )
                    add_commands(parser)
                    test_args = parser.parse_args(
                        [
                            "encrypt-save",
                            "-i",
                            str(test_file),
                            "-o",
                            str(self.test_filepath / "SAVE.convert"),
                            "-s",
                            str(save_format),
                        ]
                    )

                    self.assertTrue(test_args.func(test_args))
                    self.assertEqual(len(test_bytes), expected_save_size)

    def test_decrypt_success(self):
        for save_filename, expected_save_size in TEST_DECRYPT_PARAM_LIST:
            with self.subTest((save_filename)):
                if save_filename.suffixes[0] == ".ps5":
                    save_format = SaveFormat.PS5
                elif save_filename.suffixes[0] == ".ps4":
                    save_format = SaveFormat.PS4
                elif save_filename.suffixes[0] == ".pc":
                    save_format = SaveFormat.PC
                else:
                    raise ValueError("Invalid save format for test")
                test_file = self.test_filepath / save_filename
                assert test_file.exists()

                expected_save_bytes = test_file.read_bytes()

                test_bytes: bytearray = bytearray()
                wrapped_bytesio = BytesIO()
                mock_output_byteio = MagicMock(wraps=wrapped_bytesio)

                def store_output_bytes(output_data: bytes):
                    test_bytes.extend(output_data)
                    return len(output_data)

                mock_output_context_enter = MagicMock()
                mock_output_byteio.__enter__.return_value = mock_output_context_enter
                mock_output_context_enter.write.side_effect = store_output_bytes

                def redirect_data_byte_io(file, mode, *args):
                    if mode == "wb":
                        return mock_output_byteio
                    return BytesIO(expected_save_bytes)

                mock_open_method = MagicMock(side_effect=redirect_data_byte_io)

                with (
                    patch("io.open", mock_open_method) as _mock_file_open,
                    patch("shutil.move") as _mock_shutil_move,
                ):
                    parser = ArgumentParser(
                        description="Test Parser",
                    )
                    add_commands(parser)
                    test_args = parser.parse_args(
                        [
                            "decrypt-save",
                            "-i",
                            str(test_file),
                            "-o",
                            str(self.test_filepath / "SAVE.convert"),
                            "-s",
                            str(save_format),
                        ]
                    )

                    self.assertTrue(test_args.func(test_args))
                    self.assertEqual(len(test_bytes), expected_save_size)

    def test_convert_encrypt_save_roundtrip(self):
        for save_filename, expected_save_size, convert_formats in TEST_CONVERT_ENCRYPT_PARAM_LIST:
            for convert_format in convert_formats:
                with self.subTest(filename=save_filename, conversion=convert_format):
                    test_file = self.test_filepath / save_filename
                    assert test_file.exists()

                    expected_save_bytes = test_file.read_bytes()

                    test_bytes: bytearray = bytearray()
                    wrapped_bytesio = BytesIO()
                    mock_output_byteio = MagicMock(wraps=wrapped_bytesio)

                    def store_output_bytes(output_data: bytes):
                        test_bytes.extend(output_data)
                        return len(output_data)

                    mock_output_context_enter = MagicMock()
                    mock_output_byteio.__enter__.return_value = mock_output_context_enter
                    mock_output_context_enter.write.side_effect = store_output_bytes

                    def redirect_data_byte_io(file, mode, *args):
                        if mode == "wb":
                            return mock_output_byteio
                        return BytesIO(expected_save_bytes)

                    mock_open_method = MagicMock(side_effect=redirect_data_byte_io)

                    with (
                        patch("io.open", mock_open_method) as _mock_file_open,
                        patch("shutil.move") as _mock_shutil_move,
                    ):
                        parser = ArgumentParser(
                            description="Test Parser",
                        )
                        add_commands(parser)
                        test_args = parser.parse_args(
                            [
                                "convert-encrypted-save",
                                "-i",
                                str(test_file),
                                "-o",
                                str(self.test_filepath / "SAVE.convert"),
                                "-f",
                                str(convert_format),
                            ]
                        )

                        # Convert from PS5 to PC save
                        self.assertTrue(test_args.func(test_args))
                        self.assertEqual(len(test_bytes), expected_save_size)
                        # Now convert from PC save back to PS5 save
                        pc_converted_bytes = test_bytes.copy()
                        test_bytes.clear()

                        def redirect_input_from_byte_io(file, mode, *args):
                            if mode == "wb":
                                return mock_output_byteio
                            # Use the bytes from the previous conversion of PS5 -> PC for the conversion
                            # of PC -> PS5
                            nonlocal pc_converted_bytes
                            return BytesIO(pc_converted_bytes)

                        mock_open_method.side_effect = redirect_input_from_byte_io
                        test_args.convert_format = convert_format.create_reverse()
                        self.assertTrue(test_args.func(test_args))
                        self.assertEqual(len(test_bytes), expected_save_size)
                    self.assertSequenceEqual(expected_save_bytes, test_bytes)

    def test_decrypt_encrypt_roundtrip(self):
        for save_filename, expected_save_size in TEST_DECRYPT_ENCRYPT_ROUND_TRIP_PARAM_LIST:
            with self.subTest((save_filename)):
                if save_filename.suffixes[0] == ".ps5":
                    save_format = SaveFormat.PS5
                elif save_filename.suffixes[0] == ".ps4":
                    save_format = SaveFormat.PS4
                elif save_filename.suffixes[0] == ".pc":
                    save_format = SaveFormat.PC
                else:
                    raise ValueError("Invalid save format for test")
                test_file = self.test_filepath / save_filename
                assert test_file.exists()

                expected_save_bytes = test_file.read_bytes()

                test_bytes: bytearray = bytearray()
                wrapped_bytesio = BytesIO()
                mock_output_byteio = MagicMock(wraps=wrapped_bytesio)

                def store_output_bytes(output_data: bytes):
                    test_bytes.extend(output_data)
                    return len(output_data)

                mock_output_context_enter = MagicMock()
                mock_output_byteio.__enter__.return_value = mock_output_context_enter
                mock_output_context_enter.write.side_effect = store_output_bytes

                def redirect_data_byte_io(file, mode, *args):
                    if mode == "wb":
                        return mock_output_byteio
                    return BytesIO(expected_save_bytes)

                mock_open_method = MagicMock(side_effect=redirect_data_byte_io)

                with (
                    patch("io.open", mock_open_method) as _mock_file_open,
                    patch("shutil.move") as _mock_shutil_move,
                ):
                    parser = ArgumentParser(
                        description="Test Parser",
                    )
                    add_commands(parser)
                    test_args = parser.parse_args(
                        [
                            "decrypt-save",
                            "-i",
                            str(test_file),
                            "-o",
                            str(self.test_filepath / "SAVE.convert.dec"),
                            "-s",
                            str(save_format),
                        ]
                    )

                    # Convert from PS5 to PC save
                    self.assertTrue(test_args.func(test_args))
                    self.assertEqual(len(test_bytes), expected_save_size)
                    # Now convert from PC save back to PS5 save
                    pc_converted_bytes = test_bytes.copy()
                    test_bytes.clear()

                    def redirect_input_from_byte_io(file, mode, *args):
                        if mode == "wb":
                            return mock_output_byteio
                        # Use the bytes from the previous conversion of PS5 -> PC for the conversion
                        # of PC -> PS5
                        nonlocal pc_converted_bytes
                        return BytesIO(pc_converted_bytes)

                    mock_open_method.side_effect = redirect_input_from_byte_io
                    # Now test the encrypt save method
                    test_args = parser.parse_args(
                        [
                            "encrypt-save",
                            "-i",
                            str(test_file),
                            "-o",
                            str(self.test_filepath / "SAVE.convert.enc"),
                            "-s",
                            str(save_format),
                        ]
                    )
                    self.assertTrue(test_args.func(test_args))
                    self.assertEqual(len(test_bytes), expected_save_size)
                self.assertSequenceEqual(expected_save_bytes, test_bytes)

    def test_dump_save_section_offsets_success(self):
        for save_filename, _ in TEST_DUMP_ITEM_OFFSETS_PARAM_LIST:
            with self.subTest((save_filename)):
                if save_filename.suffixes[0] == ".ps5":
                    save_format = SaveFormat.PS5
                elif save_filename.suffixes[0] == ".ps4":
                    save_format = SaveFormat.PS4
                elif save_filename.suffixes[0] == ".pc":
                    save_format = SaveFormat.PC
                else:
                    raise ValueError("Invalid save format for test")
                test_file = self.test_filepath / save_filename
                assert test_file.exists()

                expected_save_bytes = test_file.read_bytes()

                test_bytes: bytearray = bytearray()
                wrapped_bytesio = BytesIO()
                mock_output_byteio = MagicMock(wraps=wrapped_bytesio)

                def store_output_bytes(output_data: bytes):
                    test_bytes.extend(output_data)
                    return len(output_data)

                mock_output_context_enter = MagicMock()
                mock_output_byteio.__enter__.return_value = mock_output_context_enter
                mock_output_context_enter.write.side_effect = store_output_bytes

                def redirect_data_byte_io(file, mode, *args):
                    if mode == "wb":
                        return mock_output_byteio
                    return BytesIO(expected_save_bytes)

                mock_open_method = MagicMock(side_effect=redirect_data_byte_io)

                with (
                    patch("io.open", mock_open_method) as _mock_file_open,
                    patch("shutil.move") as _mock_shutil_move,
                ):
                    parser = ArgumentParser(
                        description="Test Parser",
                    )
                    add_commands(parser)
                    test_args = parser.parse_args(
                        [
                            "dump-save-offsets",
                            "-i",
                            str(test_file),
                            "-s",
                            str(save_format),
                        ]
                    )

                    self.assertTrue(test_args.func(test_args))
