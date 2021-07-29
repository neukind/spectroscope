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
            default=[],
        ),
    ],
    "database": [
        ConfigOption(
            name="database_uri",
            param_type=str,
            description="Uri of the mongodb database",
            default="mongodb://localhost:27017",
        ),
        ConfigOption(
            name="database_name",
            param_type=str,
            description="The database name of the mongodb",
            default="spectroscope",
        ),
        ConfigOption(
            name="database_collection",
            param_type=str,
            description="The collection name of the mongodb",
            default="validators",
        ),
    ],
}


class DefaultConfigBuilder:
    @staticmethod
    def build() -> Dict[str, List[ConfigOption]]:
        config_data = dict(SYSTEM_MODULE_CONFIG)

        for module_ep in iter_entry_points("spectroscope.module"):
            module = module_ep.load()
            config_data[module_ep.name] = module.config_options

        return config_data
