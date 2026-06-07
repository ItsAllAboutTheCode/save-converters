import io
from argparse import ArgumentParser
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import NamedTuple
from unittest import TestCase
from unittest.mock import DEFAULT, MagicMock, patch

from save_convert.save_converter_base import (
    PC_TO_PS3_CONVERT_FORMAT,
    PS3_TO_PC_CONVERT_FORMAT,
    ConvertFormat,
    SaveFormat,
)
from save_convert.tales_of.xillia.tales_of_xillia_save_converter import (
    add_commands,
)
from save_convert.tales_of.xillia.tales_of_xillia_structs import XILLIA_PS3_SAVE_SIZE

SCRIPT_DIR = Path(__file__).parent.resolve()


class TestEncryptSaveTuple(NamedTuple):
    save_path: Path


class TestDecryptSaveTuple(NamedTuple):
    save_dir: Path


class TestCryptRoundtripTuple(NamedTuple):
    save_path: Path


class TestConvertSaveRoundtripTuple(NamedTuple):
    save_path: Path
    convert_formats: list[ConvertFormat]
    save_size_one_trip: int | None
    save_size: int | None


# Test the decrypt-save logic
TEST_DECRYPT_PARAM_LIST: list[TestDecryptSaveTuple] = [
    TestDecryptSaveTuple(Path("SAVE.pc.enc")),
]

# Test the encrypt-save logic
TEST_ENCRYPT_PARAM_LIST: list[TestEncryptSaveTuple] = [
    TestEncryptSaveTuple(Path("SAVE.pc.dec")),
]

# Test the convert-save logic which performs
# 1. decryption(if non-PS3)
# 3. save-conversion between formats
# 3. and then encryption (if non-PS3)

TEST_CONVERT_PARAM_LIST: list[TestConvertSaveRoundtripTuple] = [
    TestConvertSaveRoundtripTuple(Path("SAVE.pc.enc"), [PC_TO_PS3_CONVERT_FORMAT], XILLIA_PS3_SAVE_SIZE, None),
    TestConvertSaveRoundtripTuple(Path("SAVE.ps3"), [PS3_TO_PC_CONVERT_FORMAT], None, XILLIA_PS3_SAVE_SIZE),
]

# Test the sequential logic of decrypt-save followed by encrypt-save
TEST_DECRYPT_ENCRYPT_ROUND_TRIP_PARAM_LIST: list[TestCryptRoundtripTuple] = [
    TestCryptRoundtripTuple(
        Path("SAVE.pc.enc"),
    ),
]


