# Historical fixed-session recorder; use capture_resilient.py for new work.
import os
from project_paths import CAPTURES
_session = CAPTURES / 'system' / 'display-idle'
_session.mkdir(parents=True, exist_ok=True)
os.chdir(_session)
import ctypes as c
import csv
import time
from pathlib import Path

LIB = '/Applications/WaveForms.app/Contents/Frameworks/dwf.framework/Versions/A/dwf'
dwf = c.CDLL(LIB)

def call(name, *args):
    if not getattr(dwf, name)(*args):
        message = c.create_string_buffer(512)
        dwf.FDwfGetLastErrorMsg(message)
        raise RuntimeError(name + ': ' + message.value.decode())

handle = c.c_int()
call('FDwfDeviceOpen', -1, c.byref(handle))
try:
    call('FDwfAnalogInChannelEnableSet', handle, 0, 1)
    call('FDwfAnalogInChannelEnableSet', handle, 1, 0)
    call('FDwfAnalogInChannelAttenuationSet', handle, 0, c.c_double(1))
    call('FDwfAnalogInChannelRangeSet', handle, 0, c.c_double(50))
    call('FDwfAnalogInChannelOffsetSet', handle, 0, c.c_double(0))
    call('FDwfAnalogInFrequencySet', handle, c.c_double(2_000_000))
    call('FDwfAnalogInBufferSizeSet', handle, 32768)
    call('FDwfAnalogInAcquisitionModeSet', handle, 0)
    call('FDwfAnalogInTriggerSourceSet', handle, c.c_ubyte(0))
    rate = c.c_double()
    count = c.c_int()
    call('FDwfAnalogInFrequencyGet', handle, c.byref(rate))
    call('FDwfAnalogInBufferSizeGet', handle, c.byref(count))
    # Allow the analog front end to settle before acquisition.
    call('FDwfAnalogInConfigure', handle, 1, 0)
    time.sleep(0.5)
    for capture in range(1, 4):
        call('FDwfAnalogInConfigure', handle, 0, 1)
        deadline = time.monotonic() + 5
        state = c.c_ubyte()
        while True:
            call('FDwfAnalogInStatus', handle, 1, c.byref(state))
            if state.value == 2:
                break
            if time.monotonic() > deadline:
                raise TimeoutError('Acquisition did not finish')
            time.sleep(0.005)
        samples = (c.c_double * count.value)()
        call('FDwfAnalogInStatusData', handle, 0, samples, count.value)
        path = Path(f'display-idle-{capture:02d}.csv')
        with path.open('w') as output:
            output.write(f'#Sample rate: {rate.value}\n#Pins: 1+ on RJ45 3; 1- on RJ45 6; GND disconnected\n')
            writer = csv.writer(output)
            writer.writerow(['Time (s)', 'Channel 1 (V)'])
            writer.writerows((i / rate.value, value) for i, value in enumerate(samples))
        print(path, count.value, rate.value, min(samples), max(samples))
        time.sleep(0.15)
finally:
    dwf.FDwfDeviceClose(handle)
