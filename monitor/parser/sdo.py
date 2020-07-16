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


class SDOParser:
    """Sub-Parser for SDO messages

    TODO: Insert more details.
    """

    def __init__(self, nodes):
        self.nodes = nodes
        self.inProgress = []
        self.downloadInitiate = None
        self.inProgressName = None
        self.clientToggle = True
        self.serverToggle = True
        self.data = []
        self.initiateComplete = False

    def parse(self, node_id, sdo: bytes):
        if not self.initiateComplete:
            self.downloadInitiate = SDODownloadInitiate(sdo)
            if self.downloadInitiate.isClient:
                self.inProgressName = self.__get_name(self.downloadInitiate.index)
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

    def __get_name(self, index: bytes):
        """
        :param index:
        :param node_id
        :return:
        """
        key = int(index[:2].hex())
        subindex_key = int(index[2:3].hex())
        index_data = self.nodes[key]
        result = index_data.parameter_name

        if index_data.sub_indices is not None:
            result += index_data.sub_indices[subindex_key].parameter_name + " "

        return result
