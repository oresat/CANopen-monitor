"""CanOpen Object Parser Library"""
from canmon.eds_utilities import *


class SDODownloadInitiate:
    def __init__(self, raw_sdo: bytes):
        self.isClient = None
        self.isExpedited = None
        self.sizeIndicator = None
        self.n = None
        self.data = None
        self.index = None

        self.decode_first_section(raw_sdo[0])
        self.index = raw_sdo[1:4]
        self.decode_data(raw_sdo[4:8])

    def decode_first_section(self, byte_value):
        command_specifier = byte_value & 0xE0
        if command_specifier == 0x20:
            self.isClient = True
        elif command_specifier == 0x60:
            self.isClient = False
        else:
            raise ValueError(f"Invalid Command Specifier Bits (7_5): '{command_specifier}'")

        if self.isClient:
            if byte_value & 0x10 > 0:
                raise ValueError(f"Invalid x value (4): {byte_value & 0x10}")

            if byte_value & 0x02 == 0:
                self.isExpedited = False
            else:
                self.isExpedited = True

            # if size indicator is set
            if byte_value & 0x01 == 0x01:
                self.sizeIndicator = True
            else:
                self.sizeIndicator = False

            if self.isExpedited and self.sizeIndicator:
                self.n = byte_value & 0x0C >> 2
            elif byte_value & 0x0C > 0:
                raise ValueError(f"Invalid n value (3_2): '{byte_value & 0x0C}")

        else:
            if byte_value & 0x1F > 0:
                raise ValueError(f"Invalid x value (4_0): '{byte_value & 0x1F}'")

    def decode_data(self, byte_value: bytes):
        if not self.isExpedited:
            if self.sizeIndicator:
                self.data = byte_value
            elif int.from_bytes(byte_value, "big") > 0:
                raise ValueError(f"Invalid data value: '{byte_value}")
        # Expedited Transfer
        else:
            if self.sizeIndicator:
                self.data = byte_value[0:4 - self.n]
                if int.from_bytes(byte_value[4 - self.n:4], "big") > 0:
                    raise ValueError(f"Data value larger than size: '{byte_value}'")
            else:
                self.data = byte_value


class SDODownloadSegment:
    def __init__(self, raw_sdo: bytes):
        self.moreSegments = None
        self.n = None
        self.data = None
        self.toggleBit = None
        self.isClient = None

        self.decode_first_section(raw_sdo[0])
        self.decode_data(raw_sdo[4:8])

    def decode_first_section(self, byte_value):
        command_specifier = byte_value & 0xE0
        if command_specifier == 0x00:
            self.isClient = True
        elif command_specifier == 0x20:
            self.isClient = False
        else:
            raise ValueError(f"Invalid Command Specifier Bits (7_5): '{command_specifier}'")

        self.toggleBit = byte_value & 0x10

        if self.isClient:
            self.n = (byte_value & 0x0E) >> 1

            if byte_value & 0x01 > 0:
                self.moreSegments = False
            else:
                self.moreSegments = True

        else:
            if byte_value & 0x1F > 0:
                raise ValueError(f"Invalid x value (4_0): '{byte_value & 0x1F}'")

    def decode_data(self, byte_value: bytes):
        if not self.isClient:
            if int.from_bytes(byte_value, "big") > 0:
                raise ValueError(f"Invalid data value: '{byte_value}")
        else:
            self.data = int.from_bytes(byte_value[0:6 - self.n], "big").to_bytes(7, "big")
            if self.n > 0:
                if int.from_bytes(byte_value[6 - self.n:6], "big") > 0:
                    raise ValueError(f"Data value larger than size: '{byte_value}'")


class ObjectParser:

    def __init__(self, nodes):
        self.nodes = nodes
        self.inProgress = []
        self.downloadInitiate = None
        self.inProgressName = None
        self.clientToggle = True
        self.serverToggle = True
        self.data = []
        self.initiateComplete = False

    def parse_sdo_download(self, node_id, sdo: bytes):
        if not self.initiateComplete:
            self.downloadInitiate = SDODownloadInitiate(sdo)
            if self.downloadInitiate.isClient:
                self.inProgressName = self.get_name(node_id, self.downloadInitiate.index)
                if self.downloadInitiate.isExpedited:
                    return self.inProgressName + "DATA GOES HERE"
                else:
                    return self.inProgressName + "Download Initiated"
            else:
                self.initiateComplete = True
                if self.downloadInitiate is None:
                    raise ValueError(f"Server Message Received Before Client Message")
                return self.inProgressName + "Download Initiated"
        else:
            download_segment = SDODownloadSegment(sdo)
            if download_segment.isClient:
                if download_segment.toggleBit == self.clientToggle:
                    raise ValueError(f"Invalid Valid Client Toggle {not self.clientToggle} expected")
                else:
                    self.clientToggle = download_segment.toggleBit
                    self.data.append(download_segment.data)
                    if not download_segment.moreSegments:
                        return self.inProgressName + str(int.from_bytes(self.data[0], "big"))
                    else:
                        return self.inProgressName + "Segment Received"
            # Server Message
            else:
                if download_segment.toggleBit == self.serverToggle:
                    raise ValueError(f"Invalid Valid Server Toggle {not self.serverToggle} expected")
                else:
                    self.serverToggle = download_segment.toggleBit
                    return self.inProgressName + "Segment Confirmed"

    def get_name(self, node_id, index: bytes):
        """
        :param index:
        :param node_id
        :return:
        """
        node = self.nodes[node_id]
        if not isinstance(node, EDSFile):
            raise ValueError(f"Type {type(node)} is not of type EDSFile")
        index_data = node.index[int.from_bytes(index, "big")]
        result = ""
        if index_data.parent_name is not None:
            result += index_data.parent_name + " "
        if index_data.parameter_name is not None:
            result += index_data.parameter_name + " "
        return result


if __name__ == "__main__":
    parser = ObjectParser(load_eds_files(os.getcwd()))

    # Initiate Client Download Message
    clientInitiateMessage = b'\x21\x30\x00\x00\x00\x00\x00\x0C'
    print(parser.parse_sdo_download(0x12, clientInitiateMessage))
    serverInitiateResponse = b'\x60\x30\x00\x00\x00\x00\x00\x00'
    print(parser.parse_sdo_download(0x12, serverInitiateResponse))
    clientDownloadSegment = b'\x11\x00\x00\x00\x00\x00\x00\x0A'
    print(parser.parse_sdo_download(0x12, clientDownloadSegment))
    serverDownloadResponse = b'\x20\x00\x00\x00\x00\x00\x00\x00'
    print(parser.parse_sdo_download(0x12, serverDownloadResponse))


    # SDO Parser test
    initiateSDO = SDODownloadInitiate(clientInitiateMessage)
    assert initiateSDO.isExpedited is False
    assert initiateSDO.isClient is True
    assert initiateSDO.sizeIndicator is True
    assert initiateSDO.index == b'\x30\x00\x00'
    assert initiateSDO.data == b'\x00\x00\x00\x0C'

    # TODO: May get multiple messages from multiple nodes, store in progress by Node-ID maybe? Until translation
