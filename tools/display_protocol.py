"""Passive decoding for the DTV+ RJ45 system bus; not the RJ11 valve bus."""
import argparse
import collections
import json
import mmap
import statistics
from pathlib import Path

from project_paths import ROOT, REPORTS, capture_base

START, END, ESCAPE = 0x88, 0x55, 0xAA


def uart_frames(samples, rate, baud=115200, invert=False):
    """Decode 8N1 with explicit polarity, ignoring sub-0.6-us edge ringing."""
    state = (samples[0] > 0) ^ invert
    required = max(1, round(rate * .6e-6))
    pending = 0
    period = rate / baud
    blocked_until = -1
    for i, value in enumerate(samples):
        if ((value > 0) ^ invert) == state:
            pending = 0
            continue
        pending += 1
        if pending < required:
            continue
        state = not state
        pending = 0
        edge = i - required + 1
        if state or edge < blocked_until:
            continue
        if edge + 9.5 * period >= len(samples):
            break
        bits = [int((samples[round(edge + (j + .5) * period)] > 0) ^ invert) for j in range(10)]
        yield {'time_s': edge / rate, 'byte': sum(bits[j + 1] << j for j in range(8)),
               'valid': bits[0] == 0 and bits[9] == 1}
        blocked_until = edge + 9.7 * period


def parse_packets(frames):
    """Use delimiters, not time gaps; retain malformed and truncated evidence."""
    packets, issues = [], []
    wire, decoded, start, escaped, valid = [], [], None, False, True
    for frame in frames:
        value, timestamp = frame['byte'], frame['time_s']
        if not wire:
            if value != START:
                issues.append({'time_s': timestamp, 'reason': 'outside_packet', 'byte': value})
                continue
            wire, decoded, start, valid = [value], [value], timestamp, frame['valid']
            continue
        valid = valid and frame['valid']
        if escaped:
            wire.append(value)
            if value not in (START, END, ESCAPE):
                issues.append({'time_s': timestamp, 'reason': 'unknown_escape', 'byte': value})
                valid = False
            decoded.append(value)
            escaped = False
            continue
        if value == START:
            issues.append({'time_s': start, 'reason': 'restarted_packet', 'wire_hex': bytes(wire).hex(' ').upper()})
            wire, decoded, start, valid = [value], [value], timestamp, frame['valid']
            continue
        wire.append(value)
        if value == ESCAPE:
            escaped = True
            continue
        decoded.append(value)
        if value != END:
            continue
        checksum = len(decoded) >= 3 and sum(decoded[:-1]) % 256 == 0
        packet = {'time_s': start, 'end_time_s': timestamp,
                  'wire_hex': bytes(wire).hex(' ').upper(),
                  'hex': bytes(decoded).hex(' ').upper(), 'framing_valid': valid,
                  'checksum_valid': checksum, 'length': len(decoded)}
        if len(decoded) >= 6:
            packet.update(field_1=decoded[1], field_2=decoded[2], message_type=decoded[3])
            if decoded[3] == 0x34 and len(decoded) >= 8:
                packet['subtype'] = decoded[4]
                if decoded[4] == 1:
                    packet['length_field_valid'] = len(decoded) == decoded[5] + 8
                    packet['length_field_offset'] = 5
                elif decoded[4] == 0 and len(decoded) >= 9:
                    packet['length_field_valid'] = len(decoded) == decoded[6] + 8
                    packet['length_field_offset'] = 6
        packets.append(packet)
        wire, decoded, escaped = [], [], False
    if wire:
        issues.append({'time_s': start, 'reason': 'truncated_packet',
                       'wire_hex': bytes(wire).hex(' ').upper(), 'pending_escape': escaped})
    return packets, issues


def decode_capture(base, invert=False, baud=115200):
    base = capture_base(base)
    meta = json.loads(Path(str(base) + '.json').read_text())
    with open(str(base) + '.f64', 'rb') as source:
        with mmap.mmap(source.fileno(), 0, access=mmap.ACCESS_READ) as mapping:
            samples = memoryview(mapping).cast('d')
            try:
                if len(samples) != meta['samples']:
                    raise ValueError('Sample count does not match metadata')
                frames = list(uart_frames(samples, meta['sample_rate'], baud=baud, invert=invert))
            finally:
                samples.release()
    packets, issues = parse_packets(frames)
    result = {'bus': 'RJ45 system bus pins 3/6', 'capture': base.relative_to(ROOT).as_posix() if base.is_relative_to(ROOT) else str(base), 'metadata': meta,
              'uart': {'baud': baud, 'data_bits': 8, 'parity': None, 'stop_bits': 1,
                       'positive_is_one': not invert, 'frames': len(frames),
                       'framing_errors': sum(not f['valid'] for f in frames)},
              'packets': packets, 'issues': issues}
    Path(str(base) + '-packets.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def summarize(result):
    good = [p for p in result['packets'] if p['framing_valid'] and p['checksum_valid']]
    polls = [p['time_s'] for p in good if p['hex'] == '88 03 00 30 45 55']
    intervals = [b-a for a,b in zip(polls,polls[1:])]
    exchanges = []
    for a,b in zip(good,good[1:]):
        if (a.get('field_1'),a.get('field_2'),a.get('message_type')) == (0,3,0x31) and (b.get('field_1'),b.get('field_2'),b.get('message_type')) == (3,0,0x34):
            exchanges.append((b['time_s']-a['end_time_s'])*1000 - 10/115200*1000)
    return {'capture': result['capture'], 'uart': result['uart'], 'complete_packets': len(result['packets']),
            'valid_packets': len(good), 'issues': dict(collections.Counter(i['reason'] for i in result['issues'])),
            'types': dict(collections.Counter(f"{p.get('message_type'):02X}" for p in good)),
            'type_34_length_checks': [sum(p.get('length_field_valid',False) for p in good),sum(p.get('message_type')==0x34 for p in good)],
            'poll_interval_ms_median': statistics.median(intervals)*1000 if intervals else None,
            '31_to_34_gap_ms_median': statistics.median(exchanges) if exchanges else None}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('captures', nargs='+', type=Path)
    parser.add_argument('--invert', action='store_true')
    parser.add_argument('--baud', type=int, default=115200)
    args = parser.parse_args()
    summaries = [summarize(decode_capture(base, invert=args.invert, baud=args.baud)) for base in args.captures]
    (REPORTS / 'display-analysis-summary.json').write_text(json.dumps(summaries, indent=2)+'\n')
    print(json.dumps(summaries, indent=2))
