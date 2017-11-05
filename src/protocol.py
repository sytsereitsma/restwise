import struct
import crcmod
import io


_HEADER = b"\x05\x05\x03\x03"
_TRAILER = b"\r\n"
_COMMAND_LENGTH = 4
_CRC_LENGTH = 4
_MIN_PACKET_SIZE = len(_HEADER) + _COMMAND_LENGTH + _CRC_LENGTH + len(_TRAILER)

_crc_function = crcmod.mkCrcFun(0x11021, rev=False, initCrc=0x0000, xorOut=0x0000)


class ProtocolException(Exception):
    pass


class CRCException(ProtocolException):
    pass


class PacketLengthException(ProtocolException):
    pass


def compute_crc(data):
    crc = _crc_function(data)
    return "{:04X}".format(crc).encode()


def create_packet(command, payload):
    packet_data = "{:04X}".format(command).encode() + payload
    packet = _HEADER + packet_data + compute_crc(packet_data) + _TRAILER
    return packet


class Packet:
    def __init__(self, command, data):
        self.__command = int(command.decode(), 16)
        self.__raw_data = data.decode()
        self.__data = {}
        self.add_hex_int16("sequence_number", 0)

    def __getitem__(self, item):
        return self.__data[item]

    def __repr__(self):
        packet_type = type(self).__name__
        return "{}(0x{:04X})#{}, data = {}".format(packet_type, self.__command, self.__data["sequence_number"], self.__raw_data)

    def __str__(self):
        packet_type = type(self).__name__
        txt = "{}(0x{:04X})\n".format(packet_type, self.__command)
        max_name_len = max(map(lambda k: len(k), self.__data))
        for k, v in self.__data.items():
            fmt = "  {" + ":{}s".format(max_name_len) + "} = "

            if type(v) is int:
                fmt += "0x{:X}\n"
            else:
                fmt += "{}\n"

            txt += fmt.format(k, v)

        return txt

    @property
    def command(self):
        return self.__command

    @property
    def data(self):
        return self.__raw_data

    def add_bool(self, name, start):
        value = self.__raw_data[start: start + 2] != "00"
        self.__data[name] = value

    def add_hex_int8(self, name, start):
        self.__add_hex_int(name, start, 2)

    def add_hex_int16(self, name, start):
        self.__add_hex_int(name, start, 4)

    def add_hex_int64(self, name, start):
        self.__add_hex_int(name, start, 16)

    def __add_hex_int(self, name, start, length):
        value = int(self.__raw_data[start: start + length], 16)
        self.__data[name] = value


class AckPacket(Packet):
    COMMAND = b"0000"

    def __init__(self, data):
        super(AckPacket, self).__init__(self.COMMAND, data)
        self.add_hex_int16("response_code", 4)


class StickStatus(Packet):
    COMMAND = b"0011"

    def __init__(self, data):
        super(StickStatus, self).__init__(self.COMMAND, data)
        self.add_hex_int64("extended_address", 4)
        self.add_hex_int8("unknown_a", 20)
        self.add_bool("link_up", 22)
        self.add_hex_int64("network_id", 24)
        self.add_hex_int16("short_network_id", 40)


_KNOWN_PACKETS = {
    b"0000": AckPacket,
    b"0011": StickStatus
}


class Parser:
    def __init__(self):
        self.__buffer = bytes()
        self.__packets = []

    def reset(self):
        data = self.__buffer
        self.__buffer = bytes()
        return data

    @property
    def packets(self):
        packets = self.__packets
        self.__packets = []
        return packets

    def parse(self, data):
        self.__buffer += data

        count = 0
        while self.__next_packet():
            count += 1

        return count != 0

    def __next_packet(self):
        header_pos = self.__buffer.find(_HEADER)
        if header_pos != -1:
            trailer_pos = self.__buffer.find(_TRAILER, header_pos + len(_HEADER))
            if trailer_pos != -1:
                try:
                    if self.__parse_packet(self.__buffer[header_pos :trailer_pos+ len(_TRAILER)]):
                        self.__buffer = self.__buffer[trailer_pos + len(_TRAILER):]
                        return True
                except ProtocolException:
                    self.__buffer = self.__buffer[trailer_pos + len(_TRAILER):]
                    raise

        return False

    def __parse_packet(self, packet):
        if len(packet) < _MIN_PACKET_SIZE:
            raise PacketLengthException("Packet size should be at least {} bytes, this packet is {} bytes (packet: {})".format(_MIN_PACKET_SIZE, len(packet), packet))

        crc_index = -(_CRC_LENGTH + len(_TRAILER))
        packet_data = packet[4:crc_index]

        expected_crc = compute_crc(packet_data)
        actual_crc = packet[crc_index: crc_index + _CRC_LENGTH]
        if expected_crc != actual_crc:
            raise CRCException("Expected CRC {}, got {} (packet: {})".format(expected_crc, actual_crc, packet))

        command = packet_data[:4]
        data = packet_data[4:]
        if command in _KNOWN_PACKETS:
            self.__packets.append(_KNOWN_PACKETS [command](data))
        else:
            self.__packets.append(Packet(command, data))

        return True



class Stick:
    class Status:
        COMMAND = 0x000A

        def serialize(self):
            return create_packet(self.COMMAND, b"")
