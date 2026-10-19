import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import unittest
from display_protocol import parse_packets, uart_frames


def frames(values):
    return [{'time_s': i*.00009, 'byte': v, 'valid': True} for i,v in enumerate(values)]


class PacketTests(unittest.TestCase):
    def test_uart_polarity_preserves_decoded_bytes(self):
        expected = bytes.fromhex('88 03 00 30 45 55')
        bits = [1] * 20
        for byte in expected:
            bits.extend([0] + [(byte >> i) & 1 for i in range(8)] + [1])
        bits.extend([1] * 20)
        positive = [2.0 if bit else -2.0 for bit in bits for _ in range(16)]
        negative = [-value for value in positive]
        for samples, invert in ((positive, False), (negative, True)):
            decoded = list(uart_frames(samples, 115200 * 16, invert=invert))
            self.assertEqual(bytes(f['byte'] for f in decoded), expected)
            self.assertTrue(all(f['valid'] for f in decoded))

    def test_captured_escaped_checksums(self):
        examples = [
            ('88 00 03 31 02 02 25 19 06 09 65 11 0F C0 04 AA AA 55',0xAA),
            ('88 00 03 31 01 02 31 17 02 09 66 AA 88 55',0x88),
        ]
        for wire, checksum in examples:
            packets,issues = parse_packets(frames(bytes.fromhex(wire)))
            self.assertEqual(issues,[])
            self.assertTrue(packets[0]['checksum_valid'])
            self.assertEqual(bytes.fromhex(packets[0]['hex'])[-2],checksum)

    def test_startup_identity_with_escaped_end_delimiter(self):
        wire=bytes.fromhex('88 00 03 32 00 1F 00 64 01 00 75 6E 2D 6E 61 6D 65 64 20 AA 55 49 00 00 00 00 00 00 00 00 00 00 00 00 00 00 EC 55')
        packets,issues=parse_packets(frames(wire))
        self.assertEqual(issues,[])
        self.assertEqual(len(packets),1)
        self.assertTrue(packets[0]['checksum_valid'])
        self.assertIn(b'un-named UI',bytes.fromhex(packets[0]['hex']))

    def test_delimiters_without_gap(self):
        stream = frames(bytes.fromhex('88 03 00 30 45 55 88 00 03 31 00 44 55'))
        for i,f in enumerate(stream): f['time_s']=i*.000087
        packets,issues=parse_packets(stream)
        self.assertEqual(len(packets),2)
        self.assertTrue(all(p['checksum_valid'] for p in packets))
        self.assertEqual(issues,[])

    def test_corruption_and_boundary_recovery(self):
        packets,issues=parse_packets(frames(bytes.fromhex('12 88 03 88 03 00 30 44 55 88 AA')))
        self.assertFalse(packets[0]['checksum_valid'])
        self.assertEqual([i['reason'] for i in issues],['outside_packet','restarted_packet','truncated_packet'])
        self.assertTrue(issues[-1]['pending_escape'])

    def test_uart_error_is_not_silently_accepted(self):
        stream=frames(bytes.fromhex('88 03 00 30 45 55'))
        stream[2]['valid']=False
        packets,_=parse_packets(stream)
        self.assertTrue(packets[0]['checksum_valid'])
        self.assertFalse(packets[0]['framing_valid'])


if __name__=='__main__': unittest.main()
