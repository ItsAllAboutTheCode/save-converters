from io import BytesIO
from unittest import TestCase
from unittest.mock import MagicMock, patch

from pathlib import Path
from argparse import Namespace

from save_convert.save_convert_base import (
    ConvertFormat,
    SaveFormat,
)
from save_convert.vesperia_save_converter import (
    VESPERIA_PC_SAVE_SIZE,
    VESPERIA_PS3_SAVE_SIZE,
    start_convert,
)

SCRIPT_DIR = Path(__file__).parent.resolve()


class TestConvertVesperiaSave(TestCase):
    def setUp(self):
        self.test_filepath: Path = Path(SCRIPT_DIR) / "test_files"

    def test_round_trip_conversion(self):
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
            else:
                return BytesIO(expected_ps3_save_bytes)

        mock_open_method = MagicMock(side_effect=redirect_data_byte_io)

        with (
            patch("io.open", mock_open_method) as _mock_file_open,
            patch("shutil.move") as _mock_shutil_move,
        ):
            test_args = Namespace(
                input=test_file,
                output=self.test_filepath / "SAVE.convert",
                game_name="vesperia",
                convert_format=ConvertFormat(SaveFormat.PS3, SaveFormat.PC),
                patch_dlc_item_checks=False
            )
            # Convert from PS3 to PC save

            self.assertTrue(start_convert(test_args))
            self.assertEqual(len(test_bytes), VESPERIA_PC_SAVE_SIZE)
            # Now convert from PC save back to PC save
            pc_converted_bytes = test_bytes.copy()
            test_bytes.clear()

            def redirect_input_from_byte_io(file, mode, *args):
                if mode == "wb":
                    return mock_output_byteio
                else:
                    # Use the bytes from the previous conversion of PS3 -> PC for the conversion
                    # of PC -> PS3
                    nonlocal pc_converted_bytes
                    return BytesIO(pc_converted_bytes)

            mock_open_method.side_effect = redirect_input_from_byte_io
            test_args.convert_format = ConvertFormat(SaveFormat.PC, SaveFormat.PS3)
            self.assertTrue(start_convert(test_args))
            self.assertEqual(len(test_bytes), VESPERIA_PS3_SAVE_SIZE)
            self.assertSequenceEqual(expected_ps3_save_bytes, test_bytes)
