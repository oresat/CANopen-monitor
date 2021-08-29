from __future__ import annotations
import copy
import string
from re import finditer
from typing import Union
from dateutil.parser import parse as dtparse
import os
from enum import Enum


class DataType(Enum):
    BOOLEAN = '0x0001'
    INTEGER8 = '0x0002'
    INTEGER16 = '0x0003'
    INTEGER32 = '0x0004'
    UNSIGNED8 = '0x0005'
    UNSIGNED16 = '0x0006'
    UNSIGNED32 = '0x0007'
    REAL32 = '0x0008'
    VISIBLE_STRING = '0x0009'
    OCTET_STRING = '0x000A'
    UNICODE_STRING = '0x000B'
    TIME_OF_DAY = '0x000C'
    TIME_DIFFERENCE = '0x000D'
    DOMAIN = '0x000F'
    INTEGER24 = '0x0010'
    REAL64 = '0x0011'
    INTEGER40 = '0x0012'
    INTEGER48 = '0x0013'
    INTEGER56 = '0x0014'
    INTEGER64 = '0x0015'
    UNSIGNED24 = '0x0016'
    UNSIGNED40 = '0x0018'
    UNSIGNED48 = '0x0019'
    UNSIGNED56 = '0x001A'
    UNSIGNED64 = '0x001B'
    PDO_COMMUNICATION_PARAMETER = '0x0020'
    PDO_MAPPING = '0x0021'
    SDO_PARAMETER = '0x0022'
    IDENTITY = '0x0023'

    # Used by ECSS Time feature only
    ECSS_TIME = 'ECSS_TIME'

    # Data Type Groupings
    UNSIGNED_INTEGERS = (UNSIGNED8, UNSIGNED16, UNSIGNED32, UNSIGNED24,
                         UNSIGNED40, UNSIGNED48, UNSIGNED56, UNSIGNED64)

    SIGNED_INTEGERS = (INTEGER8, INTEGER16, INTEGER32, INTEGER24,
                       INTEGER40, INTEGER48, INTEGER56, INTEGER64)

    FLOATING_POINTS = (REAL32, REAL64)

    NON_FORMATTED = (DOMAIN, PDO_COMMUNICATION_PARAMETER, PDO_MAPPING,
                     SDO_PARAMETER, IDENTITY)


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


class Index:
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

    def add(self, index: Index) -> None:
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
        if value.startswith("0x") and all(c in string.hexdigits for c in value):
            return int(value[2:], 16)
        if (all(c in string.digits for c in value)):
            return int(value, 10)
        elif (all(c in string.hexdigits for c in value)):
            return int(value, 16)
        else:
            return value


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
        node.indices = copy.deepcopy(self.indices)

        if (pdo_tx_offset not in self and pdo_rx_offset not in self) or \
                (self[pdo_tx_offset].parameter_name != "TPDO mapping parameter"
                 and self[pdo_rx_offset].parameter_name != "RPDO mapping parameter"):

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

    def __getitem__(self, key: Union[int, str]) -> Index:
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
                        self.indices[index] = Index(section[1:], index)
                    else:
                        self.indices[index] \
                            .add(Index(section[1:], int(id[1], 16),
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


def load_eds_file(filepath: str, enable_ecss: bool = False) -> EDS:
    """Read in the EDS file, grab the raw lines, strip them of all escaped
    characters, then serialize into an `EDS` and return the resulting
    object.

    :param filepath: Path to an eds file
    :type filepath: str
    :param enable_ecss: Flag to enable ECSS time, defaults to False
    :type enable_ecss: bool, optional
    :return: The successfully serialized EDS file.
    :rtype: EDS
    """
    with open(filepath) as file:
        od = EDS(list(map(lambda x: x.strip(), file.read().split('\n'))))
        if enable_ecss and 0x2101 in od:
            od[0x2101].data_type = DataType.ECSS_TIME.value
        return od


def load_eds_files(filepath: str, enable_ecss: bool = False) -> dict:
    """Read a directory of OD files

    :param filepath: Directory to load files from
    :type filepath: str
    :param enable_ecss: Flag to enable ECSS time, defaults to False
    :type enable_ecss: bool, optional
    :return: dictionary of OD files with node id as key and OD as value
    :rtype: dict
    """
    configs = {}
    for file in os.listdir(filepath):
        full_path = f'{filepath}/{file}'
        if file.lower().endswith(".eds") or file.lower().endswith(".dcf"):
            config = load_eds_file(full_path, enable_ecss)
            configs[config.node_id] = config
            try:
                i = 1
                while True:
                    extended_node = config.extended_pdo_definition(i)
                    configs[config.node_id+i] = extended_node
                    i += 1
            except KeyError:
                ...

    return configs
