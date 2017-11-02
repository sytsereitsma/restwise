import unittest
import protocol
import struct


class ProtocolStickTestCase(unittest.TestCase):
    #b'\x05\x05\x03\x03000AB43C\r\n'
    def test_stick_status(self):
        packet = protocol.Stick.Status().serialize()
        self.assertEqual(b"\x05\x05\x03\x03000AB43C\r\n", packet)

        #b'\x05\x05\x03\x030000000600C19939\r\n'
        #b'\x05\x05\x03\x0300110006000D6F0001A59EDC0101FD0D6F0001A5A37234FDFF0D33\r\n'
        #b'\x83'


if __name__ == '__main__':
    unittest.main()
