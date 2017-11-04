import unittest
import unittest.mock as mock
import protocol
import command_executor

TEST_ACK = b'\x05\x05\x03\x030000000600C19939\r\n'
TEST_RESPONSE = b'\x05\x05\x03\x0300110006000D6F0001A59EDC0101FD0D6F0001A5A37234FDFF0D33\r\n'

class CommandExecutorTestCase(unittest.TestCase):
    def setUp(self):
        self.serial = mock.MagicMock()

        self.executor = command_executor.CommandExecutor(self.serial)

    def test_sends_command(self):
        self.serial.read_until.side_effect = [
            TEST_ACK,
            TEST_RESPONSE,
        ]

        self.executor.execute(b"ABCD")
        self.serial.write.assert_called_with(b"ABCD")

    def test_reads_command_ack(self):
        self.serial.read_until.side_effect = [
            TEST_ACK,
            TEST_RESPONSE,
        ]

        self.executor.execute(b"")
        self.serial.read_until.called_with(b"\r\n")

    def test_reads_ack_and_response(self):
        self.serial.read_until.side_effect = [
            TEST_ACK,
            TEST_RESPONSE,
        ]

        packet = self.executor.execute(b"")
        self.assertEqual(6, packet["sequence_number"])
        self.assertIsInstance(packet, protocol.StickStatus)

if __name__ == '__main__':
    unittest.main()
