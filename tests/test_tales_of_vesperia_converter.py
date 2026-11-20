from argparse import ArgumentParser
from io import BytesIO
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from save_convert.save_converter_base import (
    NSW_TO_PC_CONVERT_FORMAT,
    PC_TO_NSW_CONVERT_FORMAT,
    PC_TO_PS3_CONVERT_FORMAT,
    PS3_TO_PC_CONVERT_FORMAT,
)
from save_convert.tales_of.vesperia.tales_of_vesperia_save_converter import (
    VESPERIA_DEFINITIVE_SAVE_SIZE,
    VESPERIA_PS3_SAVE_SIZE,
    add_commands,
    start_convert,
)

SCRIPT_DIR = Path(__file__).parent.resolve()


class TestConvertVesperiaSave(TestCase):
    def setUp(self):
        self.test_filepath: Path = Path(SCRIPT_DIR) / "test_files/vesperia"

    def test_ps3_to_pc_round_trip_conversion(self):
        test_file = self.test_filepath / "SAVE.ps3"
        assert test_file.exists()

        expected_ps3_save_bytes = test_file.read_bytes()

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
            return BytesIO(expected_ps3_save_bytes)

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
                    "-i",
                    str(test_file),
                    "-o",
                    str(self.test_filepath / "SAVE.convert"),
                    "-f",
                    str(PS3_TO_PC_CONVERT_FORMAT),
                    "--no-patch-dlc-item-checks",
                ]
            )

            # Convert from PS3 to PC save
            self.assertTrue(test_args.func(test_args))
            self.assertEqual(len(test_bytes), VESPERIA_DEFINITIVE_SAVE_SIZE)
            # Now convert from PC save back to PS3 save
            pc_converted_bytes = test_bytes.copy()
            test_bytes.clear()

            def redirect_input_from_byte_io(file, mode, *args):
                if mode == "wb":
                    return mock_output_byteio
                # Use the bytes from the previous conversion of PS3 -> PC for the conversion
                # of PC -> PS3
                nonlocal pc_converted_bytes
                return BytesIO(pc_converted_bytes)

            mock_open_method.side_effect = redirect_input_from_byte_io
            test_args.convert_format = PC_TO_PS3_CONVERT_FORMAT
            self.assertTrue(start_convert(test_args))
            self.assertEqual(len(test_bytes), VESPERIA_PS3_SAVE_SIZE)
            self.assertSequenceEqual(expected_ps3_save_bytes, test_bytes)

    def test_pc_to_switch_round_trip_conversion(self):
        """
        Test that an PC file can be converted to a compressed Switch file and back
        """
        test_file = self.test_filepath / "SAVE.pc"
        assert test_file.exists()

        expected_pc_save_bytes = test_file.read_bytes()

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
            return BytesIO(expected_pc_save_bytes)

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
                    "-i",
                    str(test_file),
                    "-o",
                    str(self.test_filepath / "SAVE.convert"),
                    "-f",
                    str(PC_TO_NSW_CONVERT_FORMAT),
                    "--no-patch-dlc-item-checks",
                ]
            )

            self.assertTrue(test_args.func(test_args))
            # Switch file is compressed, so it should be smaller than the Definitive Edition uncompressed size
            self.assertLess(len(test_bytes), VESPERIA_DEFINITIVE_SAVE_SIZE)
            # Now convert from PC save back to Switch save
            pc_converted_bytes = test_bytes.copy()
            test_bytes.clear()

            def redirect_input_from_byte_io(file, mode, *args):
                if mode == "wb":
                    return mock_output_byteio
                nonlocal pc_converted_bytes
                return BytesIO(pc_converted_bytes)

            mock_open_method.side_effect = redirect_input_from_byte_io
            test_args.convert_format = NSW_TO_PC_CONVERT_FORMAT
            self.assertTrue(start_convert(test_args))
            self.assertEqual(len(test_bytes), VESPERIA_DEFINITIVE_SAVE_SIZE)
            self.assertSequenceEqual(expected_pc_save_bytes, test_bytes)
