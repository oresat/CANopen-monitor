"""This module is primarily responsible for providing a high-level interface
for parsing CANOpen messages according to Object Definiton files or Electronic
Data Sheet files, provided by the end user.
"""
import enum
from re import finditer
from .eds import EDS, load_eds_file
from .canopen import CANOpenParser

__all__ = [
    'CANOpenParser',
    'EDS',
    'load_eds_file',
]


# Seems like it needs comments. It's not clear to me what this is doing (this may change after consulting the docs)
# If the goal is to simply lowercase a string, this seems a bit convoluted
def camel_to_snake(old_name: str) -> str:
    new_name = ''

    for match in finditer('[A-Z0-9]+[a-z]*', old_name):
        span = match.span()
        substr = old_name[span[0]:span[1]]
        # length = span[1] - span[0] <- Not needed?
        found_submatch = False

        for sub_match in finditer('[A-Z]+', substr):
            sub_span = sub_match.span()
            sub_substr = old_name[sub_span[0]:sub_span[1]]
            sub_length = sub_span[1] - sub_span[0]

            if (sub_length > 1):
                found_submatch = True

                if (span[0] != 0):
                    new_name += '_'

                first = sub_substr[:-1]
                second = substr.replace(first, '')

                new_name += '{}_{}'.format(first, second).lower()

        if (not found_submatch):
            if (span[0] != 0):
                new_name += '_'

            new_name += substr.lower()

    return new_name
