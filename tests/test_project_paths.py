"""The layout must retain resolvable evidence and historical manifest references."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from project_paths import ROOT, CAPTURES, evidence, capture_base


class EvidencePathsTests(unittest.TestCase):
    def test_relocated_evidence_map(self):
        mapping = json.loads((CAPTURES / 'path-map.json').read_text())
        for old, new in mapping.items():
            # Raw files are local-only, so their existence is not required in a clone.
            if Path(new).suffix in ('.f64', '.pcap'):
                continue
            with self.subTest(identifier=old):
                self.assertEqual(evidence(old), ROOT / new)

    def test_historical_manifest_segment_bases(self):
        for path in CAPTURES.rglob('*-manifest.json'):
            for segment in json.loads(path.read_text())['segments']:
                with self.subTest(manifest=path.name, segment=segment['base']):
                    base = capture_base(segment['base'])
                    self.assertTrue(Path(str(base) + '.json').is_file())


if __name__ == '__main__':
    unittest.main()
