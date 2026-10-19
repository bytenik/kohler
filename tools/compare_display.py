"""Compare display packet captures without assigning unverified command meanings."""
import collections
import json
import statistics
from pathlib import Path

from project_paths import REPORTS, evidence

results = {}
for number in ('01','02','03'):
    packets = json.loads(evidence(f'display-settings-{number}-packets.json').read_text())['packets']
    pairs, gaps = [], []
    for first, second in zip(packets, packets[1:]):
        if not all(p['framing_valid'] and p['checksum_valid'] for p in (first,second)):
            continue
        a,b = bytes.fromhex(first['hex']),bytes.fromhex(second['hex'])
        if a[3] == 0x30 and b[3] == 0x31:
            gaps.append((second['time_s']-first['end_time_s']-10/115200)*1000)
        if a[3] == 0x31 and b[3] == 0x34 and len(a)>8 and a[4] == 2:
            pairs.append((a[6:8],b[7:9]))
    windows = []
    duration = json.loads(evidence(f'display-settings-{number}.json').read_text())['duration_s']
    for second in range(int(duration)+bool(duration%1)):
        keys = collections.Counter()
        for packet in packets:
            b=bytes.fromhex(packet['hex'])
            if packet['framing_valid'] and packet['checksum_valid'] and second<=packet['time_s']<second+1 and b[3]==0x31 and len(b)>8 and b[4]==2:
                keys[b[6:8].hex(' ').upper()]+=1
        windows.append({'second':second,'candidate_query_keys':dict(keys)})
    results[number]={'matching_keys':sum(a==b for a,b in pairs),'key_pairs':len(pairs),
                     'poll_reply_gap_ms_median':statistics.median(gaps), 'windows':windows}
(REPORTS / 'display-comparison.json').write_text(json.dumps(results,indent=2)+'\n')
