import string
from typing import Union
import canopen_monitor.parse as cmp
from dateutil.parser import parse as dtparse


class Metadata:
    def __init__(self, data):
        # Process all sub-data
        for e in data:
            # Skip comment lines
            if(e[0] == ';'):
                continue

            # Separate field name from field value
            key, value = e.split('=')

            # Create the proper field name
            key = cmp.camel_to_snake(key)

            # Turn date-time-like objects into datetimes
            if ('time' in key):
                value = dtparse(value).time()
            elif ('date' in key):
                value = dtparse(value).date()

            # Set the attribute
            self.__setattr__(key, value)


class Index:
    """
    Index Class is used to contain data from a single section of an .eds file
    Note: Not all possible properties are stored
    """

    def __init__(self, data, sub_id=None):
        # Determine if this is a parent index or a child index
        if (sub_id is None):
            self.is_parent = True
            self.sub_indices = []
        else:
            self.is_parent = False
            self.sub_id = sub_id
            self.sub_indices = None

        # Process all sub-data
        for e in data:
            # Skip commented lines
            if(e[0] == ';'):
                continue

            # Separate field name from field value
            key, value = e.split('=')

            # Turn number-like objects into numbers
            if(value != ''):
                if (all(c in string.digits for c in value)):
                    value = int(value, 10)
                elif(all(c in string.hexdigits for c in value)):
                    value = int(value, 16)

            self.__setattr__(cmp.camel_to_snake(key), value)

    def add(self, index) -> None:
        self.sub_indices.append(index)

    def __getitem__(self, key: int):
        return list(filter(lambda x: x.sub_id == key, self.sub_indices))[0]

    def __len__(self) -> int:
        if(self.sub_indices is None):
            return 1
        else:
            return 1 + sum(map(lambda x: len(x), self.sub_indices))


class EDS:
    def __init__(self, eds_data: [str]):
        """Parse the array of EDS lines into a dictionary of Metadata/Index
        objects.

        :param eds_data: The list of raw lines from the EDS file.
        :type eds_data: [str]
        """
        self.indices = {}

        prev = 0
        for i, line in enumerate(eds_data):
            if line == '':
                section = eds_data[prev:i]
                id = section[0][1:-1].split('sub')

                if all(c in string.hexdigits for c in id[0]):
                    if len(id) == 1:
                        self.indices[hex(int(id[0], 16))] = Index(section[1:])
                    else:
                        self.indices[hex(int(id[0], 16))] \
                            .add(Index(section[1:], sub_id=int(id[1], 16)))
                else:
                    name = section[0][1:-1]
                    self.__setattr__(cmp.camel_to_snake(name),
                                     Metadata(section[1:]))
                prev = i + 1
        self.node_id = self[0x2101].default_value

    def __len__(self) -> int:
        return sum(map(lambda x: len(x), self.indices.values()))

    def __getitem__(self, key: Union[int, str]) -> Index:
        callable = hex if type(key) == int else str
        return self.indices.get(callable(key))


def load_eds_file(filepath: str) -> EDS:
    """Read in the EDS file, grab the raw lines, strip them of all escaped
    characters, then serialize into an `EDS` and return the resulpythting
    object.

    :param filepath: Path to an eds file
    :type filepath: str

    :return: The succesfully serialized EDS file.
    :rtype: EDS
    """
    with open(filepath) as file:
        return EDS(list(map(lambda x: x.strip(), file.read().split('\n'))))