class TestConvertXilliaSave(TestCase):
    def setUp(self):
        self.test_filepath: Path = Path(SCRIPT_DIR) / "test_files/xillia"
        self.temp_directory: TemporaryDirectory[str] = TemporaryDirectory()

    def test_encrypt_success(self):
        for (save_filename,) in TEST_ENCRYPT_PARAM_LIST:
            with self.subTest((save_filename)):
                if save_filename.suffixes[0] == ".ps5":
                    save_format = SaveFormat.PS5
                elif save_filename.suffixes[0] == ".ps4":
                    save_format = SaveFormat.PS4
                elif save_filename.suffixes[0] == ".pc":
                    save_format = SaveFormat.PC
                elif save_filename.suffixes[0] == ".nsw":
                    save_format = SaveFormat.NSW
                else:
                    raise ValueError("Invalid save format for test")
                test_file = self.test_filepath / save_filename
                assert test_file.exists()

                mock_output_bytesio_dict: dict[str, tuple[MagicMock, bytearray]] = {}

                def update_bytesio(filepath: Path):
                    if filepath not in mock_output_bytesio_dict:
                        mock_output_io = MagicMock(wraps=BytesIO())
                        # Store writes in mapped in byte array
                        mock_output_context_enter = MagicMock()
                        output_byte_buffer = bytearray()

                        def store_output_bytes(output_data: bytes):
                            output_byte_buffer.extend(output_data)
                            return len(output_data)

                        mock_output_context_enter.write.side_effect = store_output_bytes
                        mock_output_io.__enter__.return_value = mock_output_context_enter
                        mock_output_bytesio_dict[filepath.name] = (mock_output_io, output_byte_buffer)

                    return mock_output_bytesio_dict[filepath.name][0]

                def redirect_data_byte_io(file, mode, *args):
                    if mode == "wb":
                        return update_bytesio(file)
                    return DEFAULT

                mock_open_method = MagicMock(side_effect=redirect_data_byte_io, wraps=io.open)

                with (
                    patch("io.open", mock_open_method) as _mock_file_open,
                    patch("shutil.move") as _mock_shutil_move,
                ):
                    parser = ArgumentParser(
                        description="Test Parser",
                    )
                    add_commands(parser)
                    output_filepath = Path(self.temp_directory.name) / "SAVE.convert"
                    test_args = parser.parse_args(
                        [
                            "encrypt-save",
                            "-i",
                            str(test_file),
                            "-o",
                            str(output_filepath),
                            "-s",
                            str(save_format),
                        ]
                    )

                    self.assertTrue(test_args.func(test_args))

    def test_decrypt_success(self):
        for (save_filename,) in TEST_DECRYPT_PARAM_LIST:
            with self.subTest((save_filename)):
                if save_filename.suffixes[0] == ".ps5":
                    save_format = SaveFormat.PS5
                elif save_filename.suffixes[0] == ".ps4":
                    save_format = SaveFormat.PS4
                elif save_filename.suffixes[0] == ".pc":
                    save_format = SaveFormat.PC
                elif save_filename.suffixes[0] == ".nsw":
                    save_format = SaveFormat.NSW
                else:
                    raise ValueError("Invalid save format for test")
                test_file = self.test_filepath / save_filename
                assert test_file.exists()

                mock_output_bytesio_dict: dict[str, tuple[MagicMock, bytearray]] = {}

                def update_bytesio(filepath: Path):
                    if filepath not in mock_output_bytesio_dict:
                        mock_output_io = MagicMock(wraps=BytesIO())
                        # Store writes in mapped in byte array
                        mock_output_context_enter = MagicMock()
                        output_byte_buffer = bytearray()

                        def store_output_bytes(output_data: bytes):
                            output_byte_buffer.extend(output_data)
                            return len(output_data)

                        mock_output_context_enter.write.side_effect = store_output_bytes
                        mock_output_io.__enter__.return_value = mock_output_context_enter
                        mock_output_bytesio_dict[filepath.name] = (mock_output_io, output_byte_buffer)

                    return mock_output_bytesio_dict[filepath.name][0]

                def redirect_data_byte_io(file, mode, *args):
                    if mode == "wb":
                        return update_bytesio(file)
                    return DEFAULT

                mock_open_method = MagicMock(side_effect=redirect_data_byte_io, wraps=io.open)

                with (
                    patch("io.open", mock_open_method) as _mock_file_open,
                    patch("shutil.move") as _mock_shutil_move,
                ):
                    parser = ArgumentParser(
                        description="Test Parser",
                    )
                    add_commands(parser)
                    output_filepath = Path(self.temp_directory.name) / "SAVE.convert"
                    test_args = parser.parse_args(
                        [
                            "decrypt-save",
                            "-i",
                            str(test_file),
                            "-o",
                            str(output_filepath),
                            "-s",
                            str(save_format),
                        ]
                    )

                    self.assertTrue(test_args.func(test_args))

    def test_convert_encrypt_save_roundtrip(self):
        for save_filename, convert_formats, expected_convert_size, expected_save_size in TEST_CONVERT_PARAM_LIST:
            for convert_format in convert_formats:
                with self.subTest(filename=save_filename, conversion=convert_format):
                    test_file = self.test_filepath / save_filename
                    assert test_file.exists()

                    mock_output_bytesio_dict: dict[str, tuple[MagicMock, bytearray]] = {}

                    def update_bytesio(filepath: Path):
                        if filepath not in mock_output_bytesio_dict:
                            mock_output_io = MagicMock(wraps=BytesIO())
                            # Store writes in mapped in byte array
                            mock_output_context_enter = MagicMock()
                            output_byte_buffer = bytearray()

                            def store_output_bytes(output_data: bytes):
                                output_byte_buffer.extend(output_data)
                                return len(output_data)

                            mock_output_context_enter.write.side_effect = store_output_bytes
                            mock_output_io.__enter__.return_value = mock_output_context_enter
                            mock_output_bytesio_dict[filepath.name] = (mock_output_io, output_byte_buffer)

                        return mock_output_bytesio_dict[filepath.name][0]

                    def redirect_data_byte_io(file, mode, *args):
                        if mode == "wb":
                            return update_bytesio(file)
                        return DEFAULT

                    mock_open_method = MagicMock(side_effect=redirect_data_byte_io, wraps=io.open)

                    with (
                        patch("io.open", mock_open_method) as _mock_file_open,
                        patch("shutil.move") as _mock_shutil_move,
                    ):
                        parser = ArgumentParser(
                            description="Test Parser",
                        )
                        add_commands(parser)
                        output_filepath = Path(self.temp_directory.name) / "SAVE.convert"
                        test_args = parser.parse_args(
                            [
                                "convert-save",
                                "-i",
                                str(test_file),
                                "-o",
                                str(output_filepath),
                                "-f",
                                str(convert_format),
                            ]
                        )

                        self.assertTrue(test_args.func(test_args))
                        mock_byteio_array_tup = mock_output_bytesio_dict.get(output_filepath.name)
                        assert mock_byteio_array_tup is not None
                        converted_bytes = mock_byteio_array_tup[1].copy()

                        if expected_convert_size is not None:
                            self.assertEqual(len(converted_bytes), expected_convert_size)

                        # Now convert from back
                        del mock_output_bytesio_dict[output_filepath.name]

                        def redirect_input_from_byte_io(file, mode, *args):
                            if mode == "wb":
                                return update_bytesio(file)
                            # Use the bytes from the previous conversion
                            nonlocal converted_bytes
                            if file.name == save_filename.name:
                                return BytesIO(converted_bytes)
                            else:
                                return DEFAULT

                        mock_open_method.side_effect = redirect_input_from_byte_io
                        test_args.convert_format = convert_format.create_reverse()
                        self.assertTrue(test_args.func(test_args))
                        mock_byteio_array_tup = mock_output_bytesio_dict.get(output_filepath.name)
                        assert mock_byteio_array_tup is not None
                        original_bytes = mock_byteio_array_tup[1]
                        if expected_save_size is not None:
                            self.assertEqual(len(original_bytes), expected_save_size)

    def test_save_decrypt_encrypt_roundtrip(self):
        for (save_filename,) in TEST_DECRYPT_ENCRYPT_ROUND_TRIP_PARAM_LIST:
            with self.subTest((save_filename)):
                if save_filename.suffixes[0] == ".ps5":
                    save_format = SaveFormat.PS5
                elif save_filename.suffixes[0] == ".ps4":
                    save_format = SaveFormat.PS4
                elif save_filename.suffixes[0] == ".pc":
                    save_format = SaveFormat.PC
                elif save_filename.suffixes[0] == ".nsw":
                    save_format = SaveFormat.NSW
                else:
                    raise ValueError("Invalid save format for test")
                test_file = self.test_filepath / save_filename
                assert test_file.exists()

                mock_output_bytesio_dict: dict[str, tuple[MagicMock, bytearray]] = {}

                def update_bytesio(filepath: Path):
                    if filepath not in mock_output_bytesio_dict:
                        mock_output_io = MagicMock(wraps=BytesIO())
                        # Store writes in mapped in byte array
                        mock_output_context_enter = MagicMock()
                        output_byte_buffer = bytearray()

                        def store_output_bytes(output_data: bytes):
                            output_byte_buffer.extend(output_data)
                            return len(output_data)

                        mock_output_context_enter.write.side_effect = store_output_bytes
                        mock_output_io.__enter__.return_value = mock_output_context_enter
                        mock_output_bytesio_dict[filepath.name] = (mock_output_io, output_byte_buffer)

                    return mock_output_bytesio_dict[filepath.name][0]

                def redirect_data_byte_io(file, mode, *args):
                    if mode == "wb":
                        return update_bytesio(file)
                    return DEFAULT

                mock_open_method = MagicMock(side_effect=redirect_data_byte_io, wraps=io.open)

                with (
                    patch("io.open", mock_open_method) as _mock_file_open,
                    patch("shutil.move") as _mock_shutil_move,
                ):
                    parser = ArgumentParser(
                        description="Test Parser",
                    )
                    add_commands(parser)
                    decrypt_filepath = Path(self.temp_directory.name) / "SAVE.convert.dec"
                    test_args = parser.parse_args(
                        [
                            "decrypt-save",
                            "-i",
                            str(test_file),
                            "-o",
                            str(decrypt_filepath),
                            "-s",
                            str(save_format),
                        ]
                    )

                    self.assertTrue(test_args.func(test_args))
                    mock_byteio_array_tup = mock_output_bytesio_dict.get(decrypt_filepath.name)
                    assert mock_byteio_array_tup is not None
                    test_bytes = mock_byteio_array_tup[1]

                    # Now convert back to encrypted save
                    converted_bytes = test_bytes.copy()
                    test_bytes.clear()

                    def redirect_input_from_byte_io(file, mode, *args):
                        if mode == "wb":
                            return update_bytesio(file)
                        # Use the bytes from the previous conversion
                        nonlocal converted_bytes
                        if file.name == decrypt_filepath.name:
                            return BytesIO(converted_bytes)
                        else:
                            return DEFAULT

                    mock_open_method.side_effect = redirect_input_from_byte_io
                    # Now test the encrypt save method
                    # The path to the encrypted save
                    encrypted_filepath = Path(self.temp_directory.name) / "SAVE.convert.enc"
                    test_args = parser.parse_args(
                        [
                            "encrypt-save",
                            "-i",
                            str(decrypt_filepath),
                            "-o",
                            str(encrypted_filepath),
                            "-s",
                            str(save_format),
                        ]
                    )

                    original_path_exists = Path.exists

                    def mock_exists_check(path: Path, *, follow_symlinks: bool = True) -> bool:
                        if path.name == decrypt_filepath.name:
                            return True
                        return original_path_exists(path, follow_symlinks=follow_symlinks)

                    with patch.object(Path, "exists", mock_exists_check) as _mock_exists_method:
                        # _mock_exists_method.side_effect = mock_exists_check
                        # _mock_exists_method.wraps = Path.exists
                        self.assertTrue(test_args.func(test_args))
