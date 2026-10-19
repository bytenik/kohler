import bisect
import csv
import json
import sys
from pathlib import Path


from project_paths import REPORTS, evidence


def decode(path, baud=115200, invert=False):
    with evidence(path).open() as source:
        rows = csv.reader(line for line in source if line.strip() and not line.startswith('#'))
        next(rows)
        data = [(float(row[0]), float(row[1])) for row in rows]
    times = [row[0] for row in data]
    volts = [row[1] for row in data]
    dt = times[1] - times[0]
    # Suppress transitions lasting less than 0.6 us, including edge ringing.
    stable = volts[0] > 0
    required = max(1, round(0.6e-6 / dt))
    pending = 0
    levels = [stable] * len(data)
    for i, voltage in enumerate(volts):
        candidate = voltage > 0
        if candidate != stable:
            pending += 1
            if pending >= required:
                stable = candidate
                for j in range(i - required + 1, i + 1):
                    levels[j] = stable
                pending = 0
        else:
            pending = 0
        levels[i] = stable
    bits = [int(level) ^ invert for level in levels]
    edges = [i for i in range(1, len(bits)) if bits[i] != bits[i - 1]]
    frames = []
    end = -1
    period = 1 / baud
    for i in edges:
        if i < end or bits[i] != 0 or bits[i - 1] != 1:
            continue
        indices = [bisect.bisect_left(times, times[i] + (j + .5) * period) for j in range(10)]
        if indices[-1] >= len(bits):
            break
        sampled = [bits[j] for j in indices]
        frames.append({'time_s': times[i], 'byte': sum(sampled[j + 1] << j for j in range(8)),
                       'valid': sampled[0] == 0 and sampled[9] == 1})
        end = bisect.bisect_left(times, times[i] + 9.7 * period)
    return frames


if __name__ == '__main__':
    results = {}
    for path in sys.argv[1:]:
        frames = decode(path)
        results[path] = frames
        print(path, 'frames', len(frames), 'invalid', sum(not f['valid'] for f in frames))
        groups = []
        for frame in frames:
            if not groups or frame['time_s'] - groups[-1][-1]['time_s'] > 120e-6:
                groups.append([])
            groups[-1].append(frame)
        for group in groups:
            print(f"  {group[0]['time_s'] * 1000:9.3f} ms", ' '.join(f"{f['byte']:02X}" + ('' if f['valid'] else '!') for f in group))
    (REPORTS / 'display-idle-decoded.json').write_text(json.dumps(results, indent=2) + '\n')
