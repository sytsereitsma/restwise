import unittest
import protocol
from parameterized import parameterized


class ProtocolTestCase(unittest.TestCase):
    def test_create_packet(self):
        packet = protocol.create_packet(0xABCD, b"EFGH")
        self.assertEqual(b"\x05\x05\x03\x03ABCDEFGH10D1\r\n", packet)

    # b'\x05\x05\x03\x03000AB43C\r\n'
    def test_stick_status(self):
        packet = protocol.Stick.Status().serialize()
        self.assertEqual(b"\x05\x05\x03\x03000AB43C\r\n", packet)

        # b'\x05\x05\x03\x030000000600C19939\r\n'
        # b'\x05\x05\x03\x0300110006000D6F0001A59EDC0101FD0D6F0001A5A37234FDFF0D33\r\n'
        # b'\x83'


class ProtocolParserTestCase(unittest.TestCase):
    def test_single_complete_packet(self):
        parser = protocol.Parser()
        assert (parser.parse(b"\x05\x05\x03\x03ABCDBEEF9F00\r\n"))

        packet = parser.packets[0]
        self.assertEqual(0xABCD, packet.command)
        self.assertEqual("BEEF", packet.data)

    def test_parsed_packets_are_removed_from_parse_buffer(self):
        parser = protocol.Parser()
        assert (parser.parse(b"\x05\x05\x03\x03ABCDBEEF9F00\r\n"))
        assert (not parser.parse(b""))

    def test_reading_packets_resets_packet_list(self):
        parser = protocol.Parser()
        assert (parser.parse(b"\x05\x05\x03\x03ABCDBEEF9F00\r\n"))

        assert parser.packets
        assert not parser.packets

    def test_fragmented_packet(self):
        parser = protocol.Parser()
        assert (not parser.parse(b"\x05\x05\x03\x03ABCDBEEF9F"))
        assert (parser.parse(b"00\r\n"))

        packet = parser.packets[0]
        self.assertEqual(0xABCD, packet.command)
        self.assertEqual("BEEF", packet.data)

    def test_data_before_packet(self):
        parser = protocol.Parser()
        assert (parser.parse(b"XXXX\x05\x05\x03\x03ABCDBEEF9F00\r\n"))

        packet = parser.packets[0]
        self.assertEqual(0xABCD, packet.command)
        self.assertEqual("BEEF", packet.data)

    def test_multiple_packets(self):
        parser = protocol.Parser()
        assert (parser.parse(b"\x05\x05\x03\x03ABCDBEEF9F00\r\n\x05\x05\x03\x03123456789015\r\n"))

        packets = parser.packets
        self.assertEqual(0xABCD, packets[0].command)
        self.assertEqual("BEEF", packets[0].data)

        self.assertEqual(0x1234, packets[1].command)
        self.assertEqual("5678", packets[1].data)

    def test_packet_crc_error(self):
        parser = protocol.Parser()
        self.assertRaises(protocol.CRCException, parser.parse, b"\x05\x05\x03\x03ABCDBEEFDEAD\r\n")

    def test_packet_length_error(self):
        parser = protocol.Parser()
        # 1 byte short
        self.assertRaises(protocol.PacketLengthException, parser.parse, b"\x05\x05\x03\x03ABCDEAD\r\n")

    def test_packet_parse_error_should_clear_packet_data_from_buffer(self):
        parser = protocol.Parser()
        self.assertRaises(protocol.CRCException, parser.parse,
                          b"\x05\x05\x03\x03ABCDBEEFDEAD\r\n\x05\x05\x03\x03123456789015\r\n")

        assert (parser.parse(b""))
        packet = parser.packets[0]
        self.assertEqual(0x1234, packet.command)
        self.assertEqual("5678", packet.data)

    @parameterized.expand([
        (b"0000ABCD00C1", protocol.AckPacket),
        (b"00110006000D6F0001A59EDC0100FD0D6F0001A5A37234FDFF", protocol.StickStatus)
    ])
    def test_promotes_packets_with_known_commands(self, data, cls):
        parser = protocol.Parser()
        assert (parser.parse(b"\x05\x05\x03\x03" + data + protocol.compute_crc(data) + b"\r\n"))
        self.assertIsInstance(parser.packets[0], cls)

    def test_ack_packet_parsing(self):
        ack = protocol.AckPacket(b"000A00AB")
        self.assertEqual(10, ack["sequence_number"])
        self.assertEqual(0xAB, ack["response_code"])

    def test_stick_status_packet_parsing(self):
        status = protocol.StickStatus(b"0006000D6F0001A59EDC0100FD0D6F0001A5A37234FDFF")
        self.assertEqual(6, status["sequence_number"])
        self.assertEqual(0x000D6F0001A59EDC, status["extended_address"])
        self.assertEqual(True, status["unknown_a"])
        self.assertEqual(False, status["link_up"])
        self.assertEqual(0xFD0D6F0001A5A372, status["network_id"])
        self.assertEqual(0x34FD, status["short_network_id"])

    def test_reset(self):
        parser = protocol.Parser()
        assert (not parser.parse(b"\x05\x05\x03\x03DEADBEEF"))
        self.assertEqual(b"\x05\x05\x03\x03DEADBEEF", parser.reset())
        assert (parser.parse(b"9F00\r\n\x05\x05\x03\x03ABCDBEEF9F00\r\n"))

        packet = parser.packets[0]
        self.assertEqual(0xABCD, packet.command)
        self.assertEqual("BEEF", packet.data)


if __name__ == '__main__':
    unittest.main()
