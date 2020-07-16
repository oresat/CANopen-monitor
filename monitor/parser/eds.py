"""EDS File Parser Interface"""
from re import finditer
from dateutil.parser import parse as dtparse


def camel_to_snake(string):
    res = ""

    if(string[0] != ';'):
        for i in finditer('[A-Z0-9][a-z0-9]*', string):
            span = i.span()
            if(span[0] != 0):
                res += '_'
            res += string[span[0]:span[1]].lower()
    return res


class Metadata:
    def __init__(self, name, data):
        self.name = name

        for e in data:
            key, value = e.split('=')
            key = camel_to_snake(key)
            if('time' in key):
                value = dtparse(value).time()
            elif('date' in key):
                value = dtparse(value).date()
            self.__setattr__(key, value)

    def __str__(self):
        res = self.name + ':\n'
        for key, value in self.__dict__.items():
            res += '\t\t' + str(key) + ': ' + str(value) + '\n'
        return res


class Index:
    """
    Index Class is used to contain data from a single section of a .eds file
    Note: Not all possible properties are stored
    """

    def __init__(self, id, data, sub_id=None):
        self.id = id

        if(sub_id is None):
            self.sub_indices = []
        else:
            self.sub_id = sub_id

        for e in data:
            key, value = e.split('=')
            if(value.isnumeric()):
                value = int(value)
            self.__setattr__(camel_to_snake(key), value)

    def add_subindex(self, index):
        self.sub_indices.append(index)

    def get_subindex(self, i):
        return filter(lambda x: x.sub_id == i, self.sub_indices)

    def __str__(self):
        res = str(self.id)
        if(self.sub_indices is not None):
            res += "(sub-indicies: " + str(len(self.sub_indices)) + "):\n"
        for key, value in self.__dict__.items():
            res += "\t" + str(key) + ': ' + str(value) + '\n'
        return res


def parse(eds_data):
    """
    Parse the array of EDS lines into a dictionary of Metadata/Index objects.
    """
    indices = {}

    prev = 0
    for i, line in enumerate(eds_data):
        if(line == ''):
            section = eds_data[prev:i]
            id = section[0][1:-1].split('sub')

            if(id[0].isnumeric()):
                if(len(id) == 1):
                    indices[int(id[0])] = Index(int(id[0]), section[1:])
                else:
                    indices[int(id[0])].add_subindex(Index(int(id[0]),
                                                           section[1:],
                                                           sub_id=int(id[1])))
            else:
                name = section[0][1:-1]
                indices[name] = Metadata(name, section[1:])
            prev = i + 1
    return indices


def load_eds_file(filepath):
    """
    Read in the EDS file, grab the raw lines, then parse them and return
    the dictionary of Metadata/Index objects.
    """
    raw_lines = []

    file = open(filepath)
    for line in file:
        raw_lines.append(line.strip())
    file.close()

    return parse(raw_lines)
