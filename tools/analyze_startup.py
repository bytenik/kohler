"""Extract display startup evidence without assigning unverified field semantics."""
import collections
import json
from pathlib import Path

from project_paths import ROOT, REPORTS, capture_base

base=str(capture_base('display-startup-07-part-000'))
packets=json.loads(Path(base+'-packets.json').read_text())['packets']
identity=next(p for p in packets if p['message_type']==0x32)
initialization=next(p for p in packets if p['message_type']==0x34 and p.get('subtype')==0)
a,b=bytes.fromhex(identity['hex']),bytes.fromhex(initialization['hex'])
origin=next(p['time_s'] for p in packets if p['message_type']==0x38)
post=[p for p in packets if p['time_s']>=origin]
first_content=next(p for p in post if p['message_type']==0x31 and p['length']>7)
comparisons=[]
for first,second in zip(post,post[1:]):
    x,y=bytes.fromhex(first['hex']),bytes.fromhex(second['hex'])
    if x[3]==0x31 and y[3]==0x34 and len(x)>8:
        comparisons.append({'time_from_handshake_s':first['time_s']-origin,
                            'class_byte':x[4], 'format_byte':x[5],
                            'candidate_key_hex':x[6:8].hex(' ').upper(),
                            'request_hex':first['hex'],'following_hex':second['hex']})
result={'capture':Path(base).relative_to(ROOT).as_posix(),'handshake_origin_s':origin,
        'handshake':[{'time_from_handshake_s':p['time_s']-origin,'hex':p['hex']} for p in post[:6]],
        'aligned_slices':{'identity':'packet[4:-1]','initialization':'packet[5:-2]',
                          'length':len(a[4:-1]),
                          'differences':[{'slice_offset':i,'identity_offset':i+4,'initialization_offset':i+5,
                                          'identity_byte':x,'initialization_byte':y}
                                         for i,(x,y) in enumerate(zip(a[4:-1],b[5:-2])) if x!=y]},
        'first_nonempty_poll_reply_from_handshake_s':first_content['time_s']-origin,
        'exchanges':comparisons}
(REPORTS / 'display-startup-analysis.json').write_text(json.dumps(result,indent=2)+'\n')
print('aligned difference',result['aligned_slices'])
print('first content reply after',result['first_nonempty_poll_reply_from_handshake_s'])
for cls in (1,2):
    e=[p for p in comparisons if p['class_byte']==cls]
    print('class',cls,'exchanges',len(e),'key counts',dict(collections.Counter(p['candidate_key_hex'] for p in e)))
