import struct
import crcmod

HEADER = b"\x05\x05\x03\x03"

crc_function = crcmod.mkCrcFun(0x11021, rev=False, initCrc=0x0000, xorOut=0x0000)

def compute_crc(data):
    crc = crc_function(data)
    return "{:02X}".format(crc).encode()


class Stick:
    class Status:
        COMMAND = b"000A"

        def serialize(self):
            packet = HEADER + self.COMMAND + compute_crc(self.COMMAND) + b"\r\n"
            return packet
