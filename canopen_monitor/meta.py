from .can import MagicCANBus
from os import path
import json


class Meta:
    def __init__(self, config_dir, cache_dir):
        self.config_dir = config_dir
        self.cache_dir = cache_dir
        self.interfaces_file = self.config_dir + '/interfaces.json'
        self.nodes_file = self.config_dir + '/nodes.json'

    def save_devices(self, mcb: MagicCANBus) -> bool:
        output = {'interfaces': mcb.interface_list}
        with open(self.interfaces_file, "w") as f:
            json.dump(output, f)
            f.truncate()

    def load_devices(self, interface_args: [str]) -> [str]:
        if not path.isfile(self.interfaces_file):
            return interface_args

        with open(self.interfaces_file, "r") as f:
            interface_config = json.load(f)
            for interface in interface_config['interfaces']:
                if interface not in interface_args:
                    interface_args.append(interface)

        return interface_args

    def load_node_overrides(self) -> dict:
        pass
