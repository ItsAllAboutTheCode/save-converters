from pathlib import Path
from unittest import TestCase

from save_convert.tales_of.tales_of_tlzc_compressor import (
    CompressionSubType,
    CompressionType,
    tlzc_compress,
    tlzc_decompress,
)
from save_convert.tales_of.vesperia.tales_of_vesperia_save_converter import (
    VESPERIA_DEF_EDIT_HEADER,
)

SCRIPT_DIR = Path(__file__).parent.resolve()


class TestTLZCCompressor(TestCase):
    test_filepath: Path = Path()

    def setUp(self):
        self.test_filepath = Path(SCRIPT_DIR) / "test_files/tales_of_utilities"

    def test_compress_lzma(self):
        test_file = self.test_filepath / "SAVE.pc"
        assert test_file.exists()

        test_bytes = test_file.read_bytes()

        compressed_data, result = tlzc_compress(memoryview(test_bytes), CompressionType.LZMA)
        self.assertTrue(result)
        self.assertGreaterEqual(len(compressed_data), 0)

    def test_decompress_lzma(self):
        test_file = self.test_filepath / "SAVE.nsw"
        assert test_file.exists()

        test_bytes = test_file.read_bytes()
        compressed_view = memoryview(test_bytes)[len(VESPERIA_DEF_EDIT_HEADER) :]

        raw_data, result = tlzc_decompress(compressed_view, CompressionType.LZMA)
        self.assertTrue(result)
        self.assertGreaterEqual(len(raw_data), 0)

    def test_compress_zlib_zlib(self):
        test_file = self.test_filepath / "SAVE.pc"
        assert test_file.exists()

        test_bytes = test_file.read_bytes()

        compressed_data, result = tlzc_compress(memoryview(test_bytes), CompressionType.ZLIB, CompressionSubType.ZLIB)
        self.assertTrue(result)
        self.assertGreaterEqual(len(compressed_data), 0)

    def test_compress_zlib_deflate(self):
        test_file = self.test_filepath / "SAVE.pc"
        assert test_file.exists()

        test_bytes = test_file.read_bytes()

        compressed_data, result = tlzc_compress(
            memoryview(test_bytes), CompressionType.ZLIB, CompressionSubType.DEFLATE
        )
        self.assertTrue(result)
        self.assertGreaterEqual(len(compressed_data), 0)

    def test_decompress_zlib_zlib(self):
        test_file = self.test_filepath / "zlib_zlib.tlzc.compressed"
        assert test_file.exists()

        test_bytes = test_file.read_bytes()

        raw_data, result = tlzc_decompress(memoryview(test_bytes), CompressionType.ZLIB, CompressionSubType.ZLIB)
        self.assertTrue(result)
        self.assertGreaterEqual(len(raw_data), 0)

    def test_decompress_zlib_deflate(self):
        test_file = self.test_filepath / "zlib_deflate.tlzc.compressed"
        assert test_file.exists()

        test_bytes = test_file.read_bytes()

        raw_data, result = tlzc_decompress(memoryview(test_bytes), CompressionType.ZLIB, CompressionSubType.DEFLATE)
        self.assertTrue(result)
        self.assertGreaterEqual(len(raw_data), 0)
