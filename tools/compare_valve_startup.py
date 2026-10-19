"""Compare passive valve startup sequences, separating pre-cycle traffic."""

import argparse
import collections
import json
from pathlib import Path


from project_paths import REPORTS, capture_base, evidence


def summarize(base):
    manifest = json.loads(evidence(base + '-manifest.json').read_text())
    parts = []
    for segment in manifest['segments']:
        analysis = json.loads(evidence(segment['base'] + '-uart-odd-analysis.json').read_text())
        candidate = next(c for c in analysis['candidates'] if not c['positive_is_one'])
        packets = [p for p in candidate['candidate_packets']
                   if p['framing_valid'] and p['additive_checksum_valid']]
        discovery_index = next((i for i, p in enumerate(packets)
                                if bytes.fromhex(p['hex'])[2:4] == b'\x1f\x3a'), None)
        origin = packets[discovery_index]['time_s'] if discovery_index is not None else None
        post = packets[discovery_index:] if discovery_index is not None else []
        poll_index = next((i for i, p in enumerate(post)
                           if p['hex'] == 'AA 55 00 01 00 00'), None)
        startup = post[:poll_index] if poll_index is not None else post
        exchanges = []
        for a, b in zip(startup, startup[1:]):
            aa, bb = bytes.fromhex(a['hex']), bytes.fromhex(b['hex'])
            if aa[2] == 0 and bb[2] == 1:
                exchanges.append({'request': a['hex'], 'reply': b['hex'],
                                  'request_command_hex': f'{aa[3]:02X}',
                                  'reply_payload_hex': bb[5:-1].hex(' ').upper(),
                                  'time_after_discovery_s': a['time_s'] - origin})
        parts.append({'base': segment['base'], 'duration_s': segment['duration_s'],
                      'uart_frames': candidate['frames'], 'uart_errors': candidate['framing_errors'],
                      'candidate_packets': len(candidate['candidate_packets']),
                      'valid_packets': len(packets),
                      'decoded_bytes_accounted_for': sum(len(bytes.fromhex(p['hex'])) for p in packets),
                      'packet_counts': dict(collections.Counter(p['hex'] for p in packets)),
                      'pre_discovery_packets': discovery_index,
                      'discovery_capture_time_s': origin,
                      'startup_sequence': [p['hex'] for p in startup],
                      'startup_exchanges': exchanges,
                      'first_poll_after_discovery_s': (post[poll_index]['time_s'] - origin
                                                       if poll_index is not None else None)})
    return {'capture': base, 'interruptions': manifest['interruptions'], 'parts': parts}


parser = argparse.ArgumentParser()
parser.add_argument('captures', nargs='+')
args = parser.parse_args()
results = [summarize(base) for base in args.captures]
comparison = {'captures': results, 'startup_comparisons': []}
first = results[0]['parts'][0]
for result in results[1:]:
    other = result['parts'][0]
    comparison['startup_comparisons'].append({
        'baseline': results[0]['capture'], 'other': result['capture'],
        'same_startup_sequence': first['startup_sequence'] == other['startup_sequence'],
        'same_request_reply_bytes': ([(p['request'], p['reply']) for p in first['startup_exchanges']]
                                     == [(p['request'], p['reply']) for p in other['startup_exchanges']]),
    })
(REPORTS / 'valve-startup-comparison.json').write_text(json.dumps(comparison, indent=2) + '\n')
for r in results:
    for p in r['parts']:
        print(r['capture'], {k: v for k, v in p.items()
                             if k not in ('packet_counts', 'startup_exchanges', 'startup_sequence')})
        print('startup sequence', p['startup_sequence'])
print('comparison', comparison['startup_comparisons'])
