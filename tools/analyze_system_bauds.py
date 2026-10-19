"""Compare explicit baud/polarity candidates within contiguous system-bus captures."""

import argparse
import collections
import json
import mmap
from pathlib import Path

from project_paths import capture_base
from display_protocol import parse_packets, uart_frames


parser = argparse.ArgumentParser()
parser.add_argument('base')
parser.add_argument('--bauds', type=int, nargs='+', default=[9600, 19200, 38400, 57600, 115200])
args = parser.parse_args()
args.base = str(capture_base(args.base))
manifest = json.loads(Path(args.base + '-manifest.json').read_text())
results = []
for part in manifest['segments']:
    if not part['samples']:
        continue
    stride = max(1, int(part['sample_rate'] // 500000))
    with open(str(capture_base(part['base'])) + '.f64', 'rb') as stream:
        raw = mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ)
        original = memoryview(raw).cast('d')
        samples = original[::stride]
        rate = part['sample_rate'] / stride
        for baud in args.bauds:
            for invert in (False, True):
                frames = list(uart_frames(samples, rate, baud=baud, invert=invert))
                packets, issues = parse_packets(frames)
                valid = [p for p in packets if p['framing_valid'] and p['checksum_valid']]
                result = {'part': part['base'], 'part_duration_s': part['duration_s'],
                          'part_host_start_approx': part['started_unix_approx'],
                          'analysis_stride': stride, 'analysis_rate': rate,
                          'baud': baud, 'positive_is_one': not invert,
                          'uart_frames': len(frames),
                          'uart_errors': sum(not f['valid'] for f in frames),
                          'complete_packets': len(packets), 'valid_packets': valid,
                          'issues': dict(collections.Counter(i['reason'] for i in issues))}
                results.append(result)
                if valid:
                    print(part['base'], baud, 'positive_one', not invert,
                          'frames', len(frames), 'errors', result['uart_errors'],
                          'valid_packets', len(valid),
                          'first', valid[0]['time_s'], 'last', valid[-1]['time_s'], flush=True)
        samples.release()
        original.release()
        raw.close()
Path(args.base + '-baud-analysis.json').write_text(json.dumps({
    'manifest': manifest, 'tested_bauds': args.bauds, 'candidates': results,
}, indent=2) + '\n')
