"""EDS File Processing Library"""
import re
import configparser
import os
import pprint

PARAMETER_NAME = "ParameterName"
OBJECT_TYPE = "ObjectType"
DATA_TYPE = "DataType"
DEFAULT_VALUE = "DefaultValue"
NODE_PATTERN = r"((\d+)|(\d+sub\d+))"  # [1+digits] OR [1+digits"sub"1+digits]
CAN_NODE_ID = "CAN node ID"


class EDSFile:
    """
    EDSFile Class is used to contain data from a single .eds file
    """
    def __init__(self, filename):
        self.filename = filename
        self.node_id = None
        self.index = {}


class IndexData:
    """
    IndexData Class is used to contain data from a single section of a .eds file
    Note: Not all possible properties are stored
    """
    def __init__(self):
        self.parameter_name = None  # parameter_name
        self.parent_name = None  # parent parameter name (for sub-indices)
        self.object_type = None  # object_type
        self.data_type = None  # data_type
        self.default_value = None  # default_value


def load_eds_files(filepath):
    """
    Load all eds files from a given root folder (Checks all subdirectories)
    Dictionary can be accessed like: data[0x12].index[0x300000].parameter_name
    :param filepath: the root directory from which the search starts
    :return: a dictionary of of EDSFile objects, with the NodeID hex value as a key
    """
    eds_files = {}
    eds_parser = configparser.ConfigParser()
    for root, _, filenames in os.walk(filepath):
        for filename in filenames:
            if not filename.endswith(".eds"):
                continue
            new_node = EDSFile(filename)
            eds_parser.read(root + "/" + filename)
            for section_title in eds_parser.sections():
                index = re.match(NODE_PATTERN, section_title)
                if index is None:
                    continue

                section = eds_parser[section_title]
                section_data = IndexData()
                section_data.parameter_name = section.get(PARAMETER_NAME)
                section_data.data_type = section.get(DATA_TYPE)
                section_data.default_value = section.get(DEFAULT_VALUE)
                section_data.object_type = section.get(OBJECT_TYPE)

                if section_data.parameter_name == CAN_NODE_ID:
                    new_node.node_id = section_data.default_value

                if "sub" in section_title:
                    locations = str(section_title).split("sub")
                    location = (int(locations[0], 16) << 8) + (int(locations[1], 16))
                    section_data.parent_name = eds_parser[locations[0]][PARAMETER_NAME]
                else:
                    location = int(section_title, 16) << 8

                new_node.index[location] = section_data
            eds_files[int(new_node.node_id, 16)] = new_node

    return eds_files


if __name__ == "__main__":
    """Function for testing, requires a eds file to be in the current directory or subdirectory"""
    data = load_eds_files(os.getcwd())
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(vars(data[0x12].index[0x300000]))
