"""This module is primarily responsible for providing a high-level interface
for parsing CANOpen messages according to Object Definiton files or Electronic
Data Sheet files, provided by the end user.
"""
from .eds import EDS, load_eds_file, load_eds_files, DataType
from .canopen import CANOpenParser

__all__ = [
    'CANOpenParser',
    'EDS',
    'load_eds_file',
    'DataType',
    'load_eds_files'
]
