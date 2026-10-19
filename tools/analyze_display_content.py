"""Inventory printable content in validated display-bus packets."""

import collections
import json
from pathlib import Path
import re


from project_paths import CAPTURES, REPORTS

results = {}
for path in sorted(CAPTURES.rglob('*-packets.json')):
    packets = json.loads(path.read_text())['packets']
    valid = [p for p in packets if p['framing_valid'] and p['checksum_valid']]
    strings = collections.defaultdict(list)
    for packet in valid:
        data = bytes.fromhex(packet['hex'])
        # Printable runs are candidates, not proof of encoded text. Numeric
        # fields can happen to contain printable ASCII bytes.
        for match in re.finditer(rb'[\x20-\x7e]{5,}', data[4:-2]):
            strings[match.group().decode('ascii')].append({
                'time_s': packet['time_s'], 'hex': packet['hex'],
            })
    results[path.stem] = {
        'valid_packets': len(valid),
        'maximum_unescaped_packet_bytes': max((p['length'] for p in valid), default=0),
        'printable_candidates': dict(strings),
    }

(REPORTS / 'display-content-analysis.json').write_text(json.dumps(results, indent=2) + '\n')
