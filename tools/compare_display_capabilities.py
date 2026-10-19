"""Compare validated display state responses across saved accessory sessions."""
import collections
import json
from pathlib import Path


from project_paths import ROOT, CAPTURES, REPORTS, evidence


def responses(path):
    result = collections.defaultdict(collections.Counter)
    observations = collections.defaultdict(list)
    for packet in json.loads(path.read_text()).get('packets', []):
        data = bytes.fromhex(packet['hex'])
        if not (packet['framing_valid'] and packet['checksum_valid']):
            continue
        if len(data) < 11 or data[1:5] != bytes([3, 0, 0x34, 1]):
            continue
        if len(data) != data[5] + 8:
            continue
        key = data[7:9].hex(' ').upper()
        payload = data[9:-2].hex(' ').upper()
        result[key][payload] += 1
        observations[key].append({'time_s': packet['time_s'], 'payload': payload,
                                  'packet_hex': packet['hex']})
    return result, observations


def main():
    early_path = evidence('display-settings-01-packets.json')
    connected_path = evidence('system-display-amplifier-10-part-000-packets.json')
    early, _ = responses(early_path)
    connected, _ = responses(connected_path)
    shared = sorted(early.keys() & connected.keys())
    changes = {key: {'earlier': dict(early[key]), 'amplifier_connected': dict(connected[key])}
               for key in shared if set(early[key]) != set(connected[key])}
    candidate_sessions = {}
    for path in sorted(CAPTURES.rglob('*packets.json')):
        values, observations = responses(path)
        if '25 13' in values:
            candidate_sessions[path.name] = {
                'payload_counts': dict(values['25 13']),
                'observations': observations['25 13'],
            }
    result = {
        'baseline': early_path.relative_to(ROOT).as_posix(), 'comparison': connected_path.relative_to(ROOT).as_posix(),
        'shared_keys': shared, 'changed_shared_keys': changes,
        'unchanged_shared_keys': [key for key in shared if key not in changes],
        'candidate_key': '25 13', 'candidate_sessions': candidate_sessions,
        'interpretation': 'Payload offsets 1 and 3 change from 00 to 02 in amplifier-connected sessions. Capability/status candidate; not an isolated causal test.',
        'limitations': ['Earlier sessions lack a uniformly verified amplifier-presence snapshot.',
                        'Captures differ in valve/screen/time state.',
                        'Subtype-00 initialization and other message types are outside this comparison.',
                        'Payload offset 5 also changes during populated playback; this block is not established as presence-only.'],
    }
    (REPORTS / 'display-capability-comparison.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'shared_keys': len(shared), 'changed': changes,
                      'sessions_with_candidate': len(candidate_sessions)}, indent=2))


if __name__ == '__main__':
    main()
