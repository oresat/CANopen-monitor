from __future__ import annotations
from abc import ABC

import os

from .can import MagicCANBus
from os import path
import json
from json import JSONDecodeError


class Meta:
    def __init__(self, config_dir, cache_dir):
        self.config_dir = config_dir
        self.cache_dir = cache_dir
        self.interfaces_file = self.config_dir + '/interfaces.json'
        self.nodes_file = self.config_dir + '/nodes.json'
        self.feature_file = self.config_dir + '/features.json'

    def save_interfaces(self, mcb: MagicCANBus) -> None:
        interfaceConfig = InterfaceConfig()
        interfaceConfig.interfaces = mcb.interface_list
        write_config(self.interfaces_file, interfaceConfig)

    def load_interfaces(self, interface_args: [str]) -> [str]:
        interfaceConfig = InterfaceConfig()
        load_config(self.interfaces_file, interfaceConfig)
        for interface in interfaceConfig.interfaces:
            if interface not in interface_args:
                interface_args.append(interface)

        return interface_args

    def load_features(self) -> FeatureConfig:
        features = FeatureConfig()
        load_config(self.feature_file, features)
        return features

    def load_node_overrides(self) -> dict:
        pass


def write_config(filename: str, config: Config) -> None:
    output = config.__dict__
    with open(filename, "w") as f:
        json.dump(output, f, indent=4)
        f.truncate()


def load_config(filename: str, config: Config) -> None:
    try:
        if not path.isfile(filename):
            return write_config(filename, config)

        with open(filename, "r") as f:
            json_data = json.load(f)

        parsed_version = str(json_data.get('version', '1.0')).split('.')

        # Major version mismatch or invalid version indicates a breaking change
        if len(parsed_version) != 2 or not parsed_version[0].isnumeric() or\
                not parsed_version[1].isnumeric() or int(parsed_version[0]) != config.MAJOR:
            return overwrite_config(filename, config)

        return config.load(json_data)

    except (JSONDecodeError, OSError, IOError):
        return overwrite_config(filename, config)


def overwrite_config(filename: str, config: Config) -> None:
    if path.isfile(filename):
        backup_filename = filename + ".bak"
        count = 1
        while path.isfile(backup_filename):
            backup_filename = filename + f"-{count}.bak"
            count += 1

        os.rename(filename, backup_filename)

    return write_config(filename, config)


class Config(ABC):
    MAJOR = 1
    MINOR = 0

    def __init__(self, major: int, minor: int):
        self.version = f"{major}.{minor}"

    def load(self, data: dict) -> None:
        self.version = data.get('version', self.version)


class FeatureConfig(Config):
    MAJOR = 1
    MINOR = 0

    def __init__(self):
        super().__init__(self.MAJOR, self.MINOR)
        self.ecss_time = False

    def load(self, data: dict) -> None:
        super().load(data)
        self.ecss_time = data.get('ecss_time', self.ecss_time)


class InterfaceConfig(Config):
    MAJOR = 1
    MINOR = 0

    def __init__(self):
        super().__init__(self.MAJOR, self.MINOR)
        self.interfaces = []

    def load(self, data: dict) -> None:
        super().load(data)

        loaded_interfaces = data.get('interfaces', self.interfaces)
        for interface in loaded_interfaces:
            self.interfaces.append(interface)
