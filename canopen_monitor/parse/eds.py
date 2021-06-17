from __future__ import annotations

import copy
import re
import string
from re import finditer
from typing import Union, Callable
from dateutil.parser import parse as dtparse
import os
from configparser import ConfigParser, SectionProxy

from .utilities import ObjectType, DataType


def camel_to_snake(old_str: str) -> str:
    """
    Converts camel cased string to snake case, counting groups of repeated
    capital letters (such as "PDO") as one unit That is, string like
    "PDO_group" become "pdo_group" instead of "p_d_o_group"

    :param old_str: The string to convert to camel_case
    :type old_str: str

    :return: the camel-cased string
    :rtype: str
    """
    # Find all groups that contains one or more capital letters followed by
    # one or more lowercase letters The new, camel_cased string will be built
    # up along the way
    new_str = ""
    for match in finditer('[A-Z0-9]+[a-z]*', old_str):
        span = match.span()
        substr = old_str[span[0]:span[1]]
        found_submatch = False

        # Add a "_" to the newstring to separate the current match group from
        # the previous It looks like we shouldn't need to worry about getting
        # "_strings_like_this", because they don't seem to happen
        if (span[0] != 0):
            new_str += '_'

        # Find all sub-groups of *more than one* capital letters within the
        # match group, and separate them with "_" characters, Append the
        # subgroups to the new_str as they are found If no subgroups are
        # found, just append the match group to the new_str
        for sub_match in finditer('[A-Z]+', substr):
            sub_span = sub_match.span()
            sub_substr = old_str[sub_span[0]:sub_span[1]]
            sub_length = sub_span[1] - sub_span[0]

            if (sub_length > 1):
                found_submatch = True

                first = sub_substr[:-1]
                second = substr.replace(first, '')

                new_str += '{}_{}'.format(first, second).lower()

        if (not found_submatch):
            new_str += substr.lower()

    return new_str


class Metadata:
    def __init__(self, data):
        # Process all sub-data
        for e in data:
            # Skip comment lines
            if (e[0] == ';'):
                continue

            # Separate field name from field value
            key, value = e.split('=')

            # Create the proper field name
            key = camel_to_snake(key)

            # Turn date-time-like objects into datetimes
            if ('date' in key):
                value = dtparse(value).date()
            elif ('time' in key):
                value = dtparse(value).time()

            # Set the attribute
            self.__setattr__(key, value)


class LegacyIndex:
    """
    Index Class is used to contain data from a single section of an .eds file
    Note: Not all possible properties are stored
    """

    def __init__(self, data, index: Union[str, int], is_sub=False):
        # Determine if this is a parent index or a child index
        if not is_sub:
            self.sub_indices = {}
            self.index = index[2:]
        else:
            self.sub_indices = None
            self.index = str(index)

        self.is_sub = is_sub

        # Process all sub-data
        for e in data:
            # Skip commented lines
            if (e[0] == ';'):
                continue

            # Separate field name from field value
            key, value = e.split('=')

            value = convert_value(value)

            self.__setattr__(camel_to_snake(key), value)

    """
    Add a subindex to an index object
    :param index: The subindex being added 
    :type Index
    :raise ValueError: A subindex has already been added a this subindex
    """

    def add(self, index: LegacyIndex) -> None:
        if self.sub_indices.setdefault(int(index.index), index) != index:
            raise ValueError

    """
    Add a subindex to an index object
    :param index: The subindex being added 
    :type Index
    :raise ValueError: A subindex has already been added a this subindex
    """

    def __getitem__(self, key: int):
        if key not in self.sub_indices:
            raise KeyError(f"{self.index}sub{key}")

        return self.sub_indices[key]

    def __len__(self) -> int:
        if (self.sub_indices is None):
            return 1
        else:
            return len(self.sub_indices)
            # return 1 + sum(map(lambda x: len(x), self.sub_indices))


def convert_value(value: str) -> Union[int, str]:
    # Turn number-like objects into numbers
    if (value != ''):
        if (all(c in string.hexdigits for c in value)):
            return int(value, 16)
        elif (all(c in string.digits for c in value)):
            return int(value, 10)
        else:
            return value


