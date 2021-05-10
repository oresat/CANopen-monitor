from .can import MagicCANBus


class Meta:
    def __init__(self, config_dir, cache_dir):
        self.config_dir = config_dir
        self.cache_dir = cache_dir

    def save_devices(self, mcb: MagicCANBus) -> bool:
        # TODO: Save the list of devices in MCB
        pass

    def load_devices(self) -> [str]:
        # TODO: Pass back list of interface names to populate MCB
        pass

    def load_node_overrides(self) -> dict:
        pass
