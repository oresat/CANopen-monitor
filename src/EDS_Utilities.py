"""EDS File Processing Library"""
import re
import os
import pprint


class EDSFile:
    PARAMETER_NAME = "ParameterName"
    OBJECT_TYPE = "ObjectType"
    NODE_PATTERN = r"\[((\d+)|(\d+sub\d+))\]"  # [1+digits] OR [1+digits"sub"1+digits]
    ANY_HEADER_PATTERN = r"\[(.+)\]"  # [any characters]
    VALUE_PATTERN = r"(.+)=(.*)\n"
    NODE_INFO = "FileInfo"
    NODE_DESCRIPTION = "Description"

    def __init__(self, location):
        self._location = location
        self._nodes = {}
        self.load_files()

    def get_nodes(self):
        """Get a list of nodes loaded in to system

        :returns list of nodes
        """
        return self._nodes.keys()

    def get_description(self, node):
        """Get Node Description

        :returns description string
        :raises ValueError: If node does not exist"""
        find = self.get_address(node, self.NODE_INFO)
        return self._nodes[node][find][self.NODE_DESCRIPTION]

    def get_address(self, node, index, sub_index=None):
        """Get an string address used to find node data meant for internal use

        :returns address string
        :raises ValueError if node, index and sub_index combination cannot be found
        """
        if node not in self._nodes:
            raise ValueError(f"Invalid Node '{node}'")

        if sub_index is not None:
            find = f"{index}sub{sub_index}"
        else:
            find = str(index)

        if find not in self._nodes[node]:
            raise ValueError(f"Invalid Index '{find}'")

        return find

    def get_name(self, node, index, sub_index=None):
        """Get name of value at index

        :returns name at index string
        :raises ValueError if node, index and sub_index combination cannot be found
        """
        find = self.get_address(node, index, sub_index)
        return self._nodes[node][find][self.PARAMETER_NAME]

    def get_type(self, node, index, sub_index=None):
        """Get type of value at index

        :returns type at index string
        :raises ValueError if node, index and sub_index combination cannot be found
        """
        find = self.get_address(node, index, sub_index)
        return self._nodes[node][find][self.OBJECT_TYPE]

    def load_files(self, filepath=None):
        """Load all files from given folder into self._nodes

        :param filepath: The folder to load .eds files from
        """
        if filepath is None:
            filepath = self._location
        for filename in os.listdir(filepath):
            if filename.endswith(".eds"):
                name = os.path.splitext(filename)
                self._nodes[name[0]] = {}
                new_node = self._nodes[name[0]]
                with open(filename) as f:
                    current_line = f.readline()
                    node_regex = re.compile(self.ANY_HEADER_PATTERN)
                    value_regex = re.compile(self.VALUE_PATTERN)
                    while current_line:
                        node = node_regex.search(current_line)
                        if node is not None:
                            index = node.group(1)
                            current_line = f.readline()
                            while current_line != "\n" and current_line != "":
                                value = value_regex.search(current_line)
                                if index not in new_node:
                                    new_node[index] = {}
                                new_node[index].update({value.group(1): value.group(2)})
                                current_line = f.readline()

                        current_line = f.readline()


if __name__ == "__main__":
    # This is for testing the library
    test = EDSFile(os.getcwd())

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(test._nodes)
    for test_node in test.get_nodes():
        print(test.get_description(test_node))
    print(test.get_name("test", 3000))
    print(test.get_type("test", 3000))
    print(test.get_name("test", 3000, 0))
    print(test.get_type("test", 3000, 0))
