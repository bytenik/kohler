import array
import collections
import json
from pathlib import Path

import sys
base = sys.argv[1] if len(sys.argv) > 1 else 'display-settings-01'
from project_paths import capture_base
base = str(capture_base(base))
meta = json.loads(Path(base + '.json').read_text())
samples = array.array('d')
with open(base + '.f64','rb') as source:
    samples.fromfile(source, meta['samples'])
rate = meta['sample_rate']
# Require two consecutive samples on the new side of zero to reject ringing.
edges=[]
state=samples[0]>0
pending=0
for i,value in enumerate(samples):
    if (value>0)!=state:
        pending+=1
        if pending==2:
            state=not state
            edges.append((i-1,state))
            pending=0
    else:
        pending=0
frames=[]
end=-1
period=rate/115200
for index,state in edges:
    if state or index<end or index+9.5*period>=len(samples):
        continue
    bits=[int(samples[round(index+(j+.5)*period)]>0) for j in range(10)]
    frames.append({'time_s':index/rate,'byte':sum(bits[j+1]<<j for j in range(8)),
                   'valid':bits[0]==0 and bits[9]==1})
    end=index+9.7*period
packets=[]
for frame in frames:
    if not packets or frame['time_s']-packets[-1][-1]['time_s']>120e-6:
        packets.append([])
    packets[-1].append(frame)
result=[]
for packet in packets:
    values=[f['byte'] for f in packet]
    result.append({'time_s':packet[0]['time_s'],'hex':bytes(values).hex(' ').upper(),
                   'framing_valid':all(f['valid'] for f in packet),
                   'checksum_valid':values[0]==0x88 and values[-1]==0x55 and sum(values[:-1])%256==0})
Path(base + '-decoded.json').write_text(json.dumps(result,indent=2)+'\n')
counts=collections.Counter(p['hex'] for p in result)
print('frames',len(frames),'invalid',sum(not f['valid'] for f in frames),'groups',len(result),
      'valid packets',sum(p['checksum_valid'] for p in result),'unique',len(counts))
for packet,count in counts.most_common(30):
    hits=[p for p in result if p['hex']==packet]
    print(count, 'first',round(hits[0]['time_s'],4),'last',round(hits[-1]['time_s'],4),packet)
print('Counts per second:',sorted(collections.Counter(int(p['time_s']) for p in result).items()))
