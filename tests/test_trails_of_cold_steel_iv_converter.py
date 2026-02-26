from argparse import Namespace
from io import BytesIO
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from save_convert.save_convert_base import (
    ConvertFormat,
    SaveFormat,
)
from save_convert.trails_of.cold_steel_iv.trails_of_cold_steel_iv_save_converter import (
    TRAILS_OF_COLD_STEEL_IV_PC_SAVE_SIZE,
    start_convert,
)

SCRIPT_DIR = Path(__file__).parent.resolve()


class TestConvertTrailsOfColdSteelISave(TestCase):
    def setUp(self):
        self.test_filepath: Path = Path(SCRIPT_DIR) / "test_files/cold_steel_iv"

    def test_ps4_to_pc(self):
        test_file = self.test_filepath / "SAVE.ps4"
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
            test_args = Namespace(
                input=test_file,
                output=self.test_filepath / "SAVE.convert",
                game_name="trails_of_cold_steel_iii",
                convert_format=ConvertFormat(SaveFormat.PS4, SaveFormat.PC),
                patch_dlc_item_checks=False,
            )

            # Convert from PS4 to PC save
            self.assertTrue(start_convert(test_args))
            self.assertEqual(len(test_bytes), TRAILS_OF_COLD_STEEL_IV_PC_SAVE_SIZE)
