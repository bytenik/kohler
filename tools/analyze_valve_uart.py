"""Passive UART candidates for RJ11 valve captures; no display framing assumptions."""

import argparse
import collections
import json
import mmap
from pathlib import Path


def decode(samples, rate, baud, invert, parity):
    period = rate / baud
    previous = (samples[0] > 0) ^ invert
    pending = 0
    blocked = -1
    frames = []
    for i, voltage in enumerate(samples):
        level = (voltage > 0) ^ invert
        if level == previous:
            pending = 0
            continue
        pending += 1
        if pending < max(1, round(rate * 1e-6)):
            continue
        previous = level
        edge = i - pending + 1
        pending = 0
        if level or edge < blocked:
            continue
        bit_count = 10 if parity == 'none' else 11
        positions = [round(edge + (j + .5) * period) for j in range(bit_count)]
        if positions[-1] >= len(samples):
            break
        bits = [(samples[j] > 0) ^ invert for j in positions]
        parity_valid = parity == 'none' or sum(bits[1:10]) % 2 == (parity == 'odd')
        frames.append({'time_s': edge / rate,
                       'byte': sum(int(bits[j+1]) << j for j in range(8)),
                       'valid': not bits[0] and bool(bits[-1]) and parity_valid})
        blocked = edge + (bit_count - .3) * period
    return frames


def modbus_crc(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ (0xA001 if crc & 1 else 0)
    return crc


parser = argparse.ArgumentParser()
parser.add_argument('base', type=Path)
parser.add_argument('--baud', type=int, default=9600)
parser.add_argument('--parity', choices=('none', 'even', 'odd'), default='none')
args = parser.parse_args()
from project_paths import capture_base, recording_file
args.base = capture_base(args.base)
meta = json.loads(args.base.with_suffix('.json').read_text())
if meta.get('bus') != 'valve':
    raise ValueError('Expected explicitly labeled valve capture')
results = {'bus': 'RJ11 valve pins 4/5', 'metadata': meta, 'baud_candidate': args.baud,
           'data_bits_candidate': 8, 'parity_candidate': args.parity, 'stop_bits_sampled': 1,
           'candidates': []}
with recording_file(args.base.with_suffix('.f64')) as path, path.open('rb') as stream:
    raw = mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ)
    samples = memoryview(raw).cast('d')
    for invert in (False, True):
        frames = decode(samples, meta['sample_rate'], args.baud, invert, args.parity)
        groups = []
        for frame in frames:
            if not groups or frame['time_s'] - groups[-1][-1]['time_s'] > 4.5 * 10 / args.baud:
                groups.append([])
            groups[-1].append(frame)
        messages = []
        for group in groups:
            data = bytes(f['byte'] for f in group)
            messages.append({'time_s': group[0]['time_s'], 'hex': data.hex(' ').upper(),
                             'framing_valid': all(f['valid'] for f in group),
                             'modbus_crc_valid': len(data) >= 4 and modbus_crc(data) == 0})
        result = {'positive_is_one': not invert, 'frames': len(frames),
                  'framing_errors': sum(not f['valid'] for f in frames), 'messages': messages}
        packets = []
        cursor = 0
        while cursor + 6 <= len(frames):
            if [f['byte'] for f in frames[cursor:cursor+2]] != [0xAA, 0x55]:
                cursor += 1
                continue
            length = 6 + frames[cursor+4]['byte']
            group = frames[cursor:cursor+length]
            if len(group) != length:
                break
            data = bytes(f['byte'] for f in group)
            packets.append({'time_s': group[0]['time_s'], 'hex': data.hex(' ').upper(),
                            'framing_valid': all(f['valid'] for f in group),
                            'additive_checksum_valid': sum(data) % 256 == 0,
                            'maximum_byte_start_gap_s': max(b['time_s']-a['time_s'] for a,b in zip(group,group[1:]))})
            cursor += length
        result['candidate_packets'] = packets
        results['candidates'].append(result)
        print('positive_is_one', not invert, 'frames', len(frames), 'errors', result['framing_errors'])
        print('distinct messages', dict(collections.Counter(m['hex'] for m in messages)))
        print('first messages', messages[:8])
        print('AA55 length/checksum candidates', dict(collections.Counter((p['hex'], p['framing_valid'], p['additive_checksum_valid']) for p in packets)))
    del samples
    raw.close()
Path(str(args.base) + f'-uart-{args.parity}-analysis.json').write_text(json.dumps(results, indent=2) + '\n')