class FileInfo:
    """This class encapsulates the Object Directory file's File Information
    identified in section [FileInfo] and ensures compliance with
    CANOpen Specification CiA 306 version 1.3.0"""

    def __init__(self, data: SectionProxy):
        """Create File info using configparser section
        :param data: File info section of data
        :type data: SectionProxy
        :raises KeyError: Indicates that a required entry is missing from the
        section. Check CiA 306 specification.
        :raises ValueError: Indicates that a type conversion failed"""

        self.file_name = str(data['FileName'])
        self.file_version = int(data['FileVersion'])
        self.file_revision = int(data['FileRevision'])
        self.eds_version = str(data['EDSVersion'])
        self.description = str(data['Description'])
        # creation time format is hh:mm(AM|PM)
        self.creation_time = dtparse(data['CreationTime']).time()
        # creation date format is mm-dd-yyyy
        self.creation_date = dtparse(data['CreationDate']).date()
        self.created_by = str(data['CreatedBy'])
        # modification time format is hh:mm(AM|PM)
        self.modification_time = dtparse(data['ModificationTime']).time()
        # modification date format is mm-dd-yyyy
        self.modification_date = dtparse(data['ModificationDate']).date()
        self.modified_by = str(data['ModifiedBy'])


class DeviceInfo:
    """This class encapsulates the Object Directory file's General Device
    Information identified in section [DeviceInfo] and ensures compliance with
    CANOpen Specification CiA 306 version 1.3.0"""

    def __init__(self, data: SectionProxy):
        """Create Device info using configparser section
        :param data: Device info section of data
        :type data: SectionProxy
        :raises KeyError: Indicates that a required entry is missing from the
        section. Check CiA 306 specification.
        :raises ValueError: Indicates that a type conversion failed"""

        self.vendor_name = str(data['VendorName'])
        self.vendor_number = int(data['VendorNumber'])
        self.product_name = str(data['ProductName'])
        self.product_number = int(data['ProductNumber'])
        self.revision_number = int(data['RevisionNumber'])
        # Listed as required in CiA 306, but not listed in example
        self.order_code = data.get('OrderCode', "")
        self.lss_supported = bool(data['LSS_Supported'])
        self.baud_rate_50 = bool(data['BaudRate_50'])
        self.baud_rate_250 = bool(data['BaudRate_250'])
        self.baud_rate_500 = bool(data['BaudRate_500'])
        self.baud_rate_1000 = bool(data['BaudRate_1000'])
        self.simple_boot_up_slave = bool(data['SimpleBootUpSlave'])
        self.simple_boot_up_master = bool(data['SimpleBootUpMaster'])
        self.nr_of_rx_pdo = int(data['NrOfRxPdo'])
        self.nr_of_tx_pdo = int(data['NrOfTxPdo'])


class DummyUsage:
    """This class encapsulates the Object Directory file's General Device
    Information identified in section [DeviceInfo] and ensures compliance with
    CANOpen Specification CiA 306 version 1.3.0"""

    def __init__(self, data: SectionProxy):
        """Dummy usage attributes are created dynamically because we do not
        know which indexes are selected for dummy usage. The format must use
        the following scheme defined in CiA 306:
        Dummy<data type index (without 0x-prefix)>={0|1}

        :param data: DeviceInfo section from OD file
        :type data: SectionProxy
        :raises KeyError: Indicates that the file was not generated correctly for this section
        :raises ValueError: Indicates that a type conversion failed"""

        for key in data:
            if len(key) != 9 or key[:5].lower() != "dummy":
                raise KeyError("Non dummy value in Dummy Usage section. Check "
                               "CiA 306")
            dummy_key = f"dummy_{key[5:]}"
            self.__setattr__(dummy_key, bool(data[key]))


class ObjectLists(list):
    """This class encapsulates the Object Directory file's object
    lists identified in sections [MandatoryObjects], [OptionalObjects] and
    [ManufacturerObjects] and ensures compliance with CANOpen Specification
    CiA 306 version 1.3.0"""

    def __init__(self, data: SectionProxy):
        """Object list data is stored as a list

        :param data: DeviceInfo section from OD file
        :type data: SectionProxy
        :raises KeyError: Indicates that the number of items in the object
        list does not match the supported objects attribute or the required
        supported objects attribute is missing.
        :raises ValueError: Indicates that a type conversion failed"""

        super().__init__()
        self.supported_objects = int(data['SupportedObjects'])
        for i in range(1, self.supported_objects + 1):
            self.append(data[str(i)])


