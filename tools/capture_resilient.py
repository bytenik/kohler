import ctypes as c
import json
import time
import argparse
from pathlib import Path

lib = c.CDLL('/Applications/WaveForms.app/Contents/Frameworks/dwf.framework/Versions/A/dwf')

def call(name, *args):
    if not getattr(lib, name)(*args):
        msg = c.create_string_buffer(512)
        lib.FDwfGetLastErrorMsg(msg)
        raise RuntimeError(name + ': ' + msg.value.decode())

parser = argparse.ArgumentParser()
parser.add_argument('base', nargs='?', default='display-recovery-test')
parser.add_argument('--bus', choices=('display', 'valve'), default='display')
parser.add_argument('--rate', type=float, default=500_000)
parser.add_argument('--duration', type=float, default=300)
args = parser.parse_args()
from project_paths import new_capture_base
base = str(new_capture_base(args.base, args.bus))
pins = {'1+': 3, '1-': 6} if args.bus == 'display' else {'1+': 4, '1-': 5}
if Path(base + '-manifest.json').exists():
    raise FileExistsError('Choose a new capture name; existing evidence will not be overwritten')

h = c.c_int()
call('FDwfDeviceOpen', -1, c.byref(h))
rate = c.c_double()
length = args.duration
count = lost_total = corrupt_total = 0
try:
    call('FDwfAnalogInChannelEnableSet', h, 0, 1)
    call('FDwfAnalogInChannelEnableSet', h, 1, 0)
    call('FDwfAnalogInChannelAttenuationSet', h, 0, c.c_double(1))
    call('FDwfAnalogInChannelRangeSet', h, 0, c.c_double(50))
    call('FDwfAnalogInChannelOffsetSet', h, 0, c.c_double(0))
    call('FDwfAnalogInFrequencySet', h, c.c_double(args.rate))
    call('FDwfAnalogInFrequencyGet', h, c.byref(rate))
    call('FDwfAnalogInAcquisitionModeSet', h, 3)
    call('FDwfAnalogInRecordLengthSet', h, c.c_double(length))
    call('FDwfAnalogInTriggerSourceSet', h, c.c_ubyte(0))
    call('FDwfAnalogInConfigure', h, 1, 0)
    time.sleep(.5)
    call('FDwfAnalogInConfigure', h, 0, 1)
    started = time.time()
    Path(base + '-start.json').write_text(json.dumps({'started_unix': started, 'sample_rate': rate.value}) + '\n')
    print('RECORDING: waiting for the instructed physical action.', flush=True)
    segments = []
    errors = []
    segment_count = 0
    segment_started = time.time()
    part = 0
    output = open(f'{base}-part-{part:03d}.f64', 'wb')
    def finish_segment():
        output.close()
        item = {'samples': segment_count, 'sample_rate': rate.value,
                'bus': args.bus, 'pins': pins, 'ground_connected': False,
                'duration_s': segment_count/rate.value, 'started_unix_approx': segment_started,
                'capture_complete': True, 'time_reference': 'host time near first read; not hardware synchronized'}
        Path(f'{base}-part-{part:03d}.json').write_text(json.dumps(item, indent=2)+'\n')
        segments.append({'base': f'{base}-part-{part:03d}', **item})
    try:
        while True:
            state = c.c_ubyte()
            call('FDwfAnalogInStatus', h, 1, c.byref(state))
            available, lost, corrupt = c.c_int(), c.c_int(), c.c_int()
            call('FDwfAnalogInStatusRecord', h, c.byref(available), c.byref(lost), c.byref(corrupt))
            if lost.value or corrupt.value:
                errors.append({'host_unix': time.time(), 'lost': lost.value,
                               'corrupt': corrupt.value, 'discarded_available': available.value})
                finish_segment()
                part += 1
                segment_count = 0
                segment_started = time.time()
                output = open(f'{base}-part-{part:03d}.f64', 'wb')
                print('Transfer interruption marked; recording continues in a new segment.', flush=True)
            elif available.value:
                data = (c.c_double * available.value)()
                call('FDwfAnalogInStatusData', h, 0, data, available.value)
                output.write(bytes(data))
                segment_count += available.value
            if state.value == 2:
                break
            stop_file = Path(base + '-stop.json')
            if stop_file.exists() and time.time() >= json.loads(stop_file.read_text())['stop_at_unix']:
                call('FDwfAnalogInConfigure', h, 0, 0)
                break
            if time.time() - started > length + 10:
                raise TimeoutError('Recording timed out')
            time.sleep(.001)
    finally:
        finish_segment()
        manifest = {'started_unix': started, 'sample_rate': rate.value,
                    'segments': segments, 'interruptions': errors,
                    'bus': args.bus, 'pins': pins, 'ground_connected': False}
        Path(base + '-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps({'segments':len(segments),'interruptions':len(errors)}), flush=True)
finally:
    lib.FDwfDeviceClose(h)
