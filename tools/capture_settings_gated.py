# Historical fixed-session recorder; use capture_resilient.py for new work.
import os
from project_paths import CAPTURES
_session = CAPTURES / 'system' / 'display-settings-05'
_session.mkdir(parents=True, exist_ok=True)
os.chdir(_session)
import array
import ctypes as c
import json
import time
from pathlib import Path

lib = c.CDLL('/Applications/WaveForms.app/Contents/Frameworks/dwf.framework/Versions/A/dwf')

def call(name, *args):
    if not getattr(lib, name)(*args):
        msg = c.create_string_buffer(512)
        lib.FDwfGetLastErrorMsg(msg)
        raise RuntimeError(name + ': ' + msg.value.decode())

h = c.c_int()
call('FDwfDeviceOpen', -1, c.byref(h))
rate = c.c_double()
length = 180.0
count = lost_total = corrupt_total = 0
try:
    call('FDwfAnalogInChannelEnableSet', h, 0, 1)
    call('FDwfAnalogInChannelEnableSet', h, 1, 0)
    call('FDwfAnalogInChannelAttenuationSet', h, 0, c.c_double(1))
    call('FDwfAnalogInChannelRangeSet', h, 0, c.c_double(50))
    call('FDwfAnalogInChannelOffsetSet', h, 0, c.c_double(0))
    call('FDwfAnalogInFrequencySet', h, c.c_double(500_000))
    call('FDwfAnalogInFrequencyGet', h, c.byref(rate))
    call('FDwfAnalogInAcquisitionModeSet', h, 3)
    call('FDwfAnalogInRecordLengthSet', h, c.c_double(length))
    call('FDwfAnalogInTriggerSourceSet', h, c.c_ubyte(0))
    call('FDwfAnalogInConfigure', h, 1, 0)
    time.sleep(.5)
    call('FDwfAnalogInConfigure', h, 0, 1)
    print('RECORDING: remain on main screen until the next cue.', flush=True)
    started = time.time()
    with open('display-settings-05.f64', 'wb') as output:
        while True:
            state = c.c_ubyte()
            call('FDwfAnalogInStatus', h, 1, c.byref(state))
            available, lost, corrupt = c.c_int(), c.c_int(), c.c_int()
            call('FDwfAnalogInStatusRecord', h, c.byref(available), c.byref(lost), c.byref(corrupt))
            lost_total += lost.value
            corrupt_total += corrupt.value
            if lost.value or corrupt.value:
                raise RuntimeError(f'Recording interrupted: lost={lost_total}, corrupt={corrupt_total}')
            if available.value:
                data = (c.c_double * available.value)()
                call('FDwfAnalogInStatusData', h, 0, data, available.value)
                output.write(bytes(data))
                count += available.value
            if state.value == 2:
                break
            stop_file = Path('display-settings-05-stop.json')
            if stop_file.exists():
                stop_at = json.loads(stop_file.read_text())['stop_at_unix']
                if time.time() >= stop_at:
                    call('FDwfAnalogInConfigure', h, 0, 0)
                    break
            if time.time() - started > length + 10:
                raise TimeoutError('Recording timed out')
            time.sleep(.001)
    metadata = {'sample_rate': rate.value, 'samples': count, 'duration_s': count/rate.value,
                'started_unix': started, 'lost': lost_total, 'corrupt': corrupt_total,
                'pins': {'1+': 3, '1-': 6}, 'ground_connected': False,
                'action': 'Event-controlled Settings open/close; stop 30 seconds after close acknowledgment, with 180-second maximum', 'format': 'native float64'}
    Path('display-settings-05.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print(json.dumps(metadata), flush=True)
finally:
    lib.FDwfDeviceClose(h)
