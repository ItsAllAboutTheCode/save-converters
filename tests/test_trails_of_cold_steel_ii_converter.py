from argparse import ArgumentParser
from io import BytesIO
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from save_convert.save_converter_base import (
    PC_TO_PS4_CONVERT_FORMAT,
    PS4_TO_PC_CONVERT_FORMAT,
)
from save_convert.trails_of.cold_steel_ii.trails_of_cold_steel_ii_save_converter import (
    TRAILS_OF_COLD_STEEL_II_PC_SAVE_SIZE,
    TRAILS_OF_COLD_STEEL_II_PS4_SAVE_SIZE,
    add_commands,
    start_convert,
)

SCRIPT_DIR = Path(__file__).parent.resolve()


class TestConvertTrailsOfColdSteelIISave(TestCase):
    def setUp(self):
        self.test_filepath: Path = Path(SCRIPT_DIR) / "test_files/cold_steel_ii"

    def test_ps4_to_pc(self):
        test_file = self.test_filepath / "SAVE.ps4"
        assert test_file.exists()

        expected_ps4_save_bytes = test_file.read_bytes()

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
            return BytesIO(expected_ps4_save_bytes)

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
                    str(PS4_TO_PC_CONVERT_FORMAT),
                ]
            )

            # Convert from PS4 to PC save
            self.assertTrue(start_convert(test_args))
            self.assertEqual(len(test_bytes), TRAILS_OF_COLD_STEEL_II_PC_SAVE_SIZE)

            # Now convert from PC save back to PS4 save
            pc_converted_bytes = test_bytes.copy()
            test_bytes.clear()

            def redirect_input_from_byte_io(file, mode, *args):
                if mode == "wb":
                    return mock_output_byteio
                # Use the bytes from the previous conversion
                nonlocal pc_converted_bytes
                return BytesIO(pc_converted_bytes)

            mock_open_method.side_effect = redirect_input_from_byte_io
            test_args.convert_format = PC_TO_PS4_CONVERT_FORMAT
            self.assertTrue(start_convert(test_args))
            self.assertEqual(len(test_bytes), TRAILS_OF_COLD_STEEL_II_PS4_SAVE_SIZE)
            self.assertSequenceEqual(expected_ps4_save_bytes, test_bytes)
