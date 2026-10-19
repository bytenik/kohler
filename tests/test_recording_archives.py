"""Archived recordings must be usable without an uncompressed local copy."""
import lzma
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from project_paths import recording_file
from display_protocol import decode_capture


class RecordingArchiveTests(unittest.TestCase):
    def test_unpack_and_cleanup_after_exception(self):
        with tempfile.TemporaryDirectory() as directory:
            original = Path(directory) / 'example.f64'
            payload = b'original recording bytes' * 100
            Path(str(original) + '.xz').write_bytes(lzma.compress(payload))
            with self.assertRaisesRegex(RuntimeError, 'decoder failed'):
                with recording_file(original) as unpacked:
                    self.assertEqual(unpacked.read_bytes(), payload)
                    self.assertFalse(original.exists())
                    extracted = unpacked
                    raise RuntimeError('decoder failed')
            self.assertFalse(extracted.exists())

    def test_plain_recording_preferred(self):
        with tempfile.TemporaryDirectory() as directory:
            original = Path(directory) / 'example.f64'
            original.write_bytes(b'plain')
            Path(str(original) + '.xz').write_bytes(b'not opened')
            with recording_file(original) as path:
                self.assertEqual(path, original.resolve())
            self.assertTrue(original.exists())

    def test_decoder_reads_archive_only_capture(self):
        import array
        import json
        expected = bytes.fromhex('88 03 00 30 45 55')
        bits = [1] * 20
        for byte in expected:
            bits += [0] + [(byte >> i) & 1 for i in range(8)] + [1]
        bits += [1] * 20
        samples = array.array('d', (2.0 if bit else -2.0 for bit in bits for _ in range(16)))
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory) / 'synthetic'
            Path(str(base) + '.f64.xz').write_bytes(lzma.compress(samples.tobytes()))
            Path(str(base) + '.json').write_text(json.dumps({
                'samples': len(samples), 'sample_rate': 115200 * 16,
            }))
            result = decode_capture(base)
            self.assertEqual(len(result['packets']), 1)
            self.assertEqual(result['packets'][0]['hex'], expected.hex(' ').upper())
            self.assertTrue(result['packets'][0]['checksum_valid'])
            self.assertFalse(Path(str(base) + '.f64').exists())
