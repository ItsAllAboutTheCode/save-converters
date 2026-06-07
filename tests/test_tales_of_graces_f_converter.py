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
from save_convert.tales_of.graces.tales_of_graces_f_save_converter import (
    add_commands,
)
from save_convert.tales_of.graces.tales_of_graces_f_structs import GRACES_F_RAW_SAVE_SIZE
from save_convert.tales_of.graces.tales_of_graces_f_utils import (
    DEFAULT_RAW_SAVE_BIN_FILENAME,
    DEFAULT_RAW_SYSTEM_SAVE_BIN_FILENAME,
    GRACES_F_RAW_SYSTEM_SAVE_SIZE,
    GRACES_F_REMASTERED_SAVE_SIZE,
    GRACES_F_REMASTERED_SYSTEM_SAVE_SIZE,
)

SCRIPT_DIR = Path(__file__).parent.resolve()


class TestEncryptSaveTuple(NamedTuple):
    save_path: Path
    remastered_save_size: int


class TestDecryptSaveTuple(NamedTuple):
    save_dir: Path
    raw_save_size: int


class TestCryptRoundtripTuple(NamedTuple):
    save_path: Path
    remastered_save_size: int
    raw_save_size: int


class TestCryptSaveConvertTuple(NamedTuple):
    save_path: Path
    convert_formats: list[ConvertFormat]
    save_size_one_trip: int
    save_size: int


class TestRawSaveToYamlTuple(NamedTuple):
    save_path: Path
    save_size: int


# Test the decrypt-save logic
TEST_DECRYPT_PARAM_LIST: list[TestDecryptSaveTuple] = [
    TestDecryptSaveTuple(Path("SAVE.pc.enc"), GRACES_F_RAW_SAVE_SIZE),
]

# Test the encrypt-save logic
TEST_ENCRYPT_PARAM_LIST: list[TestEncryptSaveTuple] = [
    TestEncryptSaveTuple(Path("SAVE.pc.dec"), GRACES_F_REMASTERED_SAVE_SIZE),
]

# Test the convert-save logic which performs
# 1. decryption(if non-PS3)
# 3. save-conversion between formats
# 3. and then encryption (if non-PS3)

TEST_CONVERT_PARAM_LIST: list[TestCryptSaveConvertTuple] = [
    TestCryptSaveConvertTuple(
        Path("SAVE.pc.enc"), [PC_TO_PS3_CONVERT_FORMAT], GRACES_F_RAW_SAVE_SIZE, GRACES_F_REMASTERED_SAVE_SIZE
    ),
    TestCryptSaveConvertTuple(
        Path("SAVE.ps3"), [PS3_TO_PC_CONVERT_FORMAT], GRACES_F_REMASTERED_SAVE_SIZE, GRACES_F_RAW_SAVE_SIZE
    ),
]

# Test the sequential logic of decrypt-save followed by encrypt-save
TEST_DECRYPT_ENCRYPT_ROUND_TRIP_PARAM_LIST: list[TestCryptRoundtripTuple] = [
    TestCryptRoundtripTuple(Path("SAVE.pc.enc"), GRACES_F_REMASTERED_SAVE_SIZE, GRACES_F_RAW_SAVE_SIZE),
]

# Test the roundtrip logic of decrypt-system-save followed by encrypt-system-save
TEST_SYSTEM_DECRYPT_ENCRYPT_ROUND_TRIP_PARAM_LIST: list[TestCryptRoundtripTuple] = [
    TestCryptRoundtripTuple(
        Path("SYSTEM_SAVE.pc.enc"), GRACES_F_REMASTERED_SYSTEM_SAVE_SIZE, GRACES_F_RAW_SYSTEM_SAVE_SIZE
    ),
]

TEST_NATIVE_BIN_TO_YAML_ROUND_TRIP_PARAM_LIST: list[TestRawSaveToYamlTuple] = [
    TestRawSaveToYamlTuple(Path("SAVE.ps3"), GRACES_F_RAW_SAVE_SIZE),
]


