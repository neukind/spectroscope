import importlib
from pkg_resources import iter_entry_points
from pydantic import BaseModel
from spectroscope.module import ConfigOption
from typing import Dict, List


SYSTEM_MODULE_CONFIG = {
    "spectroscope": [
        ConfigOption(
            name="eth2_endpoint",
            param_type=str,
            description="URI of the gRPC endpoint to connect to",
        ),
        ConfigOption(
            name="pubkeys",
            param_type=list,
            description="List of hex-encoded public keys to watch",
            default=[
                "0x933ad9491b62059dd065b560d256d8957a8c402cc6e8d8ee7290ae11e8f7329267a8811c397529dac52ae1342ba58c95",
                "0x8a30c341a1b23abc54affb82c13a71eaf69d770debea914ec2f8f26b6c762b0da2a5878c33e75a46602c7116b70161a2",
            ],
        ),
    ]
}


class DefaultConfigBuilder:
    @staticmethod
    def build() -> Dict[str, List[ConfigOption]]:
        config_data = dict(SYSTEM_MODULE_CONFIG)

        for module_ep in iter_entry_points("spectroscope.module"):
            module = module_ep.load()
            config_data[module_ep.name] = module.config_options

        return config_data
