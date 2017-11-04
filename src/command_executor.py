import protocol


class CommandExecutor:
    def __init__(self, serial_port):
        self.__serial_port = serial_port
        self.__parser = protocol.Parser()
        self.__history = dict()

    def __read_ack(self):
        """
        sequence_number = None
        while sequence_number is None:
            packet_received = self.__parser.parse(self.__serial_port.read_until(b"\r\n"))
            if packet_received:
                packets = self.__parser.packets
                for p in packets:
                    if p.command is protocol.AckPacket.COMMAND:
                        sequence_number = p["sequence_number"]
                        break
        return sequence_number
        """
        self.__parser.parse(self.__serial_port.read_until(b"\r\n"))
        return self.__parser.packets[0]

    def execute(self, command_packet):
        self.__serial_port.write(command_packet)
        return self.__read_ack()