class TestConvertGracesFSave(TestCase):
    def setUp(self):
        self.test_filepath: Path = Path(SCRIPT_DIR) / "test_files/graces"
        self.temp_directory: TemporaryDirectory[str] = TemporaryDirectory()

    def test_encrypt_success(self):
        for save_filename, expected_save_size in TEST_ENCRYPT_PARAM_LIST:
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
                    # Get the encrypted bytes from the mock bytesIO buffer
                    mock_byteio_array_tup = mock_output_bytesio_dict.get(output_filepath.name)
                    assert mock_byteio_array_tup is not None
                    test_bytes = mock_byteio_array_tup[1]
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
                    output_directory = Path(self.temp_directory.name) / "SAVE.convert"
                    test_args = parser.parse_args(
                        [
                            "decrypt-save",
                            "-i",
                            str(test_file),
                            "-o",
                            str(output_directory),
                            "-s",
                            str(save_format),
                        ]
                    )

                    raw_save_path = output_directory / DEFAULT_RAW_SAVE_BIN_FILENAME
                    self.assertTrue(test_args.func(test_args))
                    mock_byteio_array_tup = mock_output_bytesio_dict.get(raw_save_path.name)
                    assert mock_byteio_array_tup is not None
                    test_bytes = mock_byteio_array_tup[1]
                    self.assertEqual(len(test_bytes), expected_save_size)

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
                        self.assertEqual(len(original_bytes), expected_save_size)

    def test_save_decrypt_encrypt_roundtrip(self):
        for save_filename, remastered_save_size, raw_save_size in TEST_DECRYPT_ENCRYPT_ROUND_TRIP_PARAM_LIST:
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
                    decrypt_directory = Path(self.temp_directory.name) / "SAVE.convert.dec"
                    test_args = parser.parse_args(
                        [
                            "decrypt-save",
                            "-i",
                            str(test_file),
                            "-o",
                            str(decrypt_directory),
                            "-s",
                            str(save_format),
                        ]
                    )

                    raw_save_path = decrypt_directory / DEFAULT_RAW_SAVE_BIN_FILENAME
                    self.assertTrue(test_args.func(test_args))
                    mock_byteio_array_tup = mock_output_bytesio_dict.get(raw_save_path.name)
                    assert mock_byteio_array_tup is not None
                    test_bytes = mock_byteio_array_tup[1]
                    self.assertEqual(len(test_bytes), raw_save_size)

                    # Now convert back to encrypted save
                    converted_bytes = test_bytes.copy()
                    test_bytes.clear()

                    def redirect_input_from_byte_io(file, mode, *args):
                        if mode == "wb":
                            return update_bytesio(file)
                        # Use the bytes from the previous conversion
                        nonlocal converted_bytes
                        if file.name == raw_save_path.name:
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
                            str(decrypt_directory),
                            "-o",
                            str(encrypted_filepath),
                            "-s",
                            str(save_format),
                        ]
                    )

                    original_path_exists = Path.exists

                    def mock_exists_check(path: Path, *, follow_symlinks: bool = True) -> bool:
                        if path.name == raw_save_path.name:
                            return True
                        return original_path_exists(path, follow_symlinks=follow_symlinks)

                    with patch.object(Path, "exists", mock_exists_check) as _mock_exists_method:
                        # _mock_exists_method.side_effect = mock_exists_check
                        # _mock_exists_method.wraps = Path.exists
                        self.assertTrue(test_args.func(test_args))

                    mock_byteio_array_tup = mock_output_bytesio_dict.get(encrypted_filepath.name)
                    assert mock_byteio_array_tup is not None
                    test_bytes = mock_byteio_array_tup[1]
                    self.assertEqual(len(test_bytes), remastered_save_size)

    def test_system_save_decrypt_encrypt_roundtrip(self):
        for save_filename, remastered_save_size, raw_save_size in TEST_SYSTEM_DECRYPT_ENCRYPT_ROUND_TRIP_PARAM_LIST:
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
                    decrypt_directory = Path(self.temp_directory.name) / "SAVE.convert.dec"
                    test_args = parser.parse_args(
                        [
                            "decrypt-system-save",
                            "-i",
                            str(test_file),
                            "-o",
                            str(decrypt_directory),
                            "-s",
                            str(save_format),
                        ]
                    )

                    raw_save_path = decrypt_directory / DEFAULT_RAW_SYSTEM_SAVE_BIN_FILENAME
                    self.assertTrue(test_args.func(test_args))
                    mock_byteio_array_tup = mock_output_bytesio_dict.get(raw_save_path.name)
                    assert mock_byteio_array_tup is not None
                    test_bytes = mock_byteio_array_tup[1]
                    self.assertEqual(len(test_bytes), raw_save_size)

                    # Now convert back to encrypted save
                    converted_bytes = test_bytes.copy()
                    test_bytes.clear()

                    def redirect_input_from_byte_io(file, mode, *args):
                        if mode == "wb":
                            return update_bytesio(file)
                        # Use the bytes from the previous conversion
                        nonlocal converted_bytes
                        if file.name == raw_save_path.name:
                            return BytesIO(converted_bytes)
                        else:
                            return DEFAULT

                    mock_open_method.side_effect = redirect_input_from_byte_io
                    # Now test the encrypt save method
                    # The path to the encrypted save
                    encrypted_filepath = Path(self.temp_directory.name) / "SAVE.convert.enc"
                    test_args = parser.parse_args(
                        [
                            "encrypt-system-save",
                            "-i",
                            str(decrypt_directory),
                            "-o",
                            str(encrypted_filepath),
                            "-s",
                            str(save_format),
                        ]
                    )

                    original_path_exists = Path.exists

                    def mock_exists_check(path: Path, *, follow_symlinks: bool = True) -> bool:
                        if path.name == raw_save_path.name:
                            return True
                        return original_path_exists(path, follow_symlinks=follow_symlinks)

                    with patch.object(Path, "exists", mock_exists_check) as _mock_exists_method:
                        # _mock_exists_method.side_effect = mock_exists_check
                        # _mock_exists_method.wraps = Path.exists
                        self.assertTrue(test_args.func(test_args))

                    mock_byteio_array_tup = mock_output_bytesio_dict.get(encrypted_filepath.name)
                    assert mock_byteio_array_tup is not None
                    test_bytes = mock_byteio_array_tup[1]
                    self.assertEqual(len(test_bytes), remastered_save_size)

    def test_raw_save_yaml_roundtrip(self):
        for save_filename, expected_save_size in TEST_NATIVE_BIN_TO_YAML_ROUND_TRIP_PARAM_LIST:
            with self.subTest((save_filename)):
                if save_filename.suffixes[0] == ".ps5":
                    save_format = SaveFormat.PS5
                elif save_filename.suffixes[0] == ".ps4":
                    save_format = SaveFormat.PS4
                elif save_filename.suffixes[0] == ".ps3":
                    save_format = SaveFormat.PS3
                elif save_filename.suffixes[0] == ".pc":
                    save_format = SaveFormat.PC
                elif save_filename.suffixes[0] == ".nsw":
                    save_format = SaveFormat.NSW
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
                            "convert-save-to-yaml",
                            "-i",
                            str(test_file),
                            "-o",
                            str(Path(self.temp_directory.name) / "SAVE.yaml"),
                            "-s",
                            str(save_format),
                        ]
                    )

                    # Convert raw TOGAPP.bin save to yaml
                    self.assertTrue(test_args.func(test_args))
                    # Now convert the yaml back into a TOGAPP.bin
                    yaml_bytes = test_bytes.copy()
                    test_bytes.clear()

                    def redirect_input_from_byte_io(file, mode, *args):
                        if mode == "wb":
                            return mock_output_byteio
                        # Use the bytes from the conversion of BIN -> YAML
                        nonlocal yaml_bytes
                        return BytesIO(yaml_bytes)

                    mock_open_method.side_effect = redirect_input_from_byte_io
                    # Now test the encrypt save method
                    test_args = parser.parse_args(
                        [
                            "convert-yaml-to-save",
                            "-i",
                            str(test_file),
                            "-o",
                            str(Path(self.temp_directory.name) / "SAVE.bin"),
                            "-s",
                            str(save_format),
                        ]
                    )
                    self.assertTrue(test_args.func(test_args))
                    self.assertEqual(len(test_bytes), expected_save_size)
                self.assertSequenceEqual(expected_save_bytes, test_bytes)