class Index:
    """This class encapsulates the Object Directory file's index definitions
    identified in sections [<index>] and ensures compliance with CANOpen
    Specification CiA 306 version 1.3.0"""

    def __init__(self, data: SectionProxy):
        """Create index object from a given index Section
        :param data: index section from OD file
        :type data: SectionProxy
        :raises KeyError: indicates that a required attribute is missing
        :raises ValueError: Indicates that a type conversion failed"""

        # Sub number may be empty or missing of no sub objects exist
        sub_number = data.get('SubNumber', '0')
        sub_number = sub_number if sub_number is not None else '0'
        self.sub_number = int(sub_number)
        self.parameter_name = str(data['ParameterName'])
        # Per CiA 306 Object Type is optional and 0x7 (VAR) is to be used
        self.object_type = data.get('ObjectType', str(ObjectType.VAR))
        if self.object_type not in ObjectType.__members__:
            raise ValueError("Object type not identified")
        self.data_type = data.get('DataType')
        # Per CiA 306 Low and High Limit is optional
        self.low_limit = data.get('LowLimit')
        self.high_limit = data.get('HighLimit')
        self.access_type = data.get('AccessType')
        self.default_value = data.get('DefaultValue')
        self.pdo_mapping = data.get('PDOMapping')
        self.compact_sub_obj = data.get('CompactSubObj')
        self.obj_flags = data.get('ObjFlags', '0')

        # Type Dependent Validations
        if self.object_type == ObjectType.DOMAIN:
            self.data_type = self.data_type \
                if self.data_type is not None else DataType.DOMAIN
            self.access_type = self.access_type \
                if self.access_type is not None else "rw"
            if self.pdo_mapping is not None:
                raise ValueError("Invalid PDO Mapping")
            if self.sub_number == 0:
                raise ValueError("Invalid Sub Number")
            if self.low_limit is not None:
                raise ValueError("Invalid Low Limit")
            if self.high_limit is not None:
                raise ValueError("Invalid High Limit")
            if self.compact_sub_obj is not None:
                raise ValueError("Invalid Compact Sub Obj")
            if self.data_type not in DataType:
                raise ValueError("Data type not identified")

        elif self.object_type in ObjectType.COMPLEX_TYPES \
                and self.compact_sub_obj is None:
            if self.data_type is not None:
                raise ValueError("Invalid Data Type")
            if self.access_type is not None:
                raise ValueError("Invalid Access Type")
            if self.default_value is not None:
                raise ValueError("Invalid Default Value")
            if self.pdo_mapping is not None:
                raise ValueError("Invalid PDO Mapping")
            if self.sub_number == 0:
                raise ValueError("Invalid Sub Number")
            if self.low_limit is not None:
                raise ValueError("Invalid Low Limit")
            if self.high_limit is not None:
                raise ValueError("Invalid High Limit")

        elif self.object_type in ObjectType.COMPLEX_TYPES:
            self.pdo_mapping = bool(
                self.pdo_mapping) if self.pdo_mapping is not None else False
            if self.sub_number != 0:
                raise ValueError("Invalid Sub Number")
            if self.data_type not in DataType:
                raise ValueError("Data type not identified")

        elif self.object_type in (ObjectType.DEFTYPE, ObjectType.VAR):
            self.pdo_mapping = bool(
                self.pdo_mapping) if self.pdo_mapping is not None else False
            if self.sub_number != 0:
                raise ValueError("Invalid Sub Number")
            if self.compact_sub_obj is not None:
                raise ValueError("Invalid Compact Sub Obj")
            if self.data_type not in DataType:
                raise ValueError("Data type not identified")

        else:
            raise ValueError(f"Invalid Object Type {self.object_type}")


class OD:
    def __init__(self):
        self.node_id = None
        self.indices = {}
        self.device_commissioning = None
        # tools section is optional per CiA 306
        self.tools = None
        self.file_info = None
        self.device_info = None
        self.dummy_usage = None
        # comments section is optional per CiA 306
        self.comments = None
        self.mandatory_objects = None
        self.optional_objects = None
        self.manufacturer_objects = None

    # consider class method if we can avoid using constructor with no
    # parameters
    def extended_pdo_definition(self, offset: int) -> OD:
        # TODO: Move to constant with message types
        pdo_tx = 0x1A00
        pdo_tx_offset = 0x1A00 + (offset * 4)
        pdo_rx = 0x1600
        pdo_rx_offset = 0x1600 + (offset * 4)
        node = OD()
        node.node_id = copy.deepcopy(self.node_id)
        node.device_commissioning = copy.deepcopy(self.device_commissioning)
        node.tools = copy.deepcopy(self.tools)
        node.file_info = copy.deepcopy(self.file_info)
        node.device_info = copy.deepcopy(self.device_info)
        node.dummy_usage = copy.deepcopy(self.dummy_usage)
        node.comments = copy.deepcopy(self.dummy_usage)
        node.mandatory_objects = copy.deepcopy(self.dummy_usage)
        node.optional_objects = copy.deepcopy(self.optional_objects)
        node.manufacturer_objects = copy.deepcopy(self.manufacturer_objects)

        if (pdo_tx_offset not in self and pdo_rx_offset not in self) or \
                (self[pdo_tx_offset].parameter_name != "TPDO mapping parameter"
                 and self[
                     pdo_rx_offset].parameter_name != "RPDO mapping parameter"):
            raise KeyError("Extended PDO definitions not found")

        self.get_pdo_offset(node, pdo_tx, pdo_tx_offset)
        self.get_pdo_offset(node, pdo_rx, pdo_rx_offset)

        return node

    def get_pdo_offset(self, node: OD, start: int, offset: int):
        while offset in self:
            node[start] = copy.deepcopy(self[offset])
            start += 1
            offset += 1
            if start % 4 == 0:
                break

    def __len__(self) -> int:
        return sum(map(lambda x: len(x), self.indices.values()))

    def __getitem__(self, key: Union[int, str]) -> LegacyIndex:
        callable = hex if type(key) == int else str
        key = callable(key)
        if key not in self.indices:
            raise KeyError(key[2:])

        return self.indices[key]

    def __setitem__(self, key, value):
        callable = hex if type(key) == int else str
        key = callable(key)
        self.indices[key] = value

    def __contains__(self, item):
        callable = hex if type(item) == int else str
        item = callable(item)
        return item in self.indices


def parse_function(section: str) -> Callable:

    parsers = {
        'FileInfo': FileInfo,
        'DeviceInfo': DeviceInfo,
        'DummyUsage': DummyUsage,
        'MandatoryObjects': ObjectLists,
        'OptionalObjects': ObjectLists,
        'ManufacturerObjects': ObjectLists,
        'Comments': lambda x: None,
        'Tools': lambda x: None,
        'DeviceCommissioning': lambda x: None
    }

    if section not in parsers:
        if re.search(r"([0-9a-fA-F]+|[0-9a-fA-F]+sub[0-9a-fA-F]+)", section) is not None:
            return Index
        else:
            breakpoint()

    return parsers.get(section, lambda x: None)


class FileOD(OD):
    def __init__(self, od_file):
        super().__init__()
        parser = ConfigParser(allow_no_value=True)
        with open(od_file) as file:
            parser.read_file(file.readlines())

        for section in parser.sections():
            parse_function(section)(parser[section])


class EDS(OD):
    def __init__(self, eds_data: [str]):
        """Parse the array of EDS lines into a dictionary of Metadata/Index
        objects.

        :param eds_data: The list of raw lines from the EDS file.
        :type eds_data: [str]
        """
        super().__init__()
        self.indices = {}

        prev = 0
        for i, line in enumerate(eds_data):
            if line == '' or i == len(eds_data) - 1:
                # Handle extra empty strings
                if prev == i:
                    prev = i + 1
                    continue

                section = eds_data[prev:i]
                id = section[0][1:-1].split('sub')

                if all(c in string.hexdigits for c in id[0]):
                    index = hex(int(id[0], 16))
                    if len(id) == 1:
                        self.indices[index] = LegacyIndex(section[1:], index)
                    else:
                        self.indices[index] \
                            .add(LegacyIndex(section[1:], int(id[1], 16),
                                             is_sub=True))
                else:
                    name = section[0][1:-1]
                    self.__setattr__(camel_to_snake(name),
                                     Metadata(section[1:]))
                prev = i + 1

        if self.device_commissioning is not None:
            self.node_id = convert_value(self.device_commissioning.node_id)
        elif '0x2101' in self.indices.keys():
            self.node_id = self['0x2101'].default_value
        else:
            self.node_id = None


def load_eds_file(filepath: str) -> EDS:
    """Read in the EDS file, grab the raw lines, strip them of all escaped
    characters, then serialize into an `EDS` and return the resulting
    object.

    :param filepath: Path to an eds file
    :type filepath: str

    :return: The successfully serialized EDS file.
    :rtype: EDS
    """
    with open(filepath) as file:
        return EDS(list(map(lambda x: x.strip(), file.read().split('\n'))))


def load_eds_files(filepath: str) -> dict:
    """Read a directory of OD files

    :param filepath: Directory to load files from
    :type filepath: str
    :return: dictionary of OD files with node id as key and OD as value
    :rtype: dict
    """
    configs = {}
    for file in os.listdir(filepath):
        full_path = f'{filepath}/{file}'
        if file.lower().endswith(".eds") or file.lower().endswith(".dcf"):
            # config = load_eds_file(full_path)
            config = FileOD(full_path)
            configs[config.node_id] = config
            try:
                for i in range(config.device_info.nr_of_rxpdo):
                    extended_node = config.extended_pdo_definition(i + 1)
                    configs[config.node_id + i] = extended_node
            except KeyError:
                ...

    return configs
